"""
Schema for the Borderlands dataset.
"""
import dataclasses as dc
import enum
from typing import Iterator

import polars as pl


@dc.dataclass
class Field:
    dtype: pl.DataType
    tags: "list[str | Tags]" = dc.field(default_factory=list)
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

    def __init__(mcs, name: str, bases: tuple, newattrs: dict) -> None:
        """Adds fields to the class.

        This method adds fields to the class and sets the `__fields__` attribute.
        """

    @classmethod
    def iter(
        cls, include: list[str] = None, exclude: list[str] = None
    ) -> Iterator[Field]:
        """Iterates over the fields of the schema and yields the name and field object. Filters fields based on the `include` and `exclude` parameters.

        Args:
            include (list[str], optional): A list of tags to include. Defaults to None (no inclusion requirement).
            exclude (list[str], optional): A list of tags to exclude. Defaults to None (no exclusion filter).

        Yields:
            Iterator[tuple[str, Field]]: A tuple of the field name and field object.
        """
        for n, f in cls.__fields__.items():
            if include and all(t not in include for t in f.tags):
                continue
            if exclude and any(t in exclude for t in f.tags):
                continue
            yield f

    @classmethod
    def columns(cls, include: list[str] = None, exclude: list[str] = None) -> list[str]:
        return [f.name for f in cls.iter(include=include, exclude=exclude)]

    @classmethod
    def schema(
        cls, include: list[str] = None, exclude: list[str] = None
    ) -> dict[str, pl.DataType]:
        """Returns a dictionary schema for Polars.

        Args:
            include (list[str], optional): A list of tags to include. Defaults to None (no inclusion requirement).
            exclude (list[str], optional): A list of tags to exclude. Defaults to None (no exclusion filter).

        Returns:
            dict[str, pl.DataType]: A dictionary of the field names and their data types.
        """
        return {f.name: f.dtype for f in cls.iter(include=include, exclude=exclude)}


class Tags(enum.Enum):
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
        elif isinstance(__value, Tags):
            return self.value == __value.value
        return super().__eq__(__value)


class EquipmentLoss(Schema):
    """Schema for the equipment model."""

    # Dimensions
    country: Field = Field(pl.Utf8, tags=[Tags.dimension])
    category: Field = Field(pl.Utf8, tags=[Tags.dimension])
    model: Field = Field(pl.Utf8, tags=[Tags.dimension])
    url_hash: Field = Field(pl.Utf8, tags=[Tags.dimension])
    case_id = Field(pl.Int32, tags=[Tags.dimension])

    # Attributes
    status = Field(pl.List(pl.Utf8), tags=[Tags.attribute])
    evidence_url = Field(pl.Utf8, tags=[Tags.attribute, Tags.media])

    # Equipment Model Context
    country_of_production = Field(pl.Utf8, tags=[Tags.context, Tags.equipment])
    country_of_production_flag_url = Field(
        pl.Utf8, tags=[Tags.context, Tags.debug, Tags.equipment]
    )

    # Evidence Context
    evidence_source = Field(pl.Utf8, tags=[Tags.context, Tags.equipment])
    media_key = Field(pl.Utf8, tags=[Tags.context, Tags.equipment])

    # Lineage/debugging
    description = Field(pl.Utf8, tags=[Tags.context, Tags.debug])

    # Metadata
    as_of_date = Field(pl.Datetime, tags=[Tags.metadata])
    failed_duplicate_check = Field(pl.Boolean, tags=[Tags.metadata])
