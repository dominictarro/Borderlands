"""
Flow to retrieve the web pages of Russian and Ukrainian equipment.
"""
import datetime
import io

import polars as pl
from prefect import flow, task
from prefect.context import FlowRunContext, get_run_context

from borderlands import assets, blocks, schema
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
    key = create_oryx_key(dt, ext="parquet")
    df = df.select(schema.EquipmentLoss.columns())
    df = df.sort(schema.EquipmentLoss.columns(include=[schema.Tag.dimension]))
    with io.BytesIO() as buffer:
        df.write_parquet(buffer, compression="zstd", compression_level=22)
        buffer.seek(0)
        blob = buffer.read()
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
)
def oryx_flow() -> str:
    """Flow to retrieve the web pages of Russian and Ukrainian equipment
    losses and parse them into processable JSON documents.

    Returns:
        str: The key the DataFrame was uploaded to.
    """
    ctx: FlowRunContext = get_run_context()
    # Convert Pendulum to Python datetime
    dt = datetime.datetime.fromisoformat(ctx.flow_run.start_time.isoformat()).replace(
        microsecond=0
    )

    russian_page = get_oryx_page.submit(
        "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html"
    )
    ukrainian_page = get_oryx_page.submit(
        "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html"
    )
    naval_page = get_oryx_page.submit(
        "https://www.oryxspioenkop.com/2022/03/list-of-naval-losses-during-2022.html"
    )
    aircraft_page = get_oryx_page.submit(
        "https://www.oryxspioenkop.com/2022/03/list-of-aircraft-losses-during-2022.html"
    )
    mapper = assets.get_country_of_production_url_mapper.submit()
    category_corrections = assets.get_category_corrections.submit()
    df = tasks.concat(
        [
            parse_oryx_web_page(russian_page, "Russia"),
            parse_oryx_web_page(ukrainian_page, "Ukraine"),
            parse_oryx_web_page(naval_page, None),
            parse_oryx_web_page(aircraft_page, None),
        ]
    )
    df = pre_process_dataframe(df, mapper, category_corrections, dt)

    return upload(df, dt)
