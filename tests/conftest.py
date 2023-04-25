"""
Pytest configuration.
"""
from pathlib import Path

import pytest
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
