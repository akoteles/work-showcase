#!/usr/bin/env python

from airflow import models
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s
from pendulum import datetime
from airflow.utils.task_group import TaskGroup

accounts = ["Account1", "Account2", "Account3", "Account4", "Account5", "Account6"]

common_env_vars = [
    k8s.V1EnvVar(
        name="GCP_SECRET_PROJECT_ID", value="{{ var.value.get('COMPOSER_PROJECT_ID') }}"
    ),
    k8s.V1EnvVar(
        name="DATAPOOL_PROJECT_ID",
        value="{{ var.value.get('datapool-gcp-project-id') }}",
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
                    name="DATAPOOL_BQ_DATASET",
                    value="{{ var.value.get('datapool-bq-dataset-test') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_ALL_DATA",
                    value="{{ var.value.get('analytics-platform-account1-bq-table-all-data') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_SEARCH_TRAFFIC_DATA",
                    value="{{ var.value.get('analytics-platform-account1-bq-table-search-traffic-data') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_DISCOVER_DATA",
                    value="{{ var.value.get('analytics-platform-account1-bq-table-discover-data') }}",
                ),
                k8s.V1EnvVar(
                    name="API_KEY",
                    value="{{ var.value.get('analytics-platform-api-key-account1') }}",
                ),
            ]
        )
    elif account == "Account5":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="DATAPOOL_BQ_DATASET",
                    value="{{ var.value.get('datapool-bq-dataset-test') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_ALL_DATA",
                    value="{{ var.value.get('analytics-platform-account5-bq-table-all-data') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_SEARCH_TRAFFIC_DATA",
                    value="{{ var.value.get('analytics-platform-account5-bq-table-search-traffic-data') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_DISCOVER_DATA",
                    value="{{ var.value.get('analytics-platform-account5-bq-table-discover-data') }}",
                ),
                k8s.V1EnvVar(
                    name="API_KEY",
                    value="{{ var.value.get('analytics-platform-api-key-account5') }}",
                ),
            ]
        )
    elif account == "Account2":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="DATAPOOL_BQ_DATASET",
                    value="{{ var.value.get('datapool-account2-analytics-platform-bq-dataset') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_ALL_DATA",
                    value="{{ var.value.get('analytics-platform-account2-bq-table-all-data') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_SEARCH_TRAFFIC_DATA",
                    value="{{ var.value.get('analytics-platform-account2-bq-table-search-traffic-data') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_DISCOVER_DATA",
                    value="{{ var.value.get('analytics-platform-account2-bq-table-discover-data') }}",
                ),
                k8s.V1EnvVar(
                    name="API_KEY",
                    value="{{ var.value.get('analytics-platform-api-key-account2') }}",
                ),
            ]
        )
    elif account == "Account3":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="DATAPOOL_BQ_DATASET",
                    value="{{ var.value.get('datapool-bq-dataset-test') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_ALL_DATA",
                    value="{{ var.value.get('analytics-platform-account3-bq-table-all-data') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_SEARCH_TRAFFIC_DATA",
                    value="{{ var.value.get('analytics-platform-account3-bq-table-search-traffic-data') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_DISCOVER_DATA",
                    value="{{ var.value.get('analytics-platform-account3-bq-table-discover-data') }}",
                ),
                k8s.V1EnvVar(
                    name="API_KEY",
                    value="{{ var.value.get('analytics-platform-api-key-account3') }}",
                ),
            ]
        )
    elif account == "Account4":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="DATAPOOL_BQ_DATASET",
                    value="{{ var.value.get('datapool-bq-dataset-test') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_ALL_DATA",
                    value="{{ var.value.get('analytics-platform-account4-bq-table-all-data') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_SEARCH_TRAFFIC_DATA",
                    value="{{ var.value.get('analytics-platform-account4-bq-table-search-traffic-data') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_DISCOVER_DATA",
                    value="{{ var.value.get('analytics-platform-account4-bq-table-discover-data') }}",
                ),
                k8s.V1EnvVar(
                    name="API_KEY",
                    value="{{ var.value.get('analytics-platform-api-key-account4') }}",
                ),
            ]
        )
    elif account == "Account6":
        account_env_vars.extend(
            [
                k8s.V1EnvVar(
                    name="DATAPOOL_BQ_DATASET",
                    value="{{ var.value.get('datapool-account6-analytics-platform-bq-dataset') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_ALL_DATA",
                    value="{{ var.value.get('analytics-platform-account6-bq-table-all-data') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_SEARCH_TRAFFIC_DATA",
                    value="{{ var.value.get('analytics-platform-account6-bq-table-search-traffic-data') }}",
                ),
                k8s.V1EnvVar(
                    name="BQ_TABLE_ANALYTICS_PLATFORM_DISCOVER_DATA",
                    value="{{ var.value.get('analytics-platform-account6-bq-table-discover-data') }}",
                ),
                k8s.V1EnvVar(
                    name="API_KEY_ALL_DATA",
                    value="{{ var.value.get('analytics-platform-api-restricted-key-account6') }}",
                ),
                k8s.V1EnvVar(
                    name="API_KEY_SEARCH_TRAFFIC_DATA",
                    value="{{ var.value.get('analytics-platform-search-traffic-api-restricted-key-account6') }}",
                ),
                k8s.V1EnvVar(
                    name="API_KEY_DISCOVER_DATA",
                    value="{{ var.value.get('analytics-platform-discover-search-traffic-share-api-restricted-key-account6') }}",
                ),
            ]
        )
    return account_env_vars


with models.DAG(
    dag_id="extract-analytics-platform-last-day",
    description="Loads data from AnalyticsPlatform API only for the last day, to compensate for the missed out data collection between 20-0h.",
    schedule_interval="0 5 * * *",
    start_date=datetime(2024, 12, 1),
    tags=["AnalyticsPlatform"],
    catchup=False,
) as dag:
    for account in accounts:
        with TaskGroup(group_id=f"{account}") as account_group:
            env_vars = common_env_vars.copy()
            env_vars.extend(get_account_env_vars(account))

            _ = KubernetesPodOperator(
                namespace="composer-user-workloads",
                task_id="extract_and_load",
                image="{{ var.value.get('ARTIFACT_REGISTRY_REPOSITORY') }}/extract-analytics-platform-last-day:latest",
                container_resources=k8s.V1ResourceRequirements(
                    requests={"cpu": "250m", "memory": "500Mi"},
                    limits={"cpu": "500m", "memory": "1000Mi"},
                ),
                env_vars=env_vars,
                config_file="/home/airflow/composer_kube_config",
            )
