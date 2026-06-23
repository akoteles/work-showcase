from google.cloud import bigquery
from google.cloud.bigquery import WriteDisposition
import os

bucket = os.getenv("BUCKET")
path = os.getenv("PATH")
dataset = os.getenv("DATASET")
table = os.getenv("TABLE")
project = os.getenv("PROJECT")
truncate = os.getenv("TRUNCATE").upper() == "TRUE"
partition_by = os.getenv("PARTITION_BY")
partition_expiry = os.getenv("PARTITION_EXPIRY")
bq = bigquery.Client(project=project, location="EU")

job_config = bigquery.LoadJobConfig()
job_config.source_format = bigquery.SourceFormat.AVRO
if truncate:
    job_config.write_disposition = WriteDisposition.WRITE_TRUNCATE
else:
    job_config.write_disposition = WriteDisposition.WRITE_APPEND

if partition_by:
    if partition_expiry:
        if partition_by == "_PARTITIONTIME":
            job_config.time_partitioning = bigquery.table.TimePartitioning(expiration_ms=partition_expiry)
        else:
            job_config.time_partitioning = bigquery.table.TimePartitioning(field=partition_by,
                                                                           expiration_ms=partition_expiry)
    else:
        if partition_by == "_PARTITIONTIME":
            job_config.time_partitioning = bigquery.table.TimePartitioning()
        else:
            job_config.time_partitioning = bigquery.table.TimePartitioning(field=partition_by)

if path.endswith(".avro"):
    url = f'gs://{bucket}/{path}'
else:
    url = f'gs://{bucket}/{path}*.avro'

table_ref = f"{project}.{dataset}.{table}"
print(f"Loading data from {url} into {table_ref}")
job = bq.load_table_from_uri(url, table_ref,
                             job_config=job_config)

print(job.result())
