import aiohttp
import simplejson as json
import asyncio
import os
from google.cloud import bigquery
from google.cloud import storage

bq = bigquery.Client()

flashUrl = os.getenv("FLASH_URL")
producer_id = os.getenv("PRODUCER_ID")
security_token = os.getenv("SECURITY_TOKEN")
routing_key = os.getenv("ROUTING_KEY")
batch_len = int(os.getenv("BATCH_SIZE", "20"))
bucket = os.getenv("BUCKET")
path = os.getenv("PATH")

sent = open("sent.jsonl", "w")
with open('/app/query.sql') as fd:
    sql = fd.read()

print(f"""
Running Flash export with
flashUrl:{flashUrl}
producerId:{producer_id}
securityToken:{security_token}
routingKey:{routing_key}
logs:gs://{bucket}/{path}
batchSize:{batch_len}
query:{sql}
""")


async def main():
    async with aiohttp.ClientSession() as session:
        async def sendMessage(message):
            headers = {
                'producerid': producer_id,
                'securitytoken': security_token,
                'content-type': 'application/json'
            }
            body = {
                'routingkey': routing_key,
                'eventmessage': json.dumps(message)
            }
            async with session.post(
                    flashUrl,
                    json=body,
                    headers=headers,
                    ssl=False
            ) as resp:
                return await resp.json()
        batch = []
        to_send = bq.query(sql).result()
        for row in to_send:
            row_dao = {}
            for column in row.keys():
                val = row[column]
                row_dao[column] = val
            if len(batch) < batch_len:
                batch.append((row_dao, sendMessage(row_dao)))
            else:
                print("Waiting for batch")
                for e in batch:
                    resp = await e[1]
                    log = {'message': e[0], 'flash_response': resp}
                    sent.write(json.dumps(log) + "\n")
                batch = [(row_dao, sendMessage(row_dao))]
        print("Waiting for last batch")
        for e in batch:
            resp = await e[1]
            log = {'message': e[0], 'flash_response': resp}
            sent.write(json.dumps(log) + "\n")


asyncio.run(main())
sent.close()

gcs = storage.Client()
blob = gcs.bucket(bucket).blob(path)
blob.upload_from_filename("sent.jsonl")
