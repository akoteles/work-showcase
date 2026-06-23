from __future__ import annotations
import logging
import time
from typing import List, Optional
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

CHUNK_SIZE = 50
MAX_QUOTA_RETRIES = 3
QUOTA_SLEEP_SECONDS = 60


class YouTubeClient:
    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"
    SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
    MAX_RESULTS_PER_PAGE = 50

    def __init__(self, api_key: Optional[str] = None, credentials=None) -> None:
        if credentials:
            self._credentials = credentials
            self._api_key = None
        elif api_key:
            self._credentials = None
            self._api_key = api_key
        else:
            self._credentials, _ = google.auth.default(scopes=self.SCOPES)
            self._api_key = None
        self._service = self._build_service()

    def _build_service(self):
        if self._api_key and not self._credentials:
            return build(self.API_SERVICE_NAME, self.API_VERSION, developerKey=self._api_key)
        return build(self.API_SERVICE_NAME, self.API_VERSION, credentials=self._credentials)

    def _paginated_request(self, request_fn, **kwargs) -> List[dict]:
        items = []
        page_token = None
        retries = 0
        while True:
            if page_token:
                kwargs["pageToken"] = page_token
            try:
                request = request_fn(**kwargs)
                response = request.execute()
                retries = 0
            except HttpError as exc:
                if exc.resp.status == 403 and retries < MAX_QUOTA_RETRIES:
                    retries += 1
                    logger.warning(
                        "YouTube quota error, sleeping %ds (attempt %d)",
                        QUOTA_SLEEP_SECONDS,
                        retries,
                    )
                    time.sleep(QUOTA_SLEEP_SECONDS)
                    continue
                raise
            items.extend(response.get("items", []))
            page_token = response.get("nextPageToken")
            if not page_token:
                break
        return items

    def get_channel_stats(self, channel_ids: List[str]) -> List[dict]:
        ids_str = ",".join(channel_ids)
        items = self._paginated_request(
            self._service.channels().list,
            part="snippet,statistics",
            id=ids_str,
            maxResults=self.MAX_RESULTS_PER_PAGE,
        )
        results = []
        for item in items:
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            results.append({
                "channel_id": item["id"],
                "channel_title": snippet.get("title"),
                "published_at": snippet.get("publishedAt"),
                "subscriber_count": int(stats["subscriberCount"]) if stats.get("subscriberCount") else None,
                "view_count": int(stats["viewCount"]) if stats.get("viewCount") else None,
                "video_count": int(stats["videoCount"]) if stats.get("videoCount") else None,
                "hidden_subscriber_count": stats.get("hiddenSubscriberCount", False),
            })
        return results

    def get_videos_in_date_range(
        self,
        channel_id: str,
        published_after: str,
        published_before: str,
    ) -> List[dict]:
        items = self._paginated_request(
            self._service.search().list,
            part="id,snippet",
            channelId=channel_id,
            type="video",
            publishedAfter=published_after,
            publishedBefore=published_before,
            maxResults=self.MAX_RESULTS_PER_PAGE,
        )
        results = []
        for item in items:
            video_id = item.get("id", {}).get("videoId")
            if not video_id:
                continue
            snippet = item.get("snippet", {})
            results.append({
                "video_id": video_id,
                "title": snippet.get("title"),
                "published_at": snippet.get("publishedAt"),
            })
        return results

    def get_video_stats(self, video_ids: List[str]) -> List[dict]:
        results = []
        for i in range(0, len(video_ids), CHUNK_SIZE):
            chunk = video_ids[i:i + CHUNK_SIZE]
            items = self._paginated_request(
                self._service.videos().list,
                part="snippet,statistics,contentDetails",
                id=",".join(chunk),
                maxResults=self.MAX_RESULTS_PER_PAGE,
            )
            for item in items:
                stats = item.get("statistics", {})
                snippet = item.get("snippet", {})
                content_details = item.get("contentDetails", {})
                results.append({
                    "video_id": item["id"],
                    "channel_id": snippet.get("channelId"),
                    "title": snippet.get("title"),
                    "published_at": snippet.get("publishedAt"),
                    "view_count": int(stats["viewCount"]) if stats.get("viewCount") else None,
                    "like_count": int(stats["likeCount"]) if stats.get("likeCount") else None,
                    "comment_count": int(stats["commentCount"]) if stats.get("commentCount") else None,
                    "duration_iso": content_details.get("duration"),
                })
        return results
