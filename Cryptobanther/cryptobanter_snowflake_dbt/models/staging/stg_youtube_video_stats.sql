WITH source AS (
    SELECT
        PARTITION_DATE,
        VIDEO_ID,
        CHANNEL_ID,
        TITLE,
        PUBLISHED_AT,
        VIEW_COUNT,
        LIKE_COUNT,
        COMMENT_COUNT,
        DURATION_ISO,
        INGESTED_AT
    FROM {{ source('raw', 'youtube_video_stats') }}
),

renamed AS (
    SELECT
        PARTITION_DATE                              AS partition_date,
        VIDEO_ID                                    AS video_id,
        CHANNEL_ID                                  AS channel_id,
        TITLE                                       AS video_title,
        PUBLISHED_AT                                AS published_at,
        VIEW_COUNT                                  AS view_count,
        LIKE_COUNT                                  AS like_count,
        COMMENT_COUNT                               AS comment_count,
        DURATION_ISO                                AS duration_iso,
        INGESTED_AT                                 AS ingested_at,
        CONVERT_TIMEZONE('UTC', CURRENT_TIMESTAMP()) AS dbt_loaded_at
    FROM source
)

SELECT * FROM renamed
