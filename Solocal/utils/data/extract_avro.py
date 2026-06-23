import os
from google.cloud import bigquery
from google.cloud.bigquery.job import WriteDisposition, CreateDisposition
import secrets

bucket = os.getenv("BUCKET")
path = os.getenv("PATH")
project = os.getenv("PROJECT")
tmp_dataset = os.getenv("TMP_DATASET")

if __name__ == "__main__":
    with open("/app/query.sql", "r") as fd:
        sql = fd.read()
    tmp_table = f"{project}.{tmp_dataset}.TMP_QUERY_{secrets.token_hex(16)}"
    bq = bigquery.Client()
    job_config = bigquery.QueryJobConfig()
    job_config.write_disposition = WriteDisposition.WRITE_TRUNCATE
    job_config.create_disposition = CreateDisposition.CREATE_IF_NEEDED
    job_config.destination = tmp_table
    q = bq.query(sql, job_config=job_config)
    q.result()
    j = bq.extract_table(tmp_table, f"gs://{bucket}/{path}")
    try:
        j.result()
    finally:
        bq.delete_table(tmp_table)
