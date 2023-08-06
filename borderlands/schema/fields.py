"""A module for defining dataset schemas for Polars.
"""
import dataclasses as dc

import polars as pl

from .tags import TagSet


@dc.dataclass
class Field:
    """A class to hold the field information for a schema."""

    dtype: pl.DataType
    tags: TagSet = dc.field(default_factory=list)
    name: str = None
    description: str | None = None

    @property
    def col(self) -> pl.Expr:
        """Returns a column expression for the field."""
        return pl.col(self.name)

    def __eq__(self, __value: object) -> bool:
        """Returns whether the field is equal to the value."""
        if isinstance(__value, Field):
            return (self.name == __value.name) and (self.dtype == __value.dtype)
        return super().__eq__(__value)

    def __repr__(self) -> str:
        """Returns the string representation of the field."""
        return f"{self.name}({self.dtype})"
