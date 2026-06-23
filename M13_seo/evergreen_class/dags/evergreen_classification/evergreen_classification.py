#!/usr/bin/env python

from airflow import models
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.exceptions import AirflowSkipException
from airflow.operators.python import PythonOperator
from kubernetes.client import models as k8s
from pendulum import datetime
from common.bq_logger import AirflowBQLogger
from common.bq_etl_cdc import BQETLCDCControl
from common.bq_etl_control import get_additional_params
from utils.ms_teams import create_teams_callback

DAG_ID = "evergreen_classification"
PROCESS_NAME = "evergreen_classification"
IMAGE = "{{ var.value.get('ARTIFACT_REGISTRY_REPOSITORY') }}/evergreen_classification:latest"

CommonEnvVars = [
    k8s.V1EnvVar(name="GCP_SECRET_PROJECT_ID", value="{{ var.value.get('COMPOSER_PROJECT_ID') }}"),
    k8s.V1EnvVar(name="DATA_POOL_PROJECT_ID", value="{{ var.value.get('data-pool-gcp-project-id') }}"),
    k8s.V1EnvVar(name="TARGET_BQ_DATASET", value="{{ var.value.get('target-bq-dataset-evergreen', 'seo_classification') }}"),
    k8s.V1EnvVar(name="MS_TEAMS_WEBHOOK_URL", value="{{ var.value.get('ms-teams-webhook-seo') }}"),
]

def fetch_control_data(**kwargs):
    cdc_control = BQETLCDCControl(
        project_id=models.Variable.get('data-pool-gcp-project-id'),
        dataset_id="ops",
        gcp_conn_id="google_cloud_default"
    )

    cdc_info = cdc_control.get_cdc_env_vars(PROCESS_NAME)
    control_params = get_additional_params(PROCESS_NAME)
    result = {**cdc_info, **control_params}

    if not result.get('active_flag', True):
        print(f"Process {PROCESS_NAME} is marked as inactive. Skipping.")
        raise AirflowSkipException("Process is inactive")

    return result

with models.DAG(
    dag_id=DAG_ID,
    description="Classifies content as Evergreen/Seasonal using Decision Tree logic with SCD Type 2.",
    schedule_interval="0 7 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["SEO", "Classification", "SCD2", "Evergreen"],
    max_active_runs=1,
    default_args={
        "on_failure_callback": create_teams_callback("seo"),
        "retries": 1
    }
) as dag:

    bq_logger = AirflowBQLogger(
        project_id="{{ var.value.get('data-pool-gcp-project-id') }}",
        dataset_id="ops",
        gcp_conn_id="google_cloud_default"
    )

    cdc_control = BQETLCDCControl(
        project_id="{{ var.value.get('data-pool-gcp-project-id') }}",
        dataset_id="ops",
        gcp_conn_id="google_cloud_default"
    )

    fetch_control_task = PythonOperator(
        task_id="fetch_control_data",
        python_callable=fetch_control_data
    )

    env_vars = CommonEnvVars + [
        k8s.V1EnvVar(name="CDC_START_DT", value="{{ ti.xcom_pull(task_ids='fetch_control_data')['CDC_START_DT'] }}"),
        k8s.V1EnvVar(name="CDC_END_DT", value="{{ ti.xcom_pull(task_ids='fetch_control_data')['CDC_END_DT'] }}"),
    ]

    log_callbacks = bq_logger.create_task_callbacks(process_name=PROCESS_NAME)
    cdc_update_callback = cdc_control.create_update_callback(PROCESS_NAME)

    def combined_success_callback(context):
        log_callbacks['success'](context)
        cdc_update_callback(context)

    teams_callback = create_teams_callback("seo")
    def combined_failure_callback(context):
        log_callbacks['failure'](context)
        teams_callback(context)

    def on_task_start(context):
        bq_logger.log_task_execution(
            dag_id=context['dag'].dag_id,
            task_id=context['task'].task_id,
            run_id=context['run_id'],
            execution_date=context['execution_date'],
            process_name=PROCESS_NAME,
            log_msg="Classification Task Started",
            log_level="INFO"
        )

    classify_task = KubernetesPodOperator(
        namespace="composer-user-workloads",
        task_id="run_classification",
        image=IMAGE,
        cmds=["python", "evergreen_classification.py"],
        env_vars=env_vars,
        container_resources=k8s.V1ResourceRequirements(
            requests={"cpu": "1000m", "memory": "2Gi"},
            limits={"cpu": "2000m", "memory": "4Gi"},
        ),
        config_file="/home/airflow/composer_kube_config",
        on_success_callback=combined_success_callback,
        on_failure_callback=combined_failure_callback,
        on_execute_callback=on_task_start,
    )

    fetch_control_task >> classify_task
