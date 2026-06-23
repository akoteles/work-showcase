import sys

from google.cloud import bigquery
from google.cloud.bigquery import WriteDisposition, CreateDisposition
from google.api_core.exceptions import BadRequest
import os
import secrets
import json

urls = os.getenv("URL").split(',')
dataset = os.getenv("DATASET")
table = os.getenv("TABLE")
project = os.getenv("PROJECT")
tmp_dataset = os.getenv("TMP_DATASET")
file_format = os.getenv("FORMAT", "AVRO")
separator = os.getenv("SEPARATOR", ",")
has_header = os.getenv("HAS_HEADER", "True").upper() == "TRUE"
truncate = os.getenv("TRUNCATE").upper() == "TRUE"
jagged_rows = os.getenv("JAGGED_ROWS", "True").upper() == "TRUE"
quoted_LF = os.getenv("QUOTED_LF").upper() == "TRUE"

temp_table1 = f"{project}.{tmp_dataset}.{table}_{secrets.token_hex(8)}"
temp_table2 = False

job_config = bigquery.LoadJobConfig()
job_config.write_disposition = WriteDisposition.WRITE_TRUNCATE
job_config.create_disposition = CreateDisposition.CREATE_IF_NEEDED
job_config.allow_jagged_rows = jagged_rows
job_config.allow_quoted_newlines = quoted_LF

if file_format == "AVRO":
    job_config.source_format = bigquery.SourceFormat.AVRO
elif file_format == "CSV":
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.field_delimiter = separator
    if not has_header:
        if not os.path.exists("/app/schema.json"):
            print("ERROR: skipping CSV headers and no schema")
            sys.exit(1)
        job_config.skip_leading_rows = 0
        job_config.autodetect = False
    else:
        job_config.skip_leading_rows = 1
        if not os.path.exists("/app/schema.json"):
            job_config.autodetect = True
else:
    print(f"Unknown format {file_format}")
    sys.exit(1)

if os.path.exists("/app/schema.json"):
    schema = []
    with open("/app/schema.json") as fd:
        schema_js = json.load(fd)
    for field_js in schema_js:
        schema.append(bigquery.SchemaField.from_api_repr(field_js))
    job_config.schema = schema

bq = bigquery.Client(project=project, location="EU")
print(f"Loading {urls} into temp table {temp_table1}")
print(job_config.to_api_repr())
job = bq.load_table_from_uri(urls, temp_table1,
                             job_config=job_config)
try:
    job.result()
except BadRequest as e:
    for e in job.errors:
        print('ERROR: {}'.format(e['message']))
    sys.exit(1)
try:
    job_config = bigquery.QueryJobConfig()
    if os.path.exists("/app/transform.sql"):
        temp_table2 = f"{project}.{tmp_dataset}.{table}_{secrets.token_hex(8)}"
        projection = []
        tmp_schema = bq.get_table(temp_table1).schema
        for field in tmp_schema:
            if field.field_type == "STRING":
                projection.append(f"trim({field.name}) as {field.name}")
            else:
                projection.append(f"{field.name}")
        sql = f"SELECT {','.join(projection)} FROM `{temp_table1}`"
        job_config.destination = temp_table2
        bq.query(sql, job_config=job_config).result()
        with open("/app/transform.sql") as fd:
            sql = fd.read()
        sql = sql.format(temp_table=temp_table2)
        job_config.destination = f"{project}.{dataset}.{table}"
        if truncate:
            job_config.write_disposition = WriteDisposition.WRITE_TRUNCATE
        else:
            job_config.write_disposition = WriteDisposition.WRITE_APPEND
        print(f"Inserting into {table} :{sql}")
        q = bq.query(sql, job_config=job_config)
        print(f"{q.result().total_rows} rows affected")
    else:
        projection = []
        tmp_schema = bq.get_table(temp_table1).schema
        for field in tmp_schema:
            if field.field_type == "STRING":
                projection.append(f"trim({field.name}) as {field.name}")
            else:
                projection.append(f"{field.name}")
        sql = f"SELECT {','.join(projection)} FROM `{temp_table1}`"
        job_config.destination = f"{project}.{dataset}.{table}"
        if truncate:
            job_config.write_disposition = WriteDisposition.WRITE_TRUNCATE
        else:
            job_config.write_disposition = WriteDisposition.WRITE_APPEND
        print(f"Inserting into {table} :{sql}")
        q = bq.query(sql, job_config=job_config)
        print(f"{q.result().total_rows} rows affected")
finally:
    print(f"Cleaning up temp table {temp_table1}")
    bq.delete_table(temp_table1, not_found_ok=True)
    if temp_table2:
        print(f"Cleaning up temp table {temp_table2}")
        bq.delete_table(temp_table1, not_found_ok=True)
