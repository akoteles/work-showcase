{{
  config(
    materialized = 'table',
    cluster_by   = ['partition_date', 'site_url']
  )
}}

WITH branded_split AS (
    SELECT
        partition_date,
        site_url,
        is_branded,
        total_clicks,
        total_impressions,
        overall_ctr,
        weighted_avg_position,
        unique_queries,
        unique_pages
    FROM {{ ref('int_gsc_branded_split') }}
),

pivoted AS (
    SELECT
        partition_date,
        site_url,
        SUM(total_clicks)                                            AS total_clicks,
        SUM(total_impressions)                                       AS total_impressions,
        CASE
            WHEN SUM(total_impressions) > 0
            THEN SUM(total_clicks) / SUM(total_impressions)
            ELSE 0
        END                                                          AS overall_ctr,
        SUM(total_impressions * weighted_avg_position)
            / NULLIF(SUM(total_impressions), 0)                      AS avg_position,
        SUM(CASE WHEN is_branded THEN total_clicks ELSE 0 END)       AS branded_clicks,
        SUM(CASE WHEN NOT is_branded THEN total_clicks ELSE 0 END)   AS non_branded_clicks,
        SUM(CASE WHEN is_branded THEN total_impressions ELSE 0 END)  AS branded_impressions,
        SUM(CASE WHEN NOT is_branded THEN total_impressions ELSE 0 END) AS non_branded_impressions,
        SUM(unique_queries)                                          AS total_unique_queries,
        SUM(unique_pages)                                            AS total_unique_pages,
        CONVERT_TIMEZONE('UTC', CURRENT_TIMESTAMP())                 AS refreshed_at
    FROM branded_split
    GROUP BY partition_date, site_url
),

with_ratios AS (
    SELECT
        partition_date,
        site_url,
        total_clicks,
        total_impressions,
        overall_ctr,
        avg_position,
        branded_clicks,
        non_branded_clicks,
        branded_impressions,
        non_branded_impressions,
        total_unique_queries,
        total_unique_pages,
        CASE
            WHEN total_clicks > 0
            THEN branded_clicks / total_clicks
            ELSE 0
        END                  AS branded_click_share,
        refreshed_at
    FROM pivoted
)

SELECT * FROM with_ratios
