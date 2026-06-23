#!/usr/bin/env python

import json
import requests
import logging
from google.cloud import secretmanager
from urllib.parse import urlencode, urljoin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def read_json(file_path: str) -> dict:
    """
    Reads and returns the contents of a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: The content of the JSON file as a dictionary.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def get_secret(secret_id: str, project_id: str) -> str:
    """
    Retrieves a secret from Google Cloud Secret Manager.

    Args:
        secret_id (str): The identifier of the secret.
        project_id (str): The Google Cloud project ID where the secret is stored.

    Returns:
        str: The value of the secret.
    """
    logger.info("Getting secret %s from project %s", secret_id, project_id)
    secret_manager = secretmanager.SecretManagerServiceClient()
    request = {"name": f"projects/{project_id}/secrets/{secret_id}/versions/latest"}
    response = secret_manager.access_secret_version(request=request)
    return response.payload.data.decode()


def create_url(api_url: str, endpoint: str, params: dict = None) -> str:
    """
    Constructs a complete URL from a base API URL, an endpoint, and optional query parameters.

    Args:
        api_url (str): The base API URL.
        endpoint (str): The API endpoint to be appended to the base URL.
        params (dict, optional): A dictionary of query parameters. Defaults to None.

    Returns:
        str: The fully constructed URL.
    """
    if params:
        return urljoin(api_url, endpoint) + "?" + urlencode(params)
    return urljoin(api_url, endpoint)


def post_request(url: str, headers: dict, payload: dict) -> requests.Response:
    """
    Sends a POST request with the given URL, headers, and payload.

    Args:
        url (str): The API endpoint to send the request to.
        headers (dict): Headers to include in the request.
        payload (dict): The request body.

    Returns:
        requests.Response: The response object from the request.

    Raises:
        requests.exceptions.RequestException: If the request fails.
    """
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in POST request: {e}")
        logging.error(f"Request URL: {url}")
        logging.error(f"Request Headers: {json.dumps(headers, indent=2)}")
        logging.error(f"Request Payload: {json.dumps(payload, indent=2)}")
        logging.error(
            f"Response Content: {e.response.text if e.response else 'No response content'}"
        )
        raise


if __name__ == "__main__":
    pass
