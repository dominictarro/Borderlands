"""
Module to extract data from the Oryx website and perform basic processing and restructuring.
"""

import datetime
import enum
import hashlib
import logging
from urllib.parse import urlparse

import bs4
import httpx
import polars as pl
import zoneinfo
from prefect.serializers import CompressedPickleSerializer
from prefect.tasks import exponential_backoff, task
from prefect_slack import messages
from prefecto.filesystems import task_persistence_subfolder
from prefecto.logging import get_prefect_or_default_logger
from prefecto.serializers.polars import PolarsSerializer

from .blocks import blocks
from .enums import EvidenceSource
from .parser import article, parser
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


@task(
    name="Unmapped Country Flags Alert",
    description="Sends a Slack message if there are any unmapped country flags.",
)
async def alert_on_unmapped_country_flags(df: pl.DataFrame) -> None:
    """Searches for unmapped country flags and sends a Slack message if any are found.

    Requires:
    - `EquipmentLoss.country_of_production_flag_url`
    - `EquipmentLoss.country_of_production`
    """
    logger = get_prefect_or_default_logger()
    unmapped: dict[str, str | int] = (
        df.filter(pl.col("country_of_production").is_null())[
            "country_of_production_flag_url"
        ]
        .value_counts()
        .to_dicts()
    )

    if unmapped:
        # Format the sections
        urls = [case["country_of_production_flag_url"] for case in unmapped]
        n, affected = len(urls), sum([case["counts"] for case in unmapped])
        logger.warning(
            f"Found {n} unmapped country of production flags affecting {affected} records."
        )
        message_blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "Unmapped Flag URLs"},
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Cases:*\n{n}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Affected Records:*\n{affected}",
                    },
                ],
            },
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text": "\n".join(urls)}},
        ]
        try:
            messages.send_incoming_webhook_message.fn(
                slack_webhook=blocks.webhook,
                slack_blocks=message_blocks,
            )
        except Exception as e:
            logger.error("Failed to send Slack message", exc_info=e, stack_info=True)
            logger.info("Unmapped country of production flags:\n%s", "\n".join(urls))
    else:
        logger.info("All country of production flags successfully mapped.")


class Status(enum.Enum):
    """Statuses the equipment may be in. Names convert to model names by prefixing with 'is_' like
    `is_abandoned`.
    """

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


# The various URL domains in evidence URLs and the source they are associated
# with
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
def parse_oryx_web_page(page: str, country: str | None = None) -> pl.DataFrame:
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
    data_section_index: int | None = None
    if country == "Russia":
        data_section_index = article.RUSSIA_DATA_SECTION_INDEX
    elif country == "Ukraine":
        data_section_index = article.UKRAINE_DATA_SECTION_INDEX
    elif country is None:
        pass
    else:
        raise ValueError(f"There is no equipment losses parser for '{country!r}'")

    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(page, features="html.parser")
    generator = parser.OryxParser(soup, multi=country is None, logger=logger).parse(
        data_section_index
    )
    df = pl.from_dicts(generator)
    logger.info(f"Found {len(df)} equipment losses for {country}")

    df = df.rename(
        {
            "description": "oryx_description",
            "evidence_url": "oryx_evidence_url",
            "id_": "oryx_id",
        }
    )

    if country is not None:
        # Complete the country column
        df = df.with_columns(
            pl.lit(country).alias("country"),
        )
    return df


@wrappers.force_lazyframe
@wrappers.inject_default_logger
def assign_status(lf: pl.LazyFrame, *, logger: logging.Logger) -> pl.LazyFrame:
    """Assigns statuses to the equipment losses.

    Requires:
    - `EquipmentLoss.oryx_description`
    """
    logger.info("Assigning statuses to equipment losses")
    lf = lf.with_columns(
        pl.when(
            # Check if the description contains any of the keywords
            pl.any_horizontal(
                pl.col("oryx_description").str.contains(keyword) for keyword in keywords
            )
        )
        .then(pl.lit(True))
        .otherwise(pl.lit(False))
        .alias(f"is_{status.value}")
        for status, keywords in STATUS_KEYWORD_MAP.items()
    )
    return lf


@wrappers.force_lazyframe
@wrappers.inject_default_logger
def assign_country_of_production(
    lf: pl.LazyFrame, mapper: dict[str, str], *, logger: logging.Logger
) -> pl.DataFrame | pl.LazyFrame:
    """Assigns the country of production to the equipment losses.

    Requires:
    - `EquipmentLoss.country_of_production_flag_url`
    """
    logger.info("Assigning country of production flags to equipment losses")

    lf = lf.with_columns(
        pl.col("country_of_production_flag_url")
        .map_dict(mapper)
        .alias("country_of_production")
    )
    return lf


@wrappers.force_lazyframe
@wrappers.inject_default_logger
def assign_evidence_source(lf: pl.LazyFrame, *, logger: logging.Logger) -> pl.LazyFrame:
    """Assigns the evidence source to the equipment losses.

    Requires:
    - `EquipmentLoss.evidence_url`
    """
    logger.info("Assigning evidence sources to equipment losses")
    lf = lf.with_columns(
        pl.col("oryx_evidence_url")
        .apply(lambda x: urlparse(x).netloc)
        .map_dict(DOMAIN_SOURCE_MAP)
        .alias("evidence_source")
    )
    return lf


@wrappers.force_lazyframe
@wrappers.inject_default_logger
def calculate_url_hash(lf: pl.LazyFrame, *, logger: logging.Logger) -> pl.LazyFrame:
    """Calculates the SHA-256 of the UTF-8 encoded URL.

    Requires:
    - `EquipmentLoss.evidence_url`
    """
    logger.info("Calculating URL hashes")
    lf = lf.with_columns(
        pl.col("oryx_evidence_url")
        .apply(lambda url: hashlib.sha256(url.encode("utf-8")).hexdigest())
        .alias("url_hash")
    )
    return lf


@wrappers.force_lazyframe
@wrappers.inject_default_logger
def resolve_aircraft_and_naval_page_updates(
    lf: pl.LazyFrame, lookup: pl.LazyFrame, *, logger: logging.Logger
) -> pl.LazyFrame:
    """Removes losses from the old 'Aircraft' and 'Naval Ships' sections. These were
    replaced by the 'List of Naval Losses' and 'List of Aircraft Losses' pages.

    Requires:
    - `EquipmentLoss.country`
    - `EquipmentLoss.category`
    - `EquipmentLoss.model`
    - `EquipmentLoss.url_hash`
    """
    """Removes aircraft and naval losses that exist on the new pages."""
    agg = (
        lf.groupby(
            "country",
            "model",
            "url_hash",
        )
        .agg(pl.col("category").unique().alias("categories"))
        .with_columns(
            (
                pl.col("categories").list.contains(pl.lit("Aircraft"))
                | pl.col("categories").list.contains(pl.lit("Naval Ships"))
            ).alias("from_original"),
            pl.col("categories").list.lengths().alias("pages_shared_on"),
        )
    )

    # Exclude old losses that were added to the new pages
    # Find the losses that were added to the new pages
    to_replace = agg.filter(pl.col("from_original") & (pl.col("pages_shared_on") > 1))
    # Add a marker column
    to_replace = to_replace.with_columns(pl.lit(1).alias("to_replace"))
    lf = lf.join(
        to_replace,
        on=[
            "country",
            "model",
            "url_hash",
        ],
        how="left",
    ).filter(
        # Filters for cases that are not in the to_replace table or, if they are,
        # are not the old aircraft or naval category
        pl.col("to_replace").is_null()
        | (
            pl.col("to_replace").is_not_null()
            & pl.col("category").is_in(["Aircraft", "Naval Ships"]).is_not()
        )
    )

    lf = lf.join(
        lookup,
        left_on=[
            "category",
            "model",
        ],
        right_on=["old_category", "model"],
        how="left",
    ).with_columns(
        pl.when(pl.col("new_category").is_not_null())
        .then(pl.col("new_category"))
        .otherwise(pl.col("category"))
        .alias("category"),
    )

    lf = lf.drop(
        "categories",
        "from_original",
        "new_category",
        "pages_shared_on",
        "to_replace",
    )
    return lf


@wrappers.force_lazyframe
@wrappers.inject_default_logger
def calculate_case_id(lf: pl.LazyFrame, *, logger: logging.Logger) -> pl.LazyFrame:
    """Calculates the case ID for each case. The case ID helps discriminate
    situations where multiple assets are identified in the same evidence.

    Requires:
    - `EquipmentLoss.country`
    - `EquipmentLoss.category`
    - `EquipmentLoss.model`
    - `EquipmentLoss.url_hash`

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
    lf = lf.with_columns(pl.lit(1).alias("case_id")).with_columns(
        pl.col("case_id")
        .cumsum()
        .over(
            "country",
            "category",
            "model",
            "url_hash",
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
    df: pl.DataFrame,
    country_url_mapper: dict[str, str],
    category_corrections: pl.DataFrame,
    as_of_date: datetime.datetime,
) -> pl.DataFrame:
    """Performs basic preprocessing on the DataFrame.

    Parameters
    ----------
    df : pl.DataFrame
        The DataFrame to clean.
    country_url_mapper : dict[str, str]
        A dictionary mapping country flag URLs to their unique identifier.
    category_corrections : pl.DataFrame
        A DataFrame mapping old categories to new categories.
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
            pl.lit(as_of_date, dtype=pl.Datetime).alias("as_of_date"),
        )
        .collect()
        .lazy()
    )

    # Clean strings
    lf = (
        lf.with_columns(
            pl.col("category").str.strip(),
            pl.col("model").str.strip(),
            pl.col("oryx_evidence_url").str.strip(),
            pl.col("country_of_production_flag_url").str.strip(),
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
            .pipe(resolve_aircraft_and_naval_page_updates, category_corrections.lazy())
            .pipe(calculate_case_id)
        )
        .collect()
        .lazy()
    )

    # Order columns
    lf = lf.select(
        "country",
        "category",
        "model",
        "url_hash",
        "case_id",
        "is_abandoned",
        "is_captured",
        "is_damaged",
        "is_destroyed",
        "is_scuttled",
        "is_stripped",
        "is_sunk",
        "is_raised",
        "oryx_evidence_url",
        "country_of_production",
        "evidence_source",
        "oryx_description",
        "oryx_id",
        "country_of_production_flag_url",
        "as_of_date",
    )
    return lf.collect()
