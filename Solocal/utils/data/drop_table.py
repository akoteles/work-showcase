import os

from google.cloud import bigquery


if __name__ == "__main__":
    table = os.getenv('TABLE')
    bq = bigquery.Client()
    bq.delete_table(table,not_found_ok=True)

