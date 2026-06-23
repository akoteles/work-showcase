import os
from datetime import datetime, timedelta

try:
    from airflow.operators import K8SJobOperator
    from airflow.operators import GCloudApiSensor
except ImportError:
    from plugins.sudata import K8SJobOperator, GCloudApiSensor

from airflow.models import Variable, DAG

ENV = Variable.get('ENV')
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2019, 3, 25),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'catchup': False,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('pipeline_beta_audience_api-sourcing', default_args=default_args, schedule_interval=None)
dag.catchup = False
dag.doc_md = """\
#PIPELINE_BETA Api sourcing for audience (scheduled daily)
Sourcing products</br>
 - *PROJECT_ID* : acme-data-dev</br>
 - *BUCKET* : gs://acme-data-dev/pipeline_beta/ten_zoom/db/dwh_ten_zoom/productApiRepoAudience/{{ ds }}/</br>
 - *depends on * : none</br>
 - *required by *: '[pipeline_beta_audience_dailyproduit_transform DAG](./graph?dag_id=pipeline_beta_audience_dailyproduit_transform)'</br>
 - *generates* : parquet files
""".format(env=ENV)

DAG_FOLDER = os.environ.get('DAGS_FOLDER')
PROJECT_ID=Variable.get('COMMERCIAL_PROJECT')
DP_PROJECT_ID=Variable.get('DP_PROJECT')

PIPELINE_BETA_INPUTDATA_BUCKET = None
if ENV == 'dev' :
    PIPELINE_BETA_INPUTDATA_BUCKET = 'acme-data-dev'.format(env=ENV)
else :
    PIPELINE_BETA_INPUTDATA_BUCKET = 'acme-data-dev'.format(env=ENV)

PIPELINE_BETA_OUTPUT_BUCKET = 'acme-data-dev'.format(env=ENV)
PIPELINE_BETA_CONN_ID = 'bigquery-key'
PIPELINE_BETA_IMAGE_VERSION = Variable.get('PIPELINE_BETA_IMAGE_VERSION')

PIPELINE_BETA_VERSION="1.0"
PIPELINE_BETA_ARTEFACTS_BUCKET = 'gs://acme-data-dev/pipeline_beta/'.format(env=ENV)

SOURCING_TIMEOUT = 60 * 240
RETRIES = 3

host_project = Variable.get('HOST_PROJECT')
host_cluster = Variable.get('HOST_CLUSTER')
location = Variable.get('LOCATION')
region = Variable.get('REGION')


yaml_pipeline_beta_api_sourcing = """
containers:
  - name: pipeline_beta-api-sourcing
    image: registry.gitdata.example.com/data/commercial/palp-otc-spark/pipeline_beta:{{params.pipeline_beta_version}}
    resources:
      requests:
        memory: "10Gi"
        cpu: "1"
      limits:
        memory: "10Gi"
        cpu: "1"
    env:
      - name: GOOGLE_APPLICATION_CREDENTIALS
        value: "/var/secrets/google/{{ params.pipeline_beta_conn_id }}.json"
      - name: PIPELINE_BETA_WRITE_PATH
        value: "{{ params.pipeline_beta_write_path }}"
      - name: PIPELINE_BETA_OUTPUT_PATH
        value: "{{ params.pipeline_beta_output_path }}"
      - name: MAINCLASS
        value: "{{ params.mainclass }}"
      - name: DRIVERMEM
        value: '3g'
      - name: ENVIRONMENT
        value: "{{ params.environment }}"
      - name: EXECUTION_DATE
        value: "{{ ds }}"
      - name: PLATFORM
        value: "GCP"
    args: ["--audience","--full"]
    volumeMounts:
      - name: google-cloud-key
        mountPath: /var/secrets/google
        readOnly: true
    ports:
      - containerPort: 4040
imagePullSecrets:
  - name: gitlab-key
volumes:
  - name: google-cloud-key
    secret:
      secretName: "{{ params.pipeline_beta_conn_id }}"

"""

pipeline_beta_api_sourcing = None
pipeline_beta_api_sourcing = K8SJobOperator(task_id='pipeline_beta-audience-api-sourcing',
           location=location,
           project_id=host_project,
           cluster_name=host_cluster,
           name='pipeline_beta-audience-api-sourcing',
           gcp_conn_id='gcp_kub_runner',
           params={"pipeline_beta_version" : PIPELINE_BETA_IMAGE_VERSION,
                  "pipeline_beta_conn_id": PIPELINE_BETA_CONN_ID,
                   "pipeline_beta_write_path": PIPELINE_BETA_INPUTDATA_BUCKET,
                   "pipeline_beta_output_path": PIPELINE_BETA_OUTPUT_BUCKET,
                   "mainclass": 'ten.gpp.App',
                   "environment": ENV},
           namespace='composer',
           descriptor=yaml_pipeline_beta_api_sourcing,
           timeout_s=SOURCING_TIMEOUT,
           retries=RETRIES,
           dag=dag)
