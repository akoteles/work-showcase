import os

from google.cloud import bigquery
from google.cloud import storage
import time
import csv

separator = os.getenv("SEPARATOR")
encoding = os.getenv("ENCODING")
bucket = os.getenv("BUCKET")
path = os.getenv("PATH")
header = os.getenv("HEADER")
quotes = os.getenv("QUOTES")


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


def rowsToCSV(rows, output):
    def quote_def(quotes=quotes):
        if not quotes or quotes == 'None':
            return csv.QUOTE_NONE
        elif quotes == 'NON_NUMERIC':
            return csv.QUOTE_NONNUMERIC
        elif quotes == 'ALL':
            return csv.QUOTE_ALL
        else:
            raise ValueError('Unknown quote definition for csv writer')

    columns = [x.name for x in rows.schema]
    file = open(output, 'w', newline='', encoding=encoding,errors="replace")
    print(file)
    writer = csv.DictWriter(file,
                            fieldnames=columns,
                            delimiter=separator,
                            skipinitialspace=True,
                            quoting=quote_def(),
                            escapechar='\\')
    if header and not str(header).upper() == 'FALSE':
        writer.writeheader()
    count = 0
    for row in rows:
        rowdict = {}
        for k in row.keys():
            rowdict[k] = row[k]
        writer.writerow(rowdict)
        count += 1
        if count % 10000 == 0:
            file.flush()
    file.close()
    print(f"{count} lines written to CSV")


if __name__ == "__main__":
    with open("/app/query.sql", "r") as fd:
        sql = fd.read()
    bq = bigquery.Client()
    print("Querying")
    print(sql)
    res = try_query(bq, sql, 3)
    print("Writing CSV")
    rowsToCSV(res.result(), "temp.csv")
    gcs = storage.Client()
    print(f"Pushing to gs://{bucket}/{path}")
    blob = gcs.bucket(bucket_name=bucket).blob(path)
    blob.upload_from_filename("temp.csv")
