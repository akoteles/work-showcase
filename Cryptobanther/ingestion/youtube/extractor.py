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

from ingestion.youtube.client import YouTubeClient
from ingestion.youtube.schemas import CHANNEL_STATS_SCHEMA, VIDEO_STATS_SCHEMA, VIDEO_METADATA_SCHEMA

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def extract_channel_stats(
    client: YouTubeClient,
    bq: bigquery.Client,
    project: str,
    dataset: str,
    channel_ids: List[str],
    partition_date: date,
) -> int:
    channel_stats = client.get_channel_stats(channel_ids)
    if not channel_stats:
        logger.warning("No channel stats returned for %s", channel_ids)
        return 0
    ingested_at = datetime.utcnow().isoformat()
    rows = [
        {
            "partition_date": partition_date.isoformat(),
            "channel_id": s["channel_id"],
            "channel_title": s.get("channel_title"),
            "subscriber_count": s.get("subscriber_count"),
            "view_count": s.get("view_count"),
            "video_count": s.get("video_count"),
            "hidden_subscriber_count": s.get("hidden_subscriber_count"),
            "ingested_at": ingested_at,
        }
        for s in channel_stats
    ]
    table_id = f"{project}.{dataset}.youtube_channel_stats"
    delete_sql = f"""
        DELETE FROM `{table_id}`
        WHERE partition_date = @partition_date
    """
    bq.query(
        delete_sql,
        job_config=bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("partition_date", "DATE", partition_date.isoformat()),
        ]),
    ).result()
    job_config = bigquery.LoadJobConfig(
        schema=CHANNEL_STATS_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    data = io.StringIO("\n".join(json.dumps(r) for r in rows))
    job = bq.load_table_from_file(data, table_id, job_config=job_config)
    job.result()
    if job.errors:
        raise RuntimeError(f"BQ load errors: {job.errors}")
    logger.info("Loaded %d channel stat rows to %s", len(rows), table_id)
    return len(rows)


def extract_video_stats(
    client: YouTubeClient,
    bq: bigquery.Client,
    project: str,
    dataset: str,
    channel_ids: List[str],
    execution_date: date,
) -> int:
    published_after = (execution_date - timedelta(days=90)).isoformat() + "T00:00:00Z"
    published_before = execution_date.isoformat() + "T23:59:59Z"
    ingested_at = datetime.utcnow().isoformat()

    all_video_ids: List[str] = []
    for channel_id in channel_ids:
        videos = client.get_videos_in_date_range(channel_id, published_after, published_before)
        all_video_ids.extend([v["video_id"] for v in videos])
        logger.info("Found %d videos for channel %s", len(videos), channel_id)

    if not all_video_ids:
        logger.info("No videos found in date range")
        return 0

    video_stats = client.get_video_stats(all_video_ids)

    stats_rows = [
        {
            "partition_date": execution_date.isoformat(),
            "video_id": s["video_id"],
            "channel_id": s.get("channel_id"),
            "title": s.get("title"),
            "published_at": s.get("published_at"),
            "view_count": s.get("view_count"),
            "like_count": s.get("like_count"),
            "comment_count": s.get("comment_count"),
            "duration_iso": s.get("duration_iso"),
            "ingested_at": ingested_at,
        }
        for s in video_stats
    ]

    stats_table_id = f"{project}.{dataset}.youtube_video_stats"
    delete_sql = f"""
        DELETE FROM `{stats_table_id}`
        WHERE partition_date = @partition_date
    """
    bq.query(
        delete_sql,
        job_config=bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("partition_date", "DATE", execution_date.isoformat()),
        ]),
    ).result()
    job_config = bigquery.LoadJobConfig(
        schema=VIDEO_STATS_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    data = io.StringIO("\n".join(json.dumps(r) for r in stats_rows))
    job = bq.load_table_from_file(data, stats_table_id, job_config=job_config)
    job.result()
    if job.errors:
        raise RuntimeError(f"BQ load errors for video_stats: {job.errors}")

    # MERGE into video metadata using temp table
    tmp_table_id = f"{project}.{dataset}._tmp_video_metadata_{execution_date.strftime('%Y%m%d')}"
    metadata_rows = [
        {
            "video_id": s["video_id"],
            "channel_id": s.get("channel_id"),
            "title": s.get("title"),
            "published_at": s.get("published_at"),
            "view_count": s.get("view_count"),
            "like_count": s.get("like_count"),
            "comment_count": s.get("comment_count"),
            "duration_iso": s.get("duration_iso"),
            "updated_at": ingested_at,
        }
        for s in video_stats
    ]
    tmp_job_config = bigquery.LoadJobConfig(
        schema=VIDEO_METADATA_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    tmp_data = io.StringIO("\n".join(json.dumps(r) for r in metadata_rows))
    tmp_job = bq.load_table_from_file(tmp_data, tmp_table_id, job_config=tmp_job_config)
    tmp_job.result()

    merge_sql = f"""
        MERGE `{project}.{dataset}.youtube_video_metadata` T
        USING `{tmp_table_id}` S
        ON T.video_id = S.video_id
        WHEN MATCHED THEN UPDATE SET
            title = S.title,
            view_count = S.view_count,
            like_count = S.like_count,
            comment_count = S.comment_count,
            duration_iso = S.duration_iso,
            updated_at = S.updated_at
        WHEN NOT MATCHED THEN INSERT ROW
    """
    merge_job = bq.query(merge_sql)
    merge_job.result()

    bq.delete_table(tmp_table_id, not_found_ok=True)
    logger.info("Merged %d rows into youtube_video_metadata", len(metadata_rows))
    return len(stats_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="YouTube Data API ingestion")
    parser.add_argument("--execution-date", required=True)
    parser.add_argument("--channel-ids", required=True)
    parser.add_argument("--project-id", default=os.environ.get("GCP_PROJECT_ID"))
    parser.add_argument("--dataset-id", default=os.environ.get("BQ_DATASET_RAW", "raw"))
    args = parser.parse_args()

    channel_ids = [c.strip() for c in args.channel_ids.split(",")]
    execution_date = date.fromisoformat(args.execution_date)

    youtube_client = YouTubeClient()
    bq_client = bigquery.Client(project=args.project_id)

    total_rows = 0
    try:
        rows = extract_channel_stats(
            youtube_client, bq_client, args.project_id, args.dataset_id, channel_ids, execution_date
        )
        total_rows += rows
        logger.info("Channel stats: %d rows loaded", rows)

        rows = extract_video_stats(
            youtube_client, bq_client, args.project_id, args.dataset_id, channel_ids, execution_date
        )
        total_rows += rows
        logger.info("Video stats: %d rows loaded", rows)

    except Exception as exc:
        logger.error("Extraction failed: %s", exc, exc_info=True)
        print(f"XCOM: {json.dumps({'status': 'FAILED', 'error': str(exc), 'rows_loaded': total_rows})}")
        sys.exit(1)

    print(f"XCOM: {json.dumps({'status': 'SUCCESS', 'rows_loaded': total_rows, 'source': 'YOUTUBE'})}")
    sys.exit(0)


if __name__ == "__main__":
    main()
