"""
Custom blocks for the pipeline.
"""

from prefect_aws import AwsCredentials
from prefect_sqlalchemy import DatabaseCredentials
from pydantic import VERSION as PYDANTIC_VERSION

if PYDANTIC_VERSION.startswith("2."):
    from pydantic.v1 import Field, SecretStr
else:
    from pydantic import Field, SecretStr

from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncConnection


class RdsCredentials(DatabaseCredentials):
    """A Prefect Block for storing AWS RDS credentials and connecting via IAM."""

    _block_type_name = "RDS Credentials"
    _logo_url = "https://icon.icepanel.io/AWS/svg/Database/RDS.svg"

    iam_credentials: AwsCredentials = Field(
        title="IAM Credentials",
        description="The AWS credentials to connect to the RDS instance with.",
    )

    def get_engine(self) -> Connection | AsyncConnection:
        """Returns an authenticated engine that can be used to query the specified RDS database.

        Returns:
            The authenticated SQLAlchemy Connection / AsyncConnection.
        """
        client = self.iam_credentials.get_client("rds")
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds/client/generate_db_auth_token.html
        self.password = SecretStr(
            client.generate_db_auth_token(
                DBHostname=self.host,
                Port=self.port,
                DBUsername=self.username,
                Region=self.iam_credentials.region_name,
            )
        )
        self.block_initialization()
        engine = super().get_engine()
        return engine
