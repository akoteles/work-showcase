import os
import re
from google.cloud import bigquery

PROJECT = os.getenv("project_id")
PIPELINE_ALPHA_DATASET = os.getenv("dataset_id")
TMP_DATASET = os.getenv("tmp_dataset")
code_filiale = os.getenv("code_filiale")
export_bucket = os.getenv("export_bucket")
date_traitement = os.getenv("date_traitement")

print("Debut traitement")
print(code_filiale)

with open("/app/SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_REJETS_DEFINITIFS_RECUP_DA_EVENT.sql") as fd:
    query = fd.read()

client = bigquery.Client(project=PROJECT)
query_job = client.query(query)
tuples = query_job.result()

for item in tuples:
    da_event = item[0]
    print(str(da_event))

    table_to_export = 'FILILIALES_REJET_REFERENT_%s_%s' % (code_filiale, da_event.strftime("%Y%m%d"))
    export_file = 'PALP_TXT_REJETS_REFERENT_%s_%s' % (code_filiale, da_event.strftime("%Y%m%d"))

    dataset_ref = client.dataset(TMP_DATASET, project=PROJECT)
    table_ref = dataset_ref.table(table_to_export)
    job_config = bigquery.QueryJobConfig()
    job_config.destination = table_ref
    sql_final = open('/app/SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_REJETS_DEFINITIFS_AVEC_EN_TETES.sql').read()
    sql_final = sql_final.replace('$DA_EVENT', str(da_event))
    query_job = client.query(sql_final, location='EU', job_config=job_config)
    query_job.result()

    export_gcs_obj = "%s/subsidiaries_rejet_referent/%s.%s" % (export_bucket, export_file, 'CSV')
    destination_uri = "gs://{}".format(export_gcs_obj)
    job_conf = bigquery.ExtractJobConfig()
    job_conf.field_delimiter = ';'

    extract_job = client.extract_table(
        table_ref,
        destination_uri,
        location="EU",
        job_config=job_conf
    )
    extract_job.result()
    client.delete_table(table_ref)
    print("Fichiers deposés")

print("Fin de traitement")
