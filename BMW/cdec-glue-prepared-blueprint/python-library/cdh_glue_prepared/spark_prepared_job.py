from typing import Dict, Any, Optional

from cdh_glue_prepared.generic_spark_prepared_job import GenericSparkPreparedJob
from pyspark.sql import DataFrame

"""
  The main method of the GlueJob will call the method `transform` of this class `SparkPreparedJob` - once for each
  table - and pass in the table settings `table` defined in the terraform variable `job_settings`, the Pyspark
  DataFrame `df` containing the data of the corresponding table and the partition which it was read from, if
  the parameter `fetch_most_recent` was configured (`None` otherwise).
  Implement a custom class `SparkPreparedJob` which inherits from `GenericSparkPreparedJob` and the method
  `transform` to add a customized data transformation step.

  Then, pass the following variable to the terraform module

    spark_transformation_script = "path/to/my_spark_script.py",

  where the python file `my_spark_script.py` contains your implementation of the class `SparkPreparedJob` as well as
  the import statement `from generic_spark_prepared_job import GenericSparkPreparedJob`.

"""


class SparkPreparedJob(GenericSparkPreparedJob):
    def transform(self, table: Dict[str, Any], df: DataFrame, partition: Optional[Dict[str, str]] = None) -> DataFrame:
        return df
