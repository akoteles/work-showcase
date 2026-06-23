from google.cloud import bigquery

CHANNEL_STATS_SCHEMA = [
    bigquery.SchemaField("partition_date",          "DATE",      mode="REQUIRED"),
    bigquery.SchemaField("channel_id",              "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("channel_title",           "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("subscriber_count",        "INTEGER",   mode="NULLABLE"),
    bigquery.SchemaField("view_count",              "INTEGER",   mode="NULLABLE"),
    bigquery.SchemaField("video_count",             "INTEGER",   mode="NULLABLE"),
    bigquery.SchemaField("hidden_subscriber_count", "BOOLEAN",   mode="NULLABLE"),
    bigquery.SchemaField("ingested_at",             "TIMESTAMP", mode="REQUIRED"),
]

VIDEO_STATS_SCHEMA = [
    bigquery.SchemaField("partition_date",  "DATE",      mode="REQUIRED"),
    bigquery.SchemaField("video_id",        "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("channel_id",      "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("title",           "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("published_at",    "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("view_count",      "INTEGER",   mode="NULLABLE"),
    bigquery.SchemaField("like_count",      "INTEGER",   mode="NULLABLE"),
    bigquery.SchemaField("comment_count",   "INTEGER",   mode="NULLABLE"),
    bigquery.SchemaField("duration_iso",    "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("ingested_at",     "TIMESTAMP", mode="REQUIRED"),
]

VIDEO_METADATA_SCHEMA = [
    bigquery.SchemaField("video_id",       "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("channel_id",     "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("title",          "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("published_at",   "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("view_count",     "INTEGER",   mode="NULLABLE"),
    bigquery.SchemaField("like_count",     "INTEGER",   mode="NULLABLE"),
    bigquery.SchemaField("comment_count",  "INTEGER",   mode="NULLABLE"),
    bigquery.SchemaField("duration_iso",   "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("updated_at",     "TIMESTAMP", mode="REQUIRED"),
]
