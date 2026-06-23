from datetime import datetime, timedelta
from airflow.models import Variable, DAG
from airflow.operators.dummy_operator import DummyOperator

from commercial.utils.bigquery import extract_CSV
from commercial.utils import read_file
from commercial.utils.io import export_from_gcs
from commercial.utils.bigquery import execute_multi_DML

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

PIPELINE_ALPHA_DATASET = Variable.get('COMMERCIAL_DATASET')
PROJECT = Variable.get('COMMERCIAL_PROJECT')
GS_OUT_BUCKET_NAME = Variable.get('COMMERCIAL_OUTPUT_BUCKET')
ENV = Variable.get('ENV')

PARTNER = 'CRM'
CIAL_COMPONENT = 'regional_edition'

FILENAME = 'BI_REGIONAL_EDITION'
EXTENSION = 'csv'

bucket_file_path = f'{PARTNER}/{CIAL_COMPONENT}/{FILENAME}_{{{{ yesterday_ds_nodash }}}}.{EXTENSION}'

TABLE = 'TWH_STA_PALP_REGIONAL_EDITION_REPRISE'
QUERY_delete = read_file(f'/commercial/{CIAL_COMPONENT}/sql/delete_{TABLE}.sql')

QUERY = read_file(f'/commercial/{CIAL_COMPONENT}/sql/bi_{CIAL_COMPONENT}.sql')

FTP_ACK_FILENAME = 'CRM_CA.acq'

if ENV.upper() == 'PRD':
    FTP_SERVER = 'usr_cs_depot'
    FTP_FILE_PATH = f'/crm/retrait/{CIAL_COMPONENT}/'
else:
    FTP_SERVER = 'mftp01_palp'
    FTP_FILE_PATH = f'/depot/{PARTNER}/{CIAL_COMPONENT}/'

schedule = None

dag = DAG(f'pipeline_alpha_{CIAL_COMPONENT}', default_args=default_args, schedule_interval=schedule)

push_to_gcs = extract_CSV(
    name='extract_csv',
    sql=QUERY,
    bucket=GS_OUT_BUCKET_NAME,
    path=bucket_file_path,
    separator=',',
    encoding='UTF_8_SIG',
    header=False,
    quotes='ALL',
    params={
        'project_id': PROJECT,
        'dataset_id': PIPELINE_ALPHA_DATASET,
        'exec_year': '{{ execution_date.strftime("%Y") }}'
    },
    dag=dag
)

delete_table = execute_multi_DML(
    name=f'delete_{TABLE}',
    sql=QUERY_delete,
    params={
        'project_id': PROJECT,
        'dataset_id': PIPELINE_ALPHA_DATASET
    },
    dag=dag
)

export_to_ftp = export_from_gcs(
    name='export_to_ftp',
    bucket=GS_OUT_BUCKET_NAME,
    path=bucket_file_path,
    destination=f'{FTP_SERVER}:{FTP_FILE_PATH}',
    top_file=FTP_ACK_FILENAME,
    retries=3,
    timeout="15m",
    dag=dag)


done = DummyOperator(task_id='done', dag=dag)

push_to_gcs >> delete_table >> export_to_ftp >> done
