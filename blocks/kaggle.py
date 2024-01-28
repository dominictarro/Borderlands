"""
Blocks for interacting with Kaggle.
"""

import os

from dotenv import load_dotenv
from prefect.blocks.system import Secret
from pydantic import SecretStr

load_dotenv()

try:
    from . import utils
except ImportError:
    import utils

username = Secret(
    _block_document_name="secret-kaggle-username",
    value=SecretStr(os.environ["KAGGLE_USERNAME"]),
)

key = Secret(
    _block_document_name="secret-kaggle-key",
    value=SecretStr(os.environ["KAGGLE_KEY"]),
)

if __name__ == "__main__":
    utils.run(
        utils.save(username),
        utils.save(key),
    )
