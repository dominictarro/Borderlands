"""
Transformations to apply to equipment loss data.
"""
from __future__ import annotations

import enum
import hashlib
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import bs4
import pandas as pd
from prefect import task
from prefect.serializers import CompressedJSONSerializer
from prefecto.logging import get_prefect_or_default_logger

from ...utilities.blocks import task_persistence_subfolder
from .. import blocks
from ..oryx_parser import article


class Status(enum.Enum):
    """Statuses the equipment may be in."""

    ABANDONED = "abandoned"
    CAPTURED = "captured"
    DAMAGED = "damaged"
    DESTROYED = "destroyed"
    SCUTTLED = "scuttled"
    STRIPPED = "stripped"
    SUNK = "sunk"
    # TODO - perhaps abstract to 'repaired'? Or 'recovered'?
    RAISED = "raised"


# Keywords found in the loss descriptions and the status
# they are associated with
STATUS_KEYWORD_MAP = {
    Status.CAPTURED: ("captured",),
    Status.DESTROYED: ("destroyed",),
    # Typo that should be accounted for
    Status.DAMAGED: ("damaged", "damagd"),
    # Typo that should be accounted for
    Status.ABANDONED: ("abandoned", "abanonded"),
    Status.SCUTTLED: ("scuttled",),
    Status.STRIPPED: ("stripped",),
    Status.SUNK: ("sunk",),
    Status.RAISED: ("raised",),
}


# This will be important for establishing the media processor / page parser
class EvidenceSource(enum.Enum):
    """Source of the confirmation URL."""

    POST_IMG = "postimg"
    TWITTER = "twitter"
    OTHER = "other"


DOMAIN_SOURCE_MAP = {
    "i.postimg.cc": EvidenceSource.POST_IMG.value,
    "postimg.cc": EvidenceSource.POST_IMG.value,
    "postlmg.cc": EvidenceSource.POST_IMG.value,
    "twitter.com": EvidenceSource.TWITTER.value,
    "pic.twitter.com": EvidenceSource.TWITTER.value,
    "starkon.city": EvidenceSource.OTHER.value,
    "aviation-safety.net": EvidenceSource.OTHER.value,
    "en.wikipedia.org": EvidenceSource.OTHER.value,
}


@task(persist_result=False)
def convert_to_records(df: pd.DataFrame) -> list[dict]:
    """Converts a `DataFrame` to a list of dictionaries.

    Parameters
    ----------
    df : pd.DataFrame
        `DataFrame` to convert

    Returns
    -------
    list[dict]
        List of dictionaries
    """
    return df.to_dict(orient="records")


@task_persistence_subfolder(blocks.persistence_bucket)
@task(
    persist_result=True,
    # result_storage set by wrapper
    result_serializer=CompressedJSONSerializer(),
)
def parse_equipment_losses_page(
    body: bytes | str, country: str, as_of_date: datetime
) -> dict[str, Any]:
    """Transforms equipment losses from HTML bytes into a JSON of equipment
    losses for the country.

    Parameters
    ----------
    body : bytes | str
        HTML page as text
    country : str
        Name of the country whose losses are recorded in `data`
    as_of_date : datetime

    Returns
    -------
    dict[str, Any]
        A dictionary of loss cases
    """
    logger = get_prefect_or_default_logger()
    # Russian and Ukrainian pages are largely identical with the exception of
    # some sections' positions
    data_section_index: int
    if country == "Russia":
        data_section_index = article.RUSSIA_DATA_SECTION_INDEX
    elif country == "Ukraine":
        data_section_index = article.UKRAINE_DATA_SECTION_INDEX
    else:
        raise ValueError(f"There is no equipment losses parser for '{country!r}'")

    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(body, features="html.parser")
    body = soup.find(
        attrs={"class": "post-body entry-content", "itemprop": "articleBody"}
    )
    parser = article.ArticleParser(
        body, data_section_index, get_prefect_or_default_logger()
    )
    cases = list(parser.parse())

    logger.info("%s cases parsed for %s", len(cases), country)
    return dict(name=country, as_of_date=as_of_date.isoformat(), data=cases)


@task(persist_result=False)
def tabulate_loss_cases(data: dict) -> pd.DataFrame:
    """Converts the parsed dictionary to a `DataFrame`.

    Parameters
    ----------
    data : dict
        Dictionary containing the loss cases, country name, and date the data
        was extracted

    Returns
    -------
    pd.DataFrame
        A country's losses as a `DataFrame`
    """
    df = pd.DataFrame.from_records(data["data"])
    df["country"] = data["name"]
    df["as_of_date"] = data["as_of_date"]
    return df


@task(persist_result=False)
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Provides a basic clean of the `DataFrame`.

    Parameters
    ----------
    df : pd.DataFrame
        `DataFrame` to clean

    Returns
    -------
    pd.DataFrame
        Cleaned `DataFrame`
    """
    df["evidence_url"] = df["evidence_url"].str.strip()
    return df


@task(persist_result=False)
def assign_status(df: pd.DataFrame) -> pd.DataFrame:
    """Assigns each visual confirmation a list of statuses in the 'status'
    column.

    Parameters
    ----------
    df : pd.DataFrame
        `DataFrame` to assign statuses to

    Returns
    -------
    pd.DataFrame
        `DataFrame` with statuses assigned
    """
    # Set status columns
    column_set: set = set()
    # A simple 'text contains' statement for each keyword
    # TODO Find a more robust method of assessing the status of the equipment
    for status, keywords in STATUS_KEYWORD_MAP.items():
        df[status.value] = None

        column_set.add(status.value)
        for keyword in keywords:
            df.loc[df["description"].str.contains(keyword), status.value] = status.value

    columns = list(column_set)
    # Filters the row's individual status columns to only include those that
    # have been set (a.k.a. are not null)
    #
    #   | captured   | destroyed   | damaged
    # 0 | NA         | NA          | "damaged"
    # 1 | "captured" | NA          | "damaged"
    # 2 | "captured" | "destroyed" | NA
    #
    # Becomes
    #
    #   | status
    # 0 | ["damaged"]
    # 1 | ["captured", "damaged"]
    # 2 | ["captured", "destroyed"]
    #
    df["status"] = df[columns].apply(
        lambda s: list(set(filter(lambda x: pd.isna(x) is False, s))), axis=1
    )
    df = df.drop(columns=columns)
    return df


@task(persist_result=False)
def assign_country_of_production(
    df: pd.DataFrame, mapper: dict[str, str]
) -> pd.DataFrame:
    """Uses the mapper to determine the national origin of the equipment.

    Parameters
    ----------
    df : pd.DataFrame
        `DataFrame` to assign countries of production to
    mapper : dict[str, str]
        Dictionary mapping URLs to ISO Alpha-3 country codes

    Returns
    -------
    pd.DataFrame
        `DataFrame` with a country_of_production column
    """
    df["country_of_production"] = df["country_of_production_flag_url"].replace(mapper)

    # Report unmapped URLs
    unmapped = ~df["country_of_production"].isin(mapper.values())
    if unmapped.any():
        # Set those country names to NA
        df.loc[unmapped, "country_of_production"] = None

        logger = get_prefect_or_default_logger()
        # Get a list of unmapped URLs
        urls = list(df[unmapped]["country_of_production_flag_url"].unique())
        logger.warning("Unmapped URLs detected: count=%s values=%s", len(urls), urls)
    return df


@task(persist_result=False)
def assign_evidence_source(df: pd.DataFrame) -> pd.DataFrame:
    """Uses the mapper to determine the domain and source of the evidence.

    Parameters
    ----------
    df : pd.DataFrame
        `DataFrame` to assign evidence sources to

    Returns
    -------
    pd.DataFrame
        `DataFrame` with a domain and evidence_source column
    """
    df["domain"] = df["evidence_url"].apply(lambda url: urlparse(url).netloc)
    df["evidence_source"] = df["domain"].replace(DOMAIN_SOURCE_MAP)

    # Set values that were not explicitly mapped to OTHER
    # Report unmapped sources
    unmapped = ~df["evidence_source"].isin(DOMAIN_SOURCE_MAP.values())
    if unmapped.any():
        # Set those sources to NA
        df.loc[unmapped, "evidence_source"] = None

        logger = get_prefect_or_default_logger()
        domains = list(df[unmapped]["domain"].unique())
        logger.warning(
            "Unmapped domains detected: count=%s values=%s", len(domains), domains
        )

    return df


@task(persist_result=False)
def flag_duplicate_natural_keys(df: pd.DataFrame) -> pd.DataFrame:
    """Creates a 'failed_duplicate_check' column that flags rows that were
    parsed separately but cannot be discriminated.

    Parameters
    ----------
    df : pd.DataFrame
        `DataFrame` to flag duplicate natural keys in

    Returns
    -------
    pd.DataFrame
        `DataFrame` with a failed_duplicate_check column
    """
    natural_key = ["country", "category", "model", "evidence_url", "id_"]
    gdf = df.groupby(natural_key, as_index=False).agg(
        {
            "description": list,
        }
    )
    gdf["failed_duplicate_check"] = False
    gdf.loc[gdf["description"].str.len() > 1, "failed_duplicate_check"] = True
    gdf = gdf.drop(columns=["description"])
    df = df.merge(gdf, how="left", on=natural_key, suffixes=("", "_DROPME"))
    return df


@task(persist_result=False)
def calculate_url_hash(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates the SHA256 hash of the evidence URL.

    Parameters
    ----------
    df : pd.DataFrame
        `DataFrame` to calculate hashes for

    Returns
    -------
    pd.DataFrame
        `DataFrame` with a url_hash column
    """
    url_bytes = df["evidence_url"].str.encode("utf-8")
    df["url_hash"] = url_bytes.apply(
        lambda url_bytes: hashlib.sha256(url_bytes).hexdigest()
    )
    return df
