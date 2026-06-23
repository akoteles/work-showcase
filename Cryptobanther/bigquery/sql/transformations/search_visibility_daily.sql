-- Transformation: Search Visibility Daily
-- Populates reporting.search_visibility_daily from raw.gsc_search_performance
-- Run with substitution: @target_date = YYYY-MM-DD

MERGE `{project}.reporting.search_visibility_daily` T
USING (
    WITH daily_gsc AS (
        SELECT
            partition_date,
            site_url,
            query,
            page,
            clicks,
            impressions,
            ctr,
            position
        FROM `{project}.raw.gsc_search_performance`
        WHERE partition_date = @target_date
    ),
    site_agg AS (
        SELECT
            partition_date,
            site_url,
            SUM(clicks)                             AS total_clicks,
            SUM(impressions)                        AS total_impressions,
            SAFE_DIVIDE(SUM(clicks), SUM(impressions)) AS avg_ctr,
            SAFE_DIVIDE(SUM(position * impressions), SUM(impressions)) AS avg_position
        FROM daily_gsc
        GROUP BY partition_date, site_url
    ),
    top_query AS (
        SELECT
            partition_date,
            site_url,
            query AS top_query,
            ROW_NUMBER() OVER (
                PARTITION BY partition_date, site_url
                ORDER BY SUM(clicks) DESC
            ) AS rn
        FROM daily_gsc
        WHERE query IS NOT NULL
        GROUP BY partition_date, site_url, query
        QUALIFY rn = 1
    ),
    top_page AS (
        SELECT
            partition_date,
            site_url,
            page AS top_page,
            ROW_NUMBER() OVER (
                PARTITION BY partition_date, site_url
                ORDER BY SUM(clicks) DESC
            ) AS rn
        FROM daily_gsc
        WHERE page IS NOT NULL
        GROUP BY partition_date, site_url, page
        QUALIFY rn = 1
    ),
    branded AS (
        SELECT
            partition_date,
            site_url,
            SUM(CASE WHEN LOWER(query) LIKE '%cryptobanter%' OR LOWER(query) LIKE '%crypto banter%'
                THEN clicks ELSE 0 END) AS branded_clicks,
            SUM(CASE WHEN NOT (LOWER(query) LIKE '%cryptobanter%' OR LOWER(query) LIKE '%crypto banter%')
                THEN clicks ELSE 0 END) AS non_branded_clicks
        FROM daily_gsc
        WHERE query IS NOT NULL
        GROUP BY partition_date, site_url
    )
    SELECT
        sa.partition_date,
        sa.site_url,
        sa.total_clicks,
        sa.total_impressions,
        sa.avg_ctr,
        sa.avg_position,
        tq.top_query,
        tp.top_page,
        COALESCE(b.branded_clicks, 0)     AS branded_clicks,
        COALESCE(b.non_branded_clicks, 0) AS non_branded_clicks,
        CURRENT_TIMESTAMP()               AS refreshed_at
    FROM site_agg sa
    LEFT JOIN top_query tq USING (partition_date, site_url)
    LEFT JOIN top_page  tp USING (partition_date, site_url)
    LEFT JOIN branded    b USING (partition_date, site_url)
) S
ON T.partition_date = S.partition_date AND T.site_url = S.site_url
WHEN MATCHED THEN UPDATE SET
    total_clicks        = S.total_clicks,
    total_impressions   = S.total_impressions,
    avg_ctr             = S.avg_ctr,
    avg_position        = S.avg_position,
    top_query           = S.top_query,
    top_page            = S.top_page,
    branded_clicks      = S.branded_clicks,
    non_branded_clicks  = S.non_branded_clicks,
    refreshed_at        = S.refreshed_at
WHEN NOT MATCHED THEN INSERT ROW;
