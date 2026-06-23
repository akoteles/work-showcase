from datetime import datetime, timedelta

from airflow.models import Variable, DAG
from commercial.utils import kub

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

dag = DAG('pipeline_beta_audience_dailyproduit_transform', default_args=default_args, schedule_interval=None)
dag.catchup = False
dag.doc_md = """\
#PIPELINE_BETA Table audience daily (scheduled : daily)
Full sourcing from GPP for A and SR products, produces a parquet dump:</br>
 - *PROJECT_ID* : acme-data-dev</br>
 - *BUCKET* : gs://acme-data-dev/pipeline_beta/ten_zoom/db/dwh_ten_taka/tableAudience/{{ ds }}/</br>
 - *depends on * : '[pipeline_beta_audience_api-sourcing DAG](./graph?dag_id=pipeline_beta_audience_api-sourcing)'</br>
 - *generates* : parquet a parquet file for produitA and produitSR</br>
""".format(env=ENV)

PROJECT_ID = Variable.get('COMMERCIAL_PROJECT')

PIPELINE_BETA_INPUTDATA_BUCKET = Variable.get('COMMERCIAL_INPUT_BUCKET')
PIPELINE_BETA_OUTPUT_BUCKET = Variable.get('COMMERCIAL_OUTPUT_BUCKET')
PIPELINE_BETA_IMAGE_VERSION = Variable.get('PIPELINE_BETA_IMAGE_VERSION')
PIPELINE_BETA_CONN_ID = 'bigquery-key'

PIPELINE_BETA_VERSION = "1.0"
PIPELINE_BETA_ARTEFACTS_BUCKET = 'gs://acme-data-dev/pipeline_beta/'.format(env=ENV)

TRANSFORM_TIMEOUT = "4h"
RETRIES = 0

yaml_pipeline_beta_api_sourcing = """
kind: Pod
apiVersion: v1
metadata:
    name: pipeline_beta-api-sourcing
    namespace: composer
spec:
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
        args: ["--audience"]
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

pipeline_beta_table_processing = kub.KubRunOperator(
    name='pipeline_beta-audience-dailyproduit-processing',
    task_id='pipeline_beta-audience-dailyproduit-processing',
    params={"pipeline_beta_version": PIPELINE_BETA_IMAGE_VERSION,
            "pipeline_beta_conn_id": PIPELINE_BETA_CONN_ID,
            "pipeline_beta_write_path": PIPELINE_BETA_INPUTDATA_BUCKET,
            "pipeline_beta_output_path": PIPELINE_BETA_OUTPUT_BUCKET,
            "mainclass": 'daily.DailyAudience',
            "environment": ENV},
    descriptor=yaml_pipeline_beta_api_sourcing,
    timeout=TRANSFORM_TIMEOUT,
    retries=RETRIES,
    dag=dag)
