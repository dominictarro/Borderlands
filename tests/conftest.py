"""
Pytest configuration.
"""
import datetime
from io import FileIO
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch
from prefect import filesystems
from prefect.testing.utilities import prefect_test_harness

TESTS_PATH: Path = Path(__file__).parent


@pytest.fixture
def output_path() -> Path:
    """Path to the output directory."""
    output_path = TESTS_PATH / "output"
    output_path.mkdir(exist_ok=True)
    return output_path


@pytest.fixture
def test_data_path() -> Path:
    """Path to the test data directory."""
    return TESTS_PATH / "data"


# Sets the test harness so prefect flow tests are not recorded in the Orion
# database.
#
# I use this at the session-level so that all flows are run within the same
# environment.
@pytest.fixture(autouse=True, scope="session")
def with_test_harness():
    """Sets the Prefect test harness for local pipeline testing."""
    with prefect_test_harness():
        yield


@pytest.fixture
def test_bucket(bucket_dummy_path: str, monkeypatch: MonkeyPatch) -> str:
    """Path to the test bucket."""

    def mock_list_objects(self, folder: str | None = None, *args, **kwargs):
        basepath = Path(self.basepath)
        if folder is not None:
            basepath = basepath / folder
        for path in (basepath).iterdir():
            if path.is_file():
                yield {
                    "Key": path.relative_to(bucket_dummy_path).as_posix(),
                    "LastModified": datetime.datetime.fromtimestamp(
                        path.lstat().st_mtime
                    ),
                }
            else:
                dir = Path(folder) / path if folder is not None else path
                yield from self.list_objects(folder=dir, *args, **kwargs)

    def mock_read_path(self, key: str) -> bytes:
        return (Path(self.basepath) / key).read_bytes()

    def mock_upload_from_file_object(self, fo: FileIO, key: str):
        dir = Path(key).parent
        abspath = Path(self.basepath) / dir
        abspath.mkdir(parents=True, exist_ok=True)
        absfile = abspath / Path(key).name

        # Write the file to the dummy bucket.
        with open(absfile, "wb") as f:
            chunk_size = 1024 * 1024
            chunk: bytes = b""
            for i, line in enumerate(fo):
                if i % chunk_size == 0:
                    f.write(chunk)
                    chunk = line
                else:
                    chunk += line
            f.write(chunk)

    LocalFileSystem = filesystems.LocalFileSystem
    LocalFileSystem.list_objects = mock_list_objects
    LocalFileSystem.read_path = mock_read_path
    LocalFileSystem.upload_from_file_object = mock_upload_from_file_object
    monkeypatch.setattr(filesystems, "LocalFileSystem", LocalFileSystem)

    bucket: filesystems.LocalFileSystem = LocalFileSystem(
        _block_document_name="test-bucket",
        _is_anonymous=True,
        basepath=str(bucket_dummy_path.absolute()),
    )
    bucket._block_document_id = bucket._save(
        "test-bucket",
        is_anonymous=True,
        overwrite=True,
    )

    from borderlands import storage

    monkeypatch.setattr(storage, "bucket", bucket)

    yield bucket
