#!/usr/bin/env python

import os
import json
from helpers import get_secret

SEARCH_TYPES = ["Discover", "GoogleNews", "Image", "Video", "Web", "News"]

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

DATA_POOL_BIGQUERY_SA = json.loads(
    get_secret(os.getenv("DATA_POOL_BIGQUERY_SA"), os.getenv("GCP_SECRET_PROJECT_ID"))
)

MAX_DATA_AGE_DAYS = 487
