from __future__ import annotations
import logging
from typing import List, Optional
import google.auth
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

MAX_ROWS_PER_REQUEST = 25000
DIMENSIONS = ["query", "page", "country", "device"]


class SearchConsoleClient:
    API_SERVICE_NAME = "searchconsole"
    API_VERSION = "v1"
    SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

    def __init__(self, credentials=None) -> None:
        if credentials:
            self._credentials = credentials
        else:
            self._credentials, _ = google.auth.default(scopes=self.SCOPES)
        self._service = self._build_service()

    def _build_service(self):
        return build(self.API_SERVICE_NAME, self.API_VERSION, credentials=self._credentials)

    def get_verified_sites(self) -> List[str]:
        response = self._service.sites().list().execute()
        site_entries = response.get("siteEntry", [])
        verified = [
            s["siteUrl"]
            for s in site_entries
            if s.get("permissionLevel") in ("siteOwner", "siteFullUser", "siteRestrictedUser")
        ]
        logger.info("Found %d verified GSC sites", len(verified))
        return verified

    def query_search_performance(
        self,
        site_url: str,
        start_date: str,
        end_date: str,
        dimensions: Optional[List[str]] = None,
    ) -> List[dict]:
        if dimensions is None:
            dimensions = DIMENSIONS

        all_rows: List[dict] = []
        start_row = 0

        while True:
            request_body = {
                "startDate": start_date,
                "endDate": end_date,
                "dimensions": dimensions,
                "rowLimit": MAX_ROWS_PER_REQUEST,
                "startRow": start_row,
            }
            try:
                response = (
                    self._service.searchanalytics()
                    .query(siteUrl=site_url, body=request_body)
                    .execute()
                )
            except Exception as exc:
                logger.error("GSC query failed for site %s: %s", site_url, exc)
                raise

            rows = response.get("rows", [])
            if not rows:
                break

            for row in rows:
                keys = row.get("keys", [])
                record = {
                    "site_url": site_url,
                    "query": keys[0] if len(keys) > 0 else None,
                    "page": keys[1] if len(keys) > 1 else None,
                    "country": keys[2] if len(keys) > 2 else None,
                    "device": keys[3] if len(keys) > 3 else None,
                    "clicks": int(row.get("clicks", 0)),
                    "impressions": int(row.get("impressions", 0)),
                    "ctr": float(row.get("ctr", 0.0)),
                    "position": float(row.get("position", 0.0)),
                }
                all_rows.append(record)

            logger.info(
                "GSC %s: fetched %d rows (total so far: %d)",
                site_url,
                len(rows),
                len(all_rows),
            )

            if len(rows) < MAX_ROWS_PER_REQUEST:
                break

            start_row += MAX_ROWS_PER_REQUEST

        return all_rows
