import os
import sys
import traceback

from google.cloud import bigquery
from utils import files_to_treat, execute_bq_dml, extract_sql_list, markTreated

date = os.getenv("SOURCE_DATE")
bqProject = os.getenv("BQ_PROJECT")
bqDataset = os.getenv("BQ_DATASET")

TASK_NAME = "CONTROLES_RG"
bq = bigquery.Client()
files = files_to_treat(bq, TASK_NAME)

queries = extract_sql_list("/app/1_SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_MARQUAGE_REJETS.sql", sql_delimiter="--q")
isError = False
for f in files:
    print("Transforming: " + f.source)
    try:
        for i, q in enumerate(queries):
            print("Executing query {} for {}: {}...".format(i, f, q[:20]))
            da_event_str = f.da_event.strftime('%Y-%m-%d')
            q = q.replace("$CO_FILIALE", f.cd_filiale)
            q = q.replace("$DA_EVENT", da_event_str)
            res = execute_bq_dml(bq, q)
            if res.error_result is not None:
                print("Error transforming for :" + f + " : " + str(res.error_result))
                markTreated(bq, f, TASK_NAME, date, False, str(res.error_result))
                raise Exception(str(res.error_result))
        markTreated(bq, f, TASK_NAME, date)
    except:
        print("Exception in transforms for " + str(f))
        traceback.print_exc(file=sys.stdout)
        isError = True
if isError:
    raise Exception("Error in at least one transform job")
