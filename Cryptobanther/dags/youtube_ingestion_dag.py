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
    dag_id="youtube_ingestion",
    default_args=default_args,
    description="Daily YouTube channel and video stats ingestion",
    schedule_interval="0 6 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ingestion", "youtube", "gcp"],
    on_failure_callback=on_failure_callback,
) as dag:

    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    def check_youtube_api(**context) -> None:
        from ingestion.youtube.client import YouTubeClient
        channel_ids_str = Variable.get("youtube_channel_ids")
        first_channel = channel_ids_str.split(",")[0].strip()
        client = YouTubeClient()
        stats = client.get_channel_stats([first_channel])
        if not stats:
            raise ValueError(f"No stats returned for channel {first_channel} — API may be down")
        logger.info("YouTube API check passed for channel %s", first_channel)

    check_api = PythonOperator(
        task_id="check_api",
        python_callable=check_youtube_api,
    )

    extract_load = KubernetesPodOperator(
        **k8s_config.get_pod_defaults(
            task_id="extract_load",
            arguments=[
                "python", "-m", "ingestion.youtube.extractor",
                "--execution-date", "{{ ds }}",
                "--channel-ids", "{{ var.value.youtube_channel_ids }}",
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
            source_system="YOUTUBE",
            target_table=f"{project_id}.{raw_dataset}.youtube_video_stats",
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
