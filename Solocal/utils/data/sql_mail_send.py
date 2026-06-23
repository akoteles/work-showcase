import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from google.cloud import bigquery
import time
import string
import markdown

to = os.getenv("TO").split(',')
subject = os.getenv("SUBJECT")


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
    with open('/var/secrets/sendgrid/sendgrid-api.txt') as fd:
        api_key = fd.read().strip()
    with open('/app/mail.md') as fd:
        tmpl = fd.read()

    bq = bigquery.Client()
    print("Querying")
    print(sql)
    res = try_query(bq, sql, 3).result()
    tablelines = [
        '|' + '|'.join([field.name for field in res.schema]) + '|',
        '|' + '|'.join(['---' for field in res.schema]) + '|'
    ]
    for row in res:
        cols = []
        for col in row:
            cols.append(str(col))
        tablelines.append('|' + '|'.join(cols) + '|')
    table = '\n'.join(tablelines)
    text = string.Template(tmpl).substitute({'table': table})
    prefix="""
<html>
  <head>
    <style>
        table {
            border-collapse: collapse;
        }
        table, th, td {
            border: 1px solid black;
        }
        th {
            font-weight: bold;
        }
    </style>
  </head>
  <body>
    """
    html = prefix+markdown.markdown(text, extensions=['tables'])+"</body>"
    print("Sending message:")
    print(text)
    message = Mail(
        from_email=('noreply@example.com', 'SUDATA'),
        to_emails=to,
        subject=subject,
        plain_text_content=text,
        html_content=html)
    sendgrid_client = SendGridAPIClient(api_key)
    response = sendgrid_client.send(message)
    if response.status_code != 202:
        print(f"Error {response.status}")
        print(response.body)
        sys.exit(-1)
    else:
        print("Mail sent")
        sys.exit(0)
