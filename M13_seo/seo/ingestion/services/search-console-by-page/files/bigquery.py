#!/usr/bin/env python

from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime, timedelta
import logging
from typing import Dict


class BigQuery:

    def __init__(self, service_account_info: Dict, project_id: str):
        self.gcp_credentials = service_account.Credentials.from_service_account_info(
            service_account_info
        )
        self.client = bigquery.Client(
            project=project_id, credentials=self.gcp_credentials
        )
        self.project_id = project_id
        logging.info("Big Query client initialized")

    def get_most_current_date(self, dataset_name: str, table_name: str):
        query = f"""
            SELECT
            MAX(Date) AS max_date,
            FROM
            `{self.project_id}.{dataset_name}.{table_name}`
        """
        query_job = self.client.query(query)
        results = query_job.result()

        max_date = None
        for row in results:
            if row.max_date:
                max_date = datetime.strptime(str(row.max_date), "%Y-%m-%d").date()
        return max_date

    def load_data(self, dataset_name: str, table_name: str, dataframe):
        table_id = f"{self.project_id}.{dataset_name}.{table_name}"

        try:
            logging.info(
                f"Inserting {len(dataframe)} rows into BigQuery table {table_id}"
            )
            job = self.client.load_table_from_dataframe(dataframe, table_id)
            result = job.result()
            logging.info(f"Number of rows inserted: {result.output_rows}")
        except Exception as e:
            logging.error(f"Error uploading data to BigQuery: {e}")

    def get_unfinalized_dates(self, dataset_name: str, table_name: str):
        query = f"""
            SELECT DISTINCT Date
            FROM `{self.project_id}.{dataset_name}.{table_name}`
            WHERE is_final IS NOT TRUE"""
        return [row.Date for row in self.client.query(query).result()]

    def get_last_finalized_date(self, dataset_name: str, table_name: str):
        query = f"""
            SELECT MAX(Date) as last_date
            FROM `{self.project_id}.{dataset_name}.{table_name}`
            WHERE is_final IS TRUE
        """
        result = list(self.client.query(query).result())
        return result[0].last_date if result and result[0].last_date else None

    def delete_rows_by_dates(
        self, dataset_name: str, table_name: str, dates, search_type=None
    ):
        table_id = f"{self.project_id}.{dataset_name}.{table_name}"
        if not dates:
            return
        formatted_dates = ",".join(f"DATE '{date}'" for date in dates)
        if search_type:
            delete_query = f"""
                DELETE FROM `{table_id}`
                WHERE Date IN ({formatted_dates}) and SearchType = '{search_type}'
            """
        else:
            delete_query = f"""
                DELETE FROM `{table_id}`
                WHERE Date IN ({formatted_dates})
            """
        self.client.query(delete_query).result()
        logging.info(f"Deleted old rows for dates: {formatted_dates}")
