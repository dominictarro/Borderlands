"""
Test the result of transforming Oryx data.
"""
import pandas as pd

from borderlands.oryx.transform import (
    Status,
    EvidenceSource,
    tabulate_loss_cases,
    assign_country_of_production,
    assign_evidence_source,
    assign_status,
    flag_duplicate_natural_keys
)


def test_tabulate_loss_cases(ukraine_page_parse_result: list, russia_page_parse_result: list):
    """Tests tabulating the loss cases."""
    ukraine_data = dict(
        name="Ukraine",
        as_of_date="2023-04-24T22:46:47.590878",
        data = ukraine_page_parse_result,
    )
    russia_data = dict(
        name="Russia",
        as_of_date="2023-04-24T22:46:47.590878",
        data = russia_page_parse_result,
    )

    for df in map(tabulate_loss_cases.fn, (ukraine_data, russia_data)):
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert df.shape[1] == 7

        # Types
        assert df["category"].dtype == "object"
        assert df["model"].dtype == "object"
        assert df["id_"].dtype == "object"
        assert df["evidence_url"].dtype == "object"
        assert df["country_of_production_flag_url"].dtype == "object"
        assert df["country"].dtype == "object"
        assert df["as_of_date"].dtype == "object"

        assert df["country"].isin(["Ukraine", "Russia"]).all()


def test_assign_status(oryx_descriptions: list[str]):
    """Tests the assign_status function."""
    df = pd.DataFrame(oryx_descriptions, columns=["description"])
    # Make sure test file is good
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.shape[1] == 1

    # Types
    assert df["description"].dtype == "object"

    df = assign_status.fn(df)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.shape[1] == 2

    # Types
    assert df["description"].dtype == "object"
    assert df["status"].dtype == "object"
    assert df["status"].apply(lambda x: isinstance(x, list)).all()

    # Check that all statuses are valid
    statuses = [status.value for status in Status]
    # These are nested arrays
    assert df["status"].explode().isin(statuses).all()


def test_assign_country_of_production(oryx_flag_urls: list, flag_url_mapper: dict):
    """Tests the assign_country_of_production function."""
    df = pd.DataFrame(dict(country_of_production_flag_url=oryx_flag_urls))
    # Make sure test file is good
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.shape[1] == 1

    # Types
    assert df["country_of_production_flag_url"].dtype == "object"

    df = assign_country_of_production.fn(df, flag_url_mapper)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.shape[1] == 2

    # Types
    assert df["country_of_production_flag_url"].dtype == "object"
    assert df["country_of_production"].dtype == "object"

    codes = [v for k, v in flag_url_mapper.items()]
    # Check that all countries are valid
    assert df["country_of_production"].isin(codes).all()


def test_assign_country_of_production_log_warning(caplog, flag_url_mapper: dict):
    """Tests the assign_country_of_production function."""
    df = pd.DataFrame(dict(country_of_production_flag_url=[r"%%%a", r"%%%b", r"%%%c"]))
    # Make sure test file is good
    df = assign_country_of_production.fn(df, flag_url_mapper)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.shape[1] == 2

    # Types
    assert df["country_of_production_flag_url"].dtype == "object"
    assert df["country_of_production"].dtype == "object"

    # Check that the warning was logged
    assert "Unmapped URLs detected: " in caplog.text


def test_assign_evidence_source(oryx_evidence_urls: list):
    """Tests the assign_evidence_source function."""
    df = pd.DataFrame(dict(evidence_url=oryx_evidence_urls))
    # Make sure test file is good
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.shape[1] == 1

    # Types
    assert df["evidence_url"].dtype == "object"

    df = assign_evidence_source.fn(df)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.shape[1] == 3

    # Types
    assert df["evidence_url"].dtype == "object"
    assert df["evidence_source"].dtype == "object"

    sources = [source.value for source in EvidenceSource]
    # Check that all sources are valid
    assert df["evidence_source"].isin(sources).all()


def test_assign_evidence_source_log_warning(caplog):
    """Tests the assign_evidence_source function."""
    df = pd.DataFrame(dict(evidence_url=[r"%%%a", r"%%%b", r"%%%c"]))
    # Make sure test file is good
    df = assign_evidence_source.fn(df)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.shape[1] == 3

    # Types
    assert df["evidence_url"].dtype == "object"
    assert df["evidence_source"].dtype == "object"

    # Check that the warning was logged
    assert "Unmapped domains detected: " in caplog.text


def test_flag_duplicate_natural_keys():
    """Tests the flag_duplicate_natural_keys function."""
    df = pd.DataFrame(
        [
            ["Ukraine", "Aircraft", "MiG-29", "https://example.com", "12345", ""],
            ["Ukraine", "Aircraft", "MiG-29", "https://example.com", "12345", ""],
            ["Ukraine", "Aircraft", "MiG-29", "https://example.com", "12346", ""],
            ["Ukraine", "Aircraft", "MiG-29", "https://example.com", "12347", ""],
            ["Ukraine", "Aircraft", "MiG-29", "https://example.com", "12347", ""],
            ["Ukraine", "Aircraft", "MiG-29", "https://example.com", "12347", ""],
            ["Russia",  "Aircraft", "MiG-29", "https://example.com", "12346", ""],
        ],
        columns=["country", "category", "model", "evidence_url", "id_", "description"],
    )

    df = flag_duplicate_natural_keys.fn(df)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.shape[1] == 7

    # Types
    assert df["id_"].dtype == "object"
    assert df["failed_duplicate_check"].dtype == "bool"

    value_counts = df["failed_duplicate_check"].value_counts()
    assert value_counts[True] == 5
    assert value_counts[False] == 2
