"""
Flow for retrieving media referenced in Oryx confirmed losses.
"""
import datetime

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
    filter_for_files_that_need_download,
    join_media,
    update_with_results,
)
from borderlands.utilities.io_ import list_bucket, upload
from borderlands.utilities.loggers import get_prefect_or_default_logger
from borderlands.utilities.tasks import batch, batch_map, concat, tabulate_s3_objects


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


@task(persist_result=False)
def update_with_new_key(df: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    """Updates a DataFrame with a new key.

    Requires that both DataFrames have columns 'evidence_url' and 'key'.
    """
    df = df.merge(
        new[["evidence_url", "key"]],
        how="left",
        on="evidence_url",
        suffixes=("", "_new"),
    )
    df["key"] = df["key_new"].fillna(df["key"])
    df = df.drop(columns=["key_new"])
    return df


@task(persist_result=False)
def make_keys(df: pd.DataFrame) -> pd.DataFrame:
    """Creates 'key' fields for a DataFrame."""
    df["key"] = df["evidence_source"] + "/" + df["url_hash"]
    return df


@flow(
    name="Oryx Media Extraction Flow",
    description="Flow to extract media from staged Oryx losses.",
    # Hard to imagine this taking > 1 hour
    timeout_seconds=3600,
)
def extract_oryx_media(key: str | None = None) -> dict[str, str]:
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
    media_df = tabulate_s3_objects(media_files)
    df = join_media(df, media_df)
    dl_df = filter_for_files_that_need_download(df)
    dl_df = make_keys(dl_df)

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
    df = update_with_results(df, postimg_keys)

    create_dataframe_markdown_artifact(
        postimg_dl_df.describe(include="all"),
        "postimg-downloaded",
        description="Postimg.cc download results `df.describe()`.",
    )
    # df = update_with_new_key(df, dl_df)
    latest_key = release_latest(df)
    logger.info(f"Successfully released latest.json to {latest_key}.")


async def trigger_extract_oryx_media(flow: Flow, flow_run: FlowRun, state: State):
    """Triggers the media extraction flow. Expects `state` result to be the URL."""
    url = await state.result(fetch=True)
    async with get_client() as client:

        deployment: DeploymentResponse = await get_deployment(
            client, name="Oryx Media Extraction Flow/Trigger", deployment_id=None
        )

        await client.create_flow_run_from_deployment(
            deployment.id,
            parameters={"key": url},
            state=Scheduled(),
            tags=["oryx", "hook", flow_run.name],
        )


@task
def release_latest(df: pd.DataFrame) -> str:
    """Sets the latest.json file in the landing bucket."""
    records = df.applymap(lambda x: None if pd.isna(x) else x).to_dict(orient="records")
    records = [dict(sorted(r.items())) for r in records]
    payload = dict(
        metadata=dict(
            name="oryx",
            description=(
                "A collection of confirmed losses of military equipment in the"
                " Russo-Ukrainian War maintained in the open source database by Oryx."
            ),
            last_updated=datetime.datetime.utcnow().strftime(r"%Y-%m-%d %H:%M:%S %Z"),
            references=[
                "https://www.oryxspioenkop.com/",
                "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html",
                "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html",
                "https://tarro.work",
                "https://github.com/dominictarro/Borderlands",
            ],
        ),
        data=records,
    )
    return upload.fn(payload, "latest.json", blocks.landing_bucket)
