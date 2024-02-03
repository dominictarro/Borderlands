import polars as pl
import pytest

from borderlands.schema.formatter import format_type


@pytest.mark.parametrize(
    "dtype, expected",
    [
        (pl.Decimal, "numeric"),
        (pl.Boolean, "boolean"),
        (pl.Categorical, "string"),
        (pl.Utf8, "string"),
        (pl.Date, "date"),
        (pl.Datetime, "datetime"),
        (pl.Duration, "timecode"),
        (pl.Struct({"a": pl.UInt8, "b": pl.Utf8}), "struct(a: numeric, b: string)"),
        (pl.List(pl.UInt8), "list(numeric)"),
        # nesting
        (
            pl.List(pl.Struct({"a": pl.UInt8, "b": pl.Utf8})),
            "list(struct(a: numeric, b: string))",
        ),
        (
            pl.Struct({"a": pl.List(pl.UInt8), "b": pl.Utf8}),
            "struct(a: list(numeric), b: string)",
        ),
        (
            pl.Struct({"a": pl.UInt8, "b": pl.Struct({"1": pl.Utf8})}),
            "struct(a: numeric, b: struct(1: string))",
        ),
    ],
)
def test_format_type(dtype: pl.DataType, expected: str):
    assert format_type(dtype) == expected
