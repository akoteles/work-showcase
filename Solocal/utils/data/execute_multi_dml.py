import sys

from google.cloud import bigquery
import time

def try_query(client, sql, retries):
    retry_rate=12
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
        sqls = fd.read()
    bq = bigquery.Client()
    sqls = sqls.split('--q')
    for i, sql in enumerate(sqls):
        if not sql.strip() == "":
            print(f'Execute part :{i}')
            print(sql)
            try:
                res = try_query(bq, sql, 3)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                print(sql)
                raise
