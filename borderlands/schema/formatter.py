"""
Creates markdown documentation for the schema.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dataset import Dataset
    from .fields import Field


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

    def __call__(self) -> str:
        """Formats the schema into markdown.

        Args:
            schema (Schema): The schema to format.

        Returns:
            str: The formatted schema.
        """
        return "\n\n".join(
            [
                self._format_header(),
                self._format_description(),
                self._format_schema(),
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

    def _format_schema(self) -> str:
        """Formats the schema.

        Args:
            schema (Schema): The schema to format.

        Returns:
            str: The formatted schema.
        """
        return f"{'#' * (self.level + 1)} Schema" + "\n\n" + self._format_fields()

    def _format_fields(self) -> str:
        """Formats the fields of the schema.

        Args:
            schema (Schema): The schema to format.

        Returns:
            str: The formatted fields.
        """
        return (
            self._create_field_header()
            + "\n"
            + "\n".join([self._format_field(f) for f in self.dataset.schema.iter()])
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
        return f"| {field.name} | {field.dtype} | {field.description} |"
