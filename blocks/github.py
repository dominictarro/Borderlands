"""
Blocks for GitHub.
"""

import os

from dotenv import load_dotenv
from prefect_github import GitHubCredentials

load_dotenv()

try:
    from . import utils
except ImportError:
    import utils

ghc: GitHubCredentials = GitHubCredentials(
    _block_document_name="github-credentials-pat",
    token=os.environ["GITHUB_TOKEN"],
)

if __name__ == "__main__":
    utils.run(utils.save(ghc))
