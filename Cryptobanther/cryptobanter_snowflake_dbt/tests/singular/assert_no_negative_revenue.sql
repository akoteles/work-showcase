-- Singular test: ensure no negative revenue values in financial KPIs
-- Any rows returned by this query will cause the test to FAIL

SELECT
    transaction_date,
    currency_code,
    total_revenue
FROM {{ ref('mart_financial_kpis_daily') }}
WHERE total_revenue < 0
