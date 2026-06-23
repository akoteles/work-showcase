from __future__ import annotations
from typing import List
from google.cloud import bigquery

MYSQL_TO_BQ_TYPE_MAP = {
    "int": "INTEGER",
    "tinyint": "INTEGER",
    "smallint": "INTEGER",
    "mediumint": "INTEGER",
    "bigint": "INTEGER",
    "float": "FLOAT64",
    "double": "FLOAT64",
    "decimal": "FLOAT64",
    "numeric": "FLOAT64",
    "char": "STRING",
    "varchar": "STRING",
    "tinytext": "STRING",
    "text": "STRING",
    "mediumtext": "STRING",
    "longtext": "STRING",
    "enum": "STRING",
    "set": "STRING",
    "date": "DATE",
    "datetime": "TIMESTAMP",
    "timestamp": "TIMESTAMP",
    "time": "STRING",
    "year": "INTEGER",
    "boolean": "BOOLEAN",
    "bool": "BOOLEAN",
    "bit": "INTEGER",
    "binary": "BYTES",
    "varbinary": "BYTES",
    "blob": "BYTES",
    "tinyblob": "BYTES",
    "mediumblob": "BYTES",
    "longblob": "BYTES",
    "json": "STRING",
}


def mysql_type_to_bq_type(mysql_type: str) -> str:
    base_type = mysql_type.lower().split("(")[0].strip()
    return MYSQL_TO_BQ_TYPE_MAP.get(base_type, "STRING")


def build_bq_schema_from_mysql(columns: List[dict]) -> List[bigquery.SchemaField]:
    fields = []
    for col in columns:
        col_name = col["COLUMN_NAME"]
        col_type = col["DATA_TYPE"]
        is_nullable = col.get("IS_NULLABLE", "YES").upper() == "YES"
        bq_type = mysql_type_to_bq_type(col_type)
        mode = "NULLABLE" if is_nullable else "REQUIRED"
        fields.append(bigquery.SchemaField(col_name, bq_type, mode=mode))
    return fields
