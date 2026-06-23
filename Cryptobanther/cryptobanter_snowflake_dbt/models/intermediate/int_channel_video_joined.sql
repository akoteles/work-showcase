{{
  config(
    materialized = 'incremental',
    unique_key   = 'surrogate_key',
    on_schema_change = 'append_new_columns'
  )
}}

WITH channel_stats AS (
    SELECT
        partition_date,
        channel_id,
        channel_title,
        subscriber_count,
        view_count     AS channel_total_views,
        video_count    AS channel_total_videos
    FROM {{ ref('stg_youtube_channel_stats') }}
),

video_stats AS (
    SELECT
        partition_date,
        channel_id,
        video_id,
        video_title,
        published_at,
        view_count,
        like_count,
        comment_count,
        duration_iso
    FROM {{ ref('stg_youtube_video_stats') }}
),

video_agg AS (
    SELECT
        partition_date,
        channel_id,
        COUNT(DISTINCT video_id)                               AS videos_in_window,
        SUM(view_count)                                        AS total_video_views,
        SUM(like_count)                                        AS total_likes,
        SUM(comment_count)                                     AS total_comments,
        AVG(view_count)                                        AS avg_views_per_video,
        MAX(view_count)                                        AS max_video_views,
        MIN(published_at)                                      AS earliest_video_published
    FROM video_stats
    GROUP BY partition_date, channel_id
),

joined AS (
    SELECT
        c.partition_date,
        c.channel_id,
        c.channel_title,
        c.subscriber_count,
        c.channel_total_views,
        c.channel_total_videos,
        COALESCE(va.videos_in_window, 0)     AS videos_in_window,
        COALESCE(va.total_video_views, 0)    AS total_video_views,
        COALESCE(va.total_likes, 0)          AS total_likes,
        COALESCE(va.total_comments, 0)       AS total_comments,
        va.avg_views_per_video,
        va.max_video_views,
        va.earliest_video_published,
        MD5(CAST(c.partition_date AS VARCHAR) || '|' || c.channel_id) AS surrogate_key
    FROM channel_stats c
    LEFT JOIN video_agg va
        ON c.partition_date = va.partition_date
        AND c.channel_id    = va.channel_id
)

SELECT * FROM joined

{% if is_incremental() %}
WHERE partition_date > (SELECT MAX(partition_date) FROM {{ this }})
{% endif %}
