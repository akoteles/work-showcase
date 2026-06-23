import json

from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.context import SQLContext

from logging_framework.pipeline_fw_logging_class import PipelineFwLogger
from pipeline_fw_files_phase2.files_spark_ingest_job import FilesSparkIngestJob
from pipeline_fw_files_phase2.spark_ingest_job_configuration import (
    SparkIngestJobConfiguration,
)
from pipeline_fw_files_phase2.entities import IngestTarget, PartitionsConfig
from pipeline_fw_utils.parse_job_arguments import parse_arguments_from_job, JobType
from glue_files_custom import custom_files


class Connections:
    def __init__(self):
        self.sc = None
        self.spark_session = None
        self.sql_context = None

    def initialize(self, job_type, kms_key_arn):
        conf = (
            SparkConf()
            .set("spark.sql.parquet.writeLegacyFormat", "true")
            .set("spark.hadoop.fs.s3.enableServerSideEncryption", "true")
            .set("spark.hadoop.fs.s3.serverSideEncryption.kms.keyId", kms_key_arn,)
            .set("fs.s3.canned.acl", "BucketOwnerFullControl")
        )
        self.sc = SparkContext(conf=conf)

        if job_type == JobType.GLUE:
            from awsglue.context import GlueContext

            self.glue_context = GlueContext(self.sc)
            self.spark_session = self.glue_context.spark_session
        elif job_type == JobType.FARGATE:
            self.spark_session = SparkSession(self.sc)

        self.sql_context = SQLContext(
            self.spark_session.sparkContext, self.spark_session
        )


def get_configuration(spark_connection, args, job_params):
    region = job_params["target"]["aws_region"]
    config_name = job_params["config_name"]

    table_name = args["table_name"]
    table_config = next(
        item for item in job_params["table_config"] if item["table_name"] == table_name
    )

    config_name_type = get_config_name_type(config_name, job_params)

    sts_endpoint = (
        "https://sts.{}.amazonaws.com.cn".format(region)
        if args["aws_partition"] == "aws-cn"
        else "https://sts.{}.amazonaws.com".format(region)
    )

    dpu_count = job_params["dpu_count"]

    target = job_params["target"]
    raw_s3_output_path = (
        target["raw_s3_output_path"] if "raw_s3_output_path" in target else None
    )

    s3_output_path = target["s3_output_path"]
    if s3_output_path[-1] != "/":
        s3_output_path = f"{s3_output_path}/"

    glue_output_db = target["glue_output_db"]

    use_hour = False
    p_ingest_hour_name = None
    p_ingest_hour_format = None
    p_ingest_day_name = "p_ingest_day"
    p_ingest_day_format = "%Y-%m-%d"
    p_ingest_full_format = p_ingest_day_format

    if "partitions" in job_params:
        if len(job_params["partitions"]) == 1:
            p_ingest_day_name, p_ingest_day_format = list(
                job_params["partitions"][0].items()
            )[0]
            p_ingest_full_format = p_ingest_day_format
        elif len(job_params["partitions"]) == 2:
            use_hour = True
            p_ingest_day_name, p_ingest_day_format = list(
                job_params["partitions"][0].items()
            )[0]
            p_ingest_hour_name, p_ingest_hour_format = list(
                job_params["partitions"][1].items()
            )[0]
            p_ingest_full_format = p_ingest_day_format + p_ingest_hour_format

    return SparkIngestJobConfiguration(
        job_params=job_params,
        job_run_id=args["JOB_RUN_ID"],
        table_config=table_config,
        config_name_type=config_name_type,
        sts_endpoint=sts_endpoint,
        target=IngestTarget(raw_s3_output_path, s3_output_path, glue_output_db, region),
        dpu_count=dpu_count,
        table_name=table_name,
        spark_session=spark_connection.spark_session,
        sql_context=spark_connection.sql_context,
        pseudonymizer_settings=job_params.get("pseudonymizer_settings"),
        pseudonymizer_parallelism=job_params.get("pseudonymizer_parallelism"),
        partitions_config=PartitionsConfig(
            p_ingest_day_name,
            p_ingest_day_format,
            p_ingest_hour_format,
            p_ingest_full_format,
            p_ingest_hour_name,
            use_hour,
        ),
    )


def get_config_name_type(config_name, job_params):
    if (
        "tables_raw_folder_location" in job_params["target"]
    ):
        config_name_type = f"{job_params['target']['tables_raw_folder_location']}".strip(
            "/"
        )
    elif "raw_layer_config_type" in job_params:
        config_name_type = f"{config_name}_{job_params['raw_layer_config_type']}"
    else:
        config_name_type = f"{config_name}_files_ingest"
    return config_name_type


def get_logger(args, job_params, region):
    logging_lvl = job_params["logging_lvl"]
    log_group = "pipeline_fw_log_group"

    log_stream = f'{job_params["config_name"]}_{job_params["config_type"]}_{args["execution_name"]}'

    return PipelineFwLogger(
        log_group, log_stream, logging_lvl=logging_lvl, region_name=region
    )


class CustomFilesSparkIngestJob(FilesSparkIngestJob):
    def custom_files(
        self,
        *,
        job_params,
        table_name,
        df,
        spark_session,
        pseudonymizer_task,
        logger,
        job_run_id,
    ):
        return custom_files(
            job_params=job_params,
            table_name=table_name,
            df=df,
            spark_session=spark_session,
            pseudonymizer_task=pseudonymizer_task,
            logger=logger,
            job_run_id=job_run_id,
        )


def main():
    args, job_type = parse_arguments_from_job()

    job_params = json.loads(args["job_params"])
    region = job_params["target"]["aws_region"]

    if job_type == JobType.FARGATE:
        job_params["pseudonymizer_settings"]["deperso_proxies"] = {
            "http": "http://proxy:8080",
            "https": "http://proxy:8080",
        }

    logger = get_logger(args, job_params, region)
    connections = Connections()
    connections.initialize(job_type, job_params["target"]["kms_key_arn"])
    configuration = get_configuration(connections, args, job_params)

    try:
        if job_type == JobType.GLUE:
            from awsglue.job import Job

            job = Job(connections.glue_context)
            job.init(args["JOB_NAME"], args)

        files_ingest_job = CustomFilesSparkIngestJob(configuration, logger)
        files_ingest_job.run()

        if job_type == JobType.GLUE:
            job.commit()
    except Exception as e:
        logger.log(
            "f003",
            job_error=str(e),
            table_name=configuration.table_name,
            job_run_id=configuration.job_run_id,
        )
        raise


if __name__ == "__main__":
    main()
