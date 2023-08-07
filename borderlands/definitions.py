"""
Schema for the Borderlands dataset.
"""
import polars as pl

from .schema import Dataset, Field, Schema, Tag


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


##############################################################################
# DATASETS
##############################################################################

oryx = Dataset(
    label="Oryx",
    host_bucket="s3-bucket-borderlands-core",
    release_path="releases/oryx.parquet",
    schema=EquipmentLoss,
    description=(
        "The Oryx dataset is a complete collection of the equipment losses in the Oryx database. The loss cases have been cleaned and transformed into JSON objects."
        "\n\n### Sources"
        "\n\n - [Attack On Europe: Documenting Ukrainian Equipment Losses During The 2022 Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html)"
        "\n - [Attack On Europe: Documenting Russian Equipment Losses During The 2022 Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html)"
        "\n - [List Of Naval Losses During The Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/03/list-of-naval-losses-during-2022.html)"
        "\n - [List Of Aircraft Losses During The Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/03/list-of-aircraft-losses-during-2022.html)"
    ),
)

media_inventory = Dataset(
    label="Media Inventory",
    host_bucket="s3-bucket-borderlands-core",
    release_path="releases/media-inventory.parquet",
    schema=Media,
)
