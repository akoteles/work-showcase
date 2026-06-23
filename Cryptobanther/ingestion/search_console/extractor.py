from __future__ import annotations
import argparse
import io
import json
import logging
import os
import sys
from datetime import date, datetime, timedelta
from typing import List

from google.cloud import bigquery

from ingestion.search_console.client import SearchConsoleClient
from ingestion.search_console.schemas import GSC_PERFORMANCE_SCHEMA

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def delete_existing_rows(
    bq: bigquery.Client,
    project: str,
    dataset: str,
    site_url: str,
    partition_date: str,
) -> None:
    table_id = f"`{project}.{dataset}.gsc_search_performance`"
    delete_sql = f"""
        DELETE FROM {table_id}
        WHERE site_url = @site_url
          AND partition_date = @partition_date
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("site_url", "STRING", site_url),
            bigquery.ScalarQueryParameter("partition_date", "DATE", partition_date),
        ]
    )
    job = bq.query(delete_sql, job_config=job_config)
    job.result()
    logger.info("Deleted existing rows for site=%s date=%s", site_url, partition_date)


def load_rows_to_bq(
    bq: bigquery.Client,
    project: str,
    dataset: str,
    rows: List[dict],
) -> int:
    if not rows:
        return 0
    table_id = f"{project}.{dataset}.gsc_search_performance"
    job_config = bigquery.LoadJobConfig(
        schema=GSC_PERFORMANCE_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    data = io.StringIO("\n".join(json.dumps(r) for r in rows))
    job = bq.load_table_from_file(data, table_id, job_config=job_config)
    job.result()
    if job.errors:
        raise RuntimeError(f"BQ load errors: {job.errors}")
    logger.info("Loaded %d rows to %s", len(rows), table_id)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Google Search Console ingestion")
    parser.add_argument("--execution-date", required=True, help="ISO date YYYY-MM-DD")
    parser.add_argument("--site-urls", required=True, help="Comma-separated GSC site URLs")
    parser.add_argument("--project-id", default=os.environ.get("GCP_PROJECT_ID"))
    parser.add_argument("--dataset-id", default=os.environ.get("BQ_DATASET_RAW", "raw"))
    parser.add_argument("--lookback-days", type=int, default=3, help="Number of days to backfill")
    args = parser.parse_args()

    execution_date = date.fromisoformat(args.execution_date)
    site_urls = [s.strip() for s in args.site_urls.split(",") if s.strip()]

    gsc_client = SearchConsoleClient()
    bq_client = bigquery.Client(project=args.project_id)

    total_rows = 0
    try:
        for day_offset in range(args.lookback_days):
            target_date = execution_date - timedelta(days=day_offset)
            date_str = target_date.isoformat()
            ingested_at = datetime.utcnow().isoformat()

            for site_url in site_urls:
                logger.info("Processing site=%s date=%s", site_url, date_str)
                rows = gsc_client.query_search_performance(
                    site_url=site_url,
                    start_date=date_str,
                    end_date=date_str,
                )

                if not rows:
                    logger.info("No GSC data for site=%s date=%s", site_url, date_str)
                    continue

                enriched_rows = [
                    {
                        "partition_date": date_str,
                        "site_url": r["site_url"],
                        "query": r.get("query"),
                        "page": r.get("page"),
                        "country": r.get("country"),
                        "device": r.get("device"),
                        "clicks": r.get("clicks"),
                        "impressions": r.get("impressions"),
                        "ctr": r.get("ctr"),
                        "position": r.get("position"),
                        "ingested_at": ingested_at,
                    }
                    for r in rows
                ]

                delete_existing_rows(bq_client, args.project_id, args.dataset_id, site_url, date_str)
                loaded = load_rows_to_bq(bq_client, args.project_id, args.dataset_id, enriched_rows)
                total_rows += loaded
                logger.info("Loaded %d rows for site=%s date=%s", loaded, site_url, date_str)

    except Exception as exc:
        logger.error("GSC extraction failed: %s", exc, exc_info=True)
        print(f"XCOM: {json.dumps({'status': 'FAILED', 'error': str(exc), 'rows_loaded': total_rows})}")
        sys.exit(1)

    print(f"XCOM: {json.dumps({'status': 'SUCCESS', 'rows_loaded': total_rows, 'source': 'GSC'})}")
    sys.exit(0)


if __name__ == "__main__":
    main()
