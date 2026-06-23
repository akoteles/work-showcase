# CryptoBanter Snowflake dbt Project

Snowflake analytics layer mirroring the GCP BigQuery raw data. Used for cross-platform reporting and parity validation.

## Setup

```bash
cd cryptobanter_snowflake_dbt/
cp profiles.yml.example profiles.yml
# Edit profiles.yml with your Snowflake credentials

dbt deps
dbt debug --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
```

## Layer Structure

| Layer | Materialization | Purpose |
|-------|----------------|---------|
| `staging/` | view | Source-conformed models, 1:1 with raw tables |
| `intermediate/` | ephemeral | Business logic joins and transformations |
| `marts/` | table | Final reporting models for BI tools |

## Running specific models

```bash
# Run only staging models
dbt run --select staging --profiles-dir .

# Run marts and their dependencies
dbt run --select +marts --profiles-dir .

# Test a specific model
dbt test --select stg_youtube_channel_stats --profiles-dir .
```
