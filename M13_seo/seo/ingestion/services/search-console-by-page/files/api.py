#!/usr/bin/env python

from googleapiclient.discovery import build
from google.oauth2 import service_account
import logging
from typing import Dict


class SearchConsoleAPI:

    def __init__(self, service_account_info: Dict, scopes: list):
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=scopes
        )
        self.service = build("searchconsole", "v1", credentials=credentials)
        logging.info("Search Console API client initialized")

    def get_url_properties(self):
        try:
            response = self.service.sites().list().execute()
            return [site["siteUrl"] for site in response.get("siteEntry", [])]
        except Exception as e:
            logging.error(f"Error fetching URL properties: {e}")
            return []

    def fetch_data(
        self,
        site_url: str,
        start_date: str,
        end_date: str,
        search_type: str,
        data_state: str = "final",
    ):
        all_rows = []
        start_row = 0
        if search_type == "Discover":
            dimensions = ["date", "page", "country"]
        else:
            dimensions = ["date", "page", "device", "country"]

        request = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": dimensions,
            "searchType": search_type,
            "rowLimit": 25000,
            "dataState": data_state,
        }

        while True:
            request["startRow"] = start_row

            try:
                response = (
                    self.service.searchanalytics()
                    .query(siteUrl=site_url, body=request)
                    .execute()
                )
                rows = response.get("rows", [])
                all_rows.extend(rows)
                start_row += 25000

                if len(rows) < 25000:
                    break

            except Exception as e:
                logging.error(f"Error fetching data: {e}")
                break

        return all_rows
