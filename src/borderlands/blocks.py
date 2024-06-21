"""
Storage blocks for the pipeline.
"""

import asyncio

from prefect.utilities.asyncutils import sync_compatible
from prefect_aws import S3Bucket
from prefect_slack import SlackWebhook


class Blocks:
    """Class for lazy loading Prefect Blocks."""

    _bucket: S3Bucket | None = None
    _webhook: SlackWebhook | None = None

    @property
    def bucket(self) -> S3Bucket:
        """Returns the bucket for the program. Loads if it isn't already."""
        if not self._bucket:
            self._bucket = S3Bucket.load("s3-bucket-borderlands-core")
        return self._bucket

    @property
    def webhook(self) -> SlackWebhook:
        """Returns the webhook for the program. Loads if it isn't already."""
        if not self._webhook:
            self._webhook = SlackWebhook.load("slack-webhook-borderlands")
        return self._webhook

    @sync_compatible
    async def load(self):
        """Load the blocks."""
        self._bucket = (
            (await self.bucket) if asyncio.iscoroutine(self.bucket) else self.bucket
        )

        self._webhook = (
            (await self.webhook) if asyncio.iscoroutine(self.webhook) else self.webhook
        )


blocks = Blocks()
