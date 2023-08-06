"""
All datasets being released are defined in this file. This allows for a single
source of truth and easier referencing.
"""
import dataclasses as dc
import io

import polars as pl

from . import blocks
from .schema import EquipmentLoss, Media, Schema, TagSet


@dc.dataclass
class Dataset:
    """Dataset class for storing dataset information.

    Attributes:
        label (str): The label for the dataset.
        host_bucket (str): The host bucket to fetch the dataset from.
        release_path (str): The path to release the dataset to.

    """

    label: str
    host_bucket: str
    release_path: str
    schema: Schema

    def read(
        self, include: TagSet | None = None, exclude: TagSet | None = None
    ) -> pl.DataFrame:
        """Read the dataset's latest release.

        Args:
            include (TagSet, optional): A list of tags to include. Defaults to None (no inclusion requirement).
            exclude (TagSet, optional): A list of tags to exclude. Defaults to None (no exclusion filter).

        Returns:
            pl.DataFrame: The dataset's latest release.
        """
        with io.BytesIO() as f:
            blocks.core_bucket.download_object_to_file_object(self.release_path, f)
            f.seek(0)
            return (
                pl.scan_parquet(f)
                .select(self.schema.columns(include, exclude))
                .collect()
            )


oryx = Dataset(
    label="Oryx",
    host_bucket="s3-bucket-borderlands-core",
    release_path="releases/oryx.parquet",
    schema=EquipmentLoss,
)

media_inventory = Dataset(
    label="Media Inventory",
    host_bucket="s3-bucket-borderlands-core",
    release_path="releases/media-inventory.parquet",
    schema=Media,
)
