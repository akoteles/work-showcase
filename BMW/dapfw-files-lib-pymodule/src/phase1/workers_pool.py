import queue
from .entities import WorkerData
from .sftp_manager import SFTPManager
from .s3_helper import S3Helper


class WorkersPool:
    def __init__(self, count: int, sftp_manager: SFTPManager):
        self.count = count
        self.sftp_manager = sftp_manager
        self.workers_queue = queue.Queue(count)

    def initialize(self):
        for i in range(self.count):
            sftp_connection = self.sftp_manager.create_connection()
            s3_client, s3_client_resource = S3Helper.create_session()
            self.workers_queue.put(
                WorkerData(i, sftp_connection, s3_client, s3_client_resource)
            )

    def get_worker(self):
        return self.workers_queue.get()

    def put_worker(self, worker):
        self.workers_queue.put(worker)

    def cleanup(self):
        while not self.workers_queue.empty():
            worker = self.get_worker()

            if worker.sftp_connection:
                worker.sftp_connection.close()
