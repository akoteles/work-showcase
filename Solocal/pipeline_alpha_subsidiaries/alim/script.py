import datetime
import io
import json
import os
import sys
import time
import traceback

import google.cloud.storage.client as storage
from google.cloud.storage import Blob
from google.cloud import bigquery
from google.cloud.bigquery import WriteDisposition
import csv

from utils import files_to_treat, execute_bq_dml, extract_sql_list, markTreated, FileDesc

bucket = os.getenv("GCS_BUCKET")
date = os.getenv("SOURCE_DATE")
project = os.getenv("GCS_PROJECT")
bqProject = os.getenv("BQ_PROJECT")
bqDataset = os.getenv("BQ_DATASET")

name_filiale = os.getenv("NAME_FILIALE", "")
code_filiale = os.getenv("CODE_FILIALE", "")
enc = os.getenv("SOURCE_ENCODING", "ISO-8859-1")

target = os.getenv("BQ_TABLE")
log_table = "TWH_GES_PALP_SUBSIDIARIES_TRAITEMENT"

path = "subsidiaries/{0}/{1}/".format(name_filiale, date)

top_prefix = "PALP_TOP_SALES_TRANSACTIONS_{0}".format(code_filiale)
files_prefix = "PALP_TXT_SALES_TRANSACTIONS_{0}".format(code_filiale)
TASK_NAME = "SOURCE_TO_GCS"

fileQuery = """SELECT SOURCE_FILE FROM `{bqProject}.{bqDataset}.{log_table}` WHERE SOURCE_FILE='{filename}' AND TASK_SUCCESS=TRUE AND TASK_NAME='{taskname}'"""

MAX_BAD_RECORDS = 100

b = storage.Client().bucket(bucket)
bq = bigquery.Client()
table = bq.get_table(bq.dataset(dataset_id=bqDataset, project=bqProject).table(log_table))
topPath = path + top_prefix + ".csv"
print("TopPath: " + topPath)
top = b.get_blob(topPath)

print("Top: " + str(top))
if top is not None:
    files = [x for x in b.list_blobs(prefix=path + files_prefix)]
    for f in files:
        f2 = str(f.name).upper()
        print(f2)
        if f2.endswith(".CSV"):
            print("Found file:" + f2)
            fileName = f2.split('.')[-2].split('/')[-1]
            fileDate = fileName.split("_")[-1]
            q = fileQuery.format(
                bqProject=bqProject,
                bqDataset=bqDataset,
                log_table=log_table,
                filename=fileName,
                taskname=TASK_NAME
            )
            print(q)
            log_entries = bq.query(q).result()
            print([x for x in log_entries])
            if log_entries.total_rows == 0:
                print("Must be loaded: " + fileName)
                try:
                    fileDate = datetime.datetime.strptime(fileDate, '%Y%m%d')
                except:
                    print("Error parsing DA_EVENT: " + fileName)
                    break
                fileDate = fileDate.strftime('%Y-%m-%d')
                f.download_to_filename("temp.csv")
                with open("temp.csv", encoding=enc) as source:
                    with open("temp2.csv", "w", encoding="utf-8") as dest:
                        c = csv.DictReader(source, delimiter=";")
                        fields = c.fieldnames
                        fields.append('DaEvent')
                        fields.append('Code Filiale')
                        fields.append('NoFlagDeleted')
                        fields.append('LiFlagDeleted')
                        fields.append('NoRowNum')
                        c2 = csv.DictWriter(dest, fields, delimiter=";")
                        c2.writeheader()
                        for row in c:
                            row['DaEvent'] = fileDate
                            row['Code Filiale'] = code_filiale
                            row['NoFlagDeleted'] = 0
                            row['LiFlagDeleted'] = "Non"
                            row['NoRowNum'] = 0
                            c2.writerow(row)
                newBlob = Blob(f.name + ".enriched", bucket=b)
                newBlob.upload_from_filename("temp2.csv")
                u = "gs://{0}/{1}".format(bucket, newBlob.name)
                job_config = bigquery.LoadJobConfig()
                job_config.source_format = bigquery.SourceFormat.CSV
                job_config.field_delimiter = ';'
                job_config.skip_leading_rows = 1
                job_config.encoding = "UTF-8"
                job_config.write_disposition = WriteDisposition.WRITE_APPEND
                job_config.max_bad_records = MAX_BAD_RECORDS
                print("Loading: " + fileName)
                job = bq.load_table_from_uri(u, bq.dataset(dataset_id=bqDataset, project=bqProject).table(target),
                                             job_config=job_config)
                time.sleep(3)
                fd = FileDesc(source=fileName, da_event=fileDate, cd_filiale=code_filiale)
                try:
                    res = job.result()
                    if res.error_result is None:
                        print("Loaded: " + fileName)
                        markTreated(bq, fd, TASK_NAME, date=date)
                    else:
                        print("Error loading: " + fileName + " " + str(res.errors))
                        markTreated(bq, fd, TASK_NAME, date=date, success=False,
                                    comment=json.dumps(res.errors))
                except Exception as err:
                    out = io.StringIO()
                    traceback.print_tb(err.__traceback__, file=out)
                    err = out.getvalue()
                    print(sys.exc_info()[0])
                    print(err)
                    markTreated(bq, fd, TASK_NAME, date=date, success=False,
                                comment=json.dumps(str(sys.exc_info()[0])))
            else:
                print("Already loaded: " + fileName)
else:
    print("No file to load")
