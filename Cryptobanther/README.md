# CryptoBanter GCP Data Platform

## Overview

Production-grade GCP data lakehouse for CryptoBanter, ingesting YouTube analytics, Google Search Console performance data, and MySQL OLTP records into BigQuery. Includes a Snowflake dbt project for cross-platform analytics and parity validation.

## Architecture

```
                      ┌─────────────────────────────────────────────┐
                      │          Cloud Composer (Airflow 2.9)        │
                      │  youtube_ingestion  │  gsc_ingestion  │  mysql│
                      └────────────┬────────┴────────┬────────┴───┬──┘
                                   │                 │             │
                         KubernetesPodOperator (GKE)              │
                                   │                               │
          ┌────────────────────────┼─────────────────┤             │
          │                        │                 │             │
    YouTube Data API    Google Search Console    Cloud SQL (MySQL) │
          │                        │                 │             │
          └────────────────────────┴─────────────────┘             │
                                   │                               │
                          ┌────────▼────────┐                      │
                          │  GCS Staging    │                      │
                          │  Bucket         │                      │
                          └────────┬────────┘                      │
                                   │                               │
                          ┌────────▼────────────────────────────┐  │
                          │           BigQuery                   │  │
                          │  raw.*  →  reporting.*  →  marts.*  │◄─┘
                          └─────────────────────────────────────┘
                                   │
                          BQLogger + Slack Alerting
```

**Key Components:**
- **Cloud Composer / Airflow 2.9** — DAG orchestration with KubernetesPodOperator for containerised ingestion
- **BigQuery** — raw data lake + reporting layer (partitioned + clustered tables)
- **GCS** — staging bucket for intermediate files
- **BQLogger** — custom observability framework writing pipeline execution logs to BigQuery
- **Slack Alerter** — webhook-based failure/success notifications
- **Snowflake dbt** — cross-platform analytics layer with parity validation against BigQuery

## Prerequisites

- GCP project with billing enabled
- `gcloud` CLI authenticated (`gcloud auth application-default login`)
- Terraform >= 1.5
- Docker (for building the ingestion image)
- Python 3.11+
- Airflow Variables set (see Environment Setup)

## Environment Setup

1. Copy the example env file:
   ```bash
   cp .env.example .env
   ```

2. Fill in all values in `.env`.

3. Set Airflow Variables (via Airflow UI or CLI):
   ```bash
   airflow variables set gcp_project_id your-project-id
   airflow variables set bq_dataset_raw raw
   airflow variables set bq_dataset_logging logging
   airflow variables set gcs_bucket_staging cryptobanter-staging
   airflow variables set youtube_channel_ids UCXGgrKt94gR6lmN4aN3n-uQ
   airflow variables set gsc_site_urls https://cryptobanter.com/
   airflow variables set slack_webhook_url https://hooks.slack.com/services/...
   airflow variables set k8s_pod_image europe-west2-docker.pkg.dev/your-project/cryptobanter/ingestion:latest
   airflow variables set gke_namespace pipeline-workers
   airflow variables set slack_notify_on_success false
   ```

## GCP Infrastructure (Terraform)

```bash
cd terraform/
terraform init
terraform plan -var="project_id=your-project-id" -var="gcs_bucket_name=cryptobanter-staging"
terraform apply -var="project_id=your-project-id" -var="gcs_bucket_name=cryptobanter-staging"
```

This provisions:
- BigQuery datasets: `raw`, `reporting`, `logging`
- BigQuery tables with partitioning and clustering
- GCS staging bucket with 30-day lifecycle rule on temp files
- IAM bindings for the ingestion service account

## Running DAGs

DAGs are scheduled automatically. To trigger manually:

```bash
airflow dags trigger youtube_ingestion --exec-date 2024-01-15
airflow dags trigger search_console_ingestion --exec-date 2024-01-15
airflow dags trigger mysql_ingestion --exec-date 2024-01-15
```

### DAG Schedule
| DAG | Schedule | Description |
|-----|----------|-------------|
| `youtube_ingestion` | `0 6 * * *` | Daily YouTube channel + video stats |
| `search_console_ingestion` | `0 7 * * *` | Daily GSC search performance (3-day lookback) |
| `mysql_ingestion` | `0 5 * * *` | Daily MySQL OLTP incremental load |

## Observability (BQLogger + Slack)

Every pipeline run writes a log entry to `{project}.logging.pipeline_execution_logs`:

```sql
SELECT dag_id, source_system, status, rows_loaded, duration_seconds, error_message
FROM `your-project.logging.pipeline_execution_logs`
WHERE execution_date = CURRENT_DATE()
ORDER BY logged_at DESC;
```

Slack alerts fire automatically on task failure. To enable success alerts:
```bash
airflow variables set slack_notify_on_success true
```

## Docker Build

```bash
docker build -f docker/Dockerfile -t europe-west2-docker.pkg.dev/your-project/cryptobanter/ingestion:latest .
docker push europe-west2-docker.pkg.dev/your-project/cryptobanter/ingestion:latest
```

The image packages all ingestion modules. The KubernetesPodOperator passes `--execution-date`, `--channel-ids`, etc. as arguments.

## Snowflake dbt Project

Located in `cryptobanter_snowflake_dbt/`. Mirrors the BigQuery raw data for cross-platform analytics.

```bash
cd cryptobanter_snowflake_dbt/
cp profiles.yml.example profiles.yml
# Edit profiles.yml with your Snowflake credentials

dbt deps
dbt run --profiles-dir .
dbt test --profiles-dir .
```

**Layer structure:**
- `staging/` — source-conformed models (1:1 with raw tables)
- `intermediate/` — business logic joins
- `marts/` — final reporting models consumed by BI tools

## Parity Validation

The `analyses/bq_snowflake_parity.sql` script validates row counts and aggregates between BigQuery and Snowflake. Run after both platforms are loaded:

```bash
dbt run-operation validate_parity --profiles-dir .
```

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=ingestion --cov=plugins --cov-report=term-missing
```
