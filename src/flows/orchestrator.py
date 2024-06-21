"""
Flow to orchestrate the Oryx subflows.
"""

from prefect import flow, task
from prefect_aws import S3Bucket

try:
    import media
    import oryx
    import publish
except ImportError:
    from flows import media, oryx, publish

from borderlands import definitions
from borderlands.blocks import blocks
from borderlands.schema import Dataset


@task(log_prints=True)
def release_dataset(path: str, dataset: Dataset) -> str:
    """Release the dataset to the bucket."""
    src_bucket = S3Bucket.load(dataset.host_bucket)
    path = blocks.bucket.stream_from(
        src_bucket,
        path,
        dataset.release_path,
    )
    print(f"Released {dataset.label} to {dataset.release_path}")
    return path


@flow(
    name="Borderlands Flow",
    description="Flow to orchestrate the Borderlands subflows.",
)
def borderlands_flow():
    """Flow to orchestrate the Oryx subflows."""
    blocks.load()
    oryx_key = oryx.oryx_flow()
    oryx_release = release_dataset.submit(
        oryx_key,
        definitions.oryx,
    )

    media_key = media.download_media(oryx_release)
    release_dataset.submit(
        media_key,
        definitions.media_inventory,
    )

    publish.release_dataset_to_kaggle(wait_for=[oryx_release])
