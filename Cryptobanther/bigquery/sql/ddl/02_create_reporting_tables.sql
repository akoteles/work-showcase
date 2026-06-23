-- DDL: Reporting layer tables for CryptoBanter GCP Data Platform
-- Replace {project} with your GCP project ID before running

CREATE TABLE IF NOT EXISTS `{project}.reporting.channel_performance_daily`
(
    partition_date    DATE      NOT NULL,
    channel_id        STRING    NOT NULL,
    channel_title     STRING,
    subscriber_count  INT64,
    view_count        INT64,
    video_count       INT64,
    new_videos        INT64,
    total_views_7d    INT64,
    total_likes_7d    INT64,
    total_comments_7d INT64,
    avg_views_per_video FLOAT64,
    refreshed_at      TIMESTAMP NOT NULL
)
PARTITION BY partition_date
CLUSTER BY channel_id
OPTIONS (
    description = "Daily aggregated YouTube channel performance metrics",
    require_partition_filter = false
);

CREATE TABLE IF NOT EXISTS `{project}.reporting.financial_kpis_daily`
(
    kpi_date          DATE      NOT NULL,
    metric_category   STRING    NOT NULL,
    metric_name       STRING    NOT NULL,
    metric_value      FLOAT64,
    currency          STRING,
    transaction_count INT64,
    refreshed_at      TIMESTAMP NOT NULL
)
PARTITION BY kpi_date
CLUSTER BY metric_category
OPTIONS (
    description = "Daily financial KPIs derived from MySQL OLTP transactions",
    require_partition_filter = false
);

CREATE TABLE IF NOT EXISTS `{project}.reporting.search_visibility_daily`
(
    partition_date    DATE      NOT NULL,
    site_url          STRING    NOT NULL,
    total_clicks      INT64,
    total_impressions INT64,
    avg_ctr           FLOAT64,
    avg_position      FLOAT64,
    top_query         STRING,
    top_page          STRING,
    branded_clicks    INT64,
    non_branded_clicks INT64,
    refreshed_at      TIMESTAMP NOT NULL
)
PARTITION BY partition_date
CLUSTER BY site_url
OPTIONS (
    description = "Daily Google Search Console visibility summary",
    require_partition_filter = false
);
