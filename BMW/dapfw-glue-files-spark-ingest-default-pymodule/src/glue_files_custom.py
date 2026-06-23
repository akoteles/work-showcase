from pyspark.sql import DataFrame, functions as F


def custom_files(
    *,
    job_params,
    table_name,
    df: DataFrame,
    spark_session,
    pseudonymizer_task,
    logger,
    job_run_id
) -> DataFrame:
    """ Custom code to be add here. """

    return df
