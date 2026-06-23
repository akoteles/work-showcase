"""
MS Teams Webhook Integration for Airflow Alerting.

Usage:
    from hooks.ms_teams import create_teams_callback

    DEFAULT_ARGS = {
        "on_failure_callback": create_teams_callback("seo"),
    }

Secret naming: {team}_ms_teams_webhook (e.g., seo_ms_teams_webhook)
Webhook URL from Secret Manager, Airflow UI URL from Variables.
"""

import logging
import os
from typing import Any
from urllib.parse import quote

import requests
from airflow.models import Variable
from google.cloud import secretmanager

logger = logging.getLogger(__name__)


# Detect environment from Composer
_COMPOSER_ENV = os.environ.get("COMPOSER_ENVIRONMENT", "").lower()
if "dev" in _COMPOSER_ENV:
    ENV = "dev"
elif "test" in _COMPOSER_ENV:
    ENV = "test"
elif "prod" in _COMPOSER_ENV:
    ENV = "prod"
elif _COMPOSER_ENV == "":
    ENV = "local"
else:
    raise ValueError(f"Unknown environment: {_COMPOSER_ENV}")


def _get_webhook_url(team: str) -> str:
    """
    Retrieve webhook URL from Secret Manager.

    Secret naming convention: {team}_ms_teams_webhook
    """
    project_id = os.environ.get("GCP_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError("GCP_PROJECT environment variable not set")

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{team}_ms_teams_webhook/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")


def _build_airflow_url(
    base_url: str, dag_id: str, task_id: str = "", run_id: str = "", try_number: int = 0
) -> str:
    """Build Airflow UI URL. Returns empty string if base_url is empty."""
    if not base_url:
        return ""
    if task_id and run_id:
        url = f"{base_url}/dags/{dag_id}/grid?dag_run_id={quote(run_id, safe='')}&task_id={task_id}&tab=logs&try_number={try_number}"
        logger.info(f"Generated log URL: {url}")
        return url
    url = f"{base_url}/dags/{dag_id}/grid"
    logger.info(f"Generated DAG URL: {url}")
    return url


def _format_attempt_info(try_number: int, max_tries: int) -> tuple[str, int]:
    """Format attempt information for alert. Returns (attempt_info, retries_left)."""
    total_attempts = max_tries + 1
    retries_left = total_attempts - try_number

    if retries_left == 0:
        return f"{try_number} / {total_attempts} (final attempt)", retries_left
    else:
        return f"{try_number} / {total_attempts} ({retries_left} retries left)", retries_left


def _build_adaptive_card(  # noqa: PLR0913
    dag_id: str,
    task_id: str,
    attempt_info: str,
    retries_left: int,
    execution_date: str,
    error_message: str,
    log_url: str,
    dag_url: str,
) -> dict:
    """Build MS Teams Adaptive Card payload."""
    if retries_left == 0:
        title = f"🚨 DAG Failed: {dag_id}"
    else:
        title = f"⚠️ DAG Retry: {dag_id}"

    actions = []
    if log_url:
        actions.append({"type": "Action.OpenUrl", "title": "View Logs", "url": log_url})
    if dag_url:
        actions.append({"type": "Action.OpenUrl", "title": "View DAG", "url": dag_url})

    card_content = {
        "type": "AdaptiveCard",
        "version": "1.2",
        "body": [
            {
                "type": "TextBlock",
                "text": title,
                "weight": "Bolder",
                "size": "Large",
                "color": "Attention",
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "Environment:", "value": ENV},
                    {"title": "Task:", "value": task_id},
                    {"title": "Attempt:", "value": attempt_info},
                    {"title": "Execution:", "value": execution_date},
                    {"title": "Error:", "value": (error_message or "Unknown error")[:200]},
                ],
            },
        ],
    }

    if actions:
        card_content["actions"] = actions

    return {
        "type": "message",
        "attachments": [
            {"contentType": "application/vnd.microsoft.card.adaptive", "content": card_content}
        ],
    }


def create_teams_callback(team: str):
    """
    Create team-specific failure callback for Airflow.

    Args:
        team: Team name (seo, audio, social, theken, platform)

    Usage:
        DEFAULT_ARGS = {"on_failure_callback": create_teams_callback("seo")}
    """

    def callback(context: dict[str, Any]) -> None:
        ti = context["task_instance"]
        dag_id = context["dag"].dag_id
        task_id = ti.task_id
        run_id = context.get("run_id", "")
        execution_date = str(context.get("execution_date", ""))

        exception = context.get("exception")
        error_message = str(exception) if exception else "Unknown error"

        attempt_info, retries_left = _format_attempt_info(ti.try_number, ti.max_tries)

        base_url = Variable.get("AIRFLOW_UI_URL", default_var="")
        log_url = _build_airflow_url(base_url, dag_id, task_id, run_id, ti.try_number)
        dag_url = _build_airflow_url(base_url, dag_id)

        webhook_url = _get_webhook_url(team)

        payload = _build_adaptive_card(
            dag_id=dag_id,
            task_id=task_id,
            attempt_info=attempt_info,
            retries_left=retries_left,
            execution_date=execution_date,
            error_message=error_message,
            log_url=log_url,
            dag_url=dag_url,
        )

        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Teams alert sent for {dag_id}/{task_id}")

    return callback
