from __future__ import annotations
import pytest
from datetime import date, datetime
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_bq_client():
    client = MagicMock()
    client.insert_rows_json.return_value = []
    client.query.return_value.result.return_value = iter([])
    return client


@pytest.fixture
def sample_pipeline_log():
    from plugins.bq_logger import PipelineLog
    return PipelineLog(
        dag_id="youtube_ingestion",
        task_id="extract_load",
        run_id="scheduled__2024-01-15T06:00:00+00:00",
        source_system="YOUTUBE",
        target_table="my-project.raw.youtube_video_stats",
        execution_date=date(2024, 1, 15),
        start_ts=datetime(2024, 1, 15, 6, 0, 0),
        end_ts=datetime(2024, 1, 15, 6, 5, 30),
        status="SUCCESS",
        rows_extracted=250,
        rows_loaded=250,
    )


@pytest.fixture
def airflow_context():
    dag = MagicMock()
    dag.dag_id = "youtube_ingestion"
    task = MagicMock()
    task.task_id = "extract_load"
    execution_date = MagicMock()
    execution_date.date.return_value = date(2024, 1, 15)
    return {
        "dag": dag,
        "task": task,
        "execution_date": execution_date,
        "run_id": "scheduled__2024-01-15T06:00:00+00:00",
    }
