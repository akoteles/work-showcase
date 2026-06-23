import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

to=os.getenv("TO").split(',')
subject=os.getenv("SUBJECT")
contents=os.getenv("CONTENTS")

if __name__ == "__main__":

    api_key = open('/var/secrets/sendgrid/sendgrid-api.txt').read().strip()
    message = Mail(
        from_email=('noreply@example.com', 'SUDATA'),
        to_emails=to,
        subject=subject,
        plain_text_content=contents)
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
