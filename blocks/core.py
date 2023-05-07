"""
Blocks usable by all deployments.
"""
from prefect_github import GitHubRepository

borderlands_github: GitHubRepository = GitHubRepository(
    reference="main",
    repository_url="https://github.com/dominictarro/Borderlands.git",
    _block_document_name="github-repository-borderlands",
)

if __name__ == "__main__":
    borderlands_github.save(
        name=borderlands_github._block_document_name, overwrite=True
    )
