"""
Core media extraction module for Oryx.
"""
import json
import tempfile

import pandas as pd
import requests
from prefect.tasks import exponential_backoff, task
from prefect_aws import S3Bucket
from prefecto.logging import get_prefect_or_default_logger

from ... import blocks


@task
def filter_not_archived(objects: list[dict]) -> list[str]:
    """Filter out media that has already been archived."""
    return list(filter(lambda obj: "archive/" not in obj["Key"], objects))


@task(retries=3, retry_delay_seconds=exponential_backoff(2), retry_jitter_factor=0.5)
def read_staged_loss(key: str) -> pd.DataFrame:
    """Read a staged Oryx loss into a DataFrame. Creates a source_file column.

    Reads using the Borderlands bucket's read_path method. Key should be a full path.
    """
    logger = get_prefect_or_default_logger()
    try:
        logger.info(f"Reading staged loss '{key}'.")
        blob: bytes = blocks.bucket.read_path(key)
        data = json.loads(blob)
        df = pd.DataFrame(data)
    except Exception:
        logger.error(
            f"Failed to read staged loss '{key}' from {blocks.bucket}.", exc_info=1
        )
        df = pd.DataFrame([])
    df["source_file"] = key
    return df


def upload_media(r: requests.Response, key: str, bucket: S3Bucket) -> str:
    """Uploads a request's contents to the bucket."""
    # 10 MB buffer
    with tempfile.SpooledTemporaryFile(max_size=1024 * 1024 * 10, suffix=key) as fo:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            fo.write(chunk)
        fo.seek(0)

        return bucket.upload_from_file_object(fo, key)
