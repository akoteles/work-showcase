#!/usr/bin/env python

import json
import logging
from google.cloud import secretmanager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def read_json(file_path: str) -> dict:
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def get_secret(secret_id: str, project_id: str) -> str:
    logger.info("Getting secret %s from project %s", secret_id, project_id)
    secret_manager = secretmanager.SecretManagerServiceClient()
    request = {"name": f"projects/{project_id}/secrets/{secret_id}/versions/latest"}
    response = secret_manager.access_secret_version(request=request)
    return response.payload.data.decode()


if __name__ == "__main__":
    pass
