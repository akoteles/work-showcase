#!/usr/bin/env python

from airflow import models
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s
from pendulum import datetime
from airflow.utils.task_group import TaskGroup

accounts = [
    "Account1",
    "Account5",
    "Account2",
    "Account3",
    "Account4",
    "Account7",
    "Account8",
    "Account9",
    "Account10",
    "Account11",
    "Account6",
]

common_env_vars = [
    k8s.V1EnvVar(
        name="GCP_SECRET_PROJECT_ID", value="{{ var.value.get('COMPOSER_PROJECT_ID') }}"
    ),
    k8s.V1EnvVar(
        name="DATAPOOL_PROJECT_ID",
        value="{{ var.value.get('datapool-gcp-project-id') }}",
    ),
    k8s.V1EnvVar(
        name="DATAPOOL_BQ_DATASET",
        value="{{ var.value.get('datapool-bq-dataset-test') }}",
    ),
    k8s.V1EnvVar(
        name="DATAPOOL_BIGQUERY_SA",
        value="{{ var.value.get('datapool-bigquery-service-account') }}",
    ),
]


def get_account_env_vars(account):
    """
    Generate environment variables specific to an account.

    Args:
        account (str): Name of the account.

    Returns:
        list[k8s.V1EnvVar]: List of environment variables specific to the account.
    """

    account_env_vars = [
        k8s.V1EnvVar(name="ACCOUNT_NAME", value=account),
    ]

    if account == "Account1":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="BQ_TABLE_GSC",
                    value="{{ var.value.get('search-console-by-query-page-account1-bq-table') }}",
                ),
                k8s.V1EnvVar(
                    name="GSC_SA",
                    value="{{ var.value.get('search-console-account1-service-account') }}",
                ),
            ]
        )
    elif account == "Account5":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="BQ_TABLE_GSC",
                    value="{{ var.value.get('search-console-by-query-page-account5-bq-table') }}",
                ),
                k8s.V1EnvVar(
                    name="GSC_SA",
                    value="{{ var.value.get('search-console-account5-service-account') }}",
                ),
            ]
        )
    elif account == "Account2":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="BQ_TABLE_GSC",
                    value="{{ var.value.get('search-console-by-query-page-account2-bq-table') }}",
                ),
                k8s.V1EnvVar(
                    name="GSC_SA",
                    value="{{ var.value.get('search-console-account2-service-account') }}",
                ),
            ]
        )
    elif account == "Account3":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="BQ_TABLE_GSC",
                    value="{{ var.value.get('search-console-by-query-page-account3-bq-table') }}",
                ),
                k8s.V1EnvVar(
                    name="GSC_SA",
                    value="{{ var.value.get('search-console-account3-service-account') }}",
                ),
            ]
        )
    elif account == "Account4":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="BQ_TABLE_GSC",
                    value="{{ var.value.get('search-console-by-query-page-account4-bq-table') }}",
                ),
                k8s.V1EnvVar(
                    name="GSC_SA",
                    value="{{ var.value.get('search-console-account4-service-account') }}",
                ),
            ]
        )
    elif account == "Account7":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="BQ_TABLE_GSC",
                    value="{{ var.value.get('search-console-by-query-page-account7-bq-table') }}",
                ),
                k8s.V1EnvVar(
                    name="GSC_SA",
                    value="{{ var.value.get('search-console-account7-service-account') }}",
                ),
            ]
        )
    elif account == "Account8":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="BQ_TABLE_GSC",
                    value="{{ var.value.get('search-console-by-query-page-account8-bq-table') }}",
                ),
                k8s.V1EnvVar(
                    name="GSC_SA",
                    value="{{ var.value.get('search-console-account8-service-account') }}",
                ),
            ]
        )
    elif account == "Account9":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="BQ_TABLE_GSC",
                    value="{{ var.value.get('search-console-by-query-page-account9-bq-table') }}",
                ),
                k8s.V1EnvVar(
                    name="GSC_SA",
                    value="{{ var.value.get('search-console-account9-service-account') }}",
                ),
            ]
        )
    elif account == "Account10":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="BQ_TABLE_GSC",
                    value="{{ var.value.get('search-console-by-query-page-account10-bq-table') }}",
                ),
                k8s.V1EnvVar(
                    name="GSC_SA",
                    value="{{ var.value.get('search-console-account10-service-account') }}",
                ),
            ]
        )
    elif account == "Account11":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="BQ_TABLE_GSC",
                    value="{{ var.value.get('search-console-by-query-page-account11-bq-table') }}",
                ),
                k8s.V1EnvVar(
                    name="GSC_SA",
                    value="{{ var.value.get('search-console-account11-service-account') }}",
                ),
            ]
        )
    elif account == "Account6":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="BQ_TABLE_GSC",
                    value="{{ var.value.get('search-console-by-query-page-account6-bq-table') }}",
                ),
                k8s.V1EnvVar(
                    name="GSC_SA",
                    value="{{ var.value.get('search-console-account6-service-account') }}",
                ),
            ]
        )
    return account_env_vars


with models.DAG(
    dag_id="search-console-by-query-page",
    description="Loads search console data by query-page from Google Search Console API.",
    schedule_interval="50 8,10,12,14,16 * * *",
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
                image="{{ var.value.get('ARTIFACT_REGISTRY_REPOSITORY') }}/search-console-by-query-page:latest",
                container_resources=k8s.V1ResourceRequirements(
                    requests={"cpu": "250m", "memory": "500Mi"},
                    limits={"cpu": "500m", "memory": "1000Mi"},
                ),
                env_vars=env_vars,
                config_file="/home/airflow/composer_kube_config",
            )
