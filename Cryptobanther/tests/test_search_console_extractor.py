from __future__ import annotations
from unittest.mock import MagicMock, patch, call
import pytest


class TestSearchConsoleClient:
    def test_query_search_performance_pagination(self):
        from ingestion.search_console.client import SearchConsoleClient, MAX_ROWS_PER_REQUEST

        mock_service = MagicMock()
        full_page = [
            {
                "keys": ["bitcoin price", "https://cryptobanter.com/bitcoin", "usa", "DESKTOP"],
                "clicks": 100,
                "impressions": 1000,
                "ctr": 0.1,
                "position": 3.5,
            }
        ] * MAX_ROWS_PER_REQUEST
        partial_page = [
            {
                "keys": ["crypto news", "https://cryptobanter.com/news", "gbr", "MOBILE"],
                "clicks": 50,
                "impressions": 500,
                "ctr": 0.1,
                "position": 5.2,
            }
        ] * 100

        mock_service.searchanalytics.return_value.query.return_value.execute.side_effect = [
            {"rows": full_page},
            {"rows": full_page},
            {"rows": partial_page},
        ]

        with patch.object(SearchConsoleClient, "_build_service", return_value=mock_service):
            with patch("google.auth.default", return_value=(MagicMock(), "project")):
                client = SearchConsoleClient()
                client._service = mock_service
                rows = client.query_search_performance(
                    site_url="https://cryptobanter.com/",
                    start_date="2024-01-15",
                    end_date="2024-01-15",
                )

        assert mock_service.searchanalytics.return_value.query.call_count == 3
        assert len(rows) == MAX_ROWS_PER_REQUEST * 2 + 100

    def test_query_search_performance_empty_returns_empty_list(self):
        from ingestion.search_console.client import SearchConsoleClient

        mock_service = MagicMock()
        mock_service.searchanalytics.return_value.query.return_value.execute.return_value = {"rows": []}

        with patch.object(SearchConsoleClient, "_build_service", return_value=mock_service):
            with patch("google.auth.default", return_value=(MagicMock(), "project")):
                client = SearchConsoleClient()
                client._service = mock_service
                rows = client.query_search_performance(
                    site_url="https://cryptobanter.com/",
                    start_date="2024-01-15",
                    end_date="2024-01-15",
                )

        assert rows == []

    def test_extract_adds_site_url_to_each_row(self):
        from ingestion.search_console.client import SearchConsoleClient

        mock_service = MagicMock()
        mock_service.searchanalytics.return_value.query.return_value.execute.return_value = {
            "rows": [
                {
                    "keys": ["eth price", "https://cryptobanter.com/eth", "aus", "TABLET"],
                    "clicks": 20,
                    "impressions": 200,
                    "ctr": 0.1,
                    "position": 4.0,
                },
                {
                    "keys": ["defi news", "https://cryptobanter.com/defi", "usa", "MOBILE"],
                    "clicks": 30,
                    "impressions": 300,
                    "ctr": 0.1,
                    "position": 2.5,
                },
            ]
        }

        with patch.object(SearchConsoleClient, "_build_service", return_value=mock_service):
            with patch("google.auth.default", return_value=(MagicMock(), "project")):
                client = SearchConsoleClient()
                client._service = mock_service
                rows = client.query_search_performance(
                    site_url="https://cryptobanter.com/",
                    start_date="2024-01-15",
                    end_date="2024-01-15",
                )

        assert all(r["site_url"] == "https://cryptobanter.com/" for r in rows)
        assert len(rows) == 2
        assert rows[0]["query"] == "eth price"
        assert rows[1]["country"] == "usa"
