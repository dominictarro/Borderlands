"""
Pytest configuration for Oryx.
"""
import json
from pathlib import Path

import bs4
import pytest
from _pytest.monkeypatch import MonkeyPatch
from prefect import filesystems
from prefect.tasks import Task

from borderlands.oryx.oryx_parser.article import ArticleParser
from borderlands.utilities.blocks import create_child_bucket, task_persistence_subfolder


@pytest.fixture
def bucket_dummy_path(output_path: Path) -> Path:
    """Path to the dummy bucket."""
    dummy = output_path / "oryx-dummy-buckets"
    dummy.mkdir(exist_ok=True)
    return dummy


@pytest.fixture
def oryx_ukraine_webpage(test_data_path: Path) -> bs4.Tag:
    """Path to the Oryx Ukraine webpage."""
    with open(test_data_path / "oryx" / "pages" / "ukraine.html", "r") as fo:
        return bs4.BeautifulSoup(fo.read(), features="html.parser")


@pytest.fixture
def oryx_russia_webpage(test_data_path: Path) -> bs4.Tag:
    """Path to the Oryx Ukraine webpage."""
    with open(test_data_path / "oryx" / "pages" / "russia.html", "r") as fo:
        return bs4.BeautifulSoup(fo.read(), features="html.parser")


@pytest.fixture
def oryx_descriptions(test_data_path: Path) -> list[str]:
    """Descriptions of the Oryx articles."""
    with open(test_data_path / "oryx" / "descriptions.txt", "r") as fo:
        return [line.strip() for line in fo.readlines()]


@pytest.fixture
def oryx_evidence_urls(test_data_path: Path) -> list[str]:
    """URLs of the Oryx evidence."""
    with open(test_data_path / "oryx" / "evidence_urls.txt", "r") as fo:
        return [line.strip() for line in fo.readlines()]


@pytest.fixture
def oryx_flag_urls(test_data_path: Path) -> list[str]:
    """URLs of the Oryx flags."""
    with open(
        test_data_path / "oryx" / "country_of_production_flag_urls.txt", "r"
    ) as fo:
        return [line.strip() for line in fo.readlines()]


@pytest.fixture
def flag_url_mapper(test_data_path: Path) -> dict[str, str]:
    """URLs of the Oryx flags."""
    with open(
        test_data_path / "oryx" / "assets" / "country_of_production_url_mapping.json",
        "r",
    ) as fo:
        data = json.load(fo)
        return {k: v["Alpha-3"] for k, v in data.items()}


@pytest.fixture
def landed_file_path(test_data_path: Path) -> Path:
    """Path to the landed file."""
    return test_data_path / "oryx" / "landed.json"


@pytest.fixture
def oryx_bucket(test_bucket: filesystems.LocalFileSystem, monkeypatch: MonkeyPatch):
    from borderlands.oryx import blocks

    oryx_bucket = create_child_bucket(
        "borderlands-core", "-core", test_bucket, save=True
    )
    monkeypatch.setattr(blocks, "oryx_bucket", oryx_bucket)
    yield oryx_bucket


@pytest.fixture
def oryx_landing_bucket(oryx_bucket: Path, monkeypatch: MonkeyPatch):
    landing_bucket = create_child_bucket("landing", "-landing", oryx_bucket)
    Path(landing_bucket.basepath).mkdir(exist_ok=True, parents=True)
    from borderlands.oryx import blocks

    monkeypatch.setattr(blocks, "landing_bucket", landing_bucket)
    yield landing_bucket


@pytest.fixture
def oryx_media_bucket(test_bucket: Path, monkeypatch: MonkeyPatch):
    media_bucket = create_child_bucket("borderlands-media", "-media", test_bucket)
    Path(media_bucket.basepath).mkdir(exist_ok=True, parents=True)
    from borderlands.oryx import blocks

    monkeypatch.setattr(blocks, "media_bucket", media_bucket)
    yield media_bucket


@pytest.fixture
def oryx_assets_bucket(oryx_bucket: Path, monkeypatch: MonkeyPatch):
    assets_bucket = create_child_bucket("assets", "-assets", oryx_bucket)
    Path(assets_bucket.basepath).mkdir(exist_ok=True, parents=True)
    from borderlands.oryx import blocks

    monkeypatch.setattr(blocks, "assets_bucket", assets_bucket)
    yield assets_bucket


@pytest.fixture
def oryx_persistence_bucket(test_bucket: Path, monkeypatch: MonkeyPatch):
    persistence_bucket = create_child_bucket(
        "borderlands-persistence", "-persistence", test_bucket
    )
    Path(persistence_bucket.basepath).mkdir(exist_ok=True, parents=True)
    from borderlands.oryx import blocks

    monkeypatch.setattr(blocks, "persistence_bucket", persistence_bucket)
    yield persistence_bucket


@pytest.fixture(autouse=False, scope="function")
def mock_oryx_persistence_bucket_functions(
    oryx_persistence_bucket: Path, monkeypatch: MonkeyPatch
):
    """Creates a bucket that outputs to the 'tests/' directory's 'output/'."""
    from borderlands.oryx.media_stage.extract import core as media_core
    from borderlands.oryx.media_stage.extract import postimg as media_postimg
    from borderlands.oryx.stage import extract, transform

    for module in (extract, transform, media_core, media_postimg):
        for attr, value in module.__dict__.items():
            if isinstance(value, Task) and value.persist_result:
                value = task_persistence_subfolder(oryx_persistence_bucket)(value)
                monkeypatch.setattr(module, attr, value)


@pytest.fixture(autouse=False, scope="function")
def mock_blocks_import(
    test_bucket,
    oryx_bucket,
    oryx_landing_bucket,
    oryx_media_bucket,
    oryx_assets_bucket,
    oryx_persistence_bucket,
    monkeypatch,
):
    """Mocks the import of the blocks module."""
    import borderlands.oryx.blocks as blocks

    monkeypatch.setattr(blocks, "bucket", test_bucket)
    monkeypatch.setattr(blocks, "oryx_bucket", oryx_bucket)
    monkeypatch.setattr(blocks, "landing_bucket", oryx_landing_bucket)
    monkeypatch.setattr(blocks, "media_bucket", oryx_media_bucket)
    monkeypatch.setattr(blocks, "assets_bucket", oryx_assets_bucket)
    monkeypatch.setattr(blocks, "persistence_bucket", oryx_persistence_bucket)
    yield blocks


# NOTE DO NOT AUTOUSE
# When autouse is set there will be conflicts in the persistence block
# It is imported into these modules, but not updated with the mock bucket
@pytest.fixture(autouse=False, scope="function")
def mock_oryx_page_request(test_data_path: Path, monkeypatch: MonkeyPatch):
    """Mock the Cvent API to prevent API rate limit excession."""
    import requests

    def mock_request_page(url: str, *args, **kwds) -> requests.Response:
        """Mocks the extract_pages function to use a file in the tests/data directory."""
        folder = test_data_path / "oryx" / "pages"
        filename: str | None = None
        if (
            url
            == "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html"
        ):
            filename = "russia.html"
        elif (
            url
            == "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html"
        ):
            filename = "ukraine.html"

        if filename is None:
            raise ValueError(f"URL not mocked: {url}")

        with open(folder / filename, "r") as f:
            response = requests.Response()
            response.status_code = 200
            response._content = f.read().encode()
            return response

    monkeypatch.setattr(requests, "get", mock_request_page)


@pytest.fixture(autouse=False, scope="function")
def mock_asset_request(test_data_path: Path, monkeypatch):
    """Mock the asset request to prevent API rate limit excession."""
    from borderlands.oryx import assets

    def mock_request_asset(asset_name: str) -> list[dict]:
        """Mocks the extract_pages function to use a file in the tests/data directory."""
        folder = test_data_path / "oryx" / "assets"
        filename: str | None = None
        if asset_name == "country_of_production_url_mapping.json":
            filename = "country_of_production_url_mapping.json"

        if filename is None:
            raise ValueError(f"Asset not mocked: {asset_name}")

        with open(folder / filename, "rb") as f:
            return f.read()

    monkeypatch.setattr(assets, "get_asset", mock_request_asset)


@pytest.fixture
def ukraine_article_parser(oryx_ukraine_webpage: bs4.Tag) -> "ArticleParser":
    """An `ArticleParser` object."""
    body = oryx_ukraine_webpage.find(
        attrs={"class": "post-body entry-content", "itemprop": "articleBody"}
    )
    from borderlands.oryx.oryx_parser.article import UKRAINE_DATA_SECTION_INDEX

    yield ArticleParser(body, UKRAINE_DATA_SECTION_INDEX)


@pytest.fixture
def russia_article_parser(oryx_russia_webpage: bs4.Tag) -> "ArticleParser":
    """An `ArticleParser` object."""
    body = oryx_russia_webpage.find(
        attrs={"class": "post-body entry-content", "itemprop": "articleBody"}
    )
    from borderlands.oryx.oryx_parser.article import RUSSIA_DATA_SECTION_INDEX

    yield ArticleParser(body, RUSSIA_DATA_SECTION_INDEX)


@pytest.fixture
def ukraine_page_parse_result(ukraine_article_parser: "ArticleParser") -> list:
    """The result of parsing the Ukraine page."""
    yield list(ukraine_article_parser.parse())


@pytest.fixture
def russia_page_parse_result(russia_article_parser: "ArticleParser") -> list:
    """The result of parsing the Russia page."""
    yield list(russia_article_parser.parse())
