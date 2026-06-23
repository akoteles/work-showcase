import boto3
from urllib.parse import urlparse
from .date_utils import try_parsing_date
from datetime import datetime
from .ingest_job_configuration import IngestJobConfiguration
from .entities import IngestDates


def parse_bucket_and_key(path, suffix):
    parse_bucket = urlparse(path)

    if parse_bucket.path[1:]:
        s3_partition_key = f"{parse_bucket.path[1:]}{suffix}"
        if parse_bucket.path[1:][-1] != "/":
            s3_partition_key = f"{parse_bucket.path[1:]}/{suffix}"
    else:
        s3_partition_key = suffix

    return s3_partition_key, parse_bucket.netloc


def get_bucket_prefix(path):
    parse_bucket = urlparse(path)
    extra_prefix_bucket = ""
    if parse_bucket.path[1:]:
        extra_prefix_bucket = parse_bucket.path[1:]
        if parse_bucket.path[1:][-1] != "/":
            extra_prefix_bucket = f"{parse_bucket.path[1:]}/"
    return extra_prefix_bucket


class S3Helper:
    def __init__(self, configuration: IngestJobConfiguration, logger):
        self.configuration = configuration
        self.logger = logger

    @staticmethod
    def create_session():
        session = boto3.session.Session()
        s3_client = session.client("s3",)
        s3_client_resource = session.resource("s3",)
        return s3_client, s3_client_resource

    def initialize(self):
        s3_partition_key, s3_target_bucket = parse_bucket_and_key(
            self.configuration.target.output_path,
            f"{self.configuration.config_name_type}/{self.configuration.table_config['table_name']}",
        )
        self.output_bucket_prefix = get_bucket_prefix(
            self.configuration.target.output_path
        )
        self.s3_target_bucket = s3_target_bucket
        self.s3_target_partition_key = s3_partition_key
        self.s3_client = boto3.client("s3",)
        self.s3_client_resource = boto3.resource("s3",)

    def stop_multipart_upload(self, s3_key=None, upload_id=None):
        aborted_ids = []

        if upload_id:
            self.logger.log(
                "debug_glue",
                message=f"Aborting multipart uploads with UploadId={upload_id}",
            )
            self.s3_client.abort_multipart_upload(
                Bucket=self.s3_target_bucket, Key=s3_key, UploadId=upload_id
            )
            aborted_ids.append(upload_id)
            self.logger.log(
                "debug_glue",
                message=f"Aborted multipart upload with UploadId={upload_id}",
            )
        else:
            self.logger.log(
                "debug_glue",
                message=f"Aborting multipart uploads for objects with keys starting with: s3://{self.s3_target_bucket}/{s3_key}",
            )
            uploads = self.s3_client.list_multipart_uploads(
                Bucket=self.s3_target_bucket
            )

            if "Uploads" in uploads:
                for upload in uploads["Uploads"]:
                    file_key = upload["Key"]
                    if file_key.startswith(s3_key):
                        self.s3_client.abort_multipart_upload(
                            Bucket=self.s3_target_bucket,
                            Key=file_key,
                            UploadId=upload["UploadId"],
                        )
                        aborted_ids.append(upload["UploadId"])
                        self.logger.log(
                            "debug_glue",
                            message=f"Aborted multipart upload with UploadId={upload['UploadId']}",
                        )
            else:
                self.logger.log(
                    "debug_glue", message=f"No multipart uploads found to abort."
                )

        return aborted_ids

    def get_ingest_dates_from_s3(self, file_name):
        new_last_ingest_day_hour = datetime.today()
        last_ingest_day = None
        max_last_ingest_day = None

        try:
            last_ingest_day_str = (
                self.s3_client.get_object(
                    Bucket=self.s3_target_bucket,
                    Key=f"{self.s3_target_partition_key}/{file_name}",
                )["Body"]
                .read()
                .decode("utf-8")
            )

            last_ingest_day = try_parsing_date(last_ingest_day_str)
            max_last_ingest_day = last_ingest_day
        except self.s3_client.exceptions.NoSuchKey:
            last_ingest_day = None
            new_last_ingest_day_hour = self.check_bucket_folders()
        finally:
            return IngestDates(
                last_ingest_day, new_last_ingest_day_hour, max_last_ingest_day
            )

    def check_bucket_folders(self):
        try:
            partitions_config = self.configuration.partitions_config
            table_name = self.configuration.table_config["table_name"]

            bucket = self.s3_client_resource.Bucket(self.s3_target_bucket)
            prefix_key = f"{self.output_bucket_prefix}{self.configuration.config_name_type}/{table_name}/"
            for object in bucket.objects.filter(Prefix=prefix_key):
                item = object.key.split("/")
                for content in item:
                    if content.startswith(partitions_config.ingest_day_name):
                        get_p_ingest_day = content

                length_p_ingest_day_str = len(partitions_config.ingest_day_name) + 1
                length_p_ingest_day_full = len(get_p_ingest_day)
                p_ingest_day = get_p_ingest_day[
                    length_p_ingest_day_str:length_p_ingest_day_full
                ]

                if partitions_config.use_hour:
                    for content in item:
                        if content.startswith(partitions_config.ingest_hour_name):
                            get_p_ingest_hour = (
                                content
                            )

                    length_p_ingest_hour_str = (
                        len(partitions_config.ingest_hour_name) + 1
                    )
                    length_p_ingest_hour_full = len(get_p_ingest_hour)
                    p_ingest_hour = get_p_ingest_hour[
                        length_p_ingest_hour_str:length_p_ingest_hour_full
                    ]
                    p_ingest_day = p_ingest_day + p_ingest_hour

                return try_parsing_date(
                    p_ingest_day, partitions_config.ingest_full_format
                )

            return None
        except Exception:
            raise

    def get_bucket_key_for_file(self, file_name, ingest_dates: IngestDates):
        partitions_config = self.configuration.partitions_config

        if partitions_config.use_hour:
            return (
                f"{self.output_bucket_prefix}{self.configuration.config_name_type}/"
                + self.configuration.table_config["table_name"]
                + "/"
                + partitions_config.ingest_day_name
                + "="
                + str(
                    ingest_dates.new_last_ingest_day_hour.strftime(
                        partitions_config.ingest_day_format
                    )
                )
                + "/"
                + partitions_config.ingest_hour_name
                + "="
                + str(
                    ingest_dates.new_last_ingest_day_hour.strftime(
                        partitions_config.ingest_hour_format
                    )
                )
                + "/"
                + file_name
            )

        return (
            f"{self.output_bucket_prefix}{self.configuration.config_name_type}/"
            + self.configuration.table_config["table_name"]
            + "/"
            + partitions_config.ingest_day_name
            + "="
            + str(
                ingest_dates.new_last_ingest_day.strftime(
                    partitions_config.ingest_day_format
                )
            )
            + "/"
            + file_name
        )
