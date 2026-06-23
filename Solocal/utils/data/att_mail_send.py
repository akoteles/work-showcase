import base64
import os
import sys
from google.cloud import storage

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment

to = os.getenv("TO").split(',')
subject = os.getenv("SUBJECT")
contents = os.getenv("CONTENTS")
bucket = os.getenv("BUCKET")
files = os.getenv("PATHS", "").split(',')

if __name__ == "__main__":
    api_key = open('/var/secrets/sendgrid/sendgrid-api.txt').read().strip()
    gcs = storage.Client().bucket(bucket)
    message = Mail(
        from_email=('noreply@example.com', 'SUDATA'),
        to_emails=to,
        subject=subject,
        plain_text_content=contents)

    for file in files:
        name = file.split('/')[-1]
        a = Attachment()
        blob = gcs.get_blob(file)
        a.file_name=name
        a.file_type=blob.content_type
        a.file_content=base64.b64encode(blob.download_as_string()).decode()
        a.disposition="attachment"
        a.content_id=name
        message.add_attachment(a)

    sendgrid_client = SendGridAPIClient(api_key)
    print(f"Message body : {message.get()}")
    response = sendgrid_client.send(message)
    if response.status_code != 202:
        print(f"Error {response.status}")
        print(response.body)
        sys.exit(-1)
    else:
        print("Mail sent")
        sys.exit(0)
