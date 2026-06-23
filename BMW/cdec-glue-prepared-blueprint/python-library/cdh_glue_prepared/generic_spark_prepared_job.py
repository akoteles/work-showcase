from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Tuple

from cdh_glue_prepared.glue_comment_updater import GlueDescriptionUpdater
from cdh_glue_prepared.helpers import ReadWriter, MetricsPublisher
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, dense_rank
from pyspark.sql.window import Window


class GenericSparkPreparedJob:
    def __init__(
            self,
            logger,
            read_writer: ReadWriter,
            metrics_publisher: Optional[MetricsPublisher],
            source_database: str,
            prepared_database: str,
            table_settings: List[Dict[str, Any]],
            spark: SparkSession,
            clear_cache: Callable[[], None],
            glue_description_updater: GlueDescriptionUpdater,
            region: str,
            connection_parameters: Optional[Dict[str, str]] = None
    ):
        self.logger = logger
        self.read_writer = read_writer
        self.metrics_publisher = metrics_publisher
        self.source_database = source_database
        self.prepared_database = prepared_database
        self.table_settings = table_settings
        self.spark = spark
        self.clear_cache = clear_cache
        self.glue_description_updater = glue_description_updater
        self.region = region
        self.connection_parameters = connection_parameters

    def run(self):
        self.logger.info("SparkPreparedJob, run")
        for table in self.table_settings:
            self.clear_cache()
            self.logger.info(f"SparkPreparedJob, Table: {table}")
            df, partition_read = self.load_table(
                table["name"],
                table.get("fetch_most_recent"),
                table.get("additional_options")
            )
            for drop_column in table.get("drop_columns", []):
                df = df.drop(drop_column)
            for old_name, new_name in table.get("rename_columns", {}).items():
                df = df.withColumnRenamed(old_name, new_name)
            df = self.repartition(df, table.get('repartition_columns'), table.get('repartition_num_partitions'))
            df = self.consolidate(df, table.get('consolidation_primary_keys'), table.get('consolidation_sort_key'))
            df = self.transform(table, df, partition_read)
            self.save_table(table, df)
            self.glue_description_updater.update_descriptions(
                database=self.prepared_database,
                table_name=table.get("new_name", table["name"]),
                table_description=table.get("table_description", ""),
                column_description_mapping=table.get("column_description_mapping", {})
            )

        self.logger.info("SparkPreparedJob, run completed!")

    def consolidate(self, df: DataFrame, primary_keys: Optional[List[str]], sort_key: Optional[str]) -> DataFrame:
        if primary_keys and sort_key:
            window = Window.partitionBy(*[col(column_name) for column_name in primary_keys]).orderBy(
                col(sort_key).desc()
            )
            df = df.withColumn("_tmp_rank", dense_rank().over(window))
            df = df.filter(col("_tmp_rank") == 1).drop("_tmp_rank")
        return df

    def transform(self, table: Dict[str, Any], df: DataFrame, partition: Optional[Dict[str, str]] = None) -> DataFrame:
        return df

    def load_table(
            self,
            glue_table_name: str,
            fetch_most_recent: Optional[List[Dict[str, str]]] = None,
            additional_options: Optional[Dict[str, Any]] = None,
            glue_database: Optional[str] = None
    ) -> Tuple[DataFrame, Optional[Dict[str, Any]]]:
        glue_database = glue_database or self.source_database
        partition_to_read_from = None
        if fetch_most_recent:
            partition_to_read_from = self.get_most_recent_partition(glue_database, glue_table_name, fetch_most_recent)

        df = self.load_from_glue(glue_database, glue_table_name, partition_to_read_from, additional_options)
        return df, partition_to_read_from

    def load_from_glue(
            self,
            database: str,
            table_name: str,
            partition: Optional[Dict[str, str]] = None,
            additional_options: Optional[Dict[str, Any]] = None
    ) -> DataFrame:
        push_down_predicate = ""
        push_down_info = ""
        if partition:
            push_down_predicate = self.get_pushdown_predicate(partition)
            push_down_info = f"using pushdown predicate '{push_down_predicate}'"
        self.logger.info(
            f"Reading from glue table {database}.{table_name} {push_down_info}"
        )
        return self.read_writer.read_table(database, table_name, push_down_predicate, additional_options)

    def repartition(self, df: DataFrame, columns: Optional[List[str]], num_partitions: Optional[int]) -> DataFrame:
        if columns and num_partitions:
            df = df.repartition(num_partitions, *[col(column_name) for column_name in columns])
        elif columns:
            df = df.repartition(*[col(column_name) for column_name in columns])
        elif num_partitions:
            df = df.repartition(num_partitions)
        return df

    def save_table(self, table: Dict[str, Any], df: DataFrame):
        count = None
        if self._need_row_count(table):
            df = df.cache()
            count = df.count()
        new_table_name = table.get("new_name", table["name"])
        self._write_table(df, settings=table, save_as=new_table_name, number_of_rows=count)
        if self.metrics_publisher:
            self.metrics_publisher.publish_row_count(new_table_name, count)

    def _write_table(self, df: DataFrame, settings: Dict[str, Any], save_as: str, number_of_rows: Optional[int]):
        if number_of_rows == 0:
            self.logger.warn(f"Gathered zero rows for table {save_as}")
            return
        if number_of_rows is None and len(df.columns) == 0:
            self.logger.warn(f"Gathered zero columns for table {save_as}")
            return
        if "rows_per_file" in settings:
            df = df.coalesce(int(number_of_rows / settings["rows_per_file"]) + 1)

        self.logger.info(f"Saving to table {self.prepared_database}.{save_as}")
        self.read_writer.write_to_table(
            df=df,
            target_db=self.prepared_database,
            target_table=save_as,
            partition_by=settings.get('partition_by', []),
            write_mode=settings.get('write_mode', 'overwrite'),
            partition_overwrite_mode=settings.get('partition_overwrite_mode'),
            write_format=settings.get('write_format', 'parquet')
        )

    def _need_row_count(self, table_settings: Dict[str, Any]) -> bool:
        return bool(self.metrics_publisher) or ("rows_per_file" in table_settings)

    def get_most_recent_partition(self, database: str, table_name: str, fetch_most_recent: List[Dict[str, str]]):
        def parse_partition(partition: Dict[str, str]):
            return [datetime.strptime(partition[entry['column']], entry['format']) for entry in fetch_most_recent]

        partitions = self.read_writer.get_partitions(database, table_name)
        try:
            return max(partitions, key=parse_partition)
        except ValueError:
            self.logger.info(f"No partitions found for table '{database}'.'{table_name}'. Pushdown cannot be applied.")

    def get_pushdown_predicate(self, partition: Dict[str, str]):
        return " AND ".join(f"{column}=='{value}'" for column, value in partition.items())
