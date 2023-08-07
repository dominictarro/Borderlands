"""
Creates markdown documentation for the schema.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl

if TYPE_CHECKING:
    from .dataset import Dataset
    from .fields import Field
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
    """Object to create documentation from a dataset.

    Args:
        dataset (Dataset): The dataset to generate documentation for.
        level (int, optional): The header level of the documentation. Defaults to 2.
    """

    def __init__(self, dataset: Dataset, level: int = 2) -> None:
        self.dataset = dataset
        self.level = level
        assert self.level in range(1, 5), "Level must be between in range [1, 4]."

    def format(
        self, include: FieldFilter | None = None, exclude: FieldFilter | None = None
    ) -> str:
        """Formats the schema into markdown.

        Args:
            schema (Schema): The schema to format.
            include (FieldFilter, optional): A list of conditions to require for fields to be included. Performs an OR operation.
            exclude (FieldFilter, optional): A list of conditions to exclude fields with. Performs an OR operation.

        Returns:
            str: The formatted schema.
        """
        return "\n\n".join(
            [
                self._format_header(),
                self._format_description(),
                self._format_schema(include, exclude),
            ]
        )

    def _format_header(self) -> str:
        """Formats the header of the schema.

        Args:
            schema (Schema): The schema to format.

        Returns:
            str: The formatted header.
        """
        return f"{'#' * self.level} {self.dataset.label}"

    def _format_description(self) -> str:
        """Formats the description of the schema.

        Args:
            schema (Schema): The schema to format.

        Returns:
            str: The formatted description.
        """
        return self.dataset.description

    def _format_schema(
        self, include: FieldFilter | None = None, exclude: FieldFilter | None = None
    ) -> str:
        """Formats the schema.

        Args:
            schema (Schema): The schema to format.
            include (FieldFilter, optional): A list of conditions to require for fields to be included. Performs an OR operation.
            exclude (FieldFilter, optional): A list of conditions to exclude fields with. Performs an OR operation.

        Returns:
            str: The formatted schema.
        """
        return (
            f"{'#' * (self.level + 1)} Schema"
            + "\n\n"
            + self._format_fields(include=include, exclude=exclude)
        )

    def _format_fields(
        self, include: FieldFilter | None = None, exclude: FieldFilter | None = None
    ) -> str:
        """Formats the fields of the schema.

        Args:
            schema (Schema): The schema to format.
            include (FieldFilter, optional): A list of conditions to require for fields to be included. Performs an OR operation.
            exclude (FieldFilter, optional): A list of conditions to exclude fields with. Performs an OR operation.

        Returns:
            str: The formatted fields.
        """
        return (
            self._create_field_header()
            + "\n"
            + "\n".join(
                [
                    self._format_field(f)
                    for f in self.dataset.schema.iter(include=include, exclude=exclude)
                ]
            )
        )

    def _create_field_header(self) -> str:
        """Creates the field header.

        Returns:
            str: The field header.
        """
        return "| Name | Type | Description |" "\n" "| :--- | :--- | :----------- |"

    def _format_field(self, field: Field) -> str:
        """Creates a markdown row for the `field`.

        Args:
            field (Field): The field to format.

        Returns:
            str: The formatted field.
        """
        return f"| {field.name} | {format_type(field.dtype)} | {field.description} |"
