import paramiko
import boto3
import json
from io import StringIO
from .ingest_job_configuration import IngestJobConfiguration
from .entities import SFTPConnection


def get_secret(client, secret_id):
    get_secret_value_response = client.get_secret_value(SecretId=secret_id)
    secret = get_secret_value_response["SecretString"]
    secret = json.loads(secret, strict=False)
    return secret.get("username"), secret.get("key")


class SFTPManager:
    def __init__(self, configuration: IngestJobConfiguration, logger):
        self.sftp_key = ""
        self.sftp_username = ""
        self.configuration = configuration
        self.logger = logger
        self.sftp_path_src = self._get_sftp_path_src()
        self.all_sftp_options = self._set_sftp_src_dir()

    def initialize(self):
        sftp_username, sftp_key = get_secret(
            boto3.client(
                "secretsmanager", region_name=self.configuration.target.region
            ),
            self.configuration.source.secret,
        )
        self.sftp_key = sftp_key
        self.sftp_username = sftp_username

    def _get_sftp_path_src(self):
        sftp_path_src = self.configuration.source.path
        if sftp_path_src[-1] != "/":
            sftp_path_src = sftp_path_src + "/"
        if sftp_path_src[0] != "/":
            sftp_path_src = "/" + sftp_path_src
        return sftp_path_src

    def _set_sftp_src_dir(self):
        sftp_options = self.configuration.table_config["sftp_options"]
        index = 0
        for option in sftp_options:
            if option["directory"][-1] != "/":
                sftp_options[index]["directory"] = (
                    sftp_options[index]["directory"] + "/"
                )
            if option["directory"][0] == "/":
                sftp_options[index]["directory"] = sftp_options[index]["directory"][1:]
            index += 1
        return sftp_options

    def create_connection(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        try:
            transport = paramiko.Transport(
                self.configuration.source.host, int(self.configuration.source.port)
            )
        except Exception as e:
            self.logger.log(
                "f007", error="Failed to connect SFTP Server! Check host name and port",
            )
            raise e
        try:
            private_key_file = StringIO(self.sftp_key)
            pkey = paramiko.RSAKey.from_private_key(private_key_file)
            transport.connect(username=self.sftp_username, pkey=pkey)

        except Exception as identifier:
            self.logger.log(
                "f007", error="Failed to connect SFTP Server! Invalid name or key",
            )
            raise identifier

        sftp_client = paramiko.SFTPClient.from_transport(transport)
        return SFTPConnection(sftp_client, ssh_client)
