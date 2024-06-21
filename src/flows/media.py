import datetime
import io

import polars as pl
from prefect import flow, task
from prefect.context import get_run_context

from borderlands import definitions
from borderlands.blocks import blocks
from borderlands.media import (
    create_inventory_key,
    create_media_inventory_from_oryx,
    download,
    get_latest_media_inventory,
    merge_inventory_state,
)
from borderlands.utilities import tasks


@task
def upload(df: pl.DataFrame, dt: datetime.datetime) -> str:
    """Uploads the DataFrame to S3.

    Args:
        df (pl.DataFrame): The DataFrame to upload.
        dt (datetime.datetime): The datetime to use for the key.

    Returns:
        str: The key the DataFrame was uploaded to.
    """
    key = f"oryx/{create_inventory_key(dt)}"
    df = df.select(definitions.Media.columns())
    df = df.sort(definitions.Media.as_of_date.name)
    with io.BytesIO() as buffer:
        df.write_parquet(buffer, compression="zstd", compression_level=22)
        buffer.seek(0)
        blob = buffer.read()
    return tasks.upload.fn(content=blob, key=key, bucket=blocks.bucket)


@task
def download_oryx(path: str) -> pl.DataFrame:
    """Downloads the Oryx equipment losses.

    Args:
        df (pl.DataFrame): The DataFrame to download.

    Returns:
        pl.DataFrame: The DataFrame with the media downloaded.
    """
    with io.BytesIO() as buffer:
        blocks.bucket.download_object_to_file_object(path, buffer)
        buffer.seek(0)
        return pl.read_parquet(buffer)


@flow(
    name="Media Download",
    description="Flow to download new media from the Oryx dataset.",
    timeout_seconds=600,
)
def download_media(loss_key: str) -> str:
    """Download the media from the media bucket."""
    ctx = get_run_context()
    blocks.load()
    # Convert Pendulum to Python datetime
    dt = datetime.datetime.fromisoformat(ctx.flow_run.start_time.isoformat()).replace(
        microsecond=0
    )
    # Get the loss data
    oryx = download_oryx(path=loss_key)

    # Create the media inventory
    # Merge the inventories
    df = merge_inventory_state(
        current=get_latest_media_inventory(),
        empty=create_media_inventory_from_oryx(oryx),
    )

    # Download the media
    df = download(df)
    # Upload the media inventory
    return upload(df, dt)
