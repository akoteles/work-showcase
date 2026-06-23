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
        sql = fd.read()
    bq = bigquery.Client()
    print(sql)
    try_query(bq, sql, 3)
