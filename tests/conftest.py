"""
Pytest configuration.
"""

import gzip
import json
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

import bs4
import pytest
from _pytest.monkeypatch import MonkeyPatch
from prefect import task
from prefect.testing.utilities import prefect_test_harness
from prefect_aws import AwsCredentials, S3Bucket
from prefect_slack import SlackWebhook
from prefecto.logging import get_prefect_or_default_logger
from prefecto.testing.s3 import mock_bucket

if TYPE_CHECKING:
    from borderlands.parser.article import ArticleParser


TESTS_PATH: Path = Path(__file__).parent
EXPORT_PATH: Path = TESTS_PATH / "export"
if EXPORT_PATH.is_dir():
    shutil.rmtree(EXPORT_PATH)
EXPORT_PATH.mkdir(exist_ok=True)


@pytest.fixture
def test_data_path() -> Path:
    """Path to the test data directory."""
    return TESTS_PATH / "data"


@pytest.fixture(scope="session")
def credentials() -> AwsCredentials:
    """The AWS credentials."""
    yield AwsCredentials()


@pytest.fixture(scope="session")
def core_bucket(credentials: AwsCredentials) -> S3Bucket:
    """The core bucket."""
    yield S3Bucket(bucket_name="borderlands-core", credentials=credentials)


@pytest.fixture(scope="session")
def persistence_bucket(credentials: AwsCredentials) -> S3Bucket:
    """The persistence bucket."""
    yield S3Bucket(bucket_name="borderlands-persistence", credentials=credentials)


@pytest.fixture(scope="session")
def slack_webhook() -> SlackWebhook:
    """The Slack webhook."""
    yield SlackWebhook(
        _block_document_name="slack-webhook-borderlands",
        url="https://hooks.slack.com/services/...",
    )


@pytest.fixture(autouse=True, scope="session")
def prefect_db(slack_webhook, credentials, core_bucket, persistence_bucket):
    """Sets the Prefect test harness for local pipeline testing."""
    with prefect_test_harness():
        slack_webhook.save(name="slack-webhook-borderlands")
        credentials.save(name="aws-credentials-prefect")
        core_bucket.save(name="s3-bucket-borderlands-core")
        persistence_bucket.save(name="s3-bucket-borderlands-persistence")
        yield


@pytest.fixture(autouse=False, scope="function")
def mock_buckets(
    core_bucket: S3Bucket, persistence_bucket: S3Bucket, test_data_path: Path
):
    """Mocks the S3 buckets."""
    with mock_bucket(core_bucket.bucket_name):
        core_bucket.upload_from_folder(test_data_path / "buckets" / "borderlands-core")
        with mock_bucket(persistence_bucket.bucket_name, activate_moto=False):
            yield


@pytest.fixture
def oryx_descriptions(test_data_path: Path) -> list[str]:
    """Descriptions of the Oryx articles."""
    with open(test_data_path / "descriptions.txt", "r") as fo:
        return [line.strip() for line in fo.readlines()]


@pytest.fixture
def oryx_evidence_urls(test_data_path: Path) -> list[str]:
    """URLs of the Oryx evidence."""
    with open(test_data_path / "evidence_urls.txt", "r") as fo:
        return [line.strip() for line in fo.readlines()]


@pytest.fixture
def oryx_flag_urls(test_data_path: Path) -> list[str]:
    """URLs of the Oryx flags."""
    with open(test_data_path / "country_of_production_flag_urls.txt", "r") as fo:
        return [line.strip() for line in fo.readlines()]


@pytest.fixture
def flag_url_mapper(test_data_path: Path) -> dict[str, str]:
    """URLs of the Oryx flags."""
    with open(
        test_data_path
        / "buckets/borderlands-core/assets/country_of_production_url_mapping.json",
        "r",
    ) as fo:
        data = json.load(fo)
        return {k: v["Alpha-3"] for k, v in data.items()}


@pytest.fixture(autouse=False, scope="function")
def mock_slack_webhook(monkeypatch: MonkeyPatch):
    """Mocks the Slack webhook."""
    import prefect_slack.messages

    @task
    async def mock_send_incoming_webhook_message(*args, **kwds):
        """Mocks the send_incoming_webhook_message function."""
        get_prefect_or_default_logger().info("Mocked the Slack webhook")

    monkeypatch.setattr(
        prefect_slack.messages,
        "send_incoming_webhook_message",
        mock_send_incoming_webhook_message,
    )
    yield


@pytest.fixture(autouse=False, scope="function")
def mock_oryx_page_request(test_data_path: Path, monkeypatch: MonkeyPatch):
    """Mock the Cvent API to prevent API rate limit excession."""
    import requests

    def mock_request_page(url: str, *args, **kwds) -> requests.Response:
        """Mocks the extract_pages function to use a file in the tests/data directory."""
        filename: str | None = None
        if "www.oryxspioenkop.com" in url:
            folder = test_data_path / "pages"
            if (
                url
                == "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html"
            ):
                filename = "russia.html.gz"
            elif (
                url
                == "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html"
            ):
                filename = "ukraine.html.gz"
            elif (
                url
                == "https://www.oryxspioenkop.com/2022/03/list-of-naval-losses-during-2022.html"
            ):
                filename = "naval.html.gz"
            elif (
                url
                == "https://www.oryxspioenkop.com/2022/03/list-of-aircraft-losses-during-2022.html"
            ):
                filename = "aircraft.html.gz"
            else:
                raise ValueError(f"URL not mocked: {url}")

            with gzip.open(folder / filename, "rb") as f:
                response = requests.Response()
                response.status_code = 200
                response._content = f.read()
                return response

        elif "postimg.cc" in url:
            # https://i.postimg.cc/vm6DrVLL/h79.jpg
            # -> images/vm6DrVLL-h79.jpg
            parts = url.split("/")
            filename = f"{parts[-2]}-{parts[-1]}"
            folder = test_data_path / "images"
            # These are being streamed in chunks
            response = requests.Response()
            response.status_code = 200
            response.raw = open(folder / filename, "rb")
            return response
        else:
            raise ValueError(f"URL not mocked: {url}")

    monkeypatch.setattr(requests, "get", mock_request_page)
    yield


@pytest.fixture
def oryx_ukraine_webpage(test_data_path: Path) -> bs4.Tag:
    """Path to the Oryx Ukraine webpage."""
    with gzip.open(test_data_path / "pages" / "ukraine.html.gz", "r") as fo:
        return bs4.BeautifulSoup(fo.read(), features="html.parser")


@pytest.fixture
def oryx_russia_webpage(test_data_path: Path) -> bs4.Tag:
    """Path to the Oryx Ukraine webpage."""
    with gzip.open(test_data_path / "pages" / "russia.html.gz", "r") as fo:
        return bs4.BeautifulSoup(fo.read(), features="html.parser")


@pytest.fixture
def ukraine_article_parser(oryx_ukraine_webpage: bs4.Tag) -> "ArticleParser":
    """An `ArticleParser` object."""
    from borderlands.parser.article import ArticleParser

    body = oryx_ukraine_webpage.find(
        attrs={"class": "post-body entry-content", "itemprop": "articleBody"}
    )
    from borderlands.parser.article import UKRAINE_DATA_SECTION_INDEX

    yield ArticleParser(body, UKRAINE_DATA_SECTION_INDEX)


@pytest.fixture
def russia_article_parser(oryx_russia_webpage: bs4.Tag) -> "ArticleParser":
    """An `ArticleParser` object."""
    from borderlands.parser.article import ArticleParser

    body = oryx_russia_webpage.find(
        attrs={"class": "post-body entry-content", "itemprop": "articleBody"}
    )
    from borderlands.parser.article import RUSSIA_DATA_SECTION_INDEX

    yield ArticleParser(body, RUSSIA_DATA_SECTION_INDEX)


@pytest.fixture
def ukraine_page_parse_result(ukraine_article_parser: "ArticleParser") -> list:
    """The result of parsing the Ukraine page."""
    yield list(ukraine_article_parser.parse())


@pytest.fixture
def russia_page_parse_result(russia_article_parser: "ArticleParser") -> list:
    """The result of parsing the Russia page."""
    yield list(russia_article_parser.parse())
