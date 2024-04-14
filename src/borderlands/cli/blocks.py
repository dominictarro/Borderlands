"""
Blocks usable by all deployments.
"""

import os
from functools import partial

import click
from dotenv import load_dotenv

from borderlands.cli.utils import save

load_dotenv()


@click.group()
def blocks():
    """Commands for working with Prefect blocks."""
    pass


@blocks.command()
@click.option(
    "-u",
    "--aws-access-key-id",
    type=str,
    default="env:AWS_ACCESS_KEY_ID",
    help="The AWS access key ID. Prefix with 'env:' to use an environment variable.",
)
@click.option(
    "-p",
    "--aws-secret-access-key",
    type=str,
    default="env:AWS_SECRET_ACCESS_KEY",
    help="The AWS secret access key. Prefix with 'env:' to use an environment variable.",
)
@click.option(
    "-b",
    "--block-name",
    type=str,
    default="aws-credentials-prefect",
    help="The name of the block.",
)
def aws_credentials(
    aws_access_key_id: str, aws_secret_access_key: str, block_name: str
):
    """Create the AWS credentials block."""

    if aws_access_key_id.startswith("env:"):
        env_var = aws_access_key_id.split(":", maxsplit=1)[1]
        aws_access_key_id = os.getenv(env_var)

    if aws_secret_access_key.startswith("env:"):
        env_var = aws_secret_access_key.split(":", maxsplit=1)[1]
        aws_secret_access_key = os.getenv(env_var)

    from prefect_aws import AwsCredentials

    aws_credentials = AwsCredentials(
        _block_document_name=block_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    save(aws_credentials)


@blocks.command()
@click.option(
    "-n",
    "--bucket-name",
    type=str,
    default="borderlands-core",
    help="The name of the S3 bucket.",
)
@click.option(
    "-c",
    "--credentials",
    type=str,
    default="aws-credentials-prefect",
    help="The name of the AWS credentials block.",
)
@click.option(
    "-b",
    "--block-name",
    type=str,
    default="s3-bucket-borderlands-core",
    help="The name of the block.",
)
def bucket_core(bucket_name: str, credentials: str, block_name: str):
    """Create the S3 Bucket block for the core bucket."""
    from prefect_aws import AwsCredentials, S3Bucket

    aws_credentials = AwsCredentials.load(credentials)
    core_bucket = S3Bucket(
        _block_document_name=block_name,
        bucket_name=bucket_name,
        credentials=aws_credentials,
    )
    save(core_bucket)


@blocks.command()
@click.option(
    "-t",
    "--tag",
    type=str,
    default="env:ECR_IMAGE_TAG",
    help="The value of the secret. Prefix with 'env:' to use an environment variable.",
)
@click.option(
    "-b",
    "--block-name",
    type=str,
    default="ecr-image-borderlands-scrape",
    help="The name of the block.",
)
def ecr_image(tag: str, block_name: str):
    """Create the ECR image secret block."""

    if tag.startswith("env:"):
        env_var = tag.split(":", maxsplit=1)[1]
        tag = os.getenv(env_var)

    from prefect.blocks.system import Secret

    ecr = Secret(
        _block_document_name=block_name,
        value=tag,
    )
    save(ecr)


@blocks.command()
@click.option(
    "-t",
    "--token",
    type=str,
    default="env:GITHUB_TOKEN",
    help="The GitHub token. Prefix with 'env:' to use an environment variable.",
)
@click.option(
    "-b",
    "--block-name",
    type=str,
    default="github-credentials-pat",
    help="The name of the block.",
)
def github_credentials(token: str, block_name: str):
    """Create the GitHub credentials block."""
    from prefect_github import GitHubCredentials

    if token.startswith("env:"):
        env_var = token.split(":", maxsplit=1)[1]
        token = os.getenv(env_var)

    ghc = GitHubCredentials(
        _block_document_name=block_name,
        token=token,
    )
    save(ghc)


@blocks.command()
@click.option(
    "-u",
    "--username",
    type=str,
    default="env:KAGGLE_USERNAME",
    help="The Kaggle username. Prefix with 'env:' to use an environment variable.",
)
@click.option(
    "-k",
    "--key",
    type=str,
    default="env:KAGGLE_KEY",
    help="The Kaggle key. Prefix with 'env:' to use an environment variable.",
)
@click.option(
    "--username-block-name",
    type=str,
    default="secret-kaggle-username",
    help="The name of the block.",
)
@click.option(
    "--key-block-name",
    type=str,
    default="secret-kaggle-key",
    help="The name of the block.",
)
def kaggle_credentials(
    username: str, key: str, username_block_name: str, key_block_name: str
):
    """Create the Kaggle username block."""
    from prefect.blocks.system import Secret

    if username.startswith("env:"):
        env_var = username.split(":", maxsplit=1)[1]
        username = os.getenv(env_var)

    if key.startswith("env:"):
        env_var = key.split(":", maxsplit=1)[1]
        key = os.getenv(env_var)

    kaggle_username = Secret(
        _block_document_name=username_block_name,
        value=username,
    )

    kaggle_key = Secret(
        _block_document_name=key_block_name,
        value=key,
    )
    save(kaggle_username, downstream=[partial(save, kaggle_key)])


@blocks.command()
@click.option(
    "-u",
    "--url",
    type=str,
    default="env:SLACK_WEBHOOK_URL",
    help="The Slack webhook URL. Prefix with 'env:' to use an environment variable.",
)
@click.option(
    "-b",
    "--block-name",
    type=str,
    default="slack-webhook-borderlands",
    help="The name of the block.",
)
def slack_webhook(url: str, block_name: str):
    """Create the Slack webhook block."""
    from prefect_slack import SlackWebhook

    if url.startswith("env:"):
        env_var = url.split(":", maxsplit=1)[1]
        url = os.getenv(env_var)

    webhook = SlackWebhook(
        _block_document_name=block_name,
        url=url,
    )
    save(webhook)
