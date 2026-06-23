import os
from datetime import datetime, timedelta
from airflow.models import Variable, DAG
from commercial.utils import pyrunner, bigquery, read_file

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
DATASET = Variable.get('COMMERCIAL_DATASET')
PROJECT = Variable.get('COMMERCIAL_PROJECT')
BUCKET = Variable.get('COMMERCIAL_INPUT_BUCKET')
PATH = "pipeline_gamma_V2"

dag = DAG('pipeline_alpha_subsidiaries_PIPELINE_GAMMA', default_args=default_args,
          schedule_interval=None)

DAG_FOLDER = os.environ.get('DAGS_FOLDER')

init_pipeline_gamma = bigquery.execute_multi_DML(
    name="init_PIPELINE_GAMMA",
    sql=read_file("/commercial/pipeline_alpha_subsidiaries/pipeline_gamma/init/SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_ALIM_STA_DE_TEMPO.sql"),
    params={
        'project_id': PROJECT,
        'pipeline_alpha_dataset': DATASET,
    },
    timeout="1h",
    retries=2,
    dag=dag
)

do_pipeline_gamma = pyrunner.run_python(
    name="pipeline_alpha_filiale_pipeline_gamma_process",
    script=read_file("/commercial/pipeline_alpha_subsidiaries/pipeline_gamma/process.py"),
    env={
        'PROJECT': PROJECT,
        'DATASET': DATASET,
        'BUCKET': BUCKET,
        'PATH': PATH + "/{{ds}}",
    },
    timeout="15m",
    dag=dag
)

init_pipeline_gamma >> do_pipeline_gamma
