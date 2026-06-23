import os

from google.cloud import bigquery
from google.cloud.bigquery.job import WriteDisposition
import time


def try_query(client, sql, destination, truncate, retries):
    retry_rate = 12
    job_config = bigquery.QueryJobConfig()
    job_config.destination = destination
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
    q = client.query(sql, job_config=job_config)
    try:
        q.result()
    except:
        if q.error_result is not None and "Exceeded rate limits" in str(q.error_result):
            print(f"Rate limited, retrying in {retry_rate}s")
            time.sleep(retry_rate)
            for retry in range(1, retries):
                try:
                    q = client.query(sql, job_config=job_config)
                    q.result()
                    return q
                except:
                    if q.error_result is not None and "Exceeded rate limits" in str(q.error_result):
                        print(f"Rate limited, retrying in {retry_rate}s")
                        time.sleep(retry_rate)
                    else:
                        q.result()
        else:
            q.result()
    return q


if __name__ == "__main__":
    destination = os.getenv('DESTINATION')
    truncate = os.getenv('TRUNCATE').upper() == "TRUE"
    partition_by = os.getenv("PARTITION_BY")
    partition_expiry = os.getenv("PARTITION_EXPIRY")
    with open("/app/query.sql", "r") as fd:
        sql = fd.read()
    print(sql)
    bq = bigquery.Client()
    try_query(bq, sql, destination, truncate, 3)
