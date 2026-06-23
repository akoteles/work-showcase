import os
from airflow.models import Variable, DAG
from datetime import datetime, timedelta
from airflow.operators.dummy_operator import DummyOperator

from commercial.utils import read_file
from commercial.utils.bigquery import execute_multi_DML

from commercial.utils.bigquery import extract_CSV
from commercial.utils.io import export_from_gcs


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
DAG_FOLDER = os.environ.get('DAGS_FOLDER')
HOST_PROJECT = Variable.get('HOST_PROJECT')
HOST_CLUSTER = Variable.get('HOST_CLUSTER')
LOCATION = Variable.get('LOCATION')
PROJECT = Variable.get('COMMERCIAL_PROJECT')
PIPELINE_ALPHA_DATASET = Variable.get('COMMERCIAL_DATASET')
DELIMITER = '--q'
BIGQUERY_CONN = 'bigquery_dcproc'
EXPORT_BUCKET = Variable.get('COMMERCIAL_OUTPUT_BUCKET')
EXPORT_EXT = 'csv'

ENV = Variable.get('ENV')

schedule = None

PARTNER = 'RH'
CIAL_COMPONENT = 'correctif_edition'
gcs_subdir = f'{PARTNER}/{CIAL_COMPONENT}'

dag = DAG('pipeline_alpha_correctif_edition_extract', default_args=default_args, schedule_interval=schedule)

start = DummyOperator(task_id='start', dag=dag)
done = DummyOperator(task_id='done', dag=dag)

steps = [
  'extract_OTC_date_validation_inferieure_date_butoir',
  'extract_OTC_date_validation_sup_egale_date_butoir',
  'extract_VFO_date_validation_inferieure_date_butoir',
  'extract_VFO_date_validation_sup_egale_date_butoir'
]

for step in steps:
    requete = execute_multi_DML(name=step,
                                   sql=read_file(f'/commercial/{CIAL_COMPONENT}/sql/extract/{step}.sql'),
                                   params={
                                     'project_id': PROJECT,
                                     'pipeline_alpha_dataset': PIPELINE_ALPHA_DATASET
                                   },
                                   dag=dag
    )
    extract_csv = extract_CSV(
       name=f'ext_{step}',
       sql=read_file(f'/commercial/{CIAL_COMPONENT}/sql/extract/{step}.sql'),
       bucket=EXPORT_BUCKET,
       path=f'{gcs_subdir}/{step}_{{{{ds_nodash}}}}.{EXPORT_EXT}',
       encoding='ISO-8859-15',
       separator=';',
       header=True,
       quotes='None',
       params={
          'project_id': PROJECT,
          'pipeline_alpha_dataset': PIPELINE_ALPHA_DATASET
      },
      dag=dag
  )
    start >> requete >> extract_csv >> done
