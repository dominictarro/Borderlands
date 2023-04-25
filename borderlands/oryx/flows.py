"""
Module to host Prefect flows.
"""
from __future__ import annotations

from prefect import flow
from prefect.context import FlowRunContext, get_run_context

from .assets import get_country_of_production_url_mapper
from .extract import get_russian_equipment_loss_page, get_ukrainian_equipment_loss_page
from .stage import oryx_equipment_losses_for_country


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
    log_prints=True
)
def stage_oryx_equipment_losses():
    """Flow to retrieve the web pages of Russian and Ukrainian equipment
    losses and parse them into processable JSON documents.
    """
    ctx: FlowRunContext = get_run_context()
    russian_page = get_russian_equipment_loss_page.submit()
    ukrainian_page = get_ukrainian_equipment_loss_page.submit()
    mapper = get_country_of_production_url_mapper.submit()

    oryx_equipment_losses_for_country(
        page=russian_page,
        country="Russia",
        as_of_date=ctx.flow_run.start_time,
        country_of_production_mapper=mapper
    )
    oryx_equipment_losses_for_country(
        page=ukrainian_page,
        country="Ukraine",
        as_of_date=ctx.flow_run.start_time,
        country_of_production_mapper=mapper
    )
