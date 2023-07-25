"""
Flow to orchestrate the Oryx subflows.
"""
from prefect import flow, task
from prefect_aws import S3Bucket

try:
    import media
    import oryx
except ImportError:
    from flows import media, oryx

from borderlands import blocks, datasets


@task(log_prints=True)
def release_dataset(path: str, dataset: datasets.Dataset) -> str:
    """Release the dataset to the bucket."""
    src_bucket = S3Bucket.load(dataset.host_bucket)
    path = blocks.core_bucket.stream_from(
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
    oryx_key = oryx.oryx_flow()
    oryx_release = release_dataset.submit(
        oryx_key,
        datasets.oryx,
    )

    media_key = media.download_media(oryx_release)
    oryx_release = release_dataset.submit(
        media_key,
        datasets.oryx,
    )
