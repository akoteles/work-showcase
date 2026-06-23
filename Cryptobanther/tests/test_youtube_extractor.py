from __future__ import annotations
import io
import json
from datetime import date, datetime
from unittest.mock import MagicMock, patch, call
import pytest


class TestYouTubeClient:
    def test_get_channel_stats_parses_response(self):
        from ingestion.youtube.client import YouTubeClient

        mock_service = MagicMock()
        mock_response = {
            "items": [
                {
                    "id": "UCXGgrKt94gR6lmN4aN3n-uQ",
                    "snippet": {"title": "Crypto Banter", "publishedAt": "2018-01-01T00:00:00Z"},
                    "statistics": {
                        "subscriberCount": "1234567",
                        "viewCount": "99000000",
                        "videoCount": "5000",
                        "hiddenSubscriberCount": False,
                    },
                }
            ]
        }
        mock_service.channels.return_value.list.return_value.execute.return_value = mock_response

        with patch.object(YouTubeClient, "_build_service", return_value=mock_service):
            with patch("google.auth.default", return_value=(MagicMock(), "project")):
                client = YouTubeClient()
                client._service = mock_service
                stats = client.get_channel_stats(["UCXGgrKt94gR6lmN4aN3n-uQ"])

        assert len(stats) == 1
        assert stats[0]["channel_id"] == "UCXGgrKt94gR6lmN4aN3n-uQ"
        assert stats[0]["subscriber_count"] == 1234567
        assert stats[0]["view_count"] == 99000000
        assert stats[0]["channel_title"] == "Crypto Banter"

    def test_get_video_stats_chunks_requests(self):
        from ingestion.youtube.client import YouTubeClient, CHUNK_SIZE

        mock_service = MagicMock()
        mock_response = {"items": []}
        mock_service.videos.return_value.list.return_value.execute.return_value = mock_response

        with patch.object(YouTubeClient, "_build_service", return_value=mock_service):
            with patch("google.auth.default", return_value=(MagicMock(), "project")):
                client = YouTubeClient()
                client._service = mock_service
                video_ids = [f"vid_{i}" for i in range(110)]
                client.get_video_stats(video_ids)

        expected_calls = 3  # 50 + 50 + 10
        assert mock_service.videos.return_value.list.call_count == expected_calls

    def test_get_video_stats_parses_statistics_fields(self):
        from ingestion.youtube.client import YouTubeClient

        mock_service = MagicMock()
        mock_response = {
            "items": [
                {
                    "id": "dQw4w9WgXcQ",
                    "snippet": {
                        "channelId": "UCChannel1",
                        "title": "Never Gonna Give You Up",
                        "publishedAt": "2009-10-25T06:57:33Z",
                    },
                    "statistics": {
                        "viewCount": "1400000000",
                        "likeCount": "15000000",
                        "commentCount": "3000000",
                    },
                    "contentDetails": {"duration": "PT3M33S"},
                }
            ]
        }
        mock_service.videos.return_value.list.return_value.execute.return_value = mock_response

        with patch.object(YouTubeClient, "_build_service", return_value=mock_service):
            with patch("google.auth.default", return_value=(MagicMock(), "project")):
                client = YouTubeClient()
                client._service = mock_service
                stats = client.get_video_stats(["dQw4w9WgXcQ"])

        assert len(stats) == 1
        assert stats[0]["video_id"] == "dQw4w9WgXcQ"
        assert stats[0]["view_count"] == 1400000000
        assert stats[0]["like_count"] == 15000000
        assert stats[0]["duration_iso"] == "PT3M33S"
