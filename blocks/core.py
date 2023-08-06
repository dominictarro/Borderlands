"""
Blocks usable by all deployments.
"""
import os

from dotenv import load_dotenv
from prefect_aws import AwsCredentials, S3Bucket
from prefect_github import GitHubRepository
from pydantic import SecretStr

try:
    from . import tf, utils
except ImportError:
    import tf
    import utils

load_dotenv()


borderlands_github: GitHubRepository = GitHubRepository(
    reference="main",
    repository_url="https://github.com/dominictarro/Borderlands.git",
    _block_document_name="github-repository-borderlands",
)

aws_credentials = AwsCredentials(
    _block_document_name="aws-credentials-prefect",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=SecretStr(os.getenv("AWS_SECRET_ACCESS_KEY")),
)

borderlands_core = S3Bucket(
    _block_document_name="s3-bucket-borderlands-core",
    bucket_name=tf.CORE_BUCKET_NAME,
    credentials=aws_credentials,
)

borderlands_persistence = S3Bucket(
    _block_document_name="s3-bucket-borderlands-persistence",
    bucket_name=tf.PERSISTENCE_BUCKET_NAME,
    credentials=aws_credentials,
)


if __name__ == "__main__":

    utils.run(
        utils.save(
            aws_credentials,
            # These must wait for aws_credentials to be saved
            downstream=[
                utils.save(borderlands_core),
                utils.save(borderlands_persistence),
            ],
        ),
        utils.save(borderlands_github),
    )
