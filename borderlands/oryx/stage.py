"""
Module for acquiring and processing Oryx equipment loss pages.
"""
from __future__ import annotations

from datetime import datetime

import pandas as pd
from prefect.tasks import Task

from . import blocks
from .transform import (
    assign_evidence_source,
    assign_status,
    assign_country_of_production,
    clean_dataframe,
    convert_to_records,
    flag_duplicate_natural_keys,
    parse_equipment_losses_page,
    tabulate_loss_cases,
)
from ..utilities.io_ import upload


def task_with_country_tag(task: Task, country: str) -> Task:
    """Wraps a task with a country tag.

    Parameters
    ----------
    task : Task
        Task to wrap
    country : str
        Name of the country to add to the task's tags

    Returns
    -------
    Task
        Wrapped task
    """
    return task.with_options(tags=task.tags.union([country]))


def oryx_equipment_losses_for_country(
    page: bytes | str,
    country: str,
    as_of_date: datetime,
    country_of_production_mapper: dict
) -> str:
    """Submits a DAG of tasks to parse equipment losses from the Oryx
    website for a specific country.

    Parameters
    ----------
    page : bytes | str
        The web page in text
    country : str
        Name of the country
    as_of_date : datetime
        `DateTime` the flow began
    country_of_production_mapper : dict
        Mapper for country flag URLs to country names

    Returns
    -------
    str
        Path to the staged result
    """
    datestring = as_of_date.isoformat()\
        .replace(":", "-")\
        .replace(" ", "_")

    data: dict = task_with_country_tag(
        parse_equipment_losses_page, country
    ).submit(
        page, country=country, as_of_date=as_of_date
    )
    df: pd.DataFrame = task_with_country_tag(
        tabulate_loss_cases, country
    ).submit(data)
    df = task_with_country_tag(clean_dataframe, country).submit(df)
    df = task_with_country_tag(assign_status, country).submit(df)
    df = task_with_country_tag(assign_country_of_production, country).submit(
        df, country_of_production_mapper
    )
    df = task_with_country_tag(assign_evidence_source, country).submit(df)
    df = task_with_country_tag(flag_duplicate_natural_keys, country).submit(
        df
    )

    data = task_with_country_tag(convert_to_records, country).submit(df)
    # Output the country's result to a .final/ folder in stages folder
    # with the file name country_ISO.json.gz
    return task_with_country_tag(upload, country).submit(
        content=data,
        key=f"{country.lower()}_{datestring}.json",
        bucket=blocks.landing_bucket
    )
