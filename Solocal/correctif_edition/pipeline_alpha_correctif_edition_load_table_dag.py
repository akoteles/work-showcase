import os
import io
import json
from airflow.models import Variable, DAG
from datetime import datetime, timedelta

from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator

try:
  from airflow.operators import K8SJobOperator
except ImportError:
  from plugins.sudata import K8SJobOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2019, 1, 1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'catchup': False,
    'retry_delay': timedelta(minutes=5),
}

schedule = None

DAG_FOLDER = os.environ.get('DAGS_FOLDER')
INPUT_BUCKET = Variable.get('COMMERCIAL_INPUT_BUCKET')
PROJECT = Variable.get('COMMERCIAL_PROJECT')
PIPELINE_ALPHA_DATASET = Variable.get('COMMERCIAL_DATASET')
BIGQUERY_CONN = 'bigquery_dcproc'

FILENAME = 'correctif_edition'
EXTENSION = 'csv'
INPUT_REPOSITORY = 'correctif_edition'
INPUT_BUCKET_FILE_PATH = f'{INPUT_REPOSITORY}/{FILENAME}.{EXTENSION}'

TABLE_NAME = 'TMP_CORRECTIF_EDITION'
TABLE_SCHEMA_JSON = f'{DAG_FOLDER}/commercial/pipeline_alpha_tables_schema/{TABLE_NAME}_schema.json'
with io.open(TABLE_SCHEMA_JSON,'r') as fd:
    schema = json.load(fd)
fd.close()

dag = DAG('pipeline_alpha_correctif_edition_load_table', default_args=default_args, schedule_interval=schedule)

load_file_to_bq = GoogleCloudStorageToBigQueryOperator(
        task_id=f'load_{TABLE_NAME}_to_bq',
        bucket=INPUT_BUCKET,
        source_objects=[INPUT_BUCKET_FILE_PATH],
        destination_project_dataset_table=f'{PROJECT}.{PIPELINE_ALPHA_DATASET}.{TABLE_NAME}',
        source_format='CSV',
        allow_jagged_rows=False,
        skip_leading_rows=1,
        create_disposition='CREATE_IF_NEEDED',
        write_disposition='WRITE_TRUNCATE',
        autodetect=False,
        schema_fields=schema,
        field_delimiter='|',
        bigquery_conn_id=BIGQUERY_CONN,
        dag=dag
    )

done = DummyOperator(task_id='done', dag=dag)

load_file_to_bq >> done
