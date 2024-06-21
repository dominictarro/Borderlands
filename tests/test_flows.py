"""
Tests for the Oryx flow.
"""

import pytest


@pytest.mark.skip(reason="Causes crash in CI.")
def test_oryx_flow(mock_buckets, mock_oryx_page_request):
    """Test the Oryx equipment loss staging flow."""
    from flows.oryx import oryx_flow

    oryx_flow.with_options(
        retries=0,
        on_completion=[],
        on_failure=[],
        on_cancellation=[],
        on_crashed=[],
    )()


@pytest.mark.skip(reason="Causes crash in CI.")
def test_download_media(
    mock_buckets,
    mock_oryx_page_request,
):
    """Test the Oryx media extraction flow."""
    from flows.media import download_media

    download_media.with_options(
        retries=0,
        on_completion=[],
        on_failure=[],
        on_cancellation=[],
        on_crashed=[],
    )(loss_key="oryx/year=2023/month=07/2023-07-23.parquet")
