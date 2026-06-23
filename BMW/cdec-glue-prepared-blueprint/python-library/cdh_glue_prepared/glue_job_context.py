import base64
import json
import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext

ARGUMENTS = [
    'JOB_NAME',
    'source_glue_database',
    'prepared_glue_database',
    's3_output_bucket',
    'aws_region',
    'kms_key_arn',
    'table_settings',
]

OPTIONAL_ARGUMENTS = [
    "metric_namespace",
    "connection_parameters"
]

for argument in OPTIONAL_ARGUMENTS:
    if f"--{argument}" in sys.argv:
        ARGUMENTS.append(argument)


class GlueJobContext:
    def __init__(self):
        self.args = getResolvedOptions(
            sys.argv,
            ARGUMENTS
        )
        if self.args.get('connection_parameters'):
            self.args['connection_parameters'] = json.loads(base64.b64decode(self.args['connection_parameters']))
        self.job_name = self.args['JOB_NAME']

    def _init_glue_context(self):
        self._sc = SparkContext.getOrCreate()
        self._sc._jsc.hadoopConfiguration().set('fs.s3.enableServerSideEncryption', 'true')
        self._sc._jsc.hadoopConfiguration().set('fs.s3.serverSideEncryption.kms.keyId', self.args['kms_key_arn'])
        self._sc._jsc.hadoopConfiguration().set('fs.s3.canned.acl', 'BucketOwnerFullControl')
        self.glue_context = GlueContext(self._sc)
        self.glue_context.setConf('spark.sql.parquet.writeLegacyFormat', 'true')
        self.logger = self.glue_context.get_logger()

    def __enter__(self):
        self._init_glue_context()
        self.job = Job(self.glue_context)
        self.job.init(self.job_name, self.args)
        self.logger.info(f"Running job {self.job_name} with arguments {self.args}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.job.commit()
        self.logger.info(f"Job {self.job_name} complete")
