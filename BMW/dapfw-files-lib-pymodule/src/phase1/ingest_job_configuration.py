from typing import Any
from .entities import SFTPSource, IngestTarget, PartitionsConfig


class IngestJobConfiguration:
    def __init__(
        self,
        *,
        job_name: str,
        job_run_id: str,
        table_config: Any,
        config_name_type: str,
        default_filemask: str,
        chunk_size: int,
        source: SFTPSource,
        target: IngestTarget,
        partitions_config: PartitionsConfig,
        threads_count=1
    ):
        self.job_name = job_name
        self.job_run_id = job_run_id
        self.table_config = table_config
        self.threads_count = threads_count
        self.config_name_type = config_name_type
        self.default_filemask = default_filemask
        self.chunk_size = chunk_size
        self.source = source
        self.target = target
        self.partitions_config = partitions_config
