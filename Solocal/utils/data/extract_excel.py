import os

from google.cloud import bigquery
from google.cloud import storage
import xlsxwriter
import time

bucket = os.getenv("BUCKET")
path = os.getenv("PATH")

max_rows = 100000


def try_query(client, sql, retries):
    retry_rate = 12
    q = client.query(sql)
    try:
        q.result()
    except:
        if q.error_result is not None and "Exceeded rate limits" in str(q.error_result):
            print(f"Rate limited, retrying in {retry_rate}s")
            time.sleep(retry_rate)
            for retry in range(1, retries):
                try:
                    q = client.query(sql)
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
    with open("/app/query.sql", "r") as fd:
        sql = fd.read()
    bq = bigquery.Client()
    print("Querying")
    print(sql)
    res = try_query(bq, sql, 3).result()
    if res.total_rows > max_rows:
        raise Exception(f"Cowardly refusing to create a huge excel file, more than {max_rows} in resultset")
    columns = [x for x in res.schema]
    rows = [x.values() for x in res]
    print("Writing XLSX")
    workbook = xlsxwriter.Workbook('/tmp/temp.xlsx')
    ws = workbook.add_worksheet()
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd;@'})
    default_format = workbook.add_format({'num_format': 'yyyy-mm-dd;@'})
    headers=[]
    for i, c in enumerate(columns):
        if c.field_type == "DATE":
            ws.set_column(0, i, 10, date_format)
        else:
            ws.set_column(0, i, 30, date_format)
        headers.append({'header':c.name})
    for i, r in enumerate(rows):
        for j, c in enumerate(r):
            ws.write(i + 1, j, c)
    ws.add_table(0, 0, res.total_rows,len(columns)-1,{'columns': headers})
    workbook.close()
    gcs = storage.Client()
    print(f"Pushing to gs://{bucket}{path}")
    blob = gcs.bucket(bucket_name=bucket).blob(path)
    blob.upload_from_filename("/tmp/temp.xlsx")
