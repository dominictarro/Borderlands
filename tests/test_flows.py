"""
Tests for the Oryx flow.
"""

import gzip
from pathlib import Path

import httpx
import pytest


@pytest.fixture
def mock_httpx_func(test_data_path: Path):

    def _mock_httpx_func(url: str, *args, **kwds) -> httpx.Response:

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
                response = httpx.Response(
                    status_code=200,
                    content=f.read(),
                    request=httpx.Request("GET", url),
                )
                return response

        elif "postimg.cc" in url:
            # https://i.postimg.cc/vm6DrVLL/h79.jpg
            # -> images/vm6DrVLL-h79.jpg
            parts = url.split("/")
            filename = f"{parts[-2]}-{parts[-1]}"
            folder = test_data_path / "images"

            # These are being streamed in chunks
            response = httpx.Response(
                status_code=200,
                content=open(folder / filename, "rb"),
                request=httpx.Request("GET", url),
            )
            return response
        else:
            raise ValueError(f"URL not mocked: {url}")

    yield _mock_httpx_func


@pytest.mark.skip(reason="Causes crash in CI.")
def test_oryx_flow(
    prefect_db, mock_buckets, mock_oryx_page_request, mock_slack_webhook
):
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
    prefect_db,
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
