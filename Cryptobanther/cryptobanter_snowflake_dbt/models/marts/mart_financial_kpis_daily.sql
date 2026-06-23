{{
  config(
    materialized = 'table',
    cluster_by   = ['transaction_date', 'currency_code']
  )
}}

WITH transactions AS (
    SELECT
        created_date        AS transaction_date,
        transaction_id,
        transaction_status,
        amount,
        currency_code,
        user_id,
        is_successful
    FROM {{ ref('stg_mysql_transactions') }}
    WHERE created_date IS NOT NULL
),

daily_summary AS (
    SELECT
        transaction_date,
        currency_code,
        COUNT(*)                                                    AS total_transactions,
        COUNT(CASE WHEN is_successful THEN 1 END)                   AS successful_transactions,
        COUNT(CASE WHEN NOT is_successful THEN 1 END)               AS failed_transactions,
        SUM(CASE WHEN is_successful THEN amount ELSE 0 END)         AS total_revenue,
        AVG(CASE WHEN is_successful THEN amount END)                AS avg_order_value,
        MAX(CASE WHEN is_successful THEN amount END)                AS max_order_value,
        MIN(CASE WHEN is_successful THEN amount END)                AS min_order_value,
        COUNT(DISTINCT CASE WHEN is_successful THEN user_id END)    AS unique_paying_users,
        CASE
            WHEN COUNT(*) > 0
            THEN COUNT(CASE WHEN is_successful THEN 1 END) / COUNT(*)
            ELSE 0
        END                                                         AS success_rate
    FROM transactions
    GROUP BY transaction_date, currency_code
),

with_metadata AS (
    SELECT
        transaction_date,
        currency_code,
        total_transactions,
        successful_transactions,
        failed_transactions,
        total_revenue,
        avg_order_value,
        max_order_value,
        min_order_value,
        unique_paying_users,
        success_rate,
        CONVERT_TIMEZONE('UTC', CURRENT_TIMESTAMP())  AS refreshed_at
    FROM daily_summary
)

SELECT * FROM with_metadata
