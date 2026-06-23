import os
import time
import sys

from google.cloud import storage

bucket_name = os.getenv("BUCKET")
path = os.getenv("PATH")
timeout_m = int(os.getenv("TIMEOUT_M", 120))

if __name__ == "__main__":
    start = time.time()
    gcs = storage.Client()
    bucket = gcs.bucket(bucket_name=bucket_name)
    blob = bucket.blob(blob_name=path)
    while not blob.exists():
        now = time.time()
        if now - start > timeout_m * 60:
            print("No TOP found before timeout")
            sys.exit(1)
        time.sleep(60)
    print(f"TOP file gs://{bucket_name}{path} found")
