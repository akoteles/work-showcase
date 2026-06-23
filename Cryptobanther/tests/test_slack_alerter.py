from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest

from plugins.slack_alerter import (
    build_failure_blocks,
    build_success_blocks,
    send_slack_message,
    on_failure_callback,
    on_success_callback,
)


def make_context(dag_id="test_dag", task_id="test_task", exception=None):
    dag = MagicMock()
    dag.dag_id = dag_id
    task = MagicMock()
    task.task_id = task_id
    task_instance = MagicMock()
    task_instance.duration = 42.5
    return {
        "dag": dag,
        "task": task,
        "task_instance": task_instance,
        "execution_date": "2024-01-15T06:00:00+00:00",
        "run_id": "scheduled__2024-01-15",
        "exception": exception,
    }


class TestBuildFailureBlocks:
    def test_failure_blocks_contain_dag_id(self):
        context = make_context(dag_id="youtube_ingestion", exception=ValueError("API timeout"))
        blocks = build_failure_blocks(context)
        block_text = str(blocks)
        assert "youtube_ingestion" in block_text

    def test_failure_blocks_contain_error_text(self):
        context = make_context(exception=RuntimeError("BQ load failed"))
        blocks = build_failure_blocks(context)
        block_text = str(blocks)
        assert "BQ load failed" in block_text

    def test_failure_blocks_truncate_long_errors(self):
        long_error = "x" * 1000
        context = make_context(exception=Exception(long_error))
        blocks = build_failure_blocks(context)
        block_text = str(blocks)
        assert len(block_text) < 5000

    def test_success_blocks_contain_duration(self):
        context = make_context()
        blocks = build_success_blocks(context)
        block_text = str(blocks)
        assert "42.5" in block_text

    def test_success_blocks_contain_dag_id(self):
        context = make_context(dag_id="mysql_ingestion")
        blocks = build_success_blocks(context)
        block_text = str(blocks)
        assert "mysql_ingestion" in block_text


class TestSendSlackMessage:
    def test_send_returns_true_on_200(self):
        with patch("plugins.slack_alerter.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_post.return_value = mock_resp
            result = send_slack_message("https://hooks.slack.com/test", [{"type": "section"}])
            assert result is True

    def test_send_returns_false_on_non_200(self):
        with patch("plugins.slack_alerter.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 429
            mock_resp.text = "rate limited"
            mock_post.return_value = mock_resp
            result = send_slack_message("https://hooks.slack.com/test", [])
            assert result is False

    def test_send_returns_false_on_exception(self):
        with patch("plugins.slack_alerter.requests.post", side_effect=ConnectionError("network error")):
            result = send_slack_message("https://hooks.slack.com/test", [])
            assert result is False


class TestCallbacks:
    def test_on_failure_callback_calls_send(self):
        context = make_context(exception=ValueError("boom"))
        with patch("plugins.slack_alerter.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_post.return_value = mock_resp
            with patch("plugins.slack_alerter.Variable") as mock_var:
                mock_var.get.return_value = "https://hooks.slack.com/test"
                on_failure_callback(context)
                assert mock_post.called

    def test_on_success_callback_skips_when_disabled(self):
        context = make_context()
        with patch("plugins.slack_alerter.requests.post") as mock_post:
            with patch("plugins.slack_alerter.Variable") as mock_var:
                mock_var.get.side_effect = lambda key, **kw: "false" if "notify" in key else "https://hooks.slack.com/test"
                on_success_callback(context)
                mock_post.assert_not_called()
