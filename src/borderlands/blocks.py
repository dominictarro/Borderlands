"""
Storage blocks for the pipeline.
"""

import asyncio
from typing import Awaitable

from prefect.blocks.core import Block
from prefect.utilities.asyncutils import sync_compatible
from prefect_aws import S3Bucket
from prefect_slack import SlackWebhook
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .utilities.blocks import RdsCredentials


class Blocks(BaseSettings):
    """Class for lazy loading Prefect Blocks."""

    model_config = SettingsConfigDict(
        env_prefix="blocks_",
        case_sensitive=False,
    )

    core_bucket_name: str = Field(
        "s3-bucket-borderlands-core",
        description="The name of the S3 bucket for result data.",
    )

    persistence_bucket_name: str = Field(
        "s3-bucket-borderlands-persistence",
        description="The name of the S3 bucket for Prefect persistence data.",
    )

    webhook_name: str = Field(
        "slack-webhook-borderlands",
        description="The name of the Slack webhook for notifications.",
    )

    rds_credentials_name: str = Field(
        "rds-credentials-borderlands",
        description="The name of the RDS credentials for the program.",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._core_bucket: S3Bucket | None = None
        self._persistence_bucket: S3Bucket | None = None
        self._webhook: SlackWebhook | None = None
        self._rds_credentials: RdsCredentials | None = None

    def copy(self) -> "Blocks":
        """Return a copy of the blocks."""
        new_blocks = Blocks()

        new_blocks._core_bucket = self._core_bucket
        new_blocks.core_bucket_name = self.core_bucket_name

        new_blocks._persistence_bucket = self._persistence_bucket
        new_blocks.persistence_bucket_name = self.persistence_bucket_name

        new_blocks._webhook = self._webhook
        new_blocks.webhook_name = self.webhook_name

        new_blocks._rds_credentials = self._rds_credentials
        new_blocks.rds_credentials_name = self.rds_credentials_name
        return new_blocks

    def reset(self):
        """Reset the blocks."""
        self._core_bucket = None
        self._persistence_bucket = None
        self._webhook = None
        self._rds_credentials = None

    @property
    def core_bucket(self) -> S3Bucket:
        """Returns the bucket for the program. Loads if it isn't already."""
        if not self._core_bucket:
            self._core_bucket = S3Bucket.load(self.core_bucket_name)
        return self._core_bucket

    @property
    def persistence_bucket(self) -> S3Bucket:
        """Returns the bucket for the program. Loads if it isn't already."""
        if not self._persistence_bucket:
            self._persistence_bucket = S3Bucket.load(self.persistence_bucket_name)
        return self._persistence_bucket

    @property
    def webhook(self) -> SlackWebhook:
        """Returns the webhook for the program. Loads if it isn't already."""
        if not self._webhook:
            self._webhook = SlackWebhook.load(self.webhook_name)
        return self._webhook

    @property
    def rds_credentials(self) -> RdsCredentials:
        """Returns the RDS credentials for the program. Loads if it isn't already."""
        if not self._rds_credentials:
            self._rds_credentials = RdsCredentials.load(self.rds_credentials_name)
        return self._rds_credentials

    @sync_compatible
    async def load(self):
        """Load the blocks."""
        self._core_bucket = _return_or_await_and_return(self.core_bucket)

        self._persistence_bucket = _return_or_await_and_return(self.persistence_bucket)

        self._webhook = _return_or_await_and_return(self.webhook)

        self._rds_credentials = _return_or_await_and_return(self.rds_credentials)


@sync_compatible
async def _return_or_await_and_return(block: Block | Awaitable[Block]) -> Block:
    """Return the block if it is already loaded, otherwise await and return."""
    if asyncio.iscoroutine(block):
        return await block
    return block


blocks = Blocks()
