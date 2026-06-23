class SFTPConnection:
    def __init__(self, sftp_client, ssh_client):
        self.sftp_client = sftp_client
        self.ssh_client = ssh_client

    def close(self):
        self.sftp_client.close()
        self.ssh_client.close()


class IngestTarget:
    def __init__(self, output_path: str, output_db: str, region: str, kms_key_arn: str):
        self.output_path = output_path
        self.output_db = output_db
        self.region = region
        self.kms_key_arn = kms_key_arn


class SFTPSource:
    def __init__(self, host: str, port: str, path: str, secret: str):
        self.host = host
        self.port = port
        self.path = path
        self.secret = secret


class WorkerData:
    def __init__(self, name, sftp_connection: SFTPConnection, s3_client, s3_resource):
        self.name = name
        self.sftp_connection = sftp_connection
        self.s3_client = s3_client
        self.s3_resource = s3_resource


class IngestDates:
    def __init__(
        self,
        last_ingest_day=None,
        new_last_ingest_day_hour=None,
        max_last_ingest_day=None,
    ):
        self.last_ingest_day = last_ingest_day
        self.new_last_ingest_day_hour = new_last_ingest_day_hour
        self.new_last_ingest_day = None
        if self.new_last_ingest_day_hour:
            self.new_last_ingest_day = self.new_last_ingest_day_hour
        self.max_last_ingest_day = max_last_ingest_day


class SFTPDirectoriesParameters:
    def __init__(
        self,
        directories_inside,
        all_folders_inside,
        incremental_level,
        incremental_datemask,
    ):
        self.directories_inside = directories_inside
        self.all_folders_inside = all_folders_inside
        self.incremental_level = incremental_level
        self.incremental_datemask = incremental_datemask


class SFTPProcessingDetails:
    def __init__(
        self,
        sftp_connection: SFTPConnection,
        sftp_path,
        sftp_option,
        directories_parameters: SFTPDirectoriesParameters,
    ):
        self.sftp_connection = sftp_connection
        self.sftp_path = sftp_path
        self.sftp_option = sftp_option
        self.directories_parameters = directories_parameters


class SFTPIngestDetails:
    def __init__(self, sftp_full_path, sftp_file_name, sftp_option):
        self.sftp_full_path = sftp_full_path
        self.sftp_file_name = sftp_file_name
        self.sftp_option = sftp_option


class PartitionsConfig:
    def __init__(
        self,
        ingest_day_name,
        ingest_day_format,
        ingest_hour_format,
        ingest_full_format,
        ingest_hour_name,
        use_hour,
    ):
        self.ingest_day_name = ingest_day_name
        self.ingest_day_format = ingest_day_format
        self.ingest_hour_format = ingest_hour_format
        self.ingest_full_format = ingest_full_format
        self.ingest_hour_name = ingest_hour_name
        self.use_hour = use_hour
