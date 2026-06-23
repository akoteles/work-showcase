{{
  config(
    materialized = 'incremental',
    unique_key   = 'surrogate_key',
    on_schema_change = 'append_new_columns'
  )
}}

WITH gsc AS (
    SELECT
        partition_date,
        site_url,
        search_query,
        landing_page,
        country_code,
        device_type,
        clicks,
        impressions,
        click_through_rate,
        avg_position,
        is_branded
    FROM {{ ref('stg_gsc_search_performance') }}
),

aggregated AS (
    SELECT
        partition_date,
        site_url,
        is_branded,
        SUM(clicks)                                      AS total_clicks,
        SUM(impressions)                                 AS total_impressions,
        CASE
            WHEN SUM(impressions) > 0
            THEN SUM(clicks) / SUM(impressions)
            ELSE 0
        END                                              AS overall_ctr,
        SUM(impressions * avg_position) / NULLIF(SUM(impressions), 0) AS weighted_avg_position,
        COUNT(DISTINCT search_query)                     AS unique_queries,
        COUNT(DISTINCT landing_page)                     AS unique_pages,
        MD5(CAST(partition_date AS VARCHAR) || '|' || site_url || '|' || CAST(is_branded AS VARCHAR)) AS surrogate_key
    FROM gsc
    GROUP BY partition_date, site_url, is_branded
)

SELECT * FROM aggregated

{% if is_incremental() %}
WHERE partition_date > (SELECT MAX(partition_date) FROM {{ this }})
{% endif %}
