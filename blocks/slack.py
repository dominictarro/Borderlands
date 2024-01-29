"""
Blocks for Slack.
"""

import os

from dotenv import load_dotenv
from prefect_slack import SlackWebhook
from pydantic import SecretStr

load_dotenv()

try:
    from . import utils
except ImportError:
    import utils


webhook: SlackWebhook = SlackWebhook(
    _block_document_name="slack-webhook-borderlands",
    url=SecretStr(os.environ["SLACK_WEBHOOK_URL"]),
)


if __name__ == "__main__":
    utils.run(utils.save(webhook))
