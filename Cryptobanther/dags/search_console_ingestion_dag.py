from __future__ import annotations
from datetime import datetime, timedelta
import json
import logging

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
    dag_id="search_console_ingestion",
    default_args=default_args,
    description="Daily Google Search Console search performance ingestion",
    schedule_interval="0 7 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ingestion", "gsc", "gcp"],
    on_failure_callback=on_failure_callback,
) as dag:

    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    def check_gsc_api(**context) -> None:
        from ingestion.search_console.client import SearchConsoleClient
        client = SearchConsoleClient()
        sites = client.get_verified_sites()
        if not sites:
            raise ValueError("No verified GSC sites found — check service account permissions")
        logger.info("GSC API check passed, found %d verified sites: %s", len(sites), sites)

    check_api = PythonOperator(
        task_id="check_api",
        python_callable=check_gsc_api,
    )

    extract_load = KubernetesPodOperator(
        **k8s_config.get_pod_defaults(
            task_id="extract_load",
            arguments=[
                "python", "-m", "ingestion.search_console.extractor",
                "--execution-date", "{{ ds }}",
                "--site-urls", "{{ var.value.gsc_site_urls }}",
                "--project-id", "{{ var.value.gcp_project_id }}",
                "--dataset-id", "{{ var.value.bq_dataset_raw }}",
                "--lookback-days", "3",
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
            source_system="GSC",
            target_table=f"{project_id}.{raw_dataset}.gsc_search_performance",
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
