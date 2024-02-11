"""
Storage blocks for the pipeline.
"""

import asyncio

from prefect.utilities.asyncutils import sync_compatible
from prefect_aws import S3Bucket
from prefect_slack import SlackWebhook
from prefecto.filesystems import create_child

from .utilities.blocks import RdsCredentials


class Blocks:
    """Class for lazy loading Prefect Blocks."""

    _core_bucket: S3Bucket | None = None
    _persistence_bucket: S3Bucket | None = None
    _oryx_bucket: S3Bucket | None = None
    _assets_bucket: S3Bucket | None = None
    _media_bucket: S3Bucket | None = None
    _webhook: SlackWebhook | None = None
    _rds_credentials: RdsCredentials | None = None

    @property
    def core_bucket(self) -> S3Bucket:
        """Returns the bucket for the program. Loads if it isn't already."""
        if not self._core_bucket:
            self._core_bucket = S3Bucket.load("s3-bucket-borderlands-core")
        return self._core_bucket

    @property
    def persistence_bucket(self) -> S3Bucket:
        """Returns the bucket for the program. Loads if it isn't already."""
        if not self._persistence_bucket:
            self._persistence_bucket = S3Bucket.load(
                "s3-bucket-borderlands-persistence"
            )
        return self._persistence_bucket

    @property
    def webhook(self) -> SlackWebhook:
        """Returns the webhook for the program. Loads if it isn't already."""
        if not self._webhook:
            self._webhook = SlackWebhook.load("slack-webhook-borderlands")
        return self._webhook

    @property
    def oryx_bucket(self) -> S3Bucket:
        """Returns the bucket for the program. Loads if it isn't already."""
        if not self._oryx_bucket:
            self._oryx_bucket = create_child(self.core_bucket, "oryx", "-oryx")
        return self._oryx_bucket

    @property
    def assets_bucket(self) -> S3Bucket:
        """Returns the bucket for the program. Loads if it isn't already."""
        if not self._assets_bucket:
            self._assets_bucket = create_child(self.core_bucket, "assets", "-assets")
        return self._assets_bucket

    @property
    def media_bucket(self) -> S3Bucket:
        """Returns the bucket for the program. Loads if it isn't already."""
        if not self._media_bucket:
            self._media_bucket = create_child(self.core_bucket, "media", "-media")
        return self._media_bucket

    @property
    def rds_credentials(self) -> RdsCredentials:
        """Returns the RDS credentials for the program. Loads if it isn't already."""
        if not self._rds_credentials:
            self._rds_credentials = RdsCredentials.load("rds-credentials-borderlands")
        return self._rds_credentials

    @sync_compatible
    async def load(self):
        """Load the blocks."""
        self._core_bucket = (
            (await self.core_bucket)
            if asyncio.iscoroutine(self.core_bucket)
            else self.core_bucket
        )

        self._persistence_bucket = (
            (await self.persistence_bucket)
            if asyncio.iscoroutine(self.persistence_bucket)
            else self.persistence_bucket
        )

        self._webhook = (
            (await self.webhook) if asyncio.iscoroutine(self.webhook) else self.webhook
        )

        self._oryx_bucket = (
            (await self.oryx_bucket)
            if asyncio.iscoroutine(self.oryx_bucket)
            else self.oryx_bucket
        )

        self._assets_bucket = (
            (await self.assets_bucket)
            if asyncio.iscoroutine(self.assets_bucket)
            else self.assets_bucket
        )

        self._media_bucket = (
            (await self.media_bucket)
            if asyncio.iscoroutine(self.media_bucket)
            else self.media_bucket
        )

        self._rds_credentials = (
            (await self.rds_credentials)
            if asyncio.iscoroutine(self.rds_credentials)
            else self.rds_credentials
        )


blocks = Blocks()
