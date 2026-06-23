-- Transformation: Financial KPIs Daily
-- Populates reporting.financial_kpis_daily from raw.mysql_transactions
-- Run with substitution: @target_date = YYYY-MM-DD

MERGE `{project}.reporting.financial_kpis_daily` T
USING (
    WITH daily_txns AS (
        SELECT
            DATE(updated_at) AS kpi_date,
            status,
            currency,
            amount
        FROM `{project}.raw.mysql_transactions`
        WHERE DATE(updated_at) = @target_date
          AND status IS NOT NULL
    ),
    revenue_by_currency AS (
        SELECT
            kpi_date,
            'revenue'      AS metric_category,
            CONCAT('total_revenue_', LOWER(COALESCE(currency, 'unknown'))) AS metric_name,
            SUM(amount)    AS metric_value,
            currency,
            COUNT(*)       AS transaction_count
        FROM daily_txns
        WHERE status IN ('completed', 'settled')
        GROUP BY kpi_date, currency
    ),
    transaction_counts AS (
        SELECT
            kpi_date,
            'volume'       AS metric_category,
            CONCAT('txn_count_', LOWER(COALESCE(status, 'unknown'))) AS metric_name,
            CAST(COUNT(*) AS FLOAT64) AS metric_value,
            NULL           AS currency,
            COUNT(*)       AS transaction_count
        FROM daily_txns
        GROUP BY kpi_date, status
    ),
    avg_order_value AS (
        SELECT
            kpi_date,
            'revenue'      AS metric_category,
            CONCAT('avg_order_value_', LOWER(COALESCE(currency, 'unknown'))) AS metric_name,
            SAFE_DIVIDE(SUM(amount), COUNT(*)) AS metric_value,
            currency,
            COUNT(*)       AS transaction_count
        FROM daily_txns
        WHERE status IN ('completed', 'settled')
        GROUP BY kpi_date, currency
    )
    SELECT kpi_date, metric_category, metric_name, metric_value, currency, transaction_count,
           CURRENT_TIMESTAMP() AS refreshed_at
    FROM revenue_by_currency
    UNION ALL
    SELECT kpi_date, metric_category, metric_name, metric_value, currency, transaction_count,
           CURRENT_TIMESTAMP() AS refreshed_at
    FROM transaction_counts
    UNION ALL
    SELECT kpi_date, metric_category, CONCAT('aov_', metric_name) AS metric_name,
           metric_value, currency, transaction_count,
           CURRENT_TIMESTAMP() AS refreshed_at
    FROM avg_order_value
) S
ON T.kpi_date = S.kpi_date
   AND T.metric_category = S.metric_category
   AND T.metric_name = S.metric_name
   AND COALESCE(T.currency, '') = COALESCE(S.currency, '')
WHEN MATCHED THEN UPDATE SET
    metric_value      = S.metric_value,
    transaction_count = S.transaction_count,
    refreshed_at      = S.refreshed_at
WHEN NOT MATCHED THEN INSERT ROW;
