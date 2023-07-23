"""
Schema for the Borderlands dataset.
"""
import dataclasses as dc
import enum
from typing import Iterator

import polars as pl


class Tag(enum.Enum):
    """A class to hold all tags for the fields."""

    attribute = "attribute"
    context = "context"
    debug = "debug"
    dimension = "dimension"
    equipment = "equipment"
    media = "media"
    metadata = "metadata"

    def __eq__(self, __value: object) -> bool:
        """Overrides the equality operator to allow for string comparison."""
        if isinstance(__value, str):
            return self.value == __value
        elif isinstance(__value, Tag):
            return self.value == __value.value
        return super().__eq__(__value)


TagSet = list[Tag | str]


@dc.dataclass
class Field:
    dtype: pl.DataType
    tags: TagSet = dc.field(default_factory=list)
    name: str = None


class Schema:
    """Base class to create a schema with. It provides a `__fields__` attribute that is
    a dictionary of the fields of the model.
    """

    __fields__: dict[str, Field] = {}

    def __init_subclass__(cls) -> None:
        """Adds fields to the __fields__ registry."""
        for k, v in cls.__dict__.items():
            if isinstance(v, Field):
                cls.__fields__[k] = v
                if v.name is None:
                    v.name = k
        return cls

    @classmethod
    def iter(
        cls,
        include: TagSet | None = None,
        exclude: TagSet | None = None,
    ) -> Iterator[Field]:
        """Iterates over the fields of the schema and yields the name and field object. Filters fields based on the `include` and `exclude` parameters.

        Args:
            include (TagSet, optional): A list of tags to include. Defaults to None (no inclusion requirement).
            exclude (TagSet, optional): A list of tags to exclude. Defaults to None (no exclusion filter).

        Yields:
            Iterator[tuple[str, Field]]: A tuple of the field name and field object.
        """
        for f in cls.__fields__.values():
            if include and all(t not in include for t in f.tags):
                continue
            if exclude and any(t in exclude for t in f.tags):
                continue
            yield f

    @classmethod
    def columns(
        cls,
        include: TagSet | None = None,
        exclude: TagSet | None = None,
    ) -> list[str]:
        return [f.name for f in cls.iter(include=include, exclude=exclude)]

    @classmethod
    def schema(
        cls,
        include: TagSet | None = None,
        exclude: TagSet | None = None,
    ) -> dict[str, pl.DataType]:
        """Returns a dictionary schema for Polars.

        Args:
            include (TagSet, optional): A list of tags to include. Defaults to None (no inclusion requirement).
            exclude (TagSet, optional): A list of tags to exclude. Defaults to None (no exclusion filter).

        Returns:
            dict[str, pl.DataType]: A dictionary of the field names and their data types.
        """
        return {f.name: f.dtype for f in cls.iter(include=include, exclude=exclude)}


class EquipmentLoss(Schema):
    """Schema for the equipment model."""

    # Dimensions
    country: Field = Field(pl.Utf8, tags=[Tag.dimension])
    category: Field = Field(pl.Utf8, tags=[Tag.dimension])
    model: Field = Field(pl.Utf8, tags=[Tag.dimension])
    url_hash: Field = Field(pl.Utf8, tags=[Tag.dimension])
    case_id = Field(pl.Int32, tags=[Tag.dimension])

    # Attributes
    status = Field(pl.List(pl.Utf8), tags=[Tag.attribute])
    evidence_url = Field(pl.Utf8, tags=[Tag.attribute, Tag.media])

    # Equipment Model Context
    country_of_production = Field(pl.Utf8, tags=[Tag.context, Tag.equipment])
    country_of_production_flag_url = Field(
        pl.Utf8, tags=[Tag.context, Tag.debug, Tag.equipment]
    )

    # Context
    evidence_source = Field(pl.Utf8, tags=[Tag.context, Tag.equipment])

    # Lineage/debugging
    description = Field(pl.Utf8, tags=[Tag.context, Tag.debug])
    id_ = Field(pl.Int32, tags=[Tag.context, Tag.debug])

    # Metadata
    as_of_date = Field(pl.Datetime, tags=[Tag.metadata])
