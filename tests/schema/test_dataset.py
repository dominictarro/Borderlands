import polars as pl

from borderlands.schema.dataset import Dataset
from borderlands.schema.schema import Field, Schema


class TestDataset:

    def test_to_markdown(self):
        s = type(
            "TestSchema",
            (Schema,),
            {
                "id_": Field(pl.Int32, tags=["1"], description="field 1"),
                "name": Field(pl.Utf8, tags=["2"], description="field 2"),
                "description": Field(pl.Utf8, tags=["2", "3"], description="field 3"),
                "non-field": "non-field",
            },
        )

        d = Dataset(
            label="test",
            host_bucket="test",
            release_path="test",
            schema=s,
            description="test msg",
        )

        assert d.to_markdown() == (
            "## test\n"
            "\n"
            "test msg\n"
            "\n"
            "### Schema\n"
            "\n"
            "| Name | Type | Description |\n"
            "| :--- | :--- | :----------- |\n"
            "| id_ | numeric | field 1 |\n"
            "| name | string | field 2 |\n"
            "| description | string | field 3 |"
        )
