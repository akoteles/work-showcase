import os
from airflow.contrib.operators.bigquery_operator import BigQueryOperator
from airflow.models import Variable, DAG
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta

from airflow.operators import K8SJobOperator


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
DATASET = Variable.get('COMMERCIAL_BIDDING_DATASET')
DATASET_AUD_CLIENT = Variable.get('COMMERCIAL_DATASET')
PROJECT = Variable.get('COMMERCIAL_PROJECT')
host_project = Variable.get('HOST_PROJECT')
host_cluster = Variable.get('HOST_CLUSTER')
location = Variable.get('LOCATION')
GS_BUCKET_NAME = Variable.get('COMMERCIAL_INPUT_BUCKET')
BIGQUERY_CONN = "bigquery_dcproc"

ENV = Variable.get('ENV')
schedule = None
if ENV == "prd":
    schedule = '0/10 4-22 * * *'

dag = DAG('commercial_bidding', default_args=default_args, schedule_interval=schedule)

SOURCING_FILES = [
    {
        "source_filename":  'stg_cmd_tr_jour.txt',
        "table_staging": "STG_CMD_TR_JOUR",
        "sql_delete_cmd": "DELETE_COMMANDES_VALIDES_BY_DAY_STG.sql",
        "sql_insert_cmd": "INSERT_COMMANDES_VALIDES_TR.sql",
        "table_cmd": "COMMANDES_VALIDES_TR",
        "table_ca": "CA_V",
        "table_top_j" : "TOP_10_JOUR_V",
        "table_top_s" : "TOP_10_SEMAINE_V"
    },
    {
        "source_filename":  'stg_cmd_tr_rp_jour.txt',
        "table_staging": "STG_CMD_TR_RP_JOUR",
        "sql_delete_cmd": "DELETE_COMMANDES_RP_BY_DAY_STG.sql",
        "sql_insert_cmd": "INSERT_COMMANDES_RP_TR.sql",
        "table_cmd": "COMMANDES_RP_TR",
        "table_ca": "CA_RP",
        "table_top_j": "TOP_10_JOUR_RP",
        "table_top_s": "TOP_10_SEMAINE_RP"
    }
]

done = DummyOperator(
    task_id='commercial_bidding_done',
    dag=dag
)

def load_file_to_bq(sourcefile, table):
    f = open("{}/commercial/commercial_bidding/yaml/commercial_bidding.yaml".format(DAG_FOLDER), mode="r", encoding="utf-8")
    descriptor = f.read()
    f.close()
    return K8SJobOperator(task_id='load_{table_id}_to_bq'.format(table_id=table),
                          location=location,
                          project_id=host_project,
                          cluster_name=host_cluster,
                          name='load_{table_id}_to_bq'.format(table_id=table),
                          gcp_conn_id='gcp_kub_runner',
                          namespace='composer',
                          descriptor=descriptor,
                          params={
                              'project': PROJECT,
                              'bucket': GS_BUCKET_NAME,
                              'dataset': DATASET,
                              'table_staging': table,
                              'source_filename': sourcefile,
                              'encoding': "ISO-8859-1"
                          },
                          timeout_s=60 * 15, dag=dag)

def delete_commandes_valides_jour(table, file_sql) :
    return  BigQueryOperator(
            task_id='delete_{table_id}_by_jour'.format(table_id=table),
            sql=str(open("{dag_folder}/commercial/commercial_bidding/sql/valide_rp/{filename}".format(dag_folder=DAG_FOLDER,
                                                             filename=file_sql), 'r').read()),
            write_disposition='WRITE_TRUNCATE',
            allow_large_results=True,
            use_legacy_sql=False,
            bigquery_conn_id=BIGQUERY_CONN,
            params={"project_id": PROJECT, "dataset_id": DATASET}.items(),
            dag=dag
        )

def insert_commande(table, file_sql):
    return BigQueryOperator(
        task_id='load_{table_id}'.format(table_id=table),
        sql=str(open("{dag_folder}/commercial/commercial_bidding/sql/valide_rp/{filename}".format(dag_folder=DAG_FOLDER,
                                                             filename=file_sql), 'r').read()),
        destination_dataset_table='{project_id}.{dataset}.{table_id}'
            .format(project_id=PROJECT, dataset=DATASET, table_id=table),
        create_disposition='CREATE_IF_NEEDED',
        write_disposition='WRITE_APPEND',
        allow_large_results=True,
        use_legacy_sql=False,
        bigquery_conn_id=BIGQUERY_CONN,
        params={"project_id": PROJECT, "dataset_id": DATASET}.items(),
        dag=dag
    )

def execute_sql_to_bq(table, file_sql):
    return BigQueryOperator(
        task_id='load_{table_id}'.format(table_id=table),
        sql=str(open("{dag_folder}/commercial/commercial_bidding/sql/valide_rp/{filename}".format(dag_folder=DAG_FOLDER,
                                                             filename=file_sql), 'r').read()),
        destination_dataset_table='{project_id}.{dataset}.{table_id}'
            .format(project_id=PROJECT, dataset=DATASET, table_id=table),
        create_disposition='CREATE_IF_NEEDED',
        write_disposition='WRITE_TRUNCATE',
        allow_large_results=True,
        use_legacy_sql=False,
        bigquery_conn_id=BIGQUERY_CONN,
        params={"project_id": PROJECT, "dataset_id": DATASET, "dataset_ntz": DATASET_AUD_CLIENT}.items(),
        dag=dag
    )

for info in SOURCING_FILES:
    source_filename = info['source_filename']
    table_sta = info['table_staging']
    sql_delete = info['sql_delete_cmd']
    sql = info['sql_insert_cmd']
    table_cmd = info['table_cmd']
    table_ca = info['table_ca']
    table_top_j = info['table_top_j']
    table_top_s = info['table_top_s']

    load_file_to_bq(source_filename, table_sta) >> \
    delete_commandes_valides_jour(table_cmd, sql_delete) >> \
    insert_commande(table_cmd, sql) >> \
    execute_sql_to_bq(table_ca, table_ca + ".sql") >> \
    execute_sql_to_bq(table_top_j, table_top_j + ".sql") >> \
    execute_sql_to_bq(table_top_s, table_top_s + ".sql") >> \
    done
