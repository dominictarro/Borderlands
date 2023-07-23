"""
Tests for the Oryx flow.
"""


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


def test_extract_oryx_media(
    mock_buckets,
    mock_oryx_page_request,
):
    """Test the Oryx media extraction flow."""
    from flows.oryx_media import extract_oryx_media

    extract_oryx_media.with_options(
        retries=0,
        on_completion=[],
        on_failure=[],
        on_cancellation=[],
        on_crashed=[],
    )("landing/latest.json")
