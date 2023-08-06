"""
Flow to release the Borderlands dataset to Kaggle.
"""
import datetime
import enum
import json
import tempfile
from contextlib import contextmanager
from pathlib import Path

from prefect import flow, task
from prefect.blocks.system import Secret
from prefect.context import get_run_context
from prefect.utilities.asyncutils import sync_compatible

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
except OSError:
    from kaggle.api.kaggle_api_extended import KaggleApi

from kaggle.rest import ApiException

from borderlands.definitions import oryx
from borderlands.schema import Dataset, Tag, TagSet

__project__ = Path(__file__).parent.parent


class DatasetStatus(enum.Enum):
    """The status of a dataset."""

    EXISTS = enum.auto()
    DOES_NOT_EXIST = enum.auto()


@sync_compatible
async def get_kaggle_authentication_config() -> dict:
    """Get the Kaggle authentication config."""
    return {
        "username": (await Secret.load("secret-kaggle-username")).get(),
        "key": (await Secret.load("secret-kaggle-key")).get(),
    }


def get_dataset_metadata() -> dict:
    """Get the dataset metadata."""
    with open(__project__ / "kaggle" / "dataset-metadata.json", "r") as f:
        return json.load(f)


def get_kaggle_client() -> KaggleApi:
    """Get a Kaggle API client."""
    api = KaggleApi()
    api._load_config(get_kaggle_authentication_config())
    return api


def update_description(metadata: dict) -> dict:
    """Updates the description in the dataset metadata file.

    Args:
        metadata (dict): The dataset metadata.

    Returns:
        dict: The updated dataset metadata.
    """
    with open(__project__ / "kaggle" / "README.md", "r") as f:
        metadata["description"] = f.read()
    return metadata


def assess_dataset_status(api: KaggleApi, metadata: dict) -> DatasetStatus:
    """Assess the status of the dataset.

    Args:
        api (KaggleApi): The Kaggle API client.
        metadata (dict): The dataset metadata.

    Returns:
        DatasetStatus: The status of the dataset.
    """
    try:
        # Dataset exists, create new version
        api.dataset_status(metadata["id"])
        return DatasetStatus.EXISTS
    except ApiException as e:
        if e.reason == "Forbidden" and e.status == 403:
            return DatasetStatus.DOES_NOT_EXIST
        raise e


def stage_dataset_as_json(
    dataset: Dataset,
    folder: str | Path,
    include: TagSet | None = None,
    exclude: TagSet | None = None,
) -> Path:
    """Stage a dataset as JSON records.

    Args:
        dataset (Dataset): The dataset to stage.
        folder (str | Path): The folder to stage the dataset to.
        include (TagSet, optional): A list of tags to include. Defaults to None (no inclusion requirement).
        exclude (TagSet, optional): A list of tags to exclude. Defaults to None (no exclusion filter).

    Returns:
        Path: The path to the staged dataset.
    """
    df = dataset.read(include, exclude)
    path = Path(folder) / f"{dataset.label}.json"
    df.write_json(path, row_oriented=True)
    return path


@contextmanager
def staged_datasets_as_json(metadata: dict):
    """Stage a list of datasets as JSON records.

    Args:
        metadata (dict): The dataset metadata.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Add the metadata file
        with open(Path(tmpdir) / "dataset-metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)

        # Add the datasets
        stage_dataset_as_json(oryx, tmpdir, exclude=[Tag.metadata, Tag.debug])
        try:
            yield tmpdir
        finally:
            pass


@task
def create_kaggle_dataset(api: KaggleApi, metadata: dict):
    """Create a new dataset.

    Args:
        api (KaggleApi): The Kaggle API client.
        metadata (dict): The dataset metadata.
    """
    with staged_datasets_as_json(metadata) as tmpdir:
        api.dataset_create_new(
            tmpdir, public=metadata["isPrivate"] is False, quiet=False
        )


@task
def update_kaggle_dataset(api: KaggleApi, metadata: dict, date: datetime.date):
    """Update the dataset.

    Args:
        api (KaggleApi): The Kaggle API client.
        metadata (dict): The dataset metadata.
        date (datetime.date): The date of the release.

    """
    with staged_datasets_as_json(metadata) as tmpdir:
        api.dataset_create_version(
            tmpdir,
            version_notes=f"{date.strftime(r'%Y-%m-%d')} Release",
            quiet=False,
            delete_old_versions=False,
        )


@flow(
    name="Release Dataset to Kaggle",
    log_prints=True,
)
def release_dataset_to_kaggle():
    """Make the Kaggle dataset."""
    api = get_kaggle_client()
    metadata = get_dataset_metadata()
    metadata = update_description(metadata)
    status = assess_dataset_status(api, metadata)

    if status == DatasetStatus.DOES_NOT_EXIST:
        create_kaggle_dataset(api, metadata)
    elif status == DatasetStatus.EXISTS:
        update_kaggle_dataset(
            api, metadata, get_run_context().flow_run.expected_start_time.date()
        )
    else:
        raise ValueError(f"Unknown dataset status {status}")
