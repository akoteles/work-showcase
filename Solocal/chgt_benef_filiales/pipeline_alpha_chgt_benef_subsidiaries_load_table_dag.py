from airflow.models import Variable, DAG
from datetime import datetime, timedelta
from airflow.operators.dummy_operator import DummyOperator
from commercial.utils import read_file, sourcing

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

INPUT_BUCKET = Variable.get('COMMERCIAL_INPUT_BUCKET')
PROJECT = Variable.get('COMMERCIAL_PROJECT')
PIPELINE_ALPHA_DATASET = Variable.get('COMMERCIAL_DATASET')

FILENAME = 'cb'
EXTENSION = 'csv'
INPUT_REPOSITORY = 'chgt_benef'
INPUT_BUCKET_FILE_PATH = f'{INPUT_REPOSITORY}/{FILENAME}.{EXTENSION}'

TABLE_NAME = 'TWH_STA_PALP_CHGMENT_BENEF_SUBSIDIARIES'
TABLE_SCHEMA_JSON = f'/commercial/pipeline_alpha_tables_schema/{TABLE_NAME}_schema.json'

schedule = None

dag = DAG('chgt_benef_subsidiaries_load_table', default_args=default_args, schedule_interval=schedule)

load_file_to_bq = sourcing.load_transform(
        name=f'load_{TABLE_NAME}_to_bq',
        urls=[f'gs://{INPUT_BUCKET}/{INPUT_BUCKET_FILE_PATH}'],
        bucket=INPUT_BUCKET,
        project=PROJECT,
        dataset=PIPELINE_ALPHA_DATASET,
        table=TABLE_NAME,
        schema=read_file(TABLE_SCHEMA_JSON),
        separator=';',
        format='CSV',
        has_header=True,
        overwrite=True,
        allow_jagged_rows=False,
        retries=1,
        dag=dag
    )

done = DummyOperator(task_id='done', dag=dag)

load_file_to_bq >> done
