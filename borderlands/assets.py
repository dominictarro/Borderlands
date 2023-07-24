"""
Module for loading static assets in the pipeline's folder.
"""
from __future__ import annotations

import json
from typing import Dict

import polars as pl
from prefect import task

from . import blocks


def get_asset(asset_name: str) -> bytes:
    """Gets the asset from the assets folder.

    Parameters
    ----------
    asset_name : str
        Name of the asset

    Returns
    -------
    bytes
        Asset
    """
    return blocks.assets_bucket.read_path(asset_name)


@task
def get_country_of_production_url_mapper() -> Dict[str, str]:
    """Gets the country of production URL mapper from the assets folder.

    Structure is like

    ```json
    {
        "https://url_of_country_flag.com/": "Country's ISO Alpha-3 Code"
    }
    ```

    Returns
    -------
    Dict[str, str]
        Dictionary mapping URLs to ISO Alpha-3 country codes
    """
    data = get_asset("country_of_production_url_mapping.json")
    mapper: dict = json.loads(data)
    return {url: lookup["Alpha-3"] for url, lookup in mapper.items()}


@task
def get_category_corrections() -> pl.DataFrame:
    """Gets the category corrections from the assets folder.

    Returns
    -------
    pl.DataFrame
        DataFrame of category corrections
    """
    data = get_asset("category_corrections.csv")
    return pl.read_csv(data)
