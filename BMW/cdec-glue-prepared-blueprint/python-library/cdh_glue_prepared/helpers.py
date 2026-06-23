from datetime import datetime
from typing import Optional, List, Dict, Any

import boto3
from pyspark.sql import DataFrame


class ReadWriter:
    def __init__(self, glue_context, output_bucket):
        self.glue_context = glue_context
        self.output_bucket = output_bucket

    def write_to_table(
            self,
            df: DataFrame,
            target_db: str,
            target_table: str,
            partition_by: Optional[List[str]] = None,
            write_mode: str = "overwrite",
            partition_overwrite_mode: Optional[str] = None,
            write_format: str = "parquet"
    ):
        default_partition_overwrite_mode = self.glue_context.getConf('spark.sql.sources.partitionOverwriteMode')
        self.glue_context.setConf("spark.sql.sources.partitionOverwriteMode", partition_overwrite_mode or default_partition_overwrite_mode)
        (
            df.write
                .option("path", self._get_output_path(target_table))
                .partitionBy(partition_by or [])
                .mode(write_mode)
                .saveAsTable(name=f"{target_db}.{target_table}", format=write_format)
        )
        self.glue_context.setConf('spark.sql.sources.partitionOverwriteMode', default_partition_overwrite_mode)

    def _get_output_path(self, table_name: str):
        return f"s3://{self.output_bucket}/{table_name}"

    def read_table(
            self,
            database: str,
            table: str,
            push_down_predicate: str = "",
            additional_options: Optional[Dict[str, Any]] = None
    ) -> DataFrame:
        dynamic_frame = self.glue_context.create_dynamic_frame_from_catalog(
            database=database,
            table_name=table,
            push_down_predicate=push_down_predicate,
            additional_options=additional_options or {}
        )
        return dynamic_frame.resolveChoice(
            choice="MATCH_CATALOG",
            database=database,
            table_name=table
        ).toDF()

    def get_partitions(self, database: str, table_name: str) -> List[Dict[str, str]]:
        partition_rows = self.glue_context.spark_session.sql(f"SHOW PARTITIONS `{database}`.`{table_name}`").collect()
        partition_expressions = [row[0].split("/") for row in partition_rows]
        return [
            {
                expression.split("=")[0]: expression.split("=")[1] for expression in partition
            }
            for partition in partition_expressions
        ]


class MetricsPublisher:
    def __init__(self, metric_namespace: str, job_name: str, region: str):
        self.metric_namespace = metric_namespace
        self.job_name = job_name
        self.region = region
        self.cloudwatch = None

    def publish_row_count(self, table_name: str, row_count: int):
        if self.cloudwatch is None:
            self.cloudwatch = boto3.client("cloudwatch", region_name=self.region)
        self.cloudwatch.put_metric_data(
            Namespace=self.metric_namespace,
            MetricData=[
                {
                    "MetricName": "Number of rows",
                    "Dimensions": [
                        {"Name": "table_name", "Value": table_name},
                        {"Name": "full_job_name", "Value": self.job_name},
                    ],
                    "Timestamp": datetime.now(),
                    "Value": row_count,
                    "Unit": "Count",
                },
            ]
        )
