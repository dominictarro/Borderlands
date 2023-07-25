"""

"""
import datetime
import functools
import io
import tempfile
from typing import Callable, Coroutine

import anyio
import httpx
import polars as pl
from prefect import task
from prefect_aws import S3Bucket
from prefecto.logging import get_prefect_or_default_logger

from . import blocks, datasets, enums, paths, schema
from .utilities import io_, web

INVENTORY_SUBFOLDER = "inventory"


@task
def create_media_inventory_from_oryx(df: pl.DataFrame) -> str:
    """Create a media inventory from the Oryx data.

    Args:
        df (pl.DataFrame): DataFrame following `schema.EquipmentLoss`.

    Returns:
        str: The key the media inventory was uploaded to.

    Requires:
        - `schema.EquipmentLoss.evidence_url`
        - `schema.EquipmentLoss.evidence_source`
        - `schema.EquipmentLoss.url_hash`
        - `schema.Media.url`
        - `schema.Media.evidence_source`
        - `schema.Media.url_hash`

    """
    lf = df.lazy()

    # Get the media from the evidence_url
    lf = (
        lf.groupby(schema.EquipmentLoss.url_hash.name)
        .agg(
            pl.col(schema.EquipmentLoss.evidence_url.name)
            .first()
            .alias(schema.Media.url.name),
            pl.col(schema.EquipmentLoss.evidence_source.name)
            .first()
            .alias(schema.Media.evidence_source.name),
        )
        .rename({schema.EquipmentLoss.url_hash.name: schema.Media.url_hash.name})
    )

    # Fill the others with None
    null_fields = schema.Media.iter(
        exclude=[schema.Tag.inherited, schema.Tag.dimension]
    )
    if null_fields:
        lf = lf.with_columns(
            pl.lit(None).cast(f.dtype).alias(f.name) for f in null_fields
        )
    lf = lf.select(schema.Media.columns())
    return lf.collect()


@task
def merge_inventory_state(current: pl.DataFrame, empty: pl.DataFrame) -> pl.DataFrame:
    """Merge the current and empty inventory states. The current state is prioritized over the empty state.

    Args:
        current (pl.DataFrame): The current inventory state.
        empty (pl.DataFrame): The empty inventory state.

    Returns:
        pl.DataFrame: The merged inventory state.
    """
    df = pl.concat([current, empty])
    lf = df.lazy()
    lf = lf.groupby(schema.Media.columns(include=[schema.Tag.dimension])).agg(
        pl.col(col).first()
        for col in schema.Media.columns(exclude=[schema.Tag.dimension])
    )
    return lf.collect()


@task
def get_latest_media_inventory() -> pl.DataFrame:
    """Get the latest media inventory from the media bucket.

    Returns:
        pl.DataFrame: The media inventory.
    """
    bucket: S3Bucket = S3Bucket.load(datasets.media_inventory.host_bucket)
    with io.BytesIO() as buffer:
        bucket.download_object_to_file_object(
            datasets.media_inventory.release_path, buffer
        )
        buffer.seek(0)
        return pl.read_parquet(buffer)


def create_inventory_key(dt: datetime.datetime) -> str:
    """Create the key for the media inventory.

    Args:
        dt (datetime.datetime): The datetime to use for the key.

    Returns:
        str: The key for the media inventory.
    """
    return f"{INVENTORY_SUBFOLDER}/{paths.create_oryx_key(dt, ext='parquet')}"


def create_media_key(ctx: dict) -> str:
    """Create the media key for downloaded media.

    Args:
        ctx (dict): The context for the media.

    Requires:
        - `schema.Media.evidence_source`
        - `schema.Media.url_hash`
        - `schema.Media.file_type`
        - `schema.Media.url`

    Returns:
        str: The media key.
    """
    return (
        f"{ctx[schema.Media.evidence_source.name]}/"
        f"{ctx[schema.Media.url_hash.name]}{ctx[schema.Media.file_type.name] or '.unknown'}"
    )


def get_downloaded_and_not_downloaded(
    df: pl.DataFrame,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Split the dataframe into two dataframes: one with the media that have been downloaded and one with the media that have not been downloaded.

    Args:
        df (pl.DataFrame): The dataframe containing the media urls.

    Requires:
        - `schema.Media.url`
        - `schema.Media.url_hash`
        - `schema.Media.media_key`

    Returns:
        tuple[pl.DataFrame, pl.DataFrame]: The downloaded and not downloaded dataframes.
    """
    downloaded = df.filter(pl.col(schema.Media.media_key.name).is_not_null())
    not_downloaded = df.filter(pl.col(schema.Media.media_key.name).is_null())
    return downloaded, not_downloaded


async def download_file(
    client: httpx.AsyncClient,
    ctx: dict,
    sem: anyio.Semaphore | None = None,
    max_attempts: int | None = 3,
):
    """Download the media from the url and upload it to the media bucket. Updates the media_key and as_of_date in the context.

    Args:
        client (httpx.AsyncClient): The httpx client to use for the download.
        ctx (dict): The context for the media.
        sem (anyio.Semaphore | None, optional): The semaphore to use for the download. Defaults to None.
        max_attempts (int | None, optional): The maximum number of attempts to download the media. Defaults to 3.

    Raises:
        httpx.HTTPStatusError: If the download fails.
    """
    logger = get_prefect_or_default_logger()
    try:
        try:
            await sem.acquire()
            url = ctx[schema.Media.url.name]

            async with client.stream("GET", url) as r:
                r.raise_for_status()
                # Infer the file type and with that the media type
                ctx[schema.Media.file_type.name] = io_.infer_media_extension(
                    ctx[schema.Media.url.name], r.headers
                )
                ctx[schema.Media.media_type.name] = (
                    enums.MediaType.IMAGE.value
                    if ctx[schema.Media.file_type.name]
                    else enums.MediaType.UNKNOWN.value
                )
                path = create_media_key(ctx)
                with tempfile.SpooledTemporaryFile(
                    prefix=ctx[schema.Media.url_hash.name], suffix=".partial"
                ) as fo:
                    async for chunk in r.aiter_bytes():
                        fo.write(chunk)
                    fo.seek(0)
                    # Assign the media key and type
                    ctx[
                        schema.Media.media_key.name
                    ] = await blocks.media_bucket.upload_from_file_object(fo, path)
                    ctx[schema.Media.as_of_date.name] = datetime.datetime.utcnow()
        finally:
            sem.release()
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Failed to download media from {url}", exc_info=e, stack_info=True
        )
        if max_attempts and max_attempts > 1:
            logger.debug(f"Retrying download of media from {url}")
            await download_file(client, ctx, sem, max_attempts - 1)
        return


__evidence_handler_registery__: dict[str, Callable[[Coroutine], Coroutine]] = {}


def get_handler(evidence_source: str) -> Callable[[Coroutine], Coroutine] | None:
    """Get the handler for the evidence source.

    Args:
        evidence_source (str): The evidence source to get the handler for.

    Returns:
        Callable[[Coroutine], Coroutine] | None: The handler or None if there is no handler for the evidence source.
    """
    return __evidence_handler_registery__.get(evidence_source)


def evidence_source_handler(
    evidence_source: enums.EvidenceSource,
) -> Callable[[Coroutine], Coroutine]:
    """Decorator for evidence source handlers.

    Args:
        evidence_source (enums.EvidenceSource): The evidence source to handle.

    Returns:
        Callable[[Coroutine], Coroutine]: The decorator.
    """

    def decorator(coro: Coroutine) -> Coroutine:
        """Wrap the coroutine in a handler for the evidence source."""

        @functools.wraps(coro)
        async def wrapper(
            df: pl.DataFrame, results: dict[str, pl.DataFrame], *args, **kwargs
        ):
            """Performs pre and post processing for the handler."""
            logger = get_prefect_or_default_logger()
            logger.info(f"Downloading {evidence_source.value} media")

            df = df.filter(
                pl.col(schema.Media.evidence_source.name) == evidence_source.value
            )
            downloaded, not_downloaded = get_downloaded_and_not_downloaded(df)

            if not_downloaded.shape[0] == 0:
                logger.info(f"No {evidence_source.value} media to download")
                return downloaded

            # Convert to dicts for async processing
            contexts: list[dict[str, str]] = not_downloaded.to_dicts()
            await coro(contexts, *args, **kwargs)
            # Convert altered contexts back to a dataframe
            newly_downloaded = pl.from_dicts(contexts, schema=schema.Media.schema())
            # Combine the downloaded and newly downloaded dataframes
            results[schema.Media.evidence_source.name] = pl.concat(
                [downloaded, newly_downloaded]
            )

        if evidence_source.value in __evidence_handler_registery__:
            raise ValueError(
                f"{evidence_source.value} is already registered as a handler"
            )

        __evidence_handler_registery__[evidence_source.value] = wrapper

        return wrapper

    return decorator


@evidence_source_handler(enums.EvidenceSource.POST_IMG)
async def download_postimg(contexts: list[dict], concurrency: int = 10):
    """Download the postimg media from the urls in the dataframe and upload them to the media bucket.

    Args:
        df (pl.DataFrame): The dataframe containing the media urls.
        concurrency (int, optional): The number of concurrent downloads. Defaults to 10.

    Requires:
        - `schema.Media.url`
        - `schema.Media.url_hash`
        - `schema.Media.media_key`
        - `schema.Media.as_of_date`
        - `schema.Media.evidence_source`
        - `schema.Media.file_type`
        - `schema.Media.media_type`

    Returns:
        pl.DataFrame: The dataframe for all postimg data with the media keys.
    """
    async with httpx.AsyncClient(headers={"User-Agent": web.USER_AGENT}) as client:
        sem = anyio.Semaphore(concurrency)
        async with anyio.create_task_group() as tg:
            for ctx in contexts:
                if (
                    ctx[schema.Media.evidence_source.name]
                    == enums.EvidenceSource.POST_IMG.value
                ):
                    tg.start_soon(download_file, client, ctx, sem)


@task
async def download(df: pl.DataFrame) -> pl.DataFrame:
    """Download the media from the urls in the dataframe and upload them to the media bucket.

    Args:
        df (pl.DataFrame): The dataframe containing the media urls.

    Returns:
        pl.DataFrame: The dataframe with the media keys.
    """
    logger = get_prefect_or_default_logger()
    evidence_sources = df[schema.Media.evidence_source.name].unique().to_list()
    results: dict[str, pl.DataFrame] = {}
    async with anyio.create_task_group() as tg:
        for evidence_source in evidence_sources:
            handler = get_handler(evidence_source)
            if handler:
                tg.start_soon(handler, df, results)
            else:
                logger.warning(f"No handler for {evidence_source}")
                results[evidence_source] = df.filter(
                    pl.col(schema.Media.evidence_source.name) == evidence_source
                )
    return pl.concat(results.values())
