-- DDL: Raw layer tables for CryptoBanter GCP Data Platform
-- Replace {project} with your GCP project ID before running

CREATE TABLE IF NOT EXISTS `{project}.raw.youtube_channel_stats`
(
    partition_date          DATE      NOT NULL,
    channel_id              STRING    NOT NULL,
    channel_title           STRING,
    subscriber_count        INT64,
    view_count              INT64,
    video_count             INT64,
    hidden_subscriber_count BOOL,
    ingested_at             TIMESTAMP NOT NULL
)
PARTITION BY partition_date
CLUSTER BY channel_id
OPTIONS (
    description = "Daily snapshot of YouTube channel-level statistics",
    require_partition_filter = false
);

CREATE TABLE IF NOT EXISTS `{project}.raw.youtube_video_stats`
(
    partition_date DATE      NOT NULL,
    video_id       STRING    NOT NULL,
    channel_id     STRING    NOT NULL,
    title          STRING,
    published_at   TIMESTAMP,
    view_count     INT64,
    like_count     INT64,
    comment_count  INT64,
    duration_iso   STRING,
    ingested_at    TIMESTAMP NOT NULL
)
PARTITION BY partition_date
CLUSTER BY channel_id, video_id
OPTIONS (
    description = "Daily snapshot of YouTube video-level statistics",
    require_partition_filter = false
);

CREATE TABLE IF NOT EXISTS `{project}.raw.youtube_video_metadata`
(
    video_id      STRING    NOT NULL,
    channel_id    STRING    NOT NULL,
    title         STRING,
    published_at  TIMESTAMP,
    view_count    INT64,
    like_count    INT64,
    comment_count INT64,
    duration_iso  STRING,
    updated_at    TIMESTAMP NOT NULL
)
CLUSTER BY channel_id
OPTIONS (
    description = "Current state of YouTube video metadata — updated via MERGE",
    require_partition_filter = false
);

CREATE TABLE IF NOT EXISTS `{project}.raw.gsc_search_performance`
(
    partition_date DATE      NOT NULL,
    site_url       STRING    NOT NULL,
    query          STRING,
    page           STRING,
    country        STRING,
    device         STRING,
    clicks         INT64,
    impressions    INT64,
    ctr            FLOAT64,
    position       FLOAT64,
    ingested_at    TIMESTAMP NOT NULL
)
PARTITION BY partition_date
CLUSTER BY site_url
OPTIONS (
    description = "Google Search Console search performance metrics by query/page/country/device",
    require_partition_filter = false
);

CREATE TABLE IF NOT EXISTS `{project}.raw.mysql_transactions`
(
    id          INT64     NOT NULL,
    status      STRING,
    amount      FLOAT64,
    currency    STRING,
    user_id     INT64,
    created_at  TIMESTAMP,
    updated_at  TIMESTAMP,
    ingested_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(updated_at)
CLUSTER BY status
OPTIONS (
    description = "Incremental load of MySQL transactions table",
    require_partition_filter = false
);

CREATE TABLE IF NOT EXISTS `{project}.logging.pipeline_execution_logs`
(
    job_id           STRING    NOT NULL,
    dag_id           STRING    NOT NULL,
    task_id          STRING    NOT NULL,
    run_id           STRING    NOT NULL,
    source_system    STRING    NOT NULL,
    target_table     STRING    NOT NULL,
    execution_date   DATE      NOT NULL,
    start_ts         TIMESTAMP NOT NULL,
    end_ts           TIMESTAMP NOT NULL,
    duration_seconds FLOAT64,
    rows_extracted   INT64,
    rows_loaded      INT64,
    status           STRING    NOT NULL,
    error_message    STRING,
    extra_json       STRING,
    logged_at        TIMESTAMP NOT NULL
)
PARTITION BY execution_date
CLUSTER BY dag_id, source_system
OPTIONS (
    description = "Pipeline execution audit log written by BQLogger",
    require_partition_filter = false
);
