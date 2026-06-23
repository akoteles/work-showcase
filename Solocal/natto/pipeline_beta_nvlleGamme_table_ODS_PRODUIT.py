from airflow.models import Variable, DAG
from datetime import datetime, timedelta
from airflow.operators.dummy_operator import DummyOperator
from commercial.utils import bigquery, read_file, kub, sourcing
try:
    from airflow.operators import K8SJobOperator
except ImportError:
    from plugins.sudata import K8SJobOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2019, 7, 22),
    'catchup': False,
    'retry_delay': timedelta(minutes=5),
}

ENV = Variable.get('ENV')
PROJECT = Variable.get('COMMERCIAL_PROJECT')
COMMERCIAL_INPUT_BUCKET = Variable.get('COMMERCIAL_INPUT_BUCKET')
COMMERCIAL_OUTPUT_BUCKET = Variable.get('COMMERCIAL_OUTPUT_BUCKET')

GKE_JOB_TIMEOUT = 60 * 60 * 2
GKE_JOB_RETRIES = 3
DATASET_NVLLE_GAMME = Variable.get('NOUVELLE_GAMME_DATASET')

PIPELINE_BETA_IMAGE_VERSION = Variable.get('PIPELINE_BETA_IMAGE_VERSION')
PIPELINE_BETA_BUCKET_NAME = "{bucket}/pipeline_beta".format(bucket=Variable.get('COMMERCIAL_INPUT_BUCKET'))

exec_date_no_dash = "{{ ds_nodash }}"
exec_date = "{{ ds }}"

dag = DAG('pipeline_beta_nvlleGamme_table_ODS_PRODUIT', default_args=default_args, schedule_interval=None)
dag.doc_md = """\
# PIPELINE_BETA - TWH_ODS_PRODUIT, scheduled once a day
""".format(INPUT_BUCKET=PIPELINE_BETA_BUCKET_NAME, date=exec_date)

start = DummyOperator(task_id='start', dag=dag)

ods_produits_descriptor = read_file('/commercial/pipeline_beta/yaml/pipeline_beta_ods_produit_descriptor.yaml')
host_project = Variable.get('HOST_PROJECT')
host_cluster = Variable.get('HOST_CLUSTER')
location = Variable.get('LOCATION')

transform_to_TWH_ODS_PRODUITS_model=K8SJobOperator(
    task_id='prepare_TWH_ODS_PRODUITS',
    location=location,
    project_id=host_project,
    cluster_name=host_cluster,
    name='pipeline_beta_prepare_TWH_ODS_PRODUIT',
    gcp_conn_id='gcp_kub_runner',
    params={"pipeline_beta_version" : PIPELINE_BETA_IMAGE_VERSION,
            "pipeline_beta_conn_id": 'bigquery-key',
            "pipeline_beta_input_path": COMMERCIAL_INPUT_BUCKET,
            "pipeline_beta_output_path": COMMERCIAL_OUTPUT_BUCKET,
            "mainclass": 'daily.DailyOdsProduit',
            "environment": ENV},
    namespace='composer',
    descriptor=ods_produits_descriptor,
    timeout_s=GKE_JOB_TIMEOUT,
    dag=dag)

path_ods_produit_avro = 'ten_zoom/db/dwh_ten_taka/tableOdsProduit'

load_to_bq = sourcing.load_avro(
    name="load_TWH_ODS_PRODUIT_to_bq",
    bucket=PIPELINE_BETA_BUCKET_NAME,
    path='{path}/{date}/'.format(path=path_ods_produit_avro, date=exec_date),
    table='TWH_ODS_PRODUIT',
    project=PROJECT,
    dataset=DATASET_NVLLE_GAMME, overwrite=True, dag=dag)

done = DummyOperator(task_id='end', dag=dag)

start >> transform_to_TWH_ODS_PRODUITS_model >> load_to_bq >> done
