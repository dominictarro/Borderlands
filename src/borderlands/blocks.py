"""
Storage blocks for the pipeline.
"""

from prefect_aws import S3Bucket
from prefecto.blocks import lazy_load
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Blocks(BaseSettings):
    """Class for lazy loading Prefect Blocks."""

    model_config = SettingsConfigDict(env_prefix="BORDERLANDS_")

    bucket_block_name: str = Field(
        default="s3-bucket-borderlands-core",
        description="The S3 bucket web pages, images, tables, and other files are stored in.",
    )

    @property
    @lazy_load("bucket_block_name")
    def bucket(self) -> S3Bucket:
        """S3 bucket for the pipeline."""


blocks = Blocks()
