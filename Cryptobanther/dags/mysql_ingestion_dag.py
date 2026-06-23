from __future__ import annotations
from datetime import datetime, timedelta
import json
import logging
import os

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator

from plugins.bq_logger import BQLogger, PipelineLog
from plugins.slack_alerter import on_failure_callback
from plugins import k8s_config

logger = logging.getLogger(__name__)

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": on_failure_callback,
}

with DAG(
    dag_id="mysql_ingestion",
    default_args=default_args,
    description="Daily MySQL OLTP incremental ingestion to BigQuery",
    schedule_interval="0 5 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ingestion", "mysql", "gcp"],
    on_failure_callback=on_failure_callback,
) as dag:

    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    def check_mysql_connection(**context) -> None:
        from ingestion.mysql.client import MySQLClient
        from sqlalchemy import text
        mysql_host = os.environ.get("MYSQL_HOST") or Variable.get("mysql_host", default_var="")
        mysql_port = int(os.environ.get("MYSQL_PORT", "3306"))
        mysql_db = os.environ.get("MYSQL_DATABASE") or Variable.get("mysql_database", default_var="")
        mysql_user = os.environ.get("MYSQL_USER") or Variable.get("mysql_user", default_var="")
        mysql_pass = os.environ.get("MYSQL_PASSWORD") or Variable.get("mysql_password", default_var="")

        client = MySQLClient(
            host=mysql_host,
            port=mysql_port,
            database=mysql_db,
            user=mysql_user,
            password=mysql_pass,
        )
        engine = client._get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 AS health_check"))
            row = result.fetchone()
            if row is None or row[0] != 1:
                raise ValueError("MySQL health check failed — unexpected result")
        client.close()
        logger.info("MySQL connection check passed for database %s@%s", mysql_db, mysql_host)

    check_api = PythonOperator(
        task_id="check_api",
        python_callable=check_mysql_connection,
    )

    extract_load = KubernetesPodOperator(
        **k8s_config.get_pod_defaults(
            task_id="extract_load",
            arguments=[
                "python", "-m", "ingestion.mysql.extractor",
                "--execution-date", "{{ ds }}",
                "--table-config", "{{ var.value.mysql_tables_config }}",
                "--project-id", "{{ var.value.gcp_project_id }}",
                "--dataset-id", "{{ var.value.bq_dataset_raw }}",
            ],
        )
    )

    def log_execution(**context) -> None:
        xcom_raw = context["task_instance"].xcom_pull(task_ids="extract_load")
        if xcom_raw:
            try:
                xcom_str = str(xcom_raw)
                if "XCOM: " in xcom_str:
                    result = json.loads(xcom_str.split("XCOM: ")[-1])
                else:
                    result = json.loads(xcom_str)
            except Exception:
                result = {"status": "UNKNOWN", "rows_loaded": 0}
        else:
            result = {"status": "UNKNOWN", "rows_loaded": 0}

        project_id = Variable.get("gcp_project_id")
        dataset_id = Variable.get("bq_dataset_logging", default_var="logging")
        raw_dataset = Variable.get("bq_dataset_raw", default_var="raw")

        entry = PipelineLog.from_airflow_context(
            context=context,
            source_system="MYSQL",
            target_table=f"{project_id}.{raw_dataset}.mysql_transactions",
            rows_extracted=result.get("rows_loaded", 0),
            rows_loaded=result.get("rows_loaded", 0),
            status=result.get("status", "UNKNOWN"),
            error_message=result.get("error"),
            extra=result,
        )
        bq_logger = BQLogger(project_id=project_id, dataset_id=dataset_id)
        bq_logger.log(entry)
        logger.info("Pipeline execution logged: status=%s rows=%s", entry.status, entry.rows_loaded)

    log_exec = PythonOperator(
        task_id="log_execution",
        python_callable=log_execution,
    )

    start >> check_api >> extract_load >> log_exec >> end
