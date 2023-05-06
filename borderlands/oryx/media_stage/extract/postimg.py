"""
Extraction module for postimg.cc.
"""
import pandas as pd
import requests
from prefect.serializers import CompressedJSONSerializer
from prefect.tasks import task, exponential_backoff

from .core import upload_media
from ... import blocks
from ....utilities.blocks import task_persistence_subfolder
from ....utilities.io_ import infer_media_extension
from ....utilities.loggers import get_prefect_or_default_logger
from ....utilities.web import USER_AGENT


@task_persistence_subfolder(blocks.persistence_bucket, "postimg")
@task(
    tags=["postimg.cc"],
    retries=3,
    retry_delay_seconds=exponential_backoff(2),
    retry_jitter_factor=0.5,
    persist_result=True,
    result_serializer=CompressedJSONSerializer(),
)
def extract_postimg_media(evidence_url: str, key: str) -> str | None:
    """Extracts media from postimg.cc. and stores it in the media bucket."""
    logger = get_prefect_or_default_logger()
    try:
        # Generate a unique ID for the media
        r: requests.Response = requests.get(evidence_url, stream=True, headers={"User-Agent": USER_AGENT})
    except Exception:
        logger.warning(f"Failed to fetch '{evidence_url}'.", exc_info=1)
        return None

    ext = infer_media_extension(headers=r.headers, url=evidence_url) or ".unknown"
    key = f"{key}{ext}"

    try:
        abs_key = upload_media(r, key, blocks.media_bucket)
        logger.debug(f"'{evidence_url}' extracted to '{abs_key}'.")
        return abs_key
    except Exception:
        logger.warning(f"Failed to stage media from '{evidence_url}'.", exc_info=1)
        return None
