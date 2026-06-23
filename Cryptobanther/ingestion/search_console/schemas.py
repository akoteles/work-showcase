from google.cloud import bigquery

GSC_PERFORMANCE_SCHEMA = [
    bigquery.SchemaField("partition_date",  "DATE",      mode="REQUIRED"),
    bigquery.SchemaField("site_url",        "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("query",           "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("page",            "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("country",         "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("device",          "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("clicks",          "INTEGER",   mode="NULLABLE"),
    bigquery.SchemaField("impressions",     "INTEGER",   mode="NULLABLE"),
    bigquery.SchemaField("ctr",             "FLOAT64",   mode="NULLABLE"),
    bigquery.SchemaField("position",        "FLOAT64",   mode="NULLABLE"),
    bigquery.SchemaField("ingested_at",     "TIMESTAMP", mode="REQUIRED"),
]
