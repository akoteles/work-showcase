import os
import re
import time

from google.cloud.bigquery import QueryJobConfig, WriteDisposition, CreateDisposition

date = os.getenv("SOURCE_DATE")
bqProject = os.getenv("BQ_PROJECT")
bqDataset = os.getenv("BQ_DATASET")
bqRegion = os.getenv("BQ_REGION")
target = "TWH_STA_PALP_SALES_TRANSACTIONS_SUBSIDIARIES"
log_table = "TWH_GES_PALP_SUBSIDIARIES_TRAITEMENT"


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

class FileDesc:
    def __init__(self, source, da_event, cd_filiale):
        self.source = source
        self.da_event = da_event
        self.cd_filiale = cd_filiale

    def __str__(self):
        return "{}({}:{})".format(self.source, self.cd_filiale, self.da_event)


def files_to_treat(bq, task_name):
    files_to_treat_query = """SELECT
            DISTINCT(SOURCE_FILE)
            ,DA_EVENT
            ,CD_FILIALE
        FROM `{project}.{dataset}.{table}`
        WHERE
        TASK_RUN='{date}'  AND
        SOURCE_FILE NOT IN (
            SELECT DISTINCT(SOURCE_FILE) FROM `{project}.{dataset}.{table}`
                WHERE TASK_RUN='{date}' AND TASK_NAME ="{task}" AND TASK_SUCCESS=TRUE
    )
""".format(
        project=bqProject,
        dataset=bqDataset,
        table=log_table,
        date=date,
        task=task_name
    )
    files = try_query(bq,files_to_treat_query,3).result()
    res = []
    for f in files:
        fd = FileDesc(f['SOURCE_FILE'], f['DA_EVENT'], f['CD_FILIALE'])
        res.append(fd)
    return res


def markTreated(bq, filedesc, task_name, date, success=True, comment=None):
    if comment is not None:
        sql = "INSERT INTO `{project}.{dataset}.{table}` (DA_EVENT,TASK_RUN,CD_FILIALE,SOURCE_FILE,TASK_NAME,TASK_SUCCESS,TASK_COMMENT) VALUES('{da_event}','{date}','{cd_filiale}','{source_file}','{task_name}',{task_succes},'{comment}')".format(
            project=bqProject,
            dataset=bqDataset,
            table=log_table,
            da_event=filedesc.da_event,
            date=str(date),
            cd_filiale=filedesc.cd_filiale,
            source_file=filedesc.source,
            task_name=task_name,
            task_succes="TRUE" if success else "FALSE",
            comment=comment
        )
    else:
        sql = "INSERT INTO `{project}.{dataset}.{table}` (DA_EVENT,TASK_RUN,CD_FILIALE,SOURCE_FILE,TASK_NAME,TASK_SUCCESS) VALUES('{da_event}','{date}','{cd_filiale}','{source_file}','{task_name}',{task_succes})".format(
            project=bqProject,
            dataset=bqDataset,
            table=log_table,
            da_event=filedesc.da_event,
            date=str(date),
            cd_filiale=filedesc.cd_filiale,
            source_file=filedesc.source,
            task_name=task_name,
            task_succes="TRUE" if success else "FALSE",
        )
    q = try_query(bq,sql,3)
    q.result()
    if q.error_result:
        raise Exception(str(q.error_result))
    return q


def extract_sql_list(file_name, sql_delimiter='--query'):
    with open(file_name, 'r', encoding='utf-8') as fp:
        content = fp.read()
    return content.split(sql_delimiter) if content else None

def execute_bq_dml(bq, sql):
    return try_query(bq,sql,3)
