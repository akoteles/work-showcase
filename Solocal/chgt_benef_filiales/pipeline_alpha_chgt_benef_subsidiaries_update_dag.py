from airflow.models import Variable, DAG
from datetime import datetime, timedelta
from airflow.operators.dummy_operator import DummyOperator

from commercial.utils import read_file
from commercial.utils.bigquery import execute_multi_DML

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

PROJECT = Variable.get('COMMERCIAL_PROJECT')
PIPELINE_ALPHA_DATASET = Variable.get('COMMERCIAL_DATASET')

schedule = None

TABLE_NAME = 'TWH_ODS_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_ORIGINAL'
sql_query = '/commercial/chgt_benef_subsidiaries/sql/UPDATE_CHGT_BENEF_SUBSIDIARIES.sql'

dag = DAG('chgt_benef_subsidiaries_update_table', default_args=default_args, schedule_interval=schedule)

updated_table = execute_multi_DML(
    name=f'update_{TABLE_NAME}_table',
    sql=read_file(sql_query),
    params={
        'project_id': PROJECT,
        'pipeline_alpha_dataset': PIPELINE_ALPHA_DATASET
    },
    dag=dag
)

done = DummyOperator(task_id='done', dag=dag)

updated_table >> done
