import os
import subprocess

from google.cloud import bigquery

bucket = os.getenv("GCS_BUCKET")
date = os.getenv("SOURCE_DATE")
name_filiale = os.getenv("NAME_FILIALE")
target = os.getenv("FILIALE_RCLONE")
bqProject = os.getenv("BQ_PROJECT")
bqDataset = os.getenv("BQ_DATASET")
bqRegion = os.getenv("BQ_REGION")

source = os.getenv("FILIALE_SOURCE")

list = subprocess.check_output(
    ["/usr/local/bin/rclone",
     "--config=/var/secrets/rclone/rclone.conf",
     "--verbose=4",
     "--ftp-concurrency=1",
     "lsl",
     "{}".format(source)]).decode('utf-8').splitlines()

list = [x.split() for x in list]
list = [[x[1] + x[2], x[3]] for x in list]
list = sorted(list, key=lambda x: x[0], reverse=True)
lastFile = list[0][1]

subprocess.check_call(["/usr/local/bin/rclone",
                       "--config=/var/secrets/rclone/rclone.conf",
                       "--verbose=4",
                       "--ftp-concurrency=1",
                       "copy",
                       "{}{}".format(source, lastFile), "/root/"])

subprocess.check_call(["/usr/local/bin/rclone",
                       "--config=/var/secrets/rclone/rclone.conf",
                       "--verbose=4",
                       "--ftp-concurrency=1",
                       "copy",
                       "/root/{}".format(lastFile), "gcs_dest_dcproc:{bucket}/subsidiaries_KRN/{filiale}/{date}".format(
        bucket=bucket,
        filiale=name_filiale,
        date=date
    )])

subprocess.check_call(["/usr/local/bin/rclone",
                       "--config=/var/secrets/rclone/rclone.conf",
                       "--verbose=4",
                       "--ftp-concurrency=1",
                       "--dry-run",
                       "copy",
                       "/root/{}".format(lastFile), "{}:".format(target)])
ct = "CREATE TABLE IF NOT EXISTS {}.PALP_EXPORT_SUBSIDIARIES_KRN (INSERT_DATE DATE NOT NULL,FILIALE STRING NOT NULL,LAST_FILE_KRN_SEND STRING)".format(
    bqDataset)

bq = bigquery.Client()
print(ct)
print(bq.query(ct, location=bqRegion, project=bqProject).result())

ins = "INSERT {}.PALP_EXPORT_SUBSIDIARIES_KRN (INSERT_DATE,FILIALE,LAST_FILE_KRN_SEND) VALUES ('{}','{}','{}')".format(
    bqDataset, date, name_filiale, lastFile)
print(ins)
print(bq.query(ins, location=bqRegion, project=bqProject).result())
print("Done")
