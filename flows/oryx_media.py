"""
Flow for retrieving media referenced in Oryx confirmed losses.
"""
import pandas as pd
from prefect import Flow, flow, task
from prefect.artifacts import create_markdown_artifact
from prefect.cli.deployment import get_deployment
from prefect.client.orchestration import get_client
from prefect.engine import FlowRun
from prefect.server.schemas.responses import DeploymentResponse
from prefect.states import Scheduled, State

from borderlands.oryx import blocks
from borderlands.oryx.media_stage.extract import postimg
from borderlands.oryx.media_stage.extract.core import read_staged_loss
from borderlands.oryx.media_stage.transform.basic import (
    build_download_dataframe,
    build_media_state,
    update_with_results,
)
from borderlands.utilities.io_ import list_bucket, upload
from borderlands.utilities.loggers import get_prefect_or_default_logger
from borderlands.utilities.tasks import batch, batch_map, concat


def create_dataframe_markdown_artifact(
    df: pd.DataFrame, key: str | None = None, description: str | None = None
) -> None:
    """Creates a markdown artifact with a table of the given DataFrame."""
    md = df.to_markdown()
    artifact_id = create_markdown_artifact(md, key=key, description=description)
    get_prefect_or_default_logger().info(
        f"Created artifact '{key}' with ID='{artifact_id}'."
    )


@task(persist_result=False)
def filter_for_source(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """Filters a DataFrame for a given source."""
    return df[df["evidence_source"] == source]


@task(persist_result=False)
def make_batches(batch_size: int, df: pd.DataFrame) -> list[dict[str, str]]:
    """Creates batches for postimg.cc."""
    return batch(
        batch_size, evidence_url=df["evidence_url"].to_list(), key=df["key"].to_list()
    )


@flow(
    name="Oryx Media Extraction Flow",
    description="Flow to extract media from staged Oryx losses.",
    # Hard to imagine this taking > 1 hour
    timeout_seconds=3600,
)
def extract_oryx_media(key: str | None = None):
    """Flow to extract media from staged Oryx losses."""
    logger = get_prefect_or_default_logger()
    # Scan the bucket for media files.
    media_files = list_bucket.submit(blocks.media_bucket)

    if key is None:
        # Scan the bucket for unarchived loss files.
        objects = list_bucket(blocks.landing_bucket)
        if len(objects) == 0:
            logger.info("No unarchived media found.")
            return
    else:
        objects = [{"Key": key}]

    # Read the staged losses into a DataFrame.
    dataframes: list[pd.DataFrame] = []
    for s3_obj in objects:
        file_df = read_staged_loss.submit(s3_obj["Key"])
        dataframes.append(file_df)
    df: pd.DataFrame = concat(dataframes)

    # Create a staged artifact.
    create_dataframe_markdown_artifact(
        df.groupby(["source_file", "country", "evidence_source"])
        .count()
        .rename(columns={"evidence_url": "count"})[["count"]]
        .reset_index(),
        "staged-losses",
    )

    # Create a download dataframe.
    # Should contain evidence_url, url_hash, evidence_source, as_of_date
    dl_df = build_download_dataframe(df, media_files)

    create_dataframe_markdown_artifact(
        dl_df.groupby(["evidence_source"])
        .count()
        .rename(columns={"evidence_url": "count"})[["count"]]
        .reset_index(),
        "download-dataframe",
        description="Dataframe of media to download.",
    )

    # Download postimg.cc
    postimg_dl_df = filter_for_source(dl_df, "postimg")
    logger.info(f"Downloading {len(postimg_dl_df)} postimg.cc images.")
    postimg_batches = make_batches(45, postimg_dl_df)
    postimg_keys = batch_map(postimg.extract_postimg_media, postimg_batches)
    postimg_dl_df = update_with_results(postimg_dl_df, postimg_keys)

    create_dataframe_markdown_artifact(
        postimg_dl_df.describe(include="all"),
        "postimg-downloaded",
        description="Postimg.cc download results `df.describe()`.",
    )

    dl_state = build_media_state(df, (postimg_dl_df,), ("postimg",))
    upload.submit(
        content=dl_state.to_csv(index=False),
        key="media_state.csv",
        bucket=blocks.assets_bucket,
    )

    create_dataframe_markdown_artifact(
        dl_state.groupby(["evidence_source", "is_downloaded"])
        .count()
        .rename({"url_hash": "count"})
        .reset_index(),
        key="media-state",
        description="Media state after extraction.",
    )


async def trigger_extract_oryx_media(flow: Flow, flow_run: FlowRun, state: State):
    """Triggers the media extraction flow. Expects `state` result to be the URL."""
    logger = get_prefect_or_default_logger()

    url = await state.result(fetch=True)
    try:
        async with get_client() as client:
            deployment: DeploymentResponse = await get_deployment(
                client, name="Oryx Media Extraction Flow/Triggered", deployment_id=None
            )

            hooked_flow_run = await client.create_flow_run_from_deployment(
                deployment.id,
                parameters={"key": url},
                state=Scheduled(),
                tags=["oryx", "hook", flow_run.name],
            )

            logger.info(
                f"Created flow run '{hooked_flow_run.name}' for deployment '{deployment.name}'."
            )
    except Exception:
        logger.warning(
            f"Errored while triggering deployment for {extract_oryx_media.name}.",
            exc_info=1,
        )
