"""
Flow to orchestrate the Oryx subflows.
"""
from prefect import flow
from prefecto.logging import get_prefect_or_default_logger

try:
    import media
    import oryx
except ImportError:
    from flows import media, oryx


@flow(
    name="Borderlands Flow",
    description="Flow to orchestrate the Borderlands subflows.",
)
def borderlands_flow():
    """Flow to orchestrate the Oryx subflows."""
    logger = get_prefect_or_default_logger()
    oryx_key = oryx.oryx_flow()
    logger.info(f"Oryx key: {oryx_key}")
    media_key = media.download_media(oryx_key)
    logger.info(f"Media key: {media_key}")
