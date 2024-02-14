"""
Pytest configuration.
"""

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from _pytest.monkeypatch import MonkeyPatch
from prefect import task
from prefect.testing.utilities import prefect_test_harness
from prefect_aws import AwsCredentials, S3Bucket
from prefect_slack import SlackWebhook
from prefecto.logging import get_prefect_or_default_logger
from prefecto.testing.s3 import mock_bucket

if TYPE_CHECKING:
    pass


TESTS_PATH: Path = Path(__file__).parent


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


@pytest.fixture(scope="session")
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
