#!/usr/bin/env python

from airflow import models
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s
from pendulum import datetime
from airflow.utils.task_group import TaskGroup

accounts = [
    "AccountA",
    "AccountB",
    "AccountC",
    "AccountD",
    "AccountE",
    "AccountF",
    "AccountG",
    "AccountH",
    "AccountI",
    "AccountJ",
    "AccountK",
]

common_env_vars = [
    k8s.V1EnvVar(
        name="GCP_SECRET_PROJECT_ID", value="{{ var.value.get('COMPOSER_PROJECT_ID') }}"
    ),
    k8s.V1EnvVar(
        name="DATA_POOL_PROJECT_ID",
        value="{{ var.value.get('data-pool-gcp-project-id') }}",
    ),
    k8s.V1EnvVar(
        name="DATA_POOL_BQ_DATASET",
        value="{{ var.value.get('data-pool-bq-dataset-test') }}",
    ),
    k8s.V1EnvVar(
        name="DATA_POOL_BIGQUERY_SA",
        value="{{ var.value.get('data-pool-bigquery-service-account') }}",
    ),
]


def get_account_env_vars(account):
    account_env_vars = [
        k8s.V1EnvVar(name="ACCOUNT_NAME", value=account),
    ]

    if account == "AccountA":
        account_env_vars.extend([k8s.V1EnvVar(name="BQ_TABLE_GSC", value="{{ var.value.get('search-console-by-query-account-a-bq-table') }}"), k8s.V1EnvVar(name="GSC_SA", value="{{ var.value.get('search-console-account-a-service-account') }}")])
    elif account == "AccountB":
        account_env_vars.extend([k8s.V1EnvVar(name="BQ_TABLE_GSC", value="{{ var.value.get('search-console-by-query-account-b-bq-table') }}"), k8s.V1EnvVar(name="GSC_SA", value="{{ var.value.get('search-console-account-b-service-account') }}")])
    elif account == "AccountC":
        account_env_vars.extend([k8s.V1EnvVar(name="BQ_TABLE_GSC", value="{{ var.value.get('search-console-by-query-account-c-bq-table') }}"), k8s.V1EnvVar(name="GSC_SA", value="{{ var.value.get('search-console-account-c-service-account') }}")])
    elif account == "AccountD":
        account_env_vars.extend([k8s.V1EnvVar(name="BQ_TABLE_GSC", value="{{ var.value.get('search-console-by-query-account-d-bq-table') }}"), k8s.V1EnvVar(name="GSC_SA", value="{{ var.value.get('search-console-account-d-service-account') }}")])
    elif account == "AccountE":
        account_env_vars.extend([k8s.V1EnvVar(name="BQ_TABLE_GSC", value="{{ var.value.get('search-console-by-query-account-e-bq-table') }}"), k8s.V1EnvVar(name="GSC_SA", value="{{ var.value.get('search-console-account-e-service-account') }}")])
    elif account == "AccountF":
        account_env_vars.extend([k8s.V1EnvVar(name="BQ_TABLE_GSC", value="{{ var.value.get('search-console-by-query-account-f-bq-table') }}"), k8s.V1EnvVar(name="GSC_SA", value="{{ var.value.get('search-console-account-f-service-account') }}")])
    elif account == "AccountG":
        account_env_vars.extend([k8s.V1EnvVar(name="BQ_TABLE_GSC", value="{{ var.value.get('search-console-by-query-account-g-bq-table') }}"), k8s.V1EnvVar(name="GSC_SA", value="{{ var.value.get('search-console-account-g-service-account') }}")])
    elif account == "AccountH":
        account_env_vars.extend([k8s.V1EnvVar(name="BQ_TABLE_GSC", value="{{ var.value.get('search-console-by-query-account-h-bq-table') }}"), k8s.V1EnvVar(name="GSC_SA", value="{{ var.value.get('search-console-account-h-service-account') }}")])
    elif account == "AccountI":
        account_env_vars.extend([k8s.V1EnvVar(name="BQ_TABLE_GSC", value="{{ var.value.get('search-console-by-query-account-i-bq-table') }}"), k8s.V1EnvVar(name="GSC_SA", value="{{ var.value.get('search-console-account-i-service-account') }}")])
    elif account == "AccountJ":
        account_env_vars.extend([k8s.V1EnvVar(name="BQ_TABLE_GSC", value="{{ var.value.get('search-console-by-query-account-j-bq-table') }}"), k8s.V1EnvVar(name="GSC_SA", value="{{ var.value.get('search-console-account-j-service-account') }}")])
    elif account == "AccountK":
        account_env_vars.extend([k8s.V1EnvVar(name="BQ_TABLE_GSC", value="{{ var.value.get('search-console-by-query-account-k-bq-table') }}"), k8s.V1EnvVar(name="GSC_SA", value="{{ var.value.get('search-console-account-k-service-account') }}")])
    return account_env_vars


with models.DAG(
    dag_id="search-console-by-query",
    description="Loads search console data by query from Google Search Console API.",
    schedule_interval="40 8,10,12,14,16 * * *",
    start_date=datetime(2024, 12, 1),
    tags=["Search Console"],
    catchup=False,
) as dag:
    for account in accounts:
        with TaskGroup(group_id=f"{account}") as account_group:
            env_vars = common_env_vars.copy()
            env_vars.extend(get_account_env_vars(account))

            _ = KubernetesPodOperator(
                namespace="composer-user-workloads",
                task_id="extract_and_load",
                image="{{ var.value.get('ARTIFACT_REGISTRY_REPOSITORY') }}/search-console-by-query:latest",
                container_resources=k8s.V1ResourceRequirements(
                    requests={"cpu": "250m", "memory": "500Mi"},
                    limits={"cpu": "500m", "memory": "1000Mi"},
                ),
                env_vars=env_vars,
                config_file="/home/airflow/composer_kube_config",
            )
