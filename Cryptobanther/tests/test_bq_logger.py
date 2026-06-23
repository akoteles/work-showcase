from __future__ import annotations
import json
from datetime import date, datetime
from unittest.mock import MagicMock, patch, call
import pytest
from freezegun import freeze_time

from plugins.bq_logger import PipelineLog, BQLogger, BQ_SCHEMA


class TestPipelineLog:
    def test_duration_seconds_computed_correctly(self, sample_pipeline_log):
        assert sample_pipeline_log.duration_seconds == 330.0

    def test_duration_seconds_none_when_no_timestamps(self):
        log = PipelineLog(
            dag_id="test_dag",
            task_id="test_task",
            run_id="run_001",
            source_system="TEST",
            target_table="project.dataset.table",
            execution_date=date(2024, 1, 15),
            start_ts=None,
            end_ts=None,
            status="SUCCESS",
        )
        assert log.duration_seconds is None

    def test_to_bq_row_serialises_all_fields(self, sample_pipeline_log):
        row = sample_pipeline_log.to_bq_row()
        assert row["dag_id"] == "youtube_ingestion"
        assert row["task_id"] == "extract_load"
        assert row["source_system"] == "YOUTUBE"
        assert row["status"] == "SUCCESS"
        assert row["rows_extracted"] == 250
        assert row["rows_loaded"] == 250
        assert row["execution_date"] == "2024-01-15"
        assert row["duration_seconds"] == 330.0

    def test_to_bq_row_serialises_extra_json(self):
        log = PipelineLog(
            dag_id="test",
            task_id="task",
            run_id="run",
            source_system="YOUTUBE",
            target_table="p.d.t",
            execution_date=date(2024, 1, 15),
            start_ts=datetime(2024, 1, 15, 6, 0),
            end_ts=datetime(2024, 1, 15, 6, 1),
            status="SUCCESS",
            extra_json={"rows_per_channel": {"ch1": 100, "ch2": 150}},
        )
        row = log.to_bq_row()
        parsed = json.loads(row["extra_json"])
        assert parsed["rows_per_channel"]["ch1"] == 100

    @freeze_time("2024-01-15 06:00:00")
    def test_from_airflow_context_populates_fields(self, airflow_context):
        log = PipelineLog.from_airflow_context(
            context=airflow_context,
            source_system="YOUTUBE",
            target_table="my-project.raw.youtube_video_stats",
            rows_extracted=500,
            rows_loaded=500,
            status="SUCCESS",
        )
        assert log.dag_id == "youtube_ingestion"
        assert log.task_id == "extract_load"
        assert log.source_system == "YOUTUBE"
        assert log.rows_extracted == 500
        assert log.status == "SUCCESS"
        assert log.execution_date == date(2024, 1, 15)

    def test_from_airflow_context_with_error(self, airflow_context):
        log = PipelineLog.from_airflow_context(
            context=airflow_context,
            source_system="GSC",
            target_table="p.d.t",
            rows_extracted=0,
            rows_loaded=0,
            status="FAILED",
            error_message="Connection timeout",
        )
        assert log.status == "FAILED"
        assert log.error_message == "Connection timeout"


class TestBQLogger:
    def test_log_inserts_row_to_bq(self, sample_pipeline_log):
        with patch("plugins.bq_logger.bigquery.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.insert_rows_json.return_value = []
            mock_client.get_table.return_value = MagicMock()
            mock_client_cls.return_value = mock_client

            logger = BQLogger(project_id="my-project", dataset_id="logging")
            logger.log(sample_pipeline_log)

            assert mock_client.insert_rows_json.called
            call_args = mock_client.insert_rows_json.call_args
            rows = call_args[0][1]
            assert len(rows) == 1
            assert rows[0]["dag_id"] == "youtube_ingestion"

    def test_log_batch_inserts_multiple_rows(self, sample_pipeline_log):
        with patch("plugins.bq_logger.bigquery.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.insert_rows_json.return_value = []
            mock_client.get_table.return_value = MagicMock()
            mock_client_cls.return_value = mock_client

            logger = BQLogger(project_id="my-project", dataset_id="logging")
            entries = [sample_pipeline_log, sample_pipeline_log]
            logger.log_batch(entries)

            call_args = mock_client.insert_rows_json.call_args
            rows = call_args[0][1]
            assert len(rows) == 2

    def test_table_created_when_not_found(self, sample_pipeline_log):
        from google.cloud.exceptions import NotFound
        with patch("plugins.bq_logger.bigquery.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get_table.side_effect = NotFound("table not found")
            mock_client.create_table.return_value = MagicMock()
            mock_client.insert_rows_json.return_value = []
            mock_client_cls.return_value = mock_client

            logger = BQLogger(project_id="my-project", dataset_id="logging")
            logger.log(sample_pipeline_log)

            assert mock_client.create_table.called

    def test_full_table_id_property(self):
        with patch("plugins.bq_logger.bigquery.Client"):
            logger = BQLogger(project_id="my-project", dataset_id="logging", table_id="custom_logs")
            assert logger.full_table_id == "my-project.logging.custom_logs"

    def test_log_batch_empty_list_does_not_call_bq(self):
        with patch("plugins.bq_logger.bigquery.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client

            logger = BQLogger(project_id="my-project", dataset_id="logging")
            logger.log_batch([])

            mock_client.insert_rows_json.assert_not_called()
