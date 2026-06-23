-- Singular test: ensure subscriber counts are non-negative
-- Any rows returned by this query will cause the test to FAIL

SELECT
    partition_date,
    channel_id,
    subscriber_count
FROM {{ ref('mart_channel_performance_daily') }}
WHERE subscriber_count < 0
