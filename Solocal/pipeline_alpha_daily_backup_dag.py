from datetime import datetime, timedelta

from airflow.models import Variable, DAG
from airflow.operators.dummy_operator import DummyOperator
from commercial.utils import pyrunner, read_file, mailing

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

schedule = None
dag = DAG('pipeline_alpha_daily_backup', default_args=default_args, schedule_interval=schedule)
dag.doc_md = """
#Dataset Backup dag

Copies every day the pipeline_alpha and tracking datasets into backup datasets

Cleans old backups code with one week daily retention and 5 weeks sunday retention
"""

PIPELINE_ALPHA_DATASET = Variable.get('COMMERCIAL_DATASET')
PIPELINE_ALPHA_PROJECT = Variable.get('COMMERCIAL_PROJECT')
TRACKING_DATASET = Variable.get('TRACKING_DATASET')
ENV = Variable.get('ENV')

backupPy = """
import sys
from google.cloud import bigquery
from google.cloud.bigquery.dataset import DatasetReference
import os

project=os.environ["PROJECT"]
source_dataset=os.environ["DATASET"]
datelabel=os.environ["DS"]

dest_dataset=f'{source_dataset}_backup_{datelabel}'

bq=bigquery.Client(project,location='EU')

source_ds=DatasetReference(project,source_dataset)
dest_ds=DatasetReference(project,dest_dataset)

print(f"Creating dataset {dest_ds}")
print(bq.create_dataset(dest_ds))

tables = [t.table_id for t in bq.list_tables(source_ds) if t.table_type=="TABLE"]

error=False

for table in tables:
    print(f"Copying table {table}")
    table_src = source_ds.table(table)
    table_dest = dest_ds.table(table)
    job_config = bigquery.CopyJobConfig()
    job_config.write_disposition = "WRITE_TRUNCATE"
    try:
        job = bq.copy_table(
            table_src,
            table_dest,
            job_config=job_config,
            location="EU",
        )  # API request

        job.result()  # Waits for job to complete.
        print('table {} loaded'.format(table_dest.path))
    except:
        if not "not allowed for this operation because it is currently a VIEW" in job.errors[0].message:
            print('WARNING table {} not loaded: {}'.format(table_dest.path,job.errors))
        else:
            print('ERROR table {} not loaded: {}'.format(table_dest.path,job.errors))
            error=True
if error:
    sys.exit(1)
else:
    sys.exit(0)
"""

cleanupPy = """
import sys

from google.cloud import bigquery
import os
import datetime
from google.cloud.bigquery.dataset import DatasetReference

project = os.environ["PROJECT"]

bq = bigquery.Client(project, location='EU')

datasets = [x.dataset_id for x in bq.list_datasets(project=project) if "_backup_" in x.dataset_id]

now = datetime.date.today()
backup_date_format = "%Y%m%d"

todelete = []

for dataset in datasets:
    try:
        ds_date = datetime.datetime.strptime(dataset.split('_')[-1], backup_date_format).date()
        age_days = (now - ds_date).days
        print(f"dataset:{dataset}, datetime:{ds_date}, age_days:{age_days}")
        if age_days > 7:
            if ds_date.weekday() == 6:
                if age_days > 7 * 5:
                    todelete.append(dataset)
            else:
                todelete.append(dataset)
    except:
        print(f"Error with dataset {dataset}")

for dataset in todelete:
    dsref = DatasetReference(project, dataset)
    print(f"Deleting dataset {dataset}")
    print(bq.delete_dataset(dataset=dataset, delete_contents=True))
 """

backup_pipeline_alpha_prd = pyrunner.run_python(
    name="do_pipeline_alpha_copy",
    script=backupPy,
    env={
        'PROJECT': PIPELINE_ALPHA_PROJECT,
        'DATASET': PIPELINE_ALPHA_DATASET,
        'DS': "{{ds_nodash}}"
    },
    timeout="1h",
    retries=0,
    dag=dag
)

backup_tracking_prd = pyrunner.run_python(
    name="do_tracking_copy",
    script=backupPy,
    env={
        'PROJECT': PIPELINE_ALPHA_PROJECT,
        'DATASET': TRACKING_DATASET,
        'DS': "{{ds_nodash}}"
    },
    timeout="1h",
    retries=0,
    dag=dag
)

start = done = DummyOperator(
    task_id='start',
    dag=dag
)

cleanup_old_backups = pyrunner.run_python(
    name="cleanup_datasets",
    script=cleanupPy,
    env={
        'PROJECT': PIPELINE_ALPHA_PROJECT,
        'DS': "{{ds_nodash}}"
    },
    timeout="30m",
    retries=0,
    dag=dag
)

if ENV.upper() == "PRD":
    contents = """Daily backup for GCP PipelineAlpha done for run {{ds}}."""
    send_ok_mail = mailing.send_mail("send_mail_ok", "[PALP] Daily Backup OK", ["alerts-prod@example.com"],
                                     contents, dag=dag)
elif ENV.upper() == "REC":
    contents = """Daily backup for GCP PipelineAlpha done for run {{ds}}."""
    send_ok_mail = mailing.send_mail("send_mail_ok", "[PALP] [REC] Daily Backup OK",
                                     ["alerts-rec@example.com"],
                                     contents, dag=dag)
else:
    send_ok_mail = DummyOperator(task_id='dummy_sendmail_dev',
                                 dag=dag)

if ENV.upper() == "PRD":
    contents = """Daily backup for GCP PipelineAlpha FAILED for run {{ds}}."""
    send_nok_mail = mailing.send_mail("send_mail_nok", "[PALP] Daily Backup FAILED", ["alerts-prod@example.com"],
                                      contents, dag=dag, trigger_rule='one_failed')
elif ENV.upper() == "REC":
    contents = """Daily backup for GCP PipelineAlpha FAILED for run {{ds}}."""
    send_nok_mail = mailing.send_mail("send_mail_nok", "[PALP] [REC] Daily Backup FAILED",
                                      ["alerts-rec@example.com"],
                                      contents, dag=dag, trigger_rule='one_failed')
else:
    send_nok_mail = DummyOperator(task_id='dummy_sendmail_nok_dev',
                                  dag=dag, trigger_rule='one_failed')

start >> [backup_tracking_prd, backup_pipeline_alpha_prd] >> cleanup_old_backups

[backup_tracking_prd, backup_pipeline_alpha_prd] >> send_ok_mail
[backup_tracking_prd, backup_pipeline_alpha_prd] >> send_nok_mail
