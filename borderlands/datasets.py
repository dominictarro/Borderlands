"""
All datasets being released are defined in this file. This allows for a single
source of truth and easier referencing.
"""
import dataclasses as dc
import io

import polars as pl

from . import blocks


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

    def read(self) -> pl.DataFrame:
        """Read the dataset's latest release."""
        with io.BytesIO() as f:
            blocks.core_bucket.download_object_to_file_object(self.release_path, f)
            f.seek(0)
            return pl.read_parquet(f)


oryx = Dataset(
    label="Oryx",
    host_bucket="s3-bucket-borderlands-core",
    release_path="releases/oryx.parquet",
)

media_inventory = Dataset(
    label="Media Inventory",
    host_bucket="s3-bucket-borderlands-core",
    release_path="releases/media-inventory.parquet",
)
