from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import io
import json
import logging


@dataclass
class ExtractionResult:
    rows_extracted: int
    rows_loaded: int
    target_table: str
    status: str
    error_message: Optional[str] = None
    metadata: Optional[dict] = None


class BaseExtractor(ABC):
    def __init__(self, project_id: str, dataset_id: str) -> None:
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def extract(self, execution_date: str, **kwargs) -> ExtractionResult:
        pass

    def _get_bq_client(self):
        from google.cloud import bigquery
        return bigquery.Client(project=self.project_id)

    def _load_to_bq(
        self,
        client,
        rows: List[dict],
        table_id: str,
        write_disposition: str = "WRITE_APPEND",
        schema=None,
    ) -> int:
        from google.cloud import bigquery
        if not rows:
            return 0
        full_table_id = f"{self.project_id}.{self.dataset_id}.{table_id}"
        json_data = "\n".join(json.dumps(row) for row in rows)
        data_file = io.StringIO(json_data)
        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )
        if schema:
            job_config.schema = schema
        else:
            job_config.autodetect = True
        job = client.load_table_from_file(data_file, full_table_id, job_config=job_config)
        job.result()
        if job.errors:
            raise RuntimeError(f"BQ load errors: {job.errors}")
        self.logger.info("Loaded %d rows to %s", len(rows), full_table_id)
        return len(rows)
