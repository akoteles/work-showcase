#!/bin/sh
set -e

# Activate Google credentials if GOOGLE_SA_KEY_JSON env var is set
if [ -n "${GOOGLE_SA_KEY_JSON}" ]; then
    echo "${GOOGLE_SA_KEY_JSON}" > /tmp/sa-key.json
    export GOOGLE_APPLICATION_CREDENTIALS=/tmp/sa-key.json
    echo "Service account credentials written to /tmp/sa-key.json"
fi

# Validate required environment variables
if [ -z "${GCP_PROJECT_ID}" ]; then
    echo "ERROR: GCP_PROJECT_ID environment variable is not set" >&2
    exit 1
fi

echo "Starting ingestion container with project=${GCP_PROJECT_ID} dataset=${BQ_DATASET_RAW:-raw}"

exec python "$@"
