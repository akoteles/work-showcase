#!/usr/bin/env python

from google.cloud import bigquery
from google.oauth2 import service_account
import logging
from typing import Dict


class BigQuery:
    """Class to handle interactions with BigQuery.

    This class provides methods to interact with Google BigQuery, including retrieving the most
    current date from a table and loading data from a Pandas DataFrame into a BigQuery table.
    """

    def __init__(self, service_account_info: Dict, project_id: str):
        """
        Initializes the BigQuery client with the provided service account credentials and project ID.

        Args:
            service_account_info (Dict): A dictionary containing the service account information for authentication.
            project_id (str): The Google Cloud project ID to interact with BigQuery.
        """
        self.gcp_credentials = service_account.Credentials.from_service_account_info(
            service_account_info
        )
        self.client = bigquery.Client(
            project=project_id, credentials=self.gcp_credentials
        )
        self.project_id = project_id
        logging.info("Big Query client initialized")

    def load_data(self, dataset_name: str, table_name: str, dataframe):
        """
        Uploads a Pandas DataFrame to a BigQuery table.

        Args:
            dataset_name (str): The name of the dataset where the table is located.
            table_name (str): The name of the table to load data into.
            dataframe (pandas.DataFrame): The Pandas DataFrame to be uploaded to the BigQuery table.

        Returns:
            None
        """
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
