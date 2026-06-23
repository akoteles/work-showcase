tests_get_configuration = [
    (
        [
            {
              "columns": [
                {
                  "name": "col1",
                  "type": "string"
                },
                {
                  "name": "beschreibung",
                  "type": "string"
                },
                {
                  "name": "id",
                  "type": "string"
                },
                {
                  "name": "vorgang",
                  "type": "string"
                },
                {
                  "name": "chronos_id",
                  "type": "string"
                },
                {
                  "name": "col6",
                  "type": "string"
                },
                {
                  "name": "col7",
                  "type": "string"
                }
              ],
              "delimiter": ";",
              "escape": "\\\\",
              "header": "false",
              "infer_schema": "false",
              "multiline": "true",
              "quote": "'",
              "table_name": "te_teste_5"
            }
        ],
        {
            "partitions": [{"p_ingest_day": "%Y-%m-%d"}, {"p_ingest_hour": "%H"}],
            "table_name": "te_teste_5",
            "aws_partition": "aws",
            "aws_region": "eu-west-1"
        },
        {
            "config_name_type_prefix": "_files_ingest",
            "sts_endpoint": "https://sts.eu-west-1.amazonaws.com"
        }
    )
]

tests_connections = [
    ("GLUE"),
    ("FARGATE")
]

tests_get_logger = [
    (
        [
            {
                "table_name": "te_logs",
                "delimiter": ";",
                "header": "false",
                "infer_schema": "true",
                "encoding": "UTF-8",
            }
        ],
        "files_ingest",
        "s3://files-ingest-test",
        "s3://files-ingest-test-raw"
    ),
]

test_config_name_type = [
    ({"target":
        {
                "tables_raw_folder_location": "tables_raw_folder_location",
        }
    },
    "tables_raw_folder_location"),
    ({
        "raw_layer_config_type": "raw_layer_config_type",
        "target": {
            "test": "none"
        }
    }, "config_name_raw_layer_config_type"),
    ({
                "target": {
                    "test": "none"
                }
    }, "config_name_files_ingest")
]
