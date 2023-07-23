"""
Flow to retrieve the web pages of Russian and Ukrainian equipment.
"""
import datetime
import gzip

import polars as pl
from prefect import flow, task
from prefect.context import FlowRunContext, get_run_context

from borderlands import assets, blocks
from borderlands.oryx import get_oryx_page, parse_oryx_web_page, pre_process_dataframe
from borderlands.paths import create_oryx_key
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
    key = create_oryx_key(dt, ext="json.gz")
    blob: bytes = gzip.compress(df.write_json(row_oriented=True).encode("utf-8"))
    return tasks.upload.fn(content=blob, key=key, bucket=blocks.landing_bucket)


@flow(
    name="Oryx Flow",
    description=(
        "Flow to extract the equipment loss data from the Russian"
        "and Ukrainian loss pages on https://www.oryxspioenkop.com/."
    ),
    # No reason this should take more than 10 minutes. Most runs will be < 30
    # seconds
    timeout_seconds=600,
    log_prints=True,
    # on_completion=[oryx_media.trigger_extract_oryx_media],
)
def oryx_flow() -> str:
    """Flow to retrieve the web pages of Russian and Ukrainian equipment
    losses and parse them into processable JSON documents.

    Returns:
        str: The key the DataFrame was uploaded to.
    """
    ctx: FlowRunContext = get_run_context()
    # Convert Pendulum to Python datetime
    dt = datetime.datetime.fromisoformat(ctx.flow_run.start_time.isoformat())

    russian_page = get_oryx_page.submit(
        "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html"
    )
    ukrainian_page = get_oryx_page.submit(
        "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html"
    )
    mapper = assets.get_country_of_production_url_mapper.submit()
    df = tasks.concat(
        [
            parse_oryx_web_page(russian_page, "Russia"),
            parse_oryx_web_page(ukrainian_page, "Ukraine"),
        ]
    )
    df = pre_process_dataframe(df, mapper, dt)

    return upload(df, dt)
