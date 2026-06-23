import os
from google.cloud import bigquery
from google.cloud.bigquery.job import WriteDisposition, CreateDisposition
import secrets

bucket = os.getenv("BUCKET")
path = os.getenv("PATH")
table = os.getenv("TABLE")

if __name__ == "__main__":
    bq = bigquery.Client()
    j = bq.extract_table(table, f"gs://{bucket}/{path}")
    j.result()
