from typing import (
    Optional,
)

import tzlocal

from pyspark.sql import (
    SparkSession,
    Window,
)

from pyspark.sql.types import (
    StructField,
    StructType,
    DoubleType,
    TimestampType,
    LongType,
    StringType,
)

import pyspark.sql.functions as func

import pyspark.sql


_spark = None


PySparkDataFrame = pyspark.sql.dataframe.DataFrame
PySparkSession = pyspark.sql.session.SparkSession


def _get_spark_session() -> PySparkSession:
    global _spark

    if _spark is None:
        _spark = SparkSession \
            .builder \
            .appName("Python Spark SQL basic example") \
            .config('spark.executor.memory', '12g') \
            .config('spark.driver.memory', '12g') \
            .config('spark.driver.maxResultSize', '0') \
            .getOrCreate()

    return _spark


def _ffill_column(data: PySparkDataFrame, column: str) -> PySparkDataFrame:
    w = Window.partitionBy('playerId') \
              .orderBy('unix_timestamp')\
              .rowsBetween(Window.unboundedPreceding, 0)
    result = data.withColumn(column, func.last(column, True).over(w))

    return result


def read_data(data_path: str,
              spark_session: Optional[PySparkSession] = None,
              input_format: str = 'json') -> PySparkDataFrame:
    spark_session = spark_session or _get_spark_session()
    schema = StructType([
        StructField('balance', DoubleType(), True),
        StructField('bet', DoubleType(), True),
        StructField('currencyCode', StringType(), True),
        StructField('deviceType', StringType(), True),
        StructField('gameId', LongType(), True),
        StructField('gameSessionId', LongType(), True),
        StructField('id', LongType(), True),
        StructField('operatorId', LongType(), True),
        StructField('playerId', LongType(), True),
        StructField('time', TimestampType(), True),
        StructField('win', DoubleType(), True),
    ])

    reader = getattr(_spark.read, input_format)
    all_data = reader(data_path, schema=schema)

    tz = tzlocal.get_localzone().zone
    utc_timestamp = func.unix_timestamp(func.from_utc_timestamp('time', tz))
    all_data = all_data.withColumn('unix_timestamp', utc_timestamp)

    all_data = _ffill_column(all_data, 'balance')

    return all_data


def _first_sessions(df: PySparkDataFrame) -> PySparkDataFrame:
    w = Window.partitionBy('playerId').orderBy('time')
    first_sessions = df.withColumn('tmp', func.row_number().over(w)) \
                       .select('playerId', 'gameSessionId')
    return first_sessions


def data_segment_first_session(df: PySparkDataFrame) -> PySparkDataFrame:
    first_sessions = _first_sessions(df)
    result = df.join(first_sessions, ['playerId', 'gameSessionId'])
    return result
