from __future__ import annotations
import argparse
import io
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, List, Optional

from google.cloud import bigquery

from ingestion.mysql.client import MySQLClient
from ingestion.mysql.schemas import build_bq_schema_from_mysql

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def get_bq_watermark(
    bq: bigquery.Client,
    project: str,
    dataset: str,
    table: str,
    watermark_col: str,
) -> Optional[Any]:
    full_table = f"`{project}.{dataset}.{table}`"
    query = f"SELECT MAX(`{watermark_col}`) AS max_val FROM {full_table}"
    try:
        result = bq.query(query).result()
        row = next(iter(result), None)
        if row is None:
            return None
        return row[0]
    except Exception as exc:
        logger.warning("Could not get BQ watermark for %s.%s: %s", table, watermark_col, exc)
        return None


def merge_to_bq(
    bq: bigquery.Client,
    project: str,
    dataset: str,
    table: str,
    rows: List[dict],
    merge_keys: List[str],
    schema: List[bigquery.SchemaField],
) -> int:
    if not rows:
        return 0

    tmp_table = f"{project}.{dataset}._tmp_{table}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    data = io.StringIO("\n".join(json.dumps(r) for r in rows))
    job = bq.load_table_from_file(data, tmp_table, job_config=job_config)
    job.result()
    if job.errors:
        raise RuntimeError(f"Temp table load errors: {job.errors}")

    on_clause = " AND ".join(f"T.`{k}` = S.`{k}`" for k in merge_keys)
    column_names = [f.name for f in schema]
    update_set = ", ".join(
        f"T.`{col}` = S.`{col}`"
        for col in column_names
        if col not in merge_keys
    )
    insert_cols = ", ".join(f"`{col}`" for col in column_names)
    insert_vals = ", ".join(f"S.`{col}`" for col in column_names)

    merge_sql = f"""
        MERGE `{project}.{dataset}.{table}` T
        USING `{tmp_table}` S
        ON {on_clause}
        WHEN MATCHED THEN UPDATE SET {update_set}
        WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
    """
    merge_job = bq.query(merge_sql)
    merge_job.result()
    bq.delete_table(tmp_table, not_found_ok=True)
    logger.info("Merged %d rows into %s.%s.%s", len(rows), project, dataset, table)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="MySQL to BigQuery incremental ingestion")
    parser.add_argument("--execution-date", required=True)
    parser.add_argument("--table-config", required=True, help="JSON array of table configurations")
    parser.add_argument("--project-id", default=os.environ.get("GCP_PROJECT_ID"))
    parser.add_argument("--dataset-id", default=os.environ.get("BQ_DATASET_RAW", "raw"))
    parser.add_argument("--mysql-host", default=os.environ.get("MYSQL_HOST"))
    parser.add_argument("--mysql-port", type=int, default=int(os.environ.get("MYSQL_PORT", "3306")))
    parser.add_argument("--mysql-database", default=os.environ.get("MYSQL_DATABASE"))
    parser.add_argument("--mysql-user", default=os.environ.get("MYSQL_USER"))
    parser.add_argument("--mysql-password", default=os.environ.get("MYSQL_PASSWORD"))
    args = parser.parse_args()

    table_configs = json.loads(args.table_config)
    mysql_client = MySQLClient(
        host=args.mysql_host,
        port=args.mysql_port,
        database=args.mysql_database,
        user=args.mysql_user,
        password=args.mysql_password,
    )
    bq_client = bigquery.Client(project=args.project_id)

    total_rows = 0
    try:
        for table_cfg in table_configs:
            table_name = table_cfg["table"]
            watermark_col = table_cfg.get("watermark_col")
            merge_keys = table_cfg.get("merge_keys", [])
            strategy = table_cfg.get("strategy", "incremental")

            logger.info("Processing table=%s strategy=%s", table_name, strategy)

            mysql_schema = mysql_client.get_table_schema(table_name)
            bq_schema = build_bq_schema_from_mysql(mysql_schema)

            if strategy == "incremental":
                last_watermark = get_bq_watermark(
                    bq_client, args.project_id, args.dataset_id, table_name, watermark_col
                )
                logger.info("Last BQ watermark for %s: %s", table_name, last_watermark)

                accumulated: List[dict] = []
                for batch in mysql_client.extract_incremental(table_name, watermark_col, last_watermark):
                    accumulated.extend(batch)
                    if len(accumulated) >= 50000:
                        rows_merged = merge_to_bq(
                            bq_client,
                            args.project_id,
                            args.dataset_id,
                            table_name,
                            accumulated,
                            merge_keys,
                            bq_schema,
                        )
                        total_rows += rows_merged
                        accumulated = []

                if accumulated:
                    rows_merged = merge_to_bq(
                        bq_client,
                        args.project_id,
                        args.dataset_id,
                        table_name,
                        accumulated,
                        merge_keys,
                        bq_schema,
                    )
                    total_rows += rows_merged

            elif strategy == "full_replace":
                bq_table_id = f"{args.project_id}.{args.dataset_id}.{table_name}"
                first_batch = True
                for batch in mysql_client.extract_full(table_name):
                    write_disp = (
                        bigquery.WriteDisposition.WRITE_TRUNCATE
                        if first_batch
                        else bigquery.WriteDisposition.WRITE_APPEND
                    )
                    job_config = bigquery.LoadJobConfig(
                        schema=bq_schema,
                        write_disposition=write_disp,
                        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                    )
                    data = io.StringIO("\n".join(json.dumps(r) for r in batch))
                    job = bq_client.load_table_from_file(data, bq_table_id, job_config=job_config)
                    job.result()
                    if job.errors:
                        raise RuntimeError(f"BQ load errors for {table_name}: {job.errors}")
                    total_rows += len(batch)
                    first_batch = False
                    logger.info("Full replace: loaded %d rows to %s", len(batch), bq_table_id)

            else:
                logger.warning("Unknown strategy '%s' for table %s, skipping", strategy, table_name)

    except Exception as exc:
        logger.error("MySQL extraction failed: %s", exc, exc_info=True)
        print(f"XCOM: {json.dumps({'status': 'FAILED', 'error': str(exc), 'rows_loaded': total_rows})}")
        sys.exit(1)
    finally:
        mysql_client.close()

    print(f"XCOM: {json.dumps({'status': 'SUCCESS', 'rows_loaded': total_rows, 'source': 'MYSQL'})}")
    sys.exit(0)


if __name__ == "__main__":
    main()
