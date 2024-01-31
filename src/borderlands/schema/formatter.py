"""
Creates markdown documentation for the schema.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import tabulate

if TYPE_CHECKING:
    from .dataset import Dataset
    from .schema import FieldFilter


def format_type(dtype: pl.DataType) -> str:
    """Format a Polars type to a more legible type.

    Args:
        dtype (pl.DataType): The Polars type.

    Returns:
        str: Formatted type.
    """
    if dtype in (
        pl.Decimal,
        pl.Float32,
        pl.Float64,
        pl.Int8,
        pl.Int16,
        pl.Int32,
        pl.Int64,
        pl.UInt8,
        pl.UInt16,
        pl.UInt32,
        pl.UInt64,
    ):
        return "numeric"
    elif dtype == pl.Boolean:
        return "boolean"
    elif dtype in (pl.Categorical, pl.Utf8):
        return "string"
    elif dtype == pl.Date:
        return "date"
    elif dtype == pl.Datetime:
        return "datetime"
    elif dtype in (pl.Duration, pl.Time):
        return "timecode"
    elif isinstance(dtype, pl.List):
        return f"list({format_type(dtype.inner)})"
    elif isinstance(dtype, pl.Struct):
        return f"struct({', '.join([f'{field.name}: {format_type(field.dtype)}' for field in dtype.fields])})"
    else:
        if isinstance(dtype, pl.DataType):
            raise ValueError(f"Unsupported datatype {dtype}")
        else:
            raise ValueError(f"Unknown datatype {dtype}")


class Formatter:
    """Mixin to generate documention for a dataset."""

    def _format_header(self: Dataset, level: int) -> str:
        """Formats the header of the schema.

        Args:
            level (int): The level of the header.

        Returns:
            str: The formatted header.
        """
        return f"{'#' * level} {self.label}"

    def _format_schema(
        self: Dataset,
        include: FieldFilter | None = None,
        exclude: FieldFilter | None = None,
    ) -> str:
        """Format the schema into markdown.

        Args:
            include (FieldFilter, optional): A list of conditions to require for fields to be included. Performs an OR operation.
            exclude (FieldFilter, optional): A list of conditions to exclude fields with. Performs an OR operation.

        Returns:
            str: The formatted schema.
        """
        fields = [
            {"Name": f.name, "Type": format_type(f.dtype), "Description": f.description}
            for f in self.schema.iter(include=include, exclude=exclude)
        ]
        return tabulate.tabulate(fields, headers="keys", tablefmt="pipe")
