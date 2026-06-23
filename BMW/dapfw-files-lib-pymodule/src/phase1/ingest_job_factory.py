from .ingest_job_configuration import IngestJobConfiguration


class IngestJobFactory:
    @staticmethod
    def get_job(configuration: IngestJobConfiguration, logger):
        if configuration.threads_count > 1:
            from .concurrent_files_ingest_job import ConcurrentFilesIngestJob

            return ConcurrentFilesIngestJob(configuration, logger)
        else:
            from .files_ingest_job import FilesIngestJob

            return FilesIngestJob(configuration, logger)
