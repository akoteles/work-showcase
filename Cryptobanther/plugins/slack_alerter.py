from __future__ import annotations
import logging
from typing import List
import requests

logger = logging.getLogger(__name__)


def build_failure_blocks(context: dict) -> list:
    dag_id = context.get("dag", {}).dag_id if hasattr(context.get("dag", None), "dag_id") else str(context.get("dag", "unknown"))
    task_id = context.get("task", {}).task_id if hasattr(context.get("task", None), "task_id") else str(context.get("task", "unknown"))
    execution_date = str(context.get("execution_date", "unknown"))
    run_id = str(context.get("run_id", "unknown"))
    exception = context.get("exception", None)
    error_text = str(exception)[:500] if exception else "No error details available"
    try:
        from airflow.models import Variable
        project = Variable.get("gcp_project_id", default_var="unknown-project")
    except Exception:
        project = "unknown-project"
    return [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": ":red_circle: Pipeline Failure", "emoji": True},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*DAG ID:*\n{dag_id}"},
                {"type": "mrkdwn", "text": f"*Task ID:*\n{task_id}"},
                {"type": "mrkdwn", "text": f"*Execution Date:*\n{execution_date}"},
                {"type": "mrkdwn", "text": f"*Error:*\n```{error_text}```"},
            ],
        },
        {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"Run ID: {run_id}"},
                {"type": "mrkdwn", "text": f"GCP Project: {project}"},
            ],
        },
    ]


def build_success_blocks(context: dict) -> list:
    dag_id = context.get("dag", {}).dag_id if hasattr(context.get("dag", None), "dag_id") else str(context.get("dag", "unknown"))
    task_id = context.get("task", {}).task_id if hasattr(context.get("task", None), "task_id") else str(context.get("task", "unknown"))
    execution_date = str(context.get("execution_date", "unknown"))
    duration = str(context.get("task_instance", {}).duration if hasattr(context.get("task_instance", None), "duration") else "unknown")
    return [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": ":white_check_mark: Pipeline Completed", "emoji": True},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*DAG ID:*\n{dag_id}"},
                {"type": "mrkdwn", "text": f"*Task ID:*\n{task_id}"},
                {"type": "mrkdwn", "text": f"*Execution Date:*\n{execution_date}"},
                {"type": "mrkdwn", "text": f"*Duration:*\n{duration}s"},
            ],
        },
    ]


def send_slack_message(webhook_url: str, blocks: list, text: str = "") -> bool:
    try:
        payload = {"blocks": blocks, "text": text}
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code != 200:
            logger.warning("Slack webhook returned non-200: %s %s", response.status_code, response.text)
            return False
        return True
    except Exception as exc:
        logger.warning("Failed to send Slack message: %s", exc)
        return False


def on_failure_callback(context: dict) -> None:
    try:
        from airflow.models import Variable
        webhook_url = Variable.get("slack_webhook_url")
    except Exception as exc:
        logger.warning("Could not get slack_webhook_url: %s", exc)
        return
    blocks = build_failure_blocks(context)
    send_slack_message(webhook_url, blocks, text="Pipeline failure detected")


def on_success_callback(context: dict) -> None:
    try:
        from airflow.models import Variable
        notify = Variable.get("slack_notify_on_success", default_var="false")
        if notify.lower() != "true":
            return
        webhook_url = Variable.get("slack_webhook_url")
    except Exception as exc:
        logger.warning("Could not get Slack variables: %s", exc)
        return
    blocks = build_success_blocks(context)
    send_slack_message(webhook_url, blocks, text="Pipeline completed successfully")
