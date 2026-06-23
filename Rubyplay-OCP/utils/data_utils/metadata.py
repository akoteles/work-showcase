import copy
import datetime
import json

from typing import (
    NoReturn,
)

from pyspark.sql import Window

import pyspark.sql.functions as func


def history_end_timestamp(data):
    return data.select(func.max(func.col('unix_timestamp'))).collect()[0][0]


def numeric_meta(data, numeric_columns=('balance', 'bet', 'win')):
    numeric_columns_summaries = data.describe(*numeric_columns) \
                                    .toPandas() \
                                    .set_index('summary') \
                                    .drop('count') \
                                    .astype(float)
    numeric_columns_summaries = {
        column: numeric_columns_summaries[column].to_dict()
        for column in numeric_columns
    }

    return numeric_columns_summaries


def categorical_meta(data, categorical_columns=('operatorId', 'currencyCode',
                                                'deviceType', 'gameId')):
    result = {column: data.groupBy(column)
                          .count()
                          .toPandas()
                          .set_index(column)['count']
                          .to_dict()
              for column in categorical_columns}

    return result


def get_first_sessions_table(all_data):
    w = Window.partitionBy('playerId').orderBy('time')
    first_sessions = all_data.withColumn('tmp', func.row_number().over(w)) \
                             .where(func.col('tmp') == 1) \
                             .drop('tmp') \
                             .select('playerId', 'gameSessionId')
    return first_sessions


def get_first_sessions(all_data):
    first_sessions = get_first_sessions_table(all_data)
    return all_data.join(first_sessions, ['playerId', 'gameSessionId'])


def collect_metadata(data):
    first_sessions = get_first_sessions(data)

    metadata = {
        'end_of_history': history_end_timestamp(data),
        'all_data': {
            'numeric_stats': numeric_meta(data),
            'categorical_stats': categorical_meta(data),
        },
        'first_sessions': {
            'numeric_stats': numeric_meta(first_sessions),
            'categorical_stats': categorical_meta(first_sessions),
        },
    }

    return metadata


def dump_metadata(metadata: dict, file_name: str) -> NoReturn:
    with open(file_name, 'w') as f:
        json.dump(metadata, f)


def read_metadata(file_name: str) -> dict:
    with open(file_name) as f:
        meta = json.load(f)

    return meta
