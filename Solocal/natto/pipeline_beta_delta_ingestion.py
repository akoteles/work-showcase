from airflow.models import Variable, DAG

from datetime import datetime, timedelta

import os
import io

from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
from airflow.contrib.operators.bigquery_operator import BigQueryOperator
from airflow.contrib.operators.bigquery_to_gcs import BigQueryToCloudStorageOperator
from airflow.operators.dummy_operator import DummyOperator
try:
    from airflow.operators import K8SJobOperator
except ImportError:
    from plugins.sudata import K8SJobOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2019, 7, 22),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'catchup': False,
    'retry_delay': timedelta(minutes=5),
}

ENV = Variable.get('ENV')
PROJECT = Variable.get('COMMERCIAL_PROJECT')
DAG_FOLDER = os.environ.get('DAGS_FOLDER')
COMMERCIAL_INPUT_BUCKET = Variable.get('COMMERCIAL_INPUT_BUCKET')
COMMERCIAL_OUTPUT_BUCKET = Variable.get('COMMERCIAL_OUTPUT_BUCKET')
BQ_CONN_ID = 'bigquery_dcproc'
DATASET_NVLLE_GAMME= Variable.get('NOUVELLE_GAMME_DATASET')
host_project = Variable.get('HOST_PROJECT')
host_cluster = Variable.get('HOST_CLUSTER')
location = Variable.get('LOCATION')
SOURCING_TIMEOUT = 60 * 240
GKE_JOB_RETRIES = 3

PIPELINE_BETA_IMAGE_VERSION = Variable.get('PIPELINE_BETA_IMAGE_VERSION')
PIPELINE_BETA_BUCKET_NAME = "{bucket}/pipeline_beta".format(bucket=Variable.get('COMMERCIAL_INPUT_BUCKET'))

exec_date_no_dash = "{{ ds_nodash }}"
exec_date = "{{ ds }}"

dag = DAG('pipeline_betaDeltaIngestion', default_args=default_args, schedule_interval=None)
dag.doc_md = """\
# PIPELINE_BETA DAILY INGESTION , scheduled once a day
The time-partitioned table PRODUCT_API_REPO_FULL keeps a full up to date record of the "Nouvelle Gamme" products. The PIPELINE_BETA DAILY INGESTION pipeline allow to
integrate daily the new modifications into this table.
The steps to update the table in the daily execution are detailed below
- Runs an extraction of the past modifications from the different APIs (GPP, LAKESIS, etc) and saves the result as an avro file on : {INPUT_BUCKET}/{date}
- Loads the Avro from INPUT_BUCKET to partition in the time-partitioned table PRODUCT_API_DAILY
- Creates a new partition in PRODUCT_API_REPO_FULL with all the content of the partition of the day before except the products appearing in the newly created
partition in PRODUCT_API_DAILY
- Loads the parquet to the newly created partition in PRODUCT_API_REPO_FULL
""".format(INPUT_BUCKET=PIPELINE_BETA_BUCKET_NAME, date= exec_date)


start = DummyOperator(task_id='start_pipeline_betaDelta',dag = dag)

with io.open('{}/commercial/pipeline_beta/yaml/pipeline_beta_delta_sourcing_descriptor.yaml'.format(DAG_FOLDER), 'r', encoding='utf-8') as fp:
    sourcing_descriptor = fp.read()
    fp.close()

create_daily_on_gcs = K8SJobOperator(task_id='pipeline_betaDelta_extract_DAILY_to_gcs',
                                     location=location,
                                     project_id=host_project,
                                     cluster_name=host_cluster,
                                     name='pipeline_beta-deta-api-sourcing',
                                     gcp_conn_id='gcp_kub_runner',
                                     params={"pipeline_beta_version" : PIPELINE_BETA_IMAGE_VERSION,
                                             "pipeline_beta_conn_id": 'bigquery-key',
                                             "pipeline_beta_write_path": COMMERCIAL_INPUT_BUCKET,
                                             "pipeline_beta_output_path": COMMERCIAL_OUTPUT_BUCKET,
                                             "mainclass": 'ten.gpp.App',
                                             "environment": ENV},
                                     namespace='composer',
                                     descriptor=sourcing_descriptor,
                                     timeout_s=SOURCING_TIMEOUT,
                                     retries=GKE_JOB_RETRIES,
                                     dag=dag)
path_daily_avro = 'ten_zoom/db/dwh_ten_zoom/productApiRepoDelta'
daily_bq_table = 'PRODUCT_API_DAILY'

load_daily_to_bq = GoogleCloudStorageToBigQueryOperator(
    task_id='pipeline_betaDelta_load_DAILY_to_bq',
    bucket=PIPELINE_BETA_BUCKET_NAME,
    source_objects=['{path}/{date}/*.avro'.format(path=path_daily_avro, date=exec_date)],
    destination_project_dataset_table='{project_id}.{dataset}.{table_id}${partition}'.format(project_id=PROJECT, table_id=daily_bq_table
                                                                                             , partition=exec_date_no_dash
                                                                                             , dataset=DATASET_NVLLE_GAMME),
    source_format='AVRO',
    create_disposition='CREATE_IF_NEEDED',
    write_disposition='WRITE_TRUNCATE',
    bigquery_conn_id=BQ_CONN_ID,
    autodetect=True,
    time_partitioning = {"expiration_ms":2592000000},
    dag=dag)

with io.open('{folder}/commercial/pipeline_beta/sql/pipeline_beta_init_daily_full_partition.sql'.format(folder=DAG_FOLDER),'r'
        , encoding='utf-8') as fp:
    sql = fp.read()
    fp.close()

full_bq_table = 'PRODUCT_API_REPO_FULL'

init_new_full_partition =  BigQueryOperator(
    task_id='pipeline_betaDelta_initiate_FULL_partition',
    sql=sql,
    write_disposition='WRITE_TRUNCATE',
    use_legacy_sql=False,
    bigquery_conn_id= BQ_CONN_ID,
    params={"project_id": PROJECT, "dataset_id": DATASET_NVLLE_GAMME},
    destination_dataset_table='{project_id}.{dataset}.{table_id}${partition}'.format(project_id=PROJECT, table_id=full_bq_table, partition=exec_date_no_dash
                                                                                     , dataset=DATASET_NVLLE_GAMME),
    dag=dag)

update_full_partition=GoogleCloudStorageToBigQueryOperator(
    task_id='pipeline_betaDelta_update_FULL_partition',
    bucket=PIPELINE_BETA_BUCKET_NAME,
    source_objects=['{path}/{date}/*.avro'.format(path=path_daily_avro, date=exec_date)],
    destination_project_dataset_table='{project_id}.{dataset}.{table_id}${partition}'.format(project_id=PROJECT, table_id=full_bq_table, partition=exec_date_no_dash
                                                                                             , dataset=DATASET_NVLLE_GAMME),
    source_format='AVRO',
    create_disposition='CREATE_IF_NEEDED',
    write_disposition='WRITE_APPEND',
    bigquery_conn_id=BQ_CONN_ID,
    autodetect=True,
    dag=dag)

export_full_to_gcs = BigQueryToCloudStorageOperator(
    task_id='pipeline_betaDelta_export_FULL_to_gcs',
    source_project_dataset_table='{project_id}.{dataset}.{table_id}${partition}'.format(project_id=PROJECT, table_id=full_bq_table, partition=exec_date_no_dash
                                                                                        , dataset=DATASET_NVLLE_GAMME),
    destination_cloud_storage_uris=['gs://{bucket}/exportFull/{date}/full-*.avro'.format(bucket=PIPELINE_BETA_BUCKET_NAME,date=exec_date)],
    export_format='Avro',
    compression='SNAPPY',
    bigquery_conn_id=BQ_CONN_ID,
    dag=dag)

done = DummyOperator(task_id='end_pipeline_betaDelta',dag = dag)

start >> create_daily_on_gcs >> load_daily_to_bq >> init_new_full_partition >> update_full_partition >> export_full_to_gcs >> done
