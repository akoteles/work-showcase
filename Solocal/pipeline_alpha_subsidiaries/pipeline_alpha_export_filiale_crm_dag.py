import os
from airflow.models import Variable, DAG
from datetime import datetime, timedelta
from commercial.utils import read_file, bigquery, io

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

schedule='0 10 * * 5'
dag = DAG('pipeline_alpha_export_filiale_crm', default_args=default_args, schedule_interval=schedule)

DAG_FOLDER = os.environ.get('DAGS_FOLDER')

PIPELINE_ALPHA_DATASET = Variable.get('COMMERCIAL_DATASET')
PROJECT = Variable.get('COMMERCIAL_PROJECT')
GS_BUCKET_NAME = Variable.get('COMMERCIAL_OUTPUT_BUCKET')

PARTNER = 'CRM'
CIAL_COMPONENT = 'subsidiaries'

EXPORT_FILENAME = 'TWH_SCO_AUTRES'
EXPORT_EXT = 'csv'

FTP_SERVER = 'usr_cs_depot'
FTP_DIR = '/crm/retrait/PHS'
FTP_ACK_FILENAME = 'TOP_TWH_SCO_AUTRES'
query = read_file('/commercial/pipeline_alpha_subsidiaries/crm/SQL_PALP_EXTRACT_SALES_TRANSACTIONS_SUBSIDIARIES_HEBDO_CRM.sql')

gcs_subdir = f'{PARTNER}/{CIAL_COMPONENT}'
gcs_file_path = f'{gcs_subdir}/{EXPORT_FILENAME}_{{{{ds_nodash}}}}.{EXPORT_EXT}'

extract_csv = bigquery.extract_CSV(name='extract_csv',
                          sql=query,
                          bucket=GS_BUCKET_NAME,
                          path=gcs_file_path,
                          separator=';',
                          encoding='utf8',
                          header=True,
                          quotes='None',
                          params={
                            'project_id': PROJECT,
                            'dataset_id': PIPELINE_ALPHA_DATASET
                          },
                          dag=dag
                          )

export_file = io.export_from_gcs(name='export_to_ftp',
                              destination=f'{FTP_SERVER}:{FTP_DIR}',
                              dest_filename=f'{EXPORT_FILENAME}.{EXPORT_EXT}',
                              bucket=GS_BUCKET_NAME,
                              path=gcs_file_path,
                              top_file=FTP_ACK_FILENAME,
                              dag=dag
                              )

extract_csv >> export_file
