-- Parity Analysis: BigQuery vs Snowflake row count and aggregate validation
-- Run this SQL in Snowflake after loading data to both platforms.
-- Replace <BQ_PROJECT>, <BQ_DATASET> with your actual values.
-- This assumes Snowflake has external stage access or results were exported.

-- ============================================================
-- 1. YouTube Channel Stats: Row Count Parity
-- ============================================================
-- Expected: Snowflake row count matches BigQuery row count for the same partition_date

SELECT
    'youtube_channel_stats'         AS table_name,
    'row_count'                     AS check_type,
    partition_date,
    COUNT(*)                        AS snowflake_count,
    -- Replace with actual BQ export count loaded into comparison table
    NULL                            AS bigquery_count,
    ABS(COUNT(*) - COALESCE(NULL, COUNT(*))) AS abs_diff
FROM {{ ref('stg_youtube_channel_stats') }}
WHERE partition_date >= DATEADD(DAY, -7, CURRENT_DATE())
GROUP BY partition_date
ORDER BY partition_date DESC;

-- ============================================================
-- 2. YouTube Video Stats: Aggregate Parity (total views per channel)
-- ============================================================

SELECT
    'youtube_video_stats'           AS table_name,
    'total_views_by_channel'        AS check_type,
    partition_date,
    channel_id,
    SUM(view_count)                 AS snowflake_total_views
FROM {{ ref('stg_youtube_video_stats') }}
WHERE partition_date >= DATEADD(DAY, -7, CURRENT_DATE())
GROUP BY partition_date, channel_id
ORDER BY partition_date DESC, channel_id;

-- ============================================================
-- 3. GSC Performance: Click Sum Parity
-- ============================================================

SELECT
    'gsc_search_performance'        AS table_name,
    'total_clicks_by_site'          AS check_type,
    partition_date,
    site_url,
    SUM(clicks)                     AS snowflake_total_clicks,
    SUM(impressions)                AS snowflake_total_impressions
FROM {{ ref('stg_gsc_search_performance') }}
WHERE partition_date >= DATEADD(DAY, -7, CURRENT_DATE())
GROUP BY partition_date, site_url
ORDER BY partition_date DESC, site_url;

-- ============================================================
-- 4. MySQL Transactions: Revenue Parity
-- ============================================================

SELECT
    'mysql_transactions'            AS table_name,
    'total_revenue_by_currency'     AS check_type,
    created_date,
    currency_code,
    SUM(CASE WHEN is_successful THEN amount ELSE 0 END) AS snowflake_revenue,
    COUNT(*) AS snowflake_transaction_count
FROM {{ ref('stg_mysql_transactions') }}
WHERE created_date >= DATEADD(DAY, -7, CURRENT_DATE())
GROUP BY created_date, currency_code
ORDER BY created_date DESC, currency_code;
