"""
Flow to retrieve the web pages of Russian and Ukrainian equipment.
"""
from __future__ import annotations

from prefect import flow
from prefect.context import FlowRunContext, get_run_context

from borderlands.oryx import assets
from borderlands.oryx import blocks
from borderlands.oryx.stage.extract import get_russian_equipment_loss_page, get_ukrainian_equipment_loss_page
from borderlands.oryx.stage.transform import (
    assign_country_of_production,
    assign_evidence_source,
    assign_status,
    clean_dataframe,
    convert_to_records,
    flag_duplicate_natural_keys,
    parse_equipment_losses_page,
    tabulate_loss_cases,
)
from borderlands.utilities.io_ import upload
from borderlands.utilities.tasks import concat


@flow(
    name="Oryx Equipment Loss Staging Flow",
    description=(
        "Flow to extract and JSONify the equipment loss data from the Russian"
        "and Ukrainian loss pages on https://www.oryxspioenkop.com/."
    ),
    # version=os.getenv("GIT_COMMIT_SHA"),
    # No reason this should take more than 10 minutes. Most runs will be < 30
    # seconds
    timeout_seconds=600,
    log_prints=True,
)
def stage_oryx_equipment_losses() -> list[dict]:
    """Flow to retrieve the web pages of Russian and Ukrainian equipment
    losses and parse them into processable JSON documents.
    """
    ctx: FlowRunContext = get_run_context()
    russian_page = get_russian_equipment_loss_page.submit()
    ukrainian_page = get_ukrainian_equipment_loss_page.submit()
    mapper = assets.get_country_of_production_url_mapper.submit()

    data_ru = parse_equipment_losses_page.submit(russian_page, "Russia", ctx.flow_run.start_time)
    data_ua = parse_equipment_losses_page.submit(ukrainian_page, "Ukraine", ctx.flow_run.start_time)
    df_ru = tabulate_loss_cases.submit(data_ru)
    df_ua = tabulate_loss_cases.submit(data_ua)
    
    df = concat([df_ru, df_ua], ignore_index=True)
    df = clean_dataframe(df)
    df = assign_status(df)
    df = assign_country_of_production(df, mapper)
    df = assign_evidence_source(df)
    df = flag_duplicate_natural_keys(df)

    records = convert_to_records(df)
    datestring = ctx.flow_run.start_time.isoformat().replace(":", "-").replace(" ", "_")
    upload(records, f"{datestring}.json", blocks.landing_bucket)

    return records
