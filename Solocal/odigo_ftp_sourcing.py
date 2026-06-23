from airflow.models import Variable, DAG

from datetime import datetime, timedelta

import os
import io
import json

from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
from airflow.operators.dummy_operator import DummyOperator

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
    'max_active_runs': 5,
    'retry_delay': timedelta(minutes=5),
}

ODIGO_BUCKET_NAME = "{bucket}/odigo".format(bucket=Variable.get('COMMERCIAL_INPUT_BUCKET'))
DAG_FOLDER = os.environ.get('DAGS_FOLDER')
PROJECT = Variable.get('COMMERCIAL_PROJECT')
host_project = Variable.get('HOST_PROJECT')
host_cluster = Variable.get('HOST_CLUSTER')
location = Variable.get('LOCATION')

dag = DAG('odigo_ftp_sourcing', default_args=default_args, schedule_interval='0 4 * * *')
dag.doc_md = """\
# ODIGO Tables FTP sourcing, scheculed daily at 04:00 AM
- Copy 4 odigo files of the execution date from FTP to GCS
- Loads the copied the files to BQ tables in a partition corresponding to the execution date. The table will be created if it doesn't exist.

To run the DAG on an interval in the past (e.g. history recovery) use backfill command with gcloud.
Example to recover history over May 2019 :

`gcloud beta composer environments run <COMPOSER_NAME>  --location=europe-west1 backfill -- odigo_ftp_sourcing  -s 2019-05-01 -e 2019-06-01 --rerun_failed_tasks`

Note that you should be using the project where the composer is deployed as default project in the gcloud configuration core/project
"""
start = DummyOperator(task_id='start',dag = dag)

yaml = """
containers:
  - name: copyrafiles
    image: registry.gitdata.example.com/data/transverse/docker-images/base-image-rclone
    resources:
      requests:
        memory: "16Mi"
        cpu: "0.5"
      limits:
        memory: "2Gi"
        cpu: "2"
    command: ["bash","-c"]
    args:
      - 'rclone --config=/var/secrets/rclone/rclone.conf --verbose=4 copy --include {{ ds_nodash }}_{{params.filename}}.csv odigo:/depot/ gcs_dest_dcproc:{{params.gs_bucket_name}}/{{ params.folder}}/'
    volumeMounts:
      - name: google-cloud-key
        mountPath: /var/secrets/google
        readOnly: true
      - name: rclone
        mountPath: /var/secrets/rclone
        readOnly: true
imagePullSecrets:
  - name: gitlab-key
volumes:
  - name: google-cloud-key
    secret:
      secretName: bigquery-key
  - name: rclone
    secret:
      secretName: rclone

"""

ODIGO_FILES = [
    {"file_name": "Tickets_Appels_Sortants_PAGESJAUNES", "folder": "sortants", "table": "TICKETS_APPELS_SORTANTS"},
    {"file_name": "Tickets_Appels_Entrants_PAGESJAUNES", "folder": "entrants", "table": "TICKETS_APPELS_ENTRANTS"},
    {"file_name": "Tickets_Campagnes_PAGESJAUNES", "folder": "campagnes", "table": "TICKETS_CAMPAGNES"},
    {"file_name": "Tickets_Rappels_PAGESJAUNES", "folder": "rappels", "table": "TICKETS_RAPPELS"},
]

yyyymmdd = '{{ds_nodash}}'

for odigo_file in ODIGO_FILES:
    file_name = odigo_file['file_name']
    folder = odigo_file['folder']
    schema_file = odigo_file['folder']
    table = odigo_file['table']
    source_file = schema_file + '/' + yyyymmdd + '_' + file_name + '.csv'

    source_to_gcs = K8SJobOperator(task_id="import_odigo_{file_name}_from_ftp".format(file_name=file_name),
               location=location,
               project_id=host_project,
               cluster_name=host_cluster,
               name="import_odigo_files",
               gcp_conn_id='gcp_kub_runner',
               params={"gs_bucket_name": ODIGO_BUCKET_NAME,
                       "filename":file_name,
                       "folder": folder},
               namespace='composer',
               descriptor=yaml,
               timeout_s=60 * 15,
               retries= 3,
               dag=dag,
               pool='odigo_ftp_sourcing_pool')

    with io.open('{folder}/commercial/odigo_tables_schema/{schema_file}_schema.json'.format(folder=DAG_FOLDER,schema_file=schema_file),
                 'r',encoding='utf-8') as f:
        schema = json.load(f)
        f.close()
    load_to_bq = GoogleCloudStorageToBigQueryOperator(
        task_id='load_odigo_{file_name}_to_bq'.format(file_name=file_name),
        bucket=ODIGO_BUCKET_NAME,
        source_objects=[source_file],
        destination_project_dataset_table='{project_id}.dwh_client.{table_id}${partition}'.format(project_id=PROJECT,table_id=table, partition=yyyymmdd),
        schema_fields=schema,
        source_format='CSV',
        allow_jagged_rows=True,
        skip_leading_rows=1,
        create_disposition='CREATE_IF_NEEDED',
        write_disposition='WRITE_TRUNCATE',
        field_delimiter=';',
        bigquery_conn_id='bigquery_dcproc',
        allow_quoted_newlines=True,
        dag=dag)

    start >> source_to_gcs >> load_to_bq
