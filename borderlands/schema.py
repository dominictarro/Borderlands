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
    inherited = "inherited"
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
    description: str = dc.field(default_factory=str)


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
    country: Field = Field(
        pl.Utf8,
        tags=[Tag.dimension],
        description="The country that suffered the equipment loss.",
    )
    category: Field = Field(
        pl.Utf8,
        tags=[Tag.dimension],
        description="The equipment category.",
    )
    model: Field = Field(
        pl.Utf8,
        tags=[Tag.dimension],
        description="The equipment model.",
    )
    url_hash: Field = Field(
        pl.Utf8,
        tags=[Tag.dimension],
        description="A SHA-256 hash of the `evidence_url`.",
    )
    case_id = Field(
        pl.Int32,
        tags=[Tag.dimension],
        description="A special ID for discriminating equipment losses when their `country`, `category`, `model`, and `url_hash` are the same.",
    )

    # Attributes
    status = Field(
        pl.List(pl.Utf8),
        tags=[Tag.attribute],
        description="The statuses of the equipment loss.",
    )
    evidence_url = Field(
        pl.Utf8,
        tags=[Tag.attribute, Tag.media],
        description="The URL to the evidence of the equipment loss.",
    )

    # Equipment Model Context
    country_of_production = Field(
        pl.Utf8,
        tags=[Tag.context, Tag.equipment],
        description="The ISO Alpha-3 code of the country that produces the `model`.",
    )
    country_of_production_flag_url = Field(
        pl.Utf8,
        tags=[Tag.context, Tag.debug, Tag.equipment],
        description="The URL to the flag of the country that produces the `model`.",
    )

    # Context
    evidence_source = Field(
        pl.Utf8,
        tags=[Tag.context, Tag.equipment],
        description="The source of the evidence.",
    )

    # Lineage/debugging
    description = Field(
        pl.Utf8,
        tags=[Tag.context, Tag.debug],
        description="The Oryx description the equipment loss was extracted from.",
    )
    id_ = Field(
        pl.Int32,
        tags=[Tag.context, Tag.debug],
        description="The Oryx ID the equipment loss was labeled with.",
    )

    # Metadata
    as_of_date = Field(
        pl.Datetime,
        tags=[Tag.metadata],
        description="The date the row was generated.",
    )


class Media(Schema):
    """Schema for the media model."""

    # Dimensions
    url_hash: Field = Field(
        pl.Utf8,
        tags=[Tag.dimension, Tag.inherited],
        description="A SHA-256 hash of the `url`.",
    )

    # Attributes
    url = Field(
        pl.Utf8,
        tags=[Tag.attribute, Tag.inherited],
        description="The URL to the evidence.",
    )
    evidence_source = Field(
        pl.Utf8,
        tags=[Tag.attribute, Tag.inherited],
        description="The source of the evidence.",
    )
    media_key = Field(
        pl.Utf8,
        tags=[Tag.attribute],
        description="The S3 Object Key to the media.",
    )
    file_type = Field(
        pl.Utf8,
        tags=[Tag.attribute],
        description="The file type/extension.",
    )
    media_type = Field(
        pl.Utf8,
        tags=[Tag.attribute],
        description="The media classification.",
    )

    # Metadata
    as_of_date = Field(
        pl.Datetime,
        tags=[Tag.metadata],
        description="The date the row was generated.",
    )
