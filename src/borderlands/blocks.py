"""
Storage blocks for the pipeline.
"""

import asyncio

from prefect.utilities.asyncutils import sync_compatible
from prefect_aws import S3Bucket


class Blocks:
    """Class for lazy loading Prefect Blocks."""

    _bucket: S3Bucket | None = None

    @property
    def bucket(self) -> S3Bucket:
        """Returns the bucket for the program. Loads if it isn't already."""
        if not self._bucket:
            self._bucket = S3Bucket.load("s3-bucket-borderlands-core")
        return self._bucket

    @sync_compatible
    async def load(self):
        """Load the blocks."""
        self._bucket = (
            (await self.bucket) if asyncio.iscoroutine(self.bucket) else self.bucket
        )


blocks = Blocks()
