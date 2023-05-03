"""
Standardized deployment conventions for Borderlands.
"""
import abc

from prefect.blocks.abstract import Block
from prefect.deployments import Deployment
from prefect_aws import ECSTask
from prefect_github import GitHubRepository


class Deployer(abc.ABC):
    """Base class for all deployers."""

    def __init__(self, base: Deployment, reference: str) -> None:
        """Initializes a deployer.

        Parameters
        ----------
        base : Deployment
            Base deployment to create development and production deployments from
        reference : str
            GitHub branch, tag, or release to deploy.
        """
        self.base = base
        self.reference = reference

    def derive_block_name(self, block: Block, production: bool) -> str:
        """Creates a unique block name using the convention."""
        if not isinstance(block, Block):
            raise TypeError(f"Expected a Block, got {type(block)}")
        # Prefixes with development or production
        # Suffixes with reference
        # e.g.
        # {development}-{__block_document_name}-{reference}
        prefix = "development" if not production else "production"
        # Prefect has limited acceptable characters (alphanumerics and hyphens)
        # Replace non-acceptable characters with hyphens
        suffix = self.reference
        suffix = suffix.replace("/", "-")
        # Remove leading and trailing hyphens
        suffix = suffix.strip("-")
        # Remove duplicate hyphens (a--b -> a-b)
        suffix = "-".join(filter(lambda x: x, suffix.split("-")))
        return f"{prefix}-{block._block_document_name}-{self.reference}"

    def deep_copy_block(self, block: Block | str) -> Block:
        """Creates a new block document with a separate ID."""
        # Create a unique GitHubRepository block
        if isinstance(block, str):
            block = getattr(self.base, block)
        elif not isinstance(block, Block):
            raise TypeError(f"Expected a Block or str, got {type(block)}")

        block = block.copy(
            exclude={"_block_document_id"}
        )
        return block

    @abc.abstractmethod
    def production(self) -> Deployment:
        """
        Creates a deployment safe for production using production conventions.

        Returns
        -------
        Deployment
            A production deployment.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def development(self, reference: str) -> Deployment:
        """
        Creates a deployment safe for development using development conventions.

        Returns
        -------
        Deployment
            A development deployment.
        """
        raise NotImplementedError


class StandardDeployer(Deployer):

    def update_ecs_task(self, block: ECSTask, production: bool) -> ECSTask:
        """Updates an infrastructure block with the reference."""
        if not isinstance(block, Block):
            raise TypeError(f"Expected a Block, got {type(block)}")

        # Pattern
        # Stream Group / Flow Name / Reference
        # e.g.
        # Development / My Flow / bug_fix
        # Production / My Flow / v1.0.0
        aws_logs_stream_group = "Development" if not production else "Production"
        block.cloudwatch_logs_options.update(
            {
                "awslogs-stream-prefix": f"{aws_logs_stream_group}/{self.base.flow_name}/{self.reference}",
            }
        )
        block._block_document_name = self.derive_block_name(block, production)
        return block

    def update_github_repository(self, block: GitHubRepository, production: bool) -> GitHubRepository:
        """Updates a storage block with the reference."""
        if not isinstance(block, Block):
            raise TypeError(f"Expected a Block, got {type(block)}")

        block.reference = self.reference
        block._block_document_name = self.derive_block_name(block, production)
        return block

    def production(self) -> Deployment:
        """Returns a production deployment."""
        # Create a unique GitHubRepository block
        github_repo: GitHubRepository = self.deep_copy_block("storage")
        github_repo = self.update_github_repository(github_repo, True)

        ecs_task: ECSTask = self.deep_copy_block("infrastructure")
        ecs_task = self.update_ecs_task(ecs_task, True)

        self.base.update(
            storage=github_repo,
            infrastructure=ecs_task,
        )
        # Create a unique ECSTask block
        return self.base

    def development(self) -> Deployment:
        """Returns a development deployment."""
        # Create a unique GitHubRepository block
        github_repo: GitHubRepository = self.deep_copy_block("storage")
        github_repo = self.update_github_repository(github_repo, False)

        ecs_task: ECSTask = self.deep_copy_block("infrastructure")
        ecs_task = self.update_ecs_task(ecs_task, False)
        # Update log level
        ecs_task.env["PREFECT_LOGGING_LEVEL"] = "DEBUG"

        self.base.update(
            storage=github_repo,
            infrastructure=ecs_task,
            name=self.base.name + f" - Development {self.reference}"
        )
        # Create a unique ECSTask block
        return self.base
