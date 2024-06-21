import io

import polars as pl
import pytest
from prefect_aws import S3Bucket

from borderlands.schema.dataset import Dataset
from borderlands.schema.schema import Field, Schema


class TestDataset:

    @pytest.fixture
    def test_schema(self) -> type[Schema]:
        return type(
            "TestSchema",
            (Schema,),
            {
                "foo": Field(pl.Int32, description="test foo"),
                "bar": Field(pl.Float64, description="test bar"),
            },
        )

    def test_read(self, mock_buckets, bucket: S3Bucket, test_schema: type[Schema]):

        with io.BytesIO() as f:
            pl.DataFrame({"foo": [1, 2, 3], "bar": [1.0, 2.0, 3.0]}).write_parquet(f)
            f.seek(0)
            bucket.upload_from_file_object(f, "test.parquet")

        dataset = Dataset(
            label="test",
            host_bucket=bucket.bucket_name,
            release_path="test.parquet",
            schema=test_schema,
            description="test dataset desc",
        )
        df = dataset.read()
        assert isinstance(df, pl.DataFrame)
        assert df.shape == (3, 2)

    def test_to_markdown(self, test_schema: type[Schema]):
        dataset = Dataset(
            label="test",
            host_bucket="test-bucket",
            release_path="test.parquet",
            schema=test_schema,
            description="test dataset desc",
        )
        md = dataset.to_markdown()

        print(md)

        assert isinstance(md, str)

        assert md == (
            "## test\n\n"
            "test dataset desc\n\n"
            "| Name   | Type    | Description   |\n"
            "|:-------|:--------|:--------------|\n"
            "| foo    | numeric | test foo      |\n"
            "| bar    | numeric | test bar      |"
        )
