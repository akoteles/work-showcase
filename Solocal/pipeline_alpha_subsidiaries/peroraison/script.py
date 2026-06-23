import os
import sys
import time
import traceback

from string import Template

import yaml
import time
from google.cloud import bigquery

from utils import files_to_treat, execute_bq_dml, extract_sql_list, markTreated

date = os.getenv("SOURCE_DATE")
bqProject = os.getenv("BQ_PROJECT")
bqDataset = os.getenv("BQ_DATASET")
bqRegion = os.getenv("BQ_REGION")

TASK_NAME = "PERORAISON"
bq = bigquery.Client()
files = files_to_treat(bq, TASK_NAME)

with open("/app/subsidiaries.yaml") as fd:
    filiales = yaml.load(fd, Loader=yaml.FullLoader)


isError = False
print("Files to treat:" + str(files))
for f in files:
    print("Executing peroraison for: " + f.source)
    print("Nothing to do, but we still mark the table, for reporting reasons")
    markTreated(bq, f, TASK_NAME, date)
if isError:
    raise Exception("Error in at least one transform job")
