import base64
import json

from cdh_glue_prepared.glue_comment_updater import GlueDescriptionUpdater
from cdh_glue_prepared.glue_job_context import GlueJobContext
from cdh_glue_prepared.helpers import MetricsPublisher, ReadWriter
from cdh_glue_prepared.spark_prepared_job import SparkPreparedJob


def main():
    with GlueJobContext() as job_context:
        read_writer = ReadWriter(job_context.glue_context, job_context.args['s3_output_bucket'])
        metrics_publisher = None
        if "metric_namespace" in job_context.args:
            metrics_publisher = MetricsPublisher(
                metric_namespace=job_context.args['metric_namespace'],
                job_name=job_context.job_name,
                region=job_context.args['aws_region']
            )
        spark_prepared_job = SparkPreparedJob(
            logger=job_context.logger,
            read_writer=read_writer,
            metrics_publisher=metrics_publisher,
            source_database=job_context.args['source_glue_database'],
            prepared_database=job_context.args['prepared_glue_database'],
            table_settings=json.loads(base64.b64decode(job_context.args['table_settings'])),
            spark=job_context.glue_context.spark_session,
            clear_cache=job_context.glue_context.clearCache,
            glue_description_updater=GlueDescriptionUpdater(job_context.logger, job_context.args['aws_region']),
            region=job_context.args['aws_region'],
            connection_parameters=job_context.args.get('connection_parameters')
        )
        spark_prepared_job.run()


if __name__ == '__main__':
    main()
