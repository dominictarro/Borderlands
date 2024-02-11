"""
Flow to retrieve the web pages of Russian and Ukrainian equipment.
"""

import datetime

from prefect import flow
from prefect.context import FlowRunContext, get_run_context

from borderlands import assets
from borderlands.blocks import blocks
from borderlands.oryx import (
    alert_on_unmapped_country_flags,
    get_oryx_page,
    load_oryx_equipment_loss_to_s3,
    load_s3_equipment_loss_to_table,
    parse_oryx_web_page,
    pre_process_dataframe,
)
from borderlands.paths import LakeNav
from borderlands.utilities import tasks


@flow(
    name="Oryx Flow",
    description=(
        "Flow to extract the equipment loss data from the Russian"
        "and Ukrainian loss pages on https://www.oryxspioenkop.com/."
    ),
    timeout_seconds=1800,
    log_prints=True,
)
def oryx_flow(prefix: str | None = None) -> str:
    """Flow to retrieve the web pages of Russian and Ukrainian equipment
    losses and parse them into processable JSON documents.

    Args:
        prefix (str, optional): The prefix to use for the S3 key. Defaults to None.

    Returns:
        str: The key the DataFrame was uploaded to.
    """
    ctx: FlowRunContext = get_run_context()
    blocks.load()
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
    alert_on_unmapped_country_flags(df)

    # Generate the key
    key = LakeNav(prefix).equipment_data(dt.strftime("%Y-%m-%d"))
    stage_key = load_oryx_equipment_loss_to_s3(df, key)
    load_s3_equipment_loss_to_table(stage_key)
