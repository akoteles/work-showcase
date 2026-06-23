import os
from datetime import datetime, timedelta

import yaml
from airflow.models import Variable, DAG
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators import ChildDagOperator
from airflow.operators.dummy_operator import DummyOperator
from commercial.utils import mailing, io, pyrunner, bigquery

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

host_project = Variable.get('HOST_PROJECT')
host_cluster = Variable.get('HOST_CLUSTER')
location = Variable.get('LOCATION')
region = Variable.get('REGION')
PIPELINE_ALPHA_DATASET = Variable.get('COMMERCIAL_DATASET')
TMP_DATASET = Variable.get('COMMERCIAL_DATASET_TMP')

PROJECT = Variable.get('COMMERCIAL_PROJECT')
schedule = None

BUCKET = Variable.get('COMMERCIAL_INPUT_BUCKET')
OUTPUT_BUCKET = Variable.get('COMMERCIAL_OUTPUT_BUCKET')
PATH = "subsidiaries/"
DAG_FOLDER = os.environ.get('DAGS_FOLDER')
ENV = os.environ.get("ENV", "DEV")

load_schedule = None


def load_file(name):
    with open("{}/commercial/pipeline_alpha_subsidiaries/{}".format(DAG_FOLDER, name), mode="r", encoding="utf-8") as fd:
        return fd.read()


def parse_yaml_file(name):
    with open("{}/commercial/pipeline_alpha_subsidiaries/{}".format(DAG_FOLDER, name), mode="rb") as fd:
        return yaml.load(fd)


def gen_sourcing(name, filiale, dag):
    if ENV.upper()=="PRD":
        return io.simple_rclone(name=f"pipeline_alpha_filiale_sourcing_{name}_fetch",
                            rclone_cmd_line="rclone --config=/var/secrets/rclone/rclone.conf --verbose=1 --ftp-concurrency=1 move --include PALP_TOP_SALES_TRANSACTIONS_* --include PALP_TXT_SALES_TRANSACTIONS_* {{ params.source }}:/ gcs_dest_dcproc:{{params.dest}}/{{ ds }}",
                            timeout="15m",
                            params={
                                'dest': "{bucket}/subsidiaries/{name}".format(bucket=BUCKET, path=PATH, name=name),
                                'source': filiale['rclone_alias']
                            },
                            dag=dag)
    else:
        return io.simple_rclone(name=f"pipeline_alpha_filiale_sourcing_{name}_fetch",
                                rclone_cmd_line="rclone --config=/var/secrets/rclone/rclone.conf --verbose=1 --ftp-concurrency=1 copy --include PALP_TOP_SALES_TRANSACTIONS_* --include PALP_TXT_SALES_TRANSACTIONS_* {{ params.source }}:/ gcs_dest_dcproc:{{params.dest}}/{{ ds }}",
                                timeout="15m",
                                params={
                                    'dest': "{bucket}/subsidiaries/{name}".format(bucket=BUCKET, path=PATH, name=name),
                                    'source': filiale['rclone_alias']
                                },
                                dag=dag)


utils = load_file("utils/__init__.py")


def gen_alim(name, filiale, dag):
    return pyrunner.run_python(
        name=f"pipeline_alpha_filiale_sourcing_{name}_load",
        script=load_file("alim/script.py"),
        files=[{'name': 'utils/__init__.py', 'value': utils}],
        env={
            'GCS_PROJECT': PROJECT,
            'GCS_BUCKET': BUCKET,
            'BQ_PROJECT': PROJECT,
            'BQ_DATASET': PIPELINE_ALPHA_DATASET,
            'BQ_REGION': region,
            'BQ_TABLE': "TWH_STA_PALP_SALES_TRANSACTIONS_SUBSIDIARIES",
            'NAME_FILIALE': name,
            'CODE_FILIALE': filiale['codefiliale'],
            'SOURCE_ENCODING': filiale['source_encoding'],
            'SOURCE_DATE': '{{ ds }}'
        },
        pool="subsidiaries_sourcing",
        dag=dag)


def gen_delete_source_files(name, filiale, dag):
    pass


def gen_krn(name, filiale, dag):
    return pyrunner.run_python(
        name=f"pipeline_alpha_filiale_sourcing_{name}_load",
        script=load_file("alim/script.py"),
        files=[{'name': 'utils/__init__.py', 'value': utils}],
        env={
            'GCS_PROJECT': PROJECT,
            'GCS_BUCKET': BUCKET,
            'BQ_PROJECT': PROJECT,
            'BQ_DATASET': PIPELINE_ALPHA_DATASET,
            'BQ_REGION': region,
            'NAME_FILIALE': name,
            'CODE_FILIALE': filiale['codefiliale'],
            'SOURCE_DATE': '{{ ds }}',
            'FILIALE_RCLONE': filiale['rclone_alias'],
            'FILIALE_SOURCE': filiale['krn_source']
        },
        timeout="15m",
        pool="subsidiaries_sourcing",
        dag=dag)


def gen_ctrl_rg(dag):
    return pyrunner.run_python(
        name=f"pipeline_alpha_filiale_Ctrl_RG",
        script=load_file("controle_rg/script.py"),
        files=[
            {'name': 'utils/__init__.py', 'value': utils},
            {'name': '1_SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_MARQUAGE_REJETS.sql',
             'value': load_file("controle_rg/1_SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_MARQUAGE_REJETS.sql")},
        ],
        env={
            'GCS_PROJECT': PROJECT,
            'BQ_PROJECT': PROJECT,
            'BQ_DATASET': PIPELINE_ALPHA_DATASET,
            'BQ_REGION': region,
            'SOURCE_DATE': '{{ ds }}',
        },
        params={
            'project_id': PROJECT,
            'pipeline_alpha_dataset': PIPELINE_ALPHA_DATASET,
        },
        timeout="1h",
        dag=dag
    )


def gen_pipeline_gamma(dag):
    return ChildDagOperator(task_id="pipeline_alpha_subsidiaries_PIPELINE_GAMMA", dag_id="pipeline_alpha_subsidiaries_PIPELINE_GAMMA", dag=dag, retries=0)


def gen_export_ctrl_rg(name, filiale, dag):
    return pyrunner.run_python(
        name=f"pipeline_alpha_filiale_Ctrl_RG_Export_{filiale['codefiliale']}",
        script=load_file("controle_rg_export/script.py"),
        files=[
            {'name': 'utils/__init__.py', 'value': utils},
            {'name': '6A_SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_REJETS_REGLES_GESTION.sql',
             'value': load_file('controle_rg_export/6A_SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_REJETS_REGLES_GESTION.sql')},
        ],
        env={
            'GCS_PROJECT': PROJECT,
            'BQ_PROJECT': PROJECT,
            'BQ_DATASET': PIPELINE_ALPHA_DATASET,
            'BQ_REGION': region,
            'NAME_FILIALE': name,
            'CODE_FILIALE': filiale['codefiliale'],
            'FILIALE_RCLONE': filiale['rclone_alias'],
            'SOURCE_DATE': '{{ ds }}',
            'EXPORT_PATH': filiale['rclone_alias'],
            'EXPORT_GCS_PATH': f"gcs_dest_dcproc:{OUTPUT_BUCKET}/{PATH}{name}"
        },
        params={
            'project_id': PROJECT,
            'pipeline_alpha_dataset': PIPELINE_ALPHA_DATASET,
        },
        timeout="15m",
        dag=dag
    )


export_query = load_file('extract_sales_transactions/SQL_PALP_EXTRACT_SALES_TRANSACTIONS_SUBSIDIARIES_QUOTIDIEN.sql')


def gen_export(name, filiale, dag, previous_task):
    filiale_rclone_alias = 'gcs_dest_dcproc'
    code_filiale = filiale['codefiliale']
    table_to_export = "TWH_ODS_PALP_SALES_TRANSACTIONS_SUBSIDIARIES"
    export_file = 'EXTRACT_SALES_TRANSACTIONS_SUBSIDIARIES_%s_{{ds_nodash}}.csv' % (code_filiale)
    top_file = 'TOP_EXTRACT_SALES_TRANSACTIONS_SUBSIDIARIES_%s_{{ds_nodash}}.csv' % (code_filiale)
    export = bigquery.extract_CSV(
        name=f"{table_to_export}_to_gcs_{name}",
        sql=export_query,
        bucket=OUTPUT_BUCKET,
        path="/filiale/{{ ds_nodash }}/" + f"{name}/{export_file}",
        separator=',',
        encoding='UTF-8',
        params={
            'code_filiale': code_filiale,
            'project_id': PROJECT,
            'dataset_id': PIPELINE_ALPHA_DATASET
        },
        dag=dag)
    push = io.export_from_gcs(name=f"{table_to_export}_to_ftp_{name}",
                              bucket=OUTPUT_BUCKET,
                              path="/filiale/{{ ds_nodash }}/" + f"{name}/{export_file}",
                              destination=f"{filiale_rclone_alias}:filiale_vente_gcp/{export_file}",
                              top_file=top_file,
                              timeout="15m",
                              dag=dag)
    previous_task >> export >> push
    return push


def gen_alim_filiales(dag, previous_task):
    SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_RECH_REFERENT = bigquery.execute_multi_DML(
        name="3_SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_RECH_REFERENT",
        sql=load_file('alim_subsidiaries/3_SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_RECH_REFERENT.sql'),
        params={
            'project_id': PROJECT,
            'pipeline_alpha_dataset': PIPELINE_ALPHA_DATASET,
        },
        timeout="1h",
        retries=2,
        dag=dag
    )

    SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_INSERT_TEMPO = bigquery.execute_multi_DML(
        name="4_SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_INSERT_TEMPO",
        sql=load_file('alim_subsidiaries/4_SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_INSERT_TEMPO.sql'),
        params={
            'project_id': PROJECT,
            'pipeline_alpha_dataset': PIPELINE_ALPHA_DATASET,
            'dureeTempo': '-1',
        },
        timeout="1h",
        retries=2,
        dag=dag
    )

    SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_INSERT_ODS = bigquery.execute_multi_DML(
        name="5_SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_INSERT_ODS",
        sql=load_file('alim_subsidiaries/5_SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_INSERT_ODS.sql'),
        params={
            'project_id': PROJECT,
            'pipeline_alpha_dataset': PIPELINE_ALPHA_DATASET,
        },
        timeout="1h",
        retries=2,
        dag=dag
    )
    previous_task >> SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_RECH_REFERENT >> SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_INSERT_TEMPO >> SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_INSERT_ODS
    return SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_INSERT_ODS


def gen_export_filiales_rejet_referents(name, filiale, dag):
    return pyrunner.run_python(
        name="export_filiale_alerting_referent_errone_{}".format(name),
        script=load_file("export_subsidiaries_rejet_referent/script.py"),
        files=[
            {'name': 'utils/__init__.py', 'value': utils},
            {'name': 'SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_REJETS_DEFINITIFS_AVEC_EN_TETES.sql',
             'value': load_file(
                 "export_subsidiaries_rejet_referent/SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_REJETS_DEFINITIFS_AVEC_EN_TETES.sql")},
            {'name': 'SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_REJETS_DEFINITIFS_RECUP_DA_EVENT.sql',
             'value': load_file(
                 "export_subsidiaries_rejet_referent/SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_REJETS_DEFINITIFS_RECUP_DA_EVENT.sql")}
        ],
        env={
            'project_id': PROJECT,
            'dataset_id': PIPELINE_ALPHA_DATASET,
            'code_filiale': filiale['codefiliale'],
            'export_bucket': OUTPUT_BUCKET,
            'tmp_dataset': TMP_DATASET,
            'date_traitement': "{{ds}}"
        },
        params={
            "project_id": PROJECT,
            "dataset_id": PIPELINE_ALPHA_DATASET,
            "co_filiale": filiale['codefiliale'],
            "date_traitement": "{{ds}}"
        },
        pool="subsidiaries_sourcing",
        timeout="15m",
        dag=dag
    )


def gen_purge_tempo(dag):
    return bigquery.execute_multi_DML(
        name="EXEC_SALES_TRANSACTIONS_SUBSIDIARIES_PURGE_TEMPO_SQL",
        sql=load_file('purge_tempo/SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_PURGE_TEMPO.sql'),
        params={
            'project_id': PROJECT,
            'pipeline_alpha_dataset': PIPELINE_ALPHA_DATASET,
        },
        verbose=True,
        timeout="1h",
        retries=2,
        dag=dag
    )


def gen_rem_transform(dag):
    return bigquery.execute_multi_DML(
        name="SQL_PALP_INSERT_ODS_REM_SALES_TRANSACTIONS_SUBSIDIARIES",
        sql=load_file('rem/SQL_PALP_INSERT_ODS_REM_SALES_TRANSACTIONS_SUBSIDIARIES.sql'),
        params={
            'project_id': PROJECT,
            'pipeline_alpha_dataset': PIPELINE_ALPHA_DATASET,
            'top_demarrage': 'A',
            'date_limite_suppr': '2017-03-30'
        },
        timeout="1h",
        retries=2,
        dag=dag
    )


def gen_rem_export(dag, previous_task):
    filename = 'dumpBi'
    extension = 'csv'
    ftp_dir = '/depot'
    ftp_server = 'mftp01_palp'
    ftp_filename = f'{filename}.{extension}'
    bucket_filename = f'subsidiaries_rem/{filename}_{{{{ds_nodash}}}}.{extension}'
    query = load_file('rem/SQL_PALP_EXTRACT_ODS_REM_SALES_TRANSACTIONS_SUBSIDIARIES.sql')

    extract_csv = bigquery.extract_CSV(
      name='subsidiaries_REM_extract_csv',
      sql=query,
      bucket=OUTPUT_BUCKET,
      path=bucket_filename,
      separator='|',
      encoding='ISO-8859-15',
      params={
        'project_id': PROJECT,
        'dataset_id': PIPELINE_ALPHA_DATASET,
      },
      header=False,
      dag=dag
    )

    export_to_ftp = io.export_from_gcs(
      name='subsidiaries_REM_push_to_ftp',
      bucket=OUTPUT_BUCKET,
      path=bucket_filename,
      destination=f'{ftp_server}:{ftp_dir}',
      dest_filename=ftp_filename,
      top_file=None,
      timeout='15m',
      dag=dag
    )

    previous_task >> extract_csv >> export_to_ftp
    return export_to_ftp


def gen_peroraison(dag):
    return pyrunner.run_python(
        name="pipeline_alpha_filiale_peroraison",
        script=load_file("peroraison/script.py"),
        files=[
            {'name': 'utils/__init__.py', 'value': utils},
            {'name': 'subsidiaries.yaml',
             'value': load_file('subsidiaries.yaml')},
        ],
        env={
            'BQ_PROJECT': PROJECT,
            'BQ_DATASET': PIPELINE_ALPHA_DATASET,
            'BQ_REGION': region,
            'SOURCE_DATE': '{{ ds }}'
        },
        pool="subsidiaries_sourcing",
        timeout="15m",
        dag=dag
    )


filiales_dag = DAG('pipeline_alpha_subsidiaries', default_args=default_args,
                   schedule_interval=load_schedule)

filiales_part1 = DAG('pipeline_alpha_subsidiaries_part1', default_args=default_args,
                     schedule_interval=None)

filiales_part2 = DAG('pipeline_alpha_subsidiaries_part2', default_args=default_args,
                     schedule_interval=None)

filiales_part3 = DAG('pipeline_alpha_subsidiaries_part3', default_args=default_args,
                     schedule_interval=None)

filiales = parse_yaml_file("subsidiaries.yaml")

purge_TWH_STA_PALP_SALES_TRANSACTIONS_SUBSIDIARIES = bigquery.execute_single_DML(
    name='purge_TWH_STA_PALP_SALES_TRANSACTIONS_SUBSIDIARIES',
    sql=f"DELETE FROM `{PROJECT}.{PIPELINE_ALPHA_DATASET}.TWH_STA_PALP_SALES_TRANSACTIONS_SUBSIDIARIES` where true",
    retries=2,
    dag=filiales_part1
)

alimSteps = []
for f in filiales:
    filiale = filiales[f]
    s = gen_sourcing(f, filiale, filiales_part1)
    a = gen_alim(f, filiale, filiales_part1)

    if filiale['envoikrn'] and 'krn_source' in filiale:
        gen_krn(f, filiale, filiales_part1)

    if ENV == "PRD":
        d = gen_delete_source_files(f, filiale, filiales_part1)
        s >> purge_TWH_STA_PALP_SALES_TRANSACTIONS_SUBSIDIARIES >> a >> d
        alimSteps.append(d)
    else:
        s >> purge_TWH_STA_PALP_SALES_TRANSACTIONS_SUBSIDIARIES >> a
        alimSteps.append(a)

part_1_done = DummyOperator(task_id="part_1_done", dag=filiales_part1)
for x in alimSteps:
    x >> part_1_done

ctrlRg = gen_ctrl_rg(filiales_part2)

extract_steps = []

for f in filiales:
    filiale = filiales[f]
    e = gen_export_ctrl_rg(f, filiale, filiales_part2)
    ctrlRg >> e
    if 'extractsales_transactions' in filiale and filiale['extractsales_transactions']:
        e2 = gen_export(f, filiale, filiales_part2, e)
        extract_steps.append(e2)
    else:
        extract_steps.append(e)

part_2_done = DummyOperator(task_id="part_2_done", dag=filiales_part2)

for step in extract_steps:
    step >> part_2_done

pipeline_gamma = gen_pipeline_gamma(filiales_part3)

alim_filiales = gen_alim_filiales(filiales_part3, pipeline_gamma)

rejet_done = DummyOperator(
    task_id='pipeline_alpha_export_subsidiaries_rejets_referents_done',
    dag=filiales_part3,
    trigger_rule=TriggerRule.ALL_DONE
)

for f in filiales:
    filiale = filiales[f]
    rejet = gen_export_filiales_rejet_referents(f, filiale, filiales_part3)
    alim_filiales >> rejet >> rejet_done

purge_tempo = gen_purge_tempo(filiales_part3)

go_purge = DummyOperator(
    task_id='go_purge',
    dag=filiales_part3,
    trigger_rule=TriggerRule.ALL_SUCCESS
)

rejet_done >> go_purge

go_purge >> purge_tempo

rem_transform = gen_rem_transform(filiales_part3)

purge_tempo >> rem_transform

rem_export = gen_rem_export(filiales_part3, rem_transform)

rem_export >> gen_peroraison(filiales_part3)

run_part1 = ChildDagOperator(task_id="run_part1", dag_id="pipeline_alpha_subsidiaries_part1", dag=filiales_dag)
run_part2 = ChildDagOperator(task_id="run_part2", dag_id="pipeline_alpha_subsidiaries_part2", dag=filiales_dag)
run_part3 = ChildDagOperator(task_id="run_part3", dag_id="pipeline_alpha_subsidiaries_part3", dag=filiales_dag)

done = DummyOperator(
    task_id='client_transform_done',
    dag=filiales_dag
)

run_part1 >> run_part2 >> run_part3 >> done

mailing.mailing_alert_component(filiales_dag, run_part3, done, 'Filiale')
