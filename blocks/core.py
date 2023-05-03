"""
Blocks usable by all deployments.
"""
from prefect_github import GitHubRepository

borderlands_github: GitHubRepository = GitHubRepository(
    reference="main",
    repository_url="https://github.com/dominictarro/Borderlands.git",
)

if __name__ == "__main__":
    borderlands_github.save(name=borderlands_github.name, overwrite=True)
