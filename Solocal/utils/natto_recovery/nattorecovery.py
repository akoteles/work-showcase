from datetime import datetime, timedelta
from datetime import date, timedelta

import os
import io

from google.cloud import bigquery
from google.cloud.bigquery import WriteDisposition


PROJECT_NAME = 'dataproc_project'
DATASET_NVLLE_GAMME= 'recovery_dataset'
PIPELINE_BETA_BUCKET_NAME = 'pipeline_beta_storage_path'

start_date = date(2020, 2, 3)
end_date = date(2020, 2, 24)
recovery_dates = [date(2020, 2, 3)]


PRODUCT_API_REPO_FULL = 'PRODUCT_API_REPO_FULL'
bq = bigquery.Client(project=PROJECT_NAME, location="EU")

def getTableFullname(table):
    return "{}.{}.{}".format(PROJECT_NAME,DATASET_NVLLE_GAMME,table)

def load_avro(table, path, write_disposition):
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.AVRO
    job_config.write_disposition = write_disposition
    job_config.time_partitioning = job_config.time_partitioning = bigquery.table.TimePartitioning()
    url = 'gs://{}/{}*.avro'.format(PIPELINE_BETA_BUCKET_NAME,path)
    table_ref = getTableFullname(table)
    print("Loading data from {} into {}".format(url,table_ref))
    job = bq.load_table_from_uri(url, table_ref, job_config=job_config)
    print(job.result())

def getDailyAvroPath(date):
    return 'ten_zoom/db/dwh_ten_zoom/productApiRepoDelta/{}/'.format(date)

def load_daily_to_bq(date) :
    date_nodash = date.strftime("%Y%m%d")
    daily_bq_table = 'PRODUCT_API_DAILY${}'.format(date_nodash)
    path= getDailyAvroPath(date)
    load_avro(daily_bq_table, path, WriteDisposition.WRITE_TRUNCATE)

def runquery(query, dest_table):
    job_config = bigquery.QueryJobConfig()
    job_config.destination = dest_table
    job_config.write_disposition = WriteDisposition.WRITE_TRUNCATE
    job_config.time_partitioning = bigquery.table.TimePartitioning()
    q = bq.query(query, job_config=job_config)
    q.result()

def init_new_full_partition(date_nodash, date, daybefore) :
    with io.open('init_daily_full_partition.sql','r', encoding='utf-8') as fp:
        sql = fp.read()
        fp.close()
    sql = sql.format(project_id=PROJECT_NAME, dataset_id=DATASET_NVLLE_GAMME,today= date, yesterday=daybefore)
    dest_table = "{}.{}.{}${}".format(PROJECT_NAME, DATASET_NVLLE_GAMME, PRODUCT_API_REPO_FULL, date_nodash)
    runquery(sql, dest_table)

def update_full_partition(date, date_nodash):
    daily_bq_table = '{}${}'.format(PRODUCT_API_REPO_FULL,date_nodash)
    path= getDailyAvroPath(date)
    load_avro(daily_bq_table, path, WriteDisposition.WRITE_APPEND)

def export_full_to_gcs():
    path = "gs://{}/exportFull/recovery/full-*.avro".format(PIPELINE_BETA_BUCKET_NAME)
    table = getTableFullname(PRODUCT_API_REPO_FULL)
    print("exporting the {} table to {}".format(table,path))
    j = bq.extract_table(table, path)
    j.result()

def run_recovery():
    delta = timedelta(days=1)
    while start_date <= end_date:
        print (start_date.strftime("%Y-%m-%d"))
        start_date_nodash = start_date.strftime("%Y%m%d")
        if start_date in recovery_dates:
            print("loading the avro of {} to the PRODUCT_API_DAILY table".format(start_date))
            load_daily_to_bq(start_date)
        print("init new full partition for :{}".format(start_date))
        init_new_full_partition(start_date_nodash, start_date, start_date-delta)
        print("update full partition for :{}".format(start_date))
        update_full_partition(start_date, start_date_nodash)
        start_date += delta
