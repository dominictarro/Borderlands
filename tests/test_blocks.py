import pytest
from prefect.blocks.system import String

from borderlands.blocks import (
    Blocks,
    _return_or_await_and_return,
)


class TestBlocks:
    def test_init_env(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("BLOCKS_CORE_BUCKET_NAME", "core-bucket")

        blocks = Blocks()
        assert blocks.core_bucket_name == "core-bucket"


def test__return_or_await_and_return(prefect_db):
    block: String = String(
        _block_document_name="string-test",
        value="test string",
    )
    block.save()

    result = _return_or_await_and_return(String.load("string-test"))
    assert isinstance(result, String)
    assert result.value == "test string"
