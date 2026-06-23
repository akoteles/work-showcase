{{
  config(
    materialized = 'table',
    cluster_by   = ['partition_date', 'channel_id']
  )
}}

WITH base AS (
    SELECT
        partition_date,
        channel_id,
        channel_title,
        subscriber_count,
        channel_total_views,
        channel_total_videos,
        videos_in_window,
        total_video_views,
        total_likes,
        total_comments,
        avg_views_per_video,
        max_video_views,
        earliest_video_published
    FROM {{ ref('int_channel_video_joined') }}
),

with_engagement_rate AS (
    SELECT
        partition_date,
        channel_id,
        channel_title,
        subscriber_count,
        channel_total_views,
        channel_total_videos,
        videos_in_window,
        total_video_views,
        total_likes,
        total_comments,
        avg_views_per_video,
        max_video_views,
        earliest_video_published,
        CASE
            WHEN total_video_views > 0
            THEN (total_likes + total_comments) / total_video_views
            ELSE 0
        END                                            AS engagement_rate,
        CASE
            WHEN subscriber_count > 0
            THEN total_video_views / subscriber_count
            ELSE NULL
        END                                            AS views_per_subscriber,
        CONVERT_TIMEZONE('UTC', CURRENT_TIMESTAMP())   AS refreshed_at
    FROM base
)

SELECT * FROM with_engagement_rate
