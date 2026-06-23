from __future__ import annotations
from datetime import timedelta
from typing import List
from airflow.models import Variable
from kubernetes import client as k8s


def get_pod_defaults(task_id: str, arguments: List[str]) -> dict:
    return {
        "task_id": task_id,
        "name": f"cryptobanter-{task_id.replace('_', '-')}",
        "namespace": Variable.get("gke_namespace", default_var="pipeline-workers"),
        "image": Variable.get("k8s_pod_image"),
        "image_pull_policy": "Always",
        "get_logs": True,
        "is_delete_operator_pod": True,
        "do_xcom_push": True,
        "arguments": arguments,
        "env_vars": {
            "GCP_PROJECT_ID": Variable.get("gcp_project_id"),
            "BQ_DATASET_RAW": Variable.get("bq_dataset_raw", default_var="raw"),
            "BQ_DATASET_LOGGING": Variable.get("bq_dataset_logging", default_var="logging"),
            "GCS_BUCKET_STAGING": Variable.get("gcs_bucket_staging"),
        },
        "container_resources": k8s.V1ResourceRequirements(
            requests={"cpu": "500m", "memory": "512Mi"},
            limits={"cpu": "2000m", "memory": "2Gi"},
        ),
        "on_finish_action": "delete_pod",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    }
