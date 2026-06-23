import logging
import requests
import json


class SlackLogHandler(logging.Handler):
    """
    Logging handler that sends ERROR and CRITICAL logs to Slack
    using an Incoming Webhook.
    """

    def __init__(self, webhook_url, level=logging.ERROR, timeout=5):
        super().__init__(level)
        self.webhook_url = webhook_url
        self.timeout = timeout

    def emit(self, record):
        try:
            message = self.format(record)
            payload = {
                "text": f":rotating_light: *Application Error*\n```{message}```"
            }

            requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
        except Exception:
            # Never let Slack logging crash your app
            pass

"how to call the above module"
"""
import logging
from slack_logger import SlackLogHandler

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T000/B000/XXXX"

logger = logging.getLogger("my_app")
logger.setLevel(logging.INFO)

slack_handler = SlackLogHandler(SLACK_WEBHOOK_URL)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
slack_handler.setFormatter(formatter)

logger.addHandler(slack_handler)

# Example usage
try:
    1 / 0
except Exception:
    logger.exception("Unhandled exception occurred")
"""