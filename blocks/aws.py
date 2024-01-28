"""
Blocks usable by all deployments.
"""

import os

from dotenv import load_dotenv
from prefect.blocks.system import Secret
from prefect_aws import AwsCredentials, S3Bucket

try:
    from . import tf, utils
except ImportError:
    import tf
    import utils

load_dotenv()

aws_credentials = AwsCredentials(
    _block_document_name="aws-credentials-prefect",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
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

ecr = Secret(
    _block_document_name="ecr-image-borderlands-scrape",
    value=os.environ["ECR_IMAGE_TAG"],
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
        utils.save(ecr),
    )
