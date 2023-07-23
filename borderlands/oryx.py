"""
Module to extract data from the Oryx website and perform basic processing and restructuring.
"""
import datetime
import enum
import hashlib
import logging
import zoneinfo
from urllib.parse import urlparse

import bs4
import httpx
import polars as pl
from prefect.serializers import CompressedPickleSerializer
from prefect.tasks import exponential_backoff, task
from prefecto.filesystems import task_persistence_subfolder
from prefecto.logging import get_prefect_or_default_logger
from prefecto.serializers.polars import PolarsSerializer

from . import blocks, schema
from .parser import article
from .utilities import web, wrappers


@task_persistence_subfolder(blocks.persistence_bucket)
@task(
    tags=["www.oryxspioenkop.com"],
    retries=4,
    retry_delay_seconds=exponential_backoff(backoff_factor=3),
    retry_jitter_factor=0.5,
    persist_result=True,
    # result_storage set by wrapper
    result_serializer=CompressedPickleSerializer(compressionlib="gzip"),
)
async def get_oryx_page(url: str) -> str:
    """Requests the Ukrainian equipment losses [web page](https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html)\
    from Oryx.

    Returns
    -------
    str
        String of the page
    """
    async with httpx.AsyncClient(headers={"User-Agent": web.USER_AGENT}) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.text


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


@task
def parse_oryx_web_page(page: str, country: str) -> pl.DataFrame:
    """Parses the Oryx web page.

    Parameters
    ----------
    page : str
        The Oryx web page as a string.
    country : str
        The country the page is for. Either 'Russia' or 'Ukraine'.

    Returns
    -------
    pl.DataFrame
        The parsed data as a Polars DataFrame with the `Equipment` model.
    """
    logger = get_prefect_or_default_logger()
    # Russian and Ukrainian pages are largely identical with the exception of
    # the data section's positions
    data_section_index: int
    if country == "Russia":
        data_section_index = article.RUSSIA_DATA_SECTION_INDEX
    elif country == "Ukraine":
        data_section_index = article.UKRAINE_DATA_SECTION_INDEX
    else:
        raise ValueError(f"There is no equipment losses parser for '{country!r}'")

    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(page, features="html.parser")
    body = soup.find(
        attrs={"class": "post-body entry-content", "itemprop": "articleBody"}
    )
    parser = article.ArticleParser(body, data_section_index, logger)

    df = pl.from_dicts(parser.parse(), schema=schema.EquipmentLoss.schema())
    logger.info(f"Found {len(df)} equipment losses for {country}")

    # Complete the country column
    df = df.with_columns(
        pl.lit(country).alias(schema.EquipmentLoss.country.name),
    )
    return df


@wrappers.force_lazyframe
@wrappers.inject_default_logger
def assign_status(lf: pl.LazyFrame, *, logger: logging.Logger) -> pl.LazyFrame:
    """Assigns statuses to the equipment losses.

    Requires:
    - `schema.EquipmentLoss.description`
    """
    logger.info("Assigning statuses to equipment losses")
    lf = lf.with_columns(
        pl.when(
            # Check if the description contains any of the keywords
            pl.any_horizontal(
                pl.col(schema.EquipmentLoss.description.name).str.contains(keyword)
                for keyword in keywords
            )
        )
        .then(pl.lit(status.value))
        .otherwise(pl.lit(None))
        .alias(status.value)
        for status, keywords in STATUS_KEYWORD_MAP.items()
    )

    status_columns = [status.value for status in Status._member_map_.values()]
    TMP = "tmp"
    # Combine the status columns into a single column
    lf = lf.with_columns(
        # Concatenate the status columns into a list
        pl.concat_list(pl.col(status) for status in status_columns)
        # Use only unique values
        #  - This is only really applies to nulls. This way there is only one null in the list. Important for next.
        .list.unique()
        # Sort the list so that nulls are first
        .list.sort().alias(TMP)
    ).with_columns(
        # If the first element of the list is null, drop it
        pl.when(pl.col(TMP).list.first().is_null())
        .then(pl.col(TMP).list.slice(1, None))
        .otherwise(pl.col(TMP))
        .alias(schema.EquipmentLoss.status.name)
    )
    lf = lf.drop(status_columns + [TMP])
    return lf


@wrappers.force_lazyframe
@wrappers.inject_default_logger
def assign_country_of_production(
    lf: pl.LazyFrame, mapper: dict[str, str], *, logger: logging.Logger
) -> pl.DataFrame | pl.LazyFrame:
    """Assigns the country of production to the equipment losses.

    Requires:
    - `schema.EquipmentLoss.country_of_production_flag_url`
    """
    logger.info("Assigning country of production flags to equipment losses")

    lf = lf.with_columns(
        pl.col(schema.EquipmentLoss.country_of_production_flag_url.name)
        .map_dict(mapper)
        .alias(schema.EquipmentLoss.country_of_production.name)
    )
    return lf


@wrappers.force_lazyframe
@wrappers.inject_default_logger
def assign_evidence_source(lf: pl.LazyFrame, *, logger: logging.Logger) -> pl.LazyFrame:
    """Assigns the evidence source to the equipment losses.

    Requires:
    - `schema.EquipmentLoss.evidence_url`
    """
    logger.info("Assigning evidence sources to equipment losses")
    lf = lf.with_columns(
        pl.col(schema.EquipmentLoss.evidence_url.name)
        .apply(lambda x: urlparse(x).netloc)
        .map_dict(DOMAIN_SOURCE_MAP)
        .alias(schema.EquipmentLoss.evidence_source.name)
    )
    return lf


@wrappers.force_lazyframe
@wrappers.inject_default_logger
def calculate_url_hash(lf: pl.LazyFrame, *, logger: logging.Logger) -> pl.LazyFrame:
    """Calculates the SHA-256 of the UTF-8 encoded URL.

    Requires:
    - `schema.EquipmentLoss.evidence_url`
    """
    logger.info("Calculating URL hashes")
    lf = lf.with_columns(
        pl.col(schema.EquipmentLoss.evidence_url.name)
        .apply(lambda url: hashlib.sha256(url.encode("utf-8")).hexdigest())
        .alias(schema.EquipmentLoss.url_hash.name)
    )
    return lf


@wrappers.force_lazyframe
@wrappers.inject_default_logger
def calculate_case_id(lf: pl.LazyFrame, *, logger: logging.Logger) -> pl.LazyFrame:
    """Calculates the case ID for each case. The case ID helps discriminate
    situations where multiple assets are identified in the same evidence.

    Requires:
    - `schema.EquipmentLoss.country`
    - `schema.EquipmentLoss.category`
    - `schema.EquipmentLoss.model`
    - `schema.EquipmentLoss.url_hash`

    Examples:

    ```csv
    country,category,model,url_hash,case_id,status
    Russia,Tanks,T-62M,6c108d7a216548daa7a82e396d888155d4eebb63f08c3b63d88a4fb1d9e7be01,1,"1, damaged and captured"
    Russia,Tanks,T-62M,6c108d7a216548daa7a82e396d888155d4eebb63f08c3b63d88a4fb1d9e7be01,2,"1, destroyed"
    ```

    Above two cases are the same asset, but the first case is damaged and captured while the second is destroyed.
    To ensure that the two cases are not conflated, the case ID is used to discriminate between the two.
    """
    logger.info("Calculating case IDs")
    lf = lf.with_columns(
        pl.lit(1).alias(schema.EquipmentLoss.case_id.name)
    ).with_columns(
        pl.col(schema.EquipmentLoss.case_id.name)
        .cumsum()
        .over(
            schema.EquipmentLoss.country.name,
            schema.EquipmentLoss.category.name,
            schema.EquipmentLoss.model.name,
            schema.EquipmentLoss.url_hash.name,
        ),
    )
    return lf


@task_persistence_subfolder(blocks.persistence_bucket)
@task(
    tags=["www.oryxspioenkop.com"],
    name="Process Parsed Oryx Equipment Losses",
    description="Cleans the parsed Oryx equipment losses and computes the basic fields.",
    result_serializer=PolarsSerializer(method="polars.json"),
    persist_result=True,
)
def pre_process_dataframe(
    df: pl.DataFrame, country_url_mapper: dict[str, str], as_of_date: datetime.datetime
) -> pl.DataFrame:
    """Performs basic preprocessing on the DataFrame.

    Parameters
    ----------
    df : pl.DataFrame
        The DataFrame to clean.
    country_url_mapper : dict[str, str]
        A dictionary mapping country flag URLs to their unique identifier.
    as_of_date : datetime.datetime
        The date the data was collected.

    Returns
    -------
    pl.DataFrame
        The cleaned DataFrame.
    """
    as_of_date = as_of_date.astimezone(zoneinfo.ZoneInfo("UTC")).replace(tzinfo=None)
    lf = df.lazy()

    # Add the as of date
    lf = (
        lf.with_columns(
            pl.lit(as_of_date, dtype=pl.Datetime).alias(
                schema.EquipmentLoss.as_of_date.name
            ),
        )
        .collect()
        .lazy()
    )

    # Clean strings
    lf = (
        lf.with_columns(
            pl.col(schema.EquipmentLoss.category.name).str.strip(),
            pl.col(schema.EquipmentLoss.model.name).str.strip(),
            pl.col(schema.EquipmentLoss.evidence_url.name).str.strip(),
            pl.col(
                schema.EquipmentLoss.country_of_production_flag_url.name
            ).str.strip(),
        )
        .collect()
        .lazy()
    )

    # Pipe the lazyframe through the transformation UDFs
    lf = (
        (
            lf.pipe(assign_status)
            .pipe(assign_country_of_production, country_url_mapper)
            .pipe(assign_evidence_source)
            .pipe(calculate_url_hash)
            .pipe(calculate_case_id)
        )
        .collect()
        .lazy()
    )
    return lf.collect()
