WITH source AS (
    SELECT
        PARTITION_DATE,
        SITE_URL,
        QUERY,
        PAGE,
        COUNTRY,
        DEVICE,
        CLICKS,
        IMPRESSIONS,
        CTR,
        POSITION,
        INGESTED_AT
    FROM {{ source('raw', 'gsc_search_performance') }}
),

renamed AS (
    SELECT
        PARTITION_DATE                              AS partition_date,
        SITE_URL                                    AS site_url,
        QUERY                                       AS search_query,
        PAGE                                        AS landing_page,
        UPPER(COUNTRY)                              AS country_code,
        UPPER(DEVICE)                               AS device_type,
        CLICKS                                      AS clicks,
        IMPRESSIONS                                 AS impressions,
        CTR                                         AS click_through_rate,
        POSITION                                    AS avg_position,
        INGESTED_AT                                 AS ingested_at,
        CASE
            WHEN LOWER(QUERY) LIKE '%cryptobanter%'
              OR LOWER(QUERY) LIKE '%crypto banter%' THEN TRUE
            ELSE FALSE
        END                                         AS is_branded,
        CONVERT_TIMEZONE('UTC', CURRENT_TIMESTAMP()) AS dbt_loaded_at
    FROM source
)

SELECT * FROM renamed
