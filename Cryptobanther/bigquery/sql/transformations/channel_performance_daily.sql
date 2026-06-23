-- Transformation: Channel Performance Daily
-- Populates reporting.channel_performance_daily from raw.youtube_channel_stats
-- and raw.youtube_video_stats for the target date.
-- Run with substitution: @target_date = YYYY-MM-DD

MERGE `{project}.reporting.channel_performance_daily` T
USING (
    WITH channel_snap AS (
        SELECT
            partition_date,
            channel_id,
            channel_title,
            subscriber_count,
            view_count,
            video_count
        FROM `{project}.raw.youtube_channel_stats`
        WHERE partition_date = @target_date
    ),
    video_agg AS (
        SELECT
            channel_id,
            COUNT(DISTINCT video_id)                              AS new_videos,
            SUM(view_count)                                       AS total_views_7d,
            SUM(like_count)                                       AS total_likes_7d,
            SUM(comment_count)                                    AS total_comments_7d,
            SAFE_DIVIDE(SUM(view_count), COUNT(DISTINCT video_id)) AS avg_views_per_video
        FROM `{project}.raw.youtube_video_stats`
        WHERE partition_date BETWEEN DATE_SUB(@target_date, INTERVAL 6 DAY) AND @target_date
        GROUP BY channel_id
    )
    SELECT
        cs.partition_date,
        cs.channel_id,
        cs.channel_title,
        cs.subscriber_count,
        cs.view_count,
        cs.video_count,
        COALESCE(va.new_videos, 0)        AS new_videos,
        COALESCE(va.total_views_7d, 0)    AS total_views_7d,
        COALESCE(va.total_likes_7d, 0)    AS total_likes_7d,
        COALESCE(va.total_comments_7d, 0) AS total_comments_7d,
        va.avg_views_per_video,
        CURRENT_TIMESTAMP()               AS refreshed_at
    FROM channel_snap cs
    LEFT JOIN video_agg va USING (channel_id)
) S
ON T.partition_date = S.partition_date AND T.channel_id = S.channel_id
WHEN MATCHED THEN UPDATE SET
    channel_title       = S.channel_title,
    subscriber_count    = S.subscriber_count,
    view_count          = S.view_count,
    video_count         = S.video_count,
    new_videos          = S.new_videos,
    total_views_7d      = S.total_views_7d,
    total_likes_7d      = S.total_likes_7d,
    total_comments_7d   = S.total_comments_7d,
    avg_views_per_video = S.avg_views_per_video,
    refreshed_at        = S.refreshed_at
WHEN NOT MATCHED THEN INSERT ROW;
