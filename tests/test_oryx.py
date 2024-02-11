import logging

import polars as pl
import pytest

from borderlands.oryx import assign_status


@pytest.fixture(scope="module")
def logger():
    return logging.getLogger(__name__)


def test_assign_status(logger):
    df = pl.DataFrame(
        [
            ["was captured"],
            ["was destroyed"],
            ["was damaged"],
            ["was damagd"],
            ["was abandoned"],
            ["was abanonded"],
            ["was scuttled"],
            ["was stripped"],
            ["was sunk"],
            ["was raised"],
        ],
        schema=dict(oryx_description=pl.Utf8),
    )
    result = assign_status(df.lazy(), logger=logger).collect()
    EXPECTED_COLUMNS = [
        "oryx_description",
        "is_captured",
        "is_destroyed",
        "is_damaged",
        "is_abandoned",
        "is_scuttled",
        "is_stripped",
        "is_sunk",
        "is_raised",
    ]
    assert result.columns == EXPECTED_COLUMNS
    assert result.melt(
        id_vars=["oryx_description"],
        value_vars=EXPECTED_COLUMNS[1:],
        variable_name="status",
        value_name="is_status",
    ).filter(pl.col("is_status"))["status"].to_list() == [
        "is_captured",
        "is_destroyed",
        "is_damaged",
        "is_damaged",
        "is_abandoned",
        "is_abandoned",
        "is_scuttled",
        "is_stripped",
        "is_sunk",
        "is_raised",
    ]
