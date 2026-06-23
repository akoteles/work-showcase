import logging
from typing import Any, Dict
from unittest.mock import Mock

import pytest
from cdh_glue_prepared.generic_spark_prepared_job import GenericSparkPreparedJob
from cdh_glue_prepared.glue_comment_updater import GlueDescriptionUpdater
from cdh_glue_prepared.helpers import ReadWriter, MetricsPublisher
from pyspark.shell import spark

LOG = logging.getLogger(__name__)
SOURCE_DB = "source_db"
PREPARED_DB = "prepared_db"
SOURCE_TABLE = "source_table"
PREPARED_TABLE = "prepared_table"
TEST_DATAFRAME = spark.createDataFrame(
    [
        ("John", "Doe", 160, "1950", "06"),
        ("John", "Foe", 170, "1940", "12"),
        ("Albert", "Doe", 180, "1950", "01"),
        ("John", "Doe", 190, "1950", "01")
    ],
    ["first_name", "last_name", "height", "year_of_birth", "month_of_birth"]
)
PARTITION_COLUMNS = ["year_of_birth", "month_of_birth"]


@pytest.fixture()
def mock_read_writer():
    def mock_read(database, table, push_down_predicate, additional_options):
        if database == SOURCE_DB and table == SOURCE_TABLE:
            return TEST_DATAFRAME.filter(push_down_predicate) if push_down_predicate else TEST_DATAFRAME

    def get_partitions(database, table):
        if database == SOURCE_DB and table == SOURCE_TABLE:
            result = []
            for row in TEST_DATAFRAME.collect():
                partition = {col: row[col] for col in PARTITION_COLUMNS}
                if partition not in result:
                    result.append(partition)
            return result

    mock = Mock(autospec=ReadWriter)
    mock.read_table.side_effect = mock_read
    mock.get_partitions.side_effect = get_partitions
    return mock


@pytest.fixture()
def mock_metrics_publisher():
    return Mock(autospec=MetricsPublisher)


@pytest.fixture()
def mock_glue_description_updater():
    return Mock(autospec=GlueDescriptionUpdater)


def get_prepared_job(
        read_writer,
        metrics_publisher,
        glue_description_updater,
        table_setting: Dict[str, Any]
) -> GenericSparkPreparedJob:
    return GenericSparkPreparedJob(
        LOG,
        read_writer=read_writer,
        metrics_publisher=metrics_publisher,
        source_database=SOURCE_DB,
        prepared_database=PREPARED_DB,
        table_settings=[{"name": SOURCE_TABLE, "new_name": PREPARED_TABLE, **table_setting}],
        spark=spark,
        glue_description_updater=glue_description_updater,
        clear_cache=lambda: None,
        region='eu-west-1'
    )


def test_basic_copy(mock_read_writer, mock_metrics_publisher, mock_glue_description_updater):
    uut = get_prepared_job(mock_read_writer, None, mock_glue_description_updater, {})

    uut.run()

    assert_df_as_expected(mock_read_writer, TEST_DATAFRAME)


def test_copy_metrics(mock_read_writer, mock_metrics_publisher, mock_glue_description_updater):
    uut = get_prepared_job(mock_read_writer, mock_metrics_publisher, mock_glue_description_updater, {})

    uut.run()

    mock_metrics_publisher.publish_row_count.assert_called_once_with(PREPARED_TABLE, TEST_DATAFRAME.count())


def test_glue_description_updater_called(mock_read_writer, mock_metrics_publisher, mock_glue_description_updater):
    uut = get_prepared_job(
        mock_read_writer,
        mock_metrics_publisher,
        mock_glue_description_updater,
        {"table_description": "mildly interesting", "column_description_mapping": {"height": "unit: cm"}}
    )

    uut.run()

    mock_glue_description_updater.update_descriptions.assert_called_once_with(
        database=PREPARED_DB,
        table_name=PREPARED_TABLE,
        table_description="mildly interesting",
        column_description_mapping={"height": "unit: cm"}
    )


def test_load_most_recent_partition(mock_read_writer, mock_glue_description_updater):
    uut = get_prepared_job(
        mock_read_writer,
        None,
        mock_glue_description_updater,
        {
            "fetch_most_recent":
                [{"column": "year_of_birth", "format": "%Y"}, {"column": "month_of_birth", "format": "%m"}]
        }
    )

    uut.run()

    expected_df = spark.createDataFrame(
        [("John", "Doe", 160, "1950", "06")], ["first_name", "last_name", "height", "year_of_birth", "month_of_birth"]
    )
    assert_df_as_expected(mock_read_writer, expected_df)


def test_rename_columns(mock_read_writer, mock_glue_description_updater):
    uut = get_prepared_job(
        mock_read_writer,
        None,
        mock_glue_description_updater,
        {"rename_columns": {"first_name": "foo", "last_name": "bar"}}
    )

    uut.run()
    expected_df = spark.createDataFrame(
        [
            ("John", "Doe", 160, "1950", "06"),
            ("John", "Foe", 170, "1940", "12"),
            ("Albert", "Doe", 180, "1950", "01"),
            ("John", "Doe", 190, "1950", "01")
        ],
        ["foo", "bar", "height", "year_of_birth", "month_of_birth"]
    )
    assert_df_as_expected(mock_read_writer, expected_df)


def test_drop_column(mock_read_writer, mock_glue_description_updater):
    uut = get_prepared_job(
        mock_read_writer,
        None,
        mock_glue_description_updater,
        {"drop_columns": {"height", "month_of_birth"}}
    )

    uut.run()
    expected_df = spark.createDataFrame(
        [
            ("John", "Doe", "1950"),
            ("John", "Foe", "1940"),
            ("Albert", "Doe", "1950"),
            ("John", "Doe", "1950")
        ],
        ["first_name", "last_name", "year_of_birth"]
    )
    assert_df_as_expected(mock_read_writer, expected_df)


def test_consolidate(mock_read_writer, mock_glue_description_updater):
    uut = get_prepared_job(
        mock_read_writer,
        None,
        mock_glue_description_updater,
        {"consolidation_primary_keys": ["first_name", "last_name"], "consolidation_sort_key": "height"}
    )

    uut.run()
    expected_df = spark.createDataFrame(
        [
            ("John", "Foe", 170, "1940", "12"),
            ("Albert", "Doe", 180, "1950", "01"),
            ("John", "Doe", 190, "1950", "01")
        ],
        ["first_name", "last_name", "height", "year_of_birth", "month_of_birth"]
    )
    assert_df_as_expected(mock_read_writer, expected_df)


def test_rows_per_file(mock_read_writer, mock_glue_description_updater):
    uut = get_prepared_job(
        mock_read_writer,
        None,
        mock_glue_description_updater,
        {"rows_per_file": TEST_DATAFRAME.count() + 1}
    )

    uut.run()

    df = mock_read_writer.write_to_table.call_args_list[0][1]['df']
    assert df.rdd.getNumPartitions() == 1


def assert_df_as_expected(mock_read_writer, expected_df):
    write_calls = mock_read_writer.write_to_table.call_args_list
    assert len(write_calls) == 1
    assert write_calls[0][1]['target_db'] == PREPARED_DB
    assert write_calls[0][1]['target_table'] == PREPARED_TABLE
    assert_dataframes_are_equal(expected_df, write_calls[0][1]['df'])


def assert_dataframes_are_equal(df1, df2):
    assert set(df1.schema.fields) == set(df2.schema.fields)
    df2 = df2.select(*df1.columns)
    assert sorted(df1.collect()) == sorted(df2.collect())
    assert df1.subtract(df2).count() == 0
    assert df2.subtract(df1).count() == 0
