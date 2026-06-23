import json
import pytest
from unittest.mock import MagicMock, patch, ANY
from . import test_data as td


def job_params_ops(table_config, aws_region, raw_layer_config_type, s3_output_path, raw_s3_output_path, partitions):
    return json.dumps(
        dict(
            logging_lvl="logging_lvl",
            config_name="files_client_pipeline",
            config_type="files_spark_ingest",
            raw_layer_config_type=raw_layer_config_type,
            num_rows_per_file=1000000,
            etl_job="files_spark_default_job",
            partitions=partitions,
            job_settings=dict(cron="00 * * * ? 2199", aws_region=aws_region),
            pseudonymizer_settings=dict(
                endpoint="endpoint",
                region="region",
                session_name="session_name",
                api_key="api_key",
                role="role",
            ),
            pseudonymizer_parallelism=2,
            dpu_count=2,
            target=dict(
                s3_output_path=s3_output_path,
                raw_s3_output_path=raw_s3_output_path,
                target_role_arn="arn:aws:iam::123456789012:role/pipeline_fw_glue_execution_pipeline_fw-ingest-default_eu-west-1",
                target_role_external_id="id",
                aws_region=aws_region,
                kms_key_arn="arn:aws:kms:eu-west-1:123456789012:key/eb739651-bf63-4545-a80a-82dfeaa28071",
                glue_output_db="files_ingest_test",
            ),
            table_config=table_config,
        )
    )


def job_params(table_config, raw_layer_config_type, s3_output_path, raw_s3_output_path):
    return json.dumps(
        dict(
            logging_lvl="logging_lvl",
            config_name="files_client_pipeline",
            config_type="files_spark_ingest",
            raw_layer_config_type=raw_layer_config_type,
            num_rows_per_file=1000000,
            etl_job="files_spark_default_job",
            job_settings=dict(cron="00 * * * ? 2199", aws_region="eu-west-1"),
            pseudonymizer_settings=dict(
                endpoint="endpoint",
                region="region",
                session_name="session_name",
                api_key="api_key",
                role="role",
            ),
            pseudonymizer_parallelism=2,
            dpu_count=2,
            target=dict(
                s3_output_path=s3_output_path,
                raw_s3_output_path=raw_s3_output_path,
                target_role_arn="arn:aws:iam::123456789012:role/pipeline_fw_glue_execution_pipeline_fw-ingest-default_eu-west-1",
                target_role_external_id="id",
                aws_region="eu-west-1",
                kms_key_arn="arn:aws:kms:eu-west-1:123456789012:key/eb739651-bf63-4545-a80a-82dfeaa28071",
                glue_output_db="files_ingest_test",
            ),
            table_config=table_config,
        )
    )


awsglue = MagicMock()
awsglue_context = MagicMock()
awsglue_job = MagicMock()
awsglue_transforms = MagicMock()
awsglue_utils = MagicMock()
awsglue_utils.getResolvedOptions.return_value = {
    "job_params": job_params(
        [
            {
                "table_name": "te_logs",
                "delimiter": ";",
                "header": "false",
                "infer_schema": "true",
                "encoding": "UTF-8",
            }
        ],
        "files_ingest",
        "s3://files-ingest-test",
        "s3://files-ingest-test-raw"
    ),
    "JOB_NAME": "JOB_NAME",
    "table_name": "te_logs",
    "JOB_RUN_ID": "JOB_RUN_ID",
    "execution_name": "execution_name",
    "aws_partition": "aws"
}


@pytest.fixture(scope='function')
def sys_modules():
    with patch.dict(
            "sys.modules",
            {
                "awsglue": awsglue,
                "awsglue.context": awsglue_context,
                "awsglue.job": awsglue_job,
                "awsglue.transforms": awsglue_transforms,
                "awsglue.utils": awsglue_utils,
                "cdh_lambda": MagicMock(),
                "cdh_lambda.deperso": MagicMock(),
                "pseudonymize": MagicMock(),
                "glue_files_custom": MagicMock()
            }
    ):
        yield


@pytest.mark.parametrize("table_config,input_data,expected", td.tests_get_configuration)
def test_get_configuration_with_partitions(table_config, input_data, expected, sys_modules):
    partitions = input_data["partitions"]

    params = job_params_ops(
        table_config,
        input_data["aws_region"],
        "files_ingest",
        "s3://files-ingest-test",
        "s3://files-ingest-test-raw",
        partitions
    )

    awsglue_utils.getResolvedOptions.return_value = {
        "job_params": params,
        "JOB_NAME": "JOB_NAME",
        "table_name": input_data["table_name"],
        "aws_partition": input_data["aws_partition"],
        "JOB_RUN_ID": "JOB_RUN_ID",
        "execution_name": "execution_name"
    }

    json_job_params = json.loads(params)

    from src.files_spark_ingest_default import get_configuration
    configuration = get_configuration(MagicMock(), awsglue_utils.getResolvedOptions(), json_job_params)

    assert configuration.table_name == input_data["table_name"]
    assert configuration.config_name_type == f'{json_job_params["config_name"]}{expected["config_name_type_prefix"]}'
    assert configuration.sts_endpoint == expected["sts_endpoint"]

    if len(partitions) > 0:
        ingest_day = partitions[0]
        ingest_day_name, ingest_day_format = list(ingest_day.items())[0]
        assert ingest_day_name == configuration.partitions_config.ingest_day_name
        assert ingest_day_format == configuration.partitions_config.ingest_day_format

    if len(partitions) == 2:
        ingest_day = partitions[1]
        ingest_hour_name, ingest_hour_format = list(ingest_day.items())[0]
        assert ingest_hour_name == configuration.partitions_config.ingest_hour_name
        assert ingest_hour_format == configuration.partitions_config.ingest_hour_format
        assert configuration.partitions_config.use_hour

@patch("logging_framework.pipeline_fw_logging_class.PipelineFwLogger")
def test_get_logger(pipeline_fw_logger, sys_modules):
    args = awsglue_utils.getResolvedOptions()
    job_params_json = json.loads(args["job_params"])
    region = job_params_json["target"]["aws_region"]

    from src.files_spark_ingest_default import get_logger
    get_logger(args, job_params_json, region)
    pipeline_fw_logger.assert_called_with(
        'pipeline_fw_log_group',
        'files_client_pipeline_files_spark_ingest_execution_name',
        region_name=job_params_json['target']['aws_region'],
        logging_lvl=job_params_json['logging_lvl']
    )


@patch("pyspark.conf.SparkConf")
@patch("pyspark.context.SparkContext")
@patch("pyspark.sql.context.SQLContext")
@pytest.mark.parametrize("job_type", td.tests_connections)
def test_connections(sql_context, spark_context, spark_conf, job_type, sys_modules):
    from src.files_spark_ingest_default import Connections, JobType
    job_config = json.loads(awsglue_utils.getResolvedOptions()['job_params'])
    job_type = JobType[job_type]
    connections = Connections()
    connections.initialize(job_type, job_config["target"]["kms_key_arn"])

    spark_conf().set.assert_any_call("spark.sql.parquet.writeLegacyFormat", "true")
    spark_conf().set().set.assert_any_call("spark.hadoop.fs.s3.enableServerSideEncryption", "true")
    spark_conf().set().set().set('spark.hadoop.fs.s3.serverSideEncryption.kms.keyId',
                                 job_config['target']['kms_key_arn']),
    spark_conf().set().set().set().set.assert_any_call("fs.s3.canned.acl", "BucketOwnerFullControl")

    if job_type == JobType.GLUE:
        glue_context = awsglue_context.GlueContext()
        sql_context.assert_called_with(glue_context.spark_session.sparkContext, glue_context.spark_session)
    else:
        spark_context._jvm.SparkSession().sqlContext().called


@patch("src.files_spark_ingest_default.get_logger")
@patch("src.files_spark_ingest_default.get_configuration")
@patch("src.files_spark_ingest_default.Connections")
@patch("src.files_spark_ingest_default.CustomFilesSparkIngestJob")
def test_main(files_spark_ingest_job, connections, get_configuration, get_logger, sys_modules):
    from src.files_spark_ingest_default import main

    main()
    awsglue_job.Job().init.assert_called_once()
    awsglue_job.Job().commit.assert_called_once()
    files_spark_ingest_job.assert_called_with(get_configuration(), get_logger())


@patch("src.files_spark_ingest_default.get_logger")
@patch("src.files_spark_ingest_default.get_configuration")
@patch("src.files_spark_ingest_default.Connections")
@patch("src.files_spark_ingest_default.CustomFilesSparkIngestJob")
def test_main_exception(files_spark_ingest_job, connections, get_configuration, get_logger, sys_modules):
    from src.files_spark_ingest_default import main
    files_spark_ingest_job().run.side_effect = Exception()

    with pytest.raises(Exception):
        main()

    get_logger().log.assert_called_with(
        "f003",
        job_error=ANY,
        table_name=ANY,
        job_run_id=ANY
    )


@pytest.mark.parametrize("params, expected_output", td.test_config_name_type)
def test_get_config_name_type(params, expected_output, sys_modules):
    from src.files_spark_ingest_default import get_config_name_type
    config_name_type = get_config_name_type("config_name", params)
    assert config_name_type == expected_output
