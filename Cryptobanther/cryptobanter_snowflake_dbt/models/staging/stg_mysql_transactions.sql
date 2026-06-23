WITH source AS (
    SELECT
        ID,
        STATUS,
        AMOUNT,
        CURRENCY,
        USER_ID,
        CREATED_AT,
        UPDATED_AT
    FROM {{ source('raw', 'mysql_transactions') }}
),

renamed AS (
    SELECT
        ID                                          AS transaction_id,
        UPPER(STATUS)                               AS transaction_status,
        AMOUNT                                      AS amount,
        UPPER(CURRENCY)                             AS currency_code,
        USER_ID                                     AS user_id,
        CREATED_AT                                  AS created_at,
        UPDATED_AT                                  AS updated_at,
        DATE(CREATED_AT)                            AS created_date,
        DATE(UPDATED_AT)                            AS updated_date,
        CASE
            WHEN UPPER(STATUS) IN ('COMPLETED', 'SETTLED') THEN TRUE
            ELSE FALSE
        END                                         AS is_successful,
        CONVERT_TIMEZONE('UTC', CURRENT_TIMESTAMP()) AS dbt_loaded_at
    FROM source
)

SELECT * FROM renamed
