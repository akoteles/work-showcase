#!/usr/bin/env python

from config import ANALYTICS_API_URL, ANALYTICS_GET_ROW_COUNT_URL, ANALYTICS_GET_DATA_URL
from helpers import create_url, post_request
import logging
import time


class AnalyticsPlatformAPI:

    def __init__(self, api_key, start_tmstp, end_tmstp):
        self.api_key = api_key
        self.start_tmstp = start_tmstp
        self.end_tmstp = end_tmstp

    def get_row_count(self, query):
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        url = create_url(ANALYTICS_API_URL, ANALYTICS_GET_ROW_COUNT_URL)
        response = post_request(url, headers, query)
        return self.extract_row_count(response.json())

    def get_data(self, query):
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        url = create_url(ANALYTICS_API_URL, ANALYTICS_GET_DATA_URL)
        logging.info("Sending request to Analytics Platform API")
        response = post_request(url, headers, query)
        try:
            response_data = response.json()
        except Exception as e:
            logging.error(f"Failed to parse JSON response: {e}")
            logging.info(f"Raw Response: {response.text}")
            raise

        return response.json()

    def pagination_get_data(
        self, query_template, max_retries=3, retry_delay=3, max_consecutive_errors=5
    ):
        page_number = 1
        data = []
        consecutive_errors = 0

        while page_number <= 20:
            time.sleep(1)
            logging.info(f"Fetching data - Page number: {page_number}")
            query_template["page-num"] = page_number

            retries = 0
            while retries < max_retries:
                try:
                    response = self.get_data(query_template)
                    extracted_data = self.extract_get_data(response)

                    if not extracted_data:
                        logging.info("No more data to fetch.")
                        return data

                    data.extend(extracted_data)
                    page_number += 1
                    consecutive_errors = 0
                    break

                except Exception as e:
                    retries += 1
                    logging.error(
                        f"Error fetching data on page {page_number} (attempt {retries}/{max_retries}): {e}"
                    )

                    if retries >= max_retries:
                        logging.error(
                            f"Max retries reached for page {page_number}. Skipping to the next page."
                        )
                        page_number += 1
                        consecutive_errors += 1
                        if consecutive_errors >= max_consecutive_errors:
                            logging.error(
                                "Consecutive errors limit reached. Returning data fetched so far."
                            )
                            return data
                    else:
                        logging.info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
        logging.info("Reached page limit of 20. Stopping pagination.")
        return data

    @staticmethod
    def extract_get_data(response):
        return response.get("DataFeed", {}).get("Rows", [])
