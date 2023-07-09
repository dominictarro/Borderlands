"""
Extraction module for postimg.cc.
"""
import requests
from prefect.serializers import CompressedJSONSerializer
from prefect.tasks import exponential_backoff, task
from prefecto.logging import get_prefect_or_default_logger

from ....utilities.blocks import task_persistence_subfolder
from ....utilities.io_ import infer_media_extension
from ....utilities.web import USER_AGENT
from ... import blocks
from .core import upload_media


@task_persistence_subfolder(blocks.persistence_bucket, "postimg")
@task(
    tags=["postimg.cc"],
    retries=3,
    retry_delay_seconds=exponential_backoff(2),
    retry_jitter_factor=0.5,
    persist_result=True,
    result_serializer=CompressedJSONSerializer(),
)
def extract_postimg_media(evidence_url: str, key: str) -> dict[str, str | None]:
    """Extracts media from postimg.cc. and stores it in the media bucket.

    Parameters
    ----------
    evidence_url : str
        The URL of the media to extract.
    key : str
        The key to store the media under in the media bucket. Should be extensionless.

    Returns
    -------
    dict[str, str | None]
        A dictionary containing the URL of the media and the key it was stored under.

    Notes
    -----
    Returned dictionary will be of the form:
    ```python
    {
        "evidence_url": "https://postimg.cc/...",
        "key": "media/...",
    }
    ```
    """
    logger = get_prefect_or_default_logger()
    result = dict(evidence_url=evidence_url, key=None)
    try:
        # Generate a unique ID for the media
        r: requests.Response = requests.get(
            evidence_url, stream=True, headers={"User-Agent": USER_AGENT}
        )
    except Exception:
        logger.warning(f"Failed to fetch '{evidence_url}'.", exc_info=1)
        return result

    ext = infer_media_extension(headers=r.headers, url=evidence_url) or ".unknown"
    # Create key, but do not update the result until successful upload
    key = f"{key}{ext}"

    try:
        abs_key = upload_media(r, key, blocks.media_bucket)
        logger.debug(f"'{evidence_url}' extracted to '{abs_key}'.")
        result["key"] = abs_key
    except Exception:
        logger.warning(f"Failed to stage media from '{evidence_url}'.", exc_info=1)
    return result
