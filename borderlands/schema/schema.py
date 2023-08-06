"""A module for defining dataset schemas for Polars.
"""
import dataclasses as dc
from typing import Iterator

import polars as pl

from .fields import Field
from .tags import Tag

FieldFilter = list[Tag | str | pl.DataType]


class Schema:
    """Base class to create a schema with. It provides a `__fields__` attribute that is
    a dictionary of the fields of the model.
    """

    __fields__: dict[str, Field] = {}

    def __init_subclass__(cls) -> None:
        """Adds fields to the __fields__ registry."""
        cls.__fields__ = {}
        for k, v in cls.__dict__.items():
            if isinstance(v, Field):
                cls.__fields__[k] = v
                if v.name is None:
                    v.name = k
        return cls

    @classmethod
    def iter(
        cls,
        include: FieldFilter | None = None,
        exclude: FieldFilter | None = None,
    ) -> Iterator[Field]:
        """Iterates over the fields of the schema and yields the name and field object. Filters fields based on the `include` and `exclude` parameters.

        Args:
            include (FieldFilter, optional): A list of tags to include. Defaults to None (no inclusion requirement).
            exclude (FieldFilter, optional): A list of tags to exclude. Defaults to None (no exclusion filter).

        Yields:
            Iterator[tuple[str, Field]]: A tuple of the field name and field object.
        """
        _filter = Filter(include=include, exclude=exclude)
        for f in cls.__fields__.values():
            if _filter.is_included(f):
                yield f

    @classmethod
    def columns(
        cls,
        include: FieldFilter | None = None,
        exclude: FieldFilter | None = None,
    ) -> list[str]:
        return [f.name for f in cls.iter(include=include, exclude=exclude)]

    @classmethod
    def schema(
        cls,
        include: FieldFilter | None = None,
        exclude: FieldFilter | None = None,
    ) -> dict[str, pl.DataType]:
        """Returns a dictionary schema for Polars.

        Args:
            include (TagSet, optional): A list of tags to include. Defaults to None (no inclusion requirement).
            exclude (TagSet, optional): A list of tags to exclude. Defaults to None (no exclusion filter).

        Returns:
            dict[str, pl.DataType]: A dictionary of the field names and their data types.
        """
        return {f.name: f.dtype for f in cls.iter(include=include, exclude=exclude)}


@dc.dataclass
class Filter:
    """A class to hold the filter information for a schema."""

    include: FieldFilter | None = None
    exclude: FieldFilter | None = None

    @staticmethod
    def has_tag(f: Field, tag: Tag) -> bool:
        """Returns whether the field has the tag.

        Args:
            f (Field): The field to check.
            tag (Tag): The tag to check.

        Returns:
            bool: Whether the field has the tag.
        """
        return tag in f.tags

    @staticmethod
    def is_datatype(f: Field, dtype: pl.DataType) -> bool:
        """Returns whether the field is the correct data type.

        Args:
            f (Field): The field to check.
            dtype (pl.DataType): The data type to check.

        Returns:
            bool: Whether the field is a data type.
        """
        return f.dtype == dtype

    def is_included(self, field: Field) -> bool:
        """Returns whether the field is included in the filter.

        Args:
            field (Field): The field to check.

        Returns:
            bool: Whether the field is included in the filter.
        """
        if self.include:
            for condition in self.include:
                if isinstance(condition, pl.DataType):
                    if not self.is_datatype(field, condition):
                        return False
                elif isinstance(condition, (Tag, str)):
                    if not self.has_tag(field, condition):
                        return False

        if self.exclude:
            for condition in self.exclude:
                if isinstance(condition, pl.DataType):
                    if self.is_datatype(field, condition):
                        return False
                elif isinstance(condition, (Tag, str)):
                    if self.has_tag(field, condition):
                        return False

        return True
