from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Any, Dict
import json
import logging
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

logger = logging.getLogger(__name__)

BQ_SCHEMA = [
    bigquery.SchemaField("job_id",           "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("dag_id",           "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("task_id",          "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("run_id",           "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("source_system",    "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("target_table",     "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("execution_date",   "DATE",      mode="REQUIRED"),
    bigquery.SchemaField("start_ts",         "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("end_ts",           "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("duration_seconds", "FLOAT64",   mode="NULLABLE"),
    bigquery.SchemaField("rows_extracted",   "INTEGER",   mode="NULLABLE"),
    bigquery.SchemaField("rows_loaded",      "INTEGER",   mode="NULLABLE"),
    bigquery.SchemaField("status",           "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("error_message",    "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("extra_json",       "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("logged_at",        "TIMESTAMP", mode="REQUIRED"),
]


@dataclass
class PipelineLog:
    dag_id: str
    task_id: str
    run_id: str
    source_system: str
    target_table: str
    execution_date: date
    start_ts: datetime
    end_ts: datetime
    status: str
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    logged_at: datetime = field(default_factory=datetime.utcnow)
    rows_extracted: Optional[int] = None
    rows_loaded: Optional[int] = None
    error_message: Optional[str] = None
    extra_json: Optional[Dict[str, Any]] = None

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.start_ts and self.end_ts:
            return (self.end_ts - self.start_ts).total_seconds()
        return None

    @classmethod
    def from_airflow_context(
        cls,
        context: dict,
        source_system: str,
        target_table: str,
        rows_extracted: int,
        rows_loaded: int,
        status: str,
        error_message: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> "PipelineLog":
        dag = context["dag"]
        task = context["task"]
        execution_date = context["execution_date"]
        ti = context.get("task_instance")
        now = datetime.utcnow()
        start_ts = getattr(ti, "start_date", None) or now
        end_ts = getattr(ti, "end_date", None) or now
        exec_date = execution_date.date() if hasattr(execution_date, "date") else execution_date
        return cls(
            dag_id=dag.dag_id,
            task_id=task.task_id,
            run_id=context["run_id"],
            source_system=source_system,
            target_table=target_table,
            execution_date=exec_date,
            start_ts=start_ts,
            end_ts=end_ts,
            status=status,
            rows_extracted=rows_extracted,
            rows_loaded=rows_loaded,
            error_message=error_message,
            extra_json=extra,
        )

    def to_bq_row(self) -> dict:
        return {
            "job_id": self.job_id,
            "dag_id": self.dag_id,
            "task_id": self.task_id,
            "run_id": self.run_id,
            "source_system": self.source_system,
            "target_table": self.target_table,
            "execution_date": self.execution_date.isoformat() if hasattr(self.execution_date, "isoformat") else str(self.execution_date),
            "start_ts": self.start_ts.isoformat() if self.start_ts else None,
            "end_ts": self.end_ts.isoformat() if self.end_ts else None,
            "duration_seconds": self.duration_seconds,
            "rows_extracted": self.rows_extracted,
            "rows_loaded": self.rows_loaded,
            "status": self.status,
            "error_message": self.error_message,
            "extra_json": json.dumps(self.extra_json) if self.extra_json else None,
            "logged_at": self.logged_at.isoformat() if self.logged_at else None,
        }


class BQLogger:
    def __init__(self, project_id: str, dataset_id: str, table_id: str = "pipeline_execution_logs") -> None:
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self._client = bigquery.Client(project=project_id)
        self._table_ensured = False

    @property
    def full_table_id(self) -> str:
        return f"{self.project_id}.{self.dataset_id}.{self.table_id}"

    def _ensure_table_exists(self) -> None:
        if self._table_ensured:
            return
        table_ref = self._client.dataset(self.dataset_id).table(self.table_id)
        try:
            self._client.get_table(table_ref)
        except NotFound:
            table = bigquery.Table(table_ref, schema=BQ_SCHEMA)
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field="execution_date",
            )
            table.clustering_fields = ["dag_id", "source_system"]
            self._client.create_table(table)
            logger.info("Created pipeline_execution_logs table: %s", self.full_table_id)
        self._table_ensured = True

    def log(self, entry: PipelineLog) -> None:
        self._ensure_table_exists()
        row = entry.to_bq_row()
        errors = self._client.insert_rows_json(self.full_table_id, [row])
        if errors:
            logger.error("BQLogger insert errors: %s", errors)
        else:
            logger.info("Logged pipeline entry job_id=%s status=%s", entry.job_id, entry.status)

    def log_batch(self, entries: List[PipelineLog]) -> None:
        if not entries:
            return
        self._ensure_table_exists()
        rows = [e.to_bq_row() for e in entries]
        errors = self._client.insert_rows_json(self.full_table_id, rows)
        if errors:
            logger.error("BQLogger batch insert errors: %s", errors)
        else:
            logger.info("Logged %d pipeline entries", len(entries))

    def get_dag_run_summary(self, dag_id: str, run_id: str) -> List[dict]:
        query = f"""
            SELECT *
            FROM `{self.full_table_id}`
            WHERE dag_id = @dag_id AND run_id = @run_id
            ORDER BY logged_at
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("dag_id", "STRING", dag_id),
                bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
            ]
        )
        results = self._client.query(query, job_config=job_config).result()
        return [dict(row) for row in results]
