-- Singular test: ensure CTR values are between 0 and 1
-- Any rows returned by this query will cause the test to FAIL

SELECT
    partition_date,
    site_url,
    overall_ctr
FROM {{ ref('mart_search_visibility_daily') }}
WHERE overall_ctr < 0 OR overall_ctr > 1
