WITH source AS (
    SELECT
        PARTITION_DATE,
        CHANNEL_ID,
        CHANNEL_TITLE,
        SUBSCRIBER_COUNT,
        VIEW_COUNT,
        VIDEO_COUNT,
        HIDDEN_SUBSCRIBER_COUNT,
        INGESTED_AT
    FROM {{ source('raw', 'youtube_channel_stats') }}
),

renamed AS (
    SELECT
        PARTITION_DATE                              AS partition_date,
        CHANNEL_ID                                  AS channel_id,
        CHANNEL_TITLE                               AS channel_title,
        SUBSCRIBER_COUNT                            AS subscriber_count,
        VIEW_COUNT                                  AS view_count,
        VIDEO_COUNT                                 AS video_count,
        HIDDEN_SUBSCRIBER_COUNT                     AS is_subscriber_count_hidden,
        INGESTED_AT                                 AS ingested_at,
        CONVERT_TIMEZONE('UTC', CURRENT_TIMESTAMP()) AS dbt_loaded_at
    FROM source
)

SELECT * FROM renamed
