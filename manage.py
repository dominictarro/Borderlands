"""
Manage Prefect deployments for production and development.
"""
import importlib
from pathlib import Path
from typing import Type

import click
from prefect.deployments import Deployment
from pygit2 import Repository

from borderlands.deployer import Deployer, StandardDeployer


@click.group()
def cli():
    """Manage Prefect deployments."""
    pass


@cli.command(context_settings=dict(show_default=True))
@click.argument("deployment", type=str)
@click.option(
    "-r",
    "--reference",
    type=str,
    default=Repository(Path(__file__).parent).head.shorthand,
    help="GitHub branch, tag, or release to deploy.",
)
@click.option(
    "-P",
    "--production",
    is_flag=True,
    help="Deploys using the production pattern.",
)
@click.option(
    "-D",
    "--deployer",
    type=str,
    help="Path or import route to a custom deployer.",
    default = None,
)
@click.option(
    "-o",
    "--output",
    type=str,
    help="Path to write the deployment to.",
    default = None,
)
@click.option(
    "-s",
    "--save",
    is_flag=True,
    help="Save the derived deployment blocks to the Prefect server.",
)
@click.option(
    "-a",
    "--apply",
    is_flag=True,
    help="Apply the deployment to the Prefect server.",
)
def deploy(deployment: str, reference: str, production: bool, deployer: str, output: str, save: bool, apply: bool):
    """Deploy Prefect flows."""
    try:
        # Expect deployment to be in the form of "path/to/deployment.py::deployment_obj"
        # or path.to.deployment::deployment_obj
        path_to_deployment, deployment_name = deployment.split("::")
        import_route = path_to_deployment.replace("/", ".").removesuffix(".py")
    except ValueError:
        click.echo("Deployment must be in the form of path/to/deployment.py::deployment_obj or path.to.deployment::deployment_obj")
        exit(1)

    try:
        module: importlib.ModuleType = importlib.import_module(import_route)
        base: Deployment = getattr(module, deployment_name)
    except ModuleNotFoundError:
        click.echo(f"Could not find deployment module {import_route}")
        exit(1)
    except AttributeError:
        click.echo(f"Could not find deployment {deployment_name} in module {import_route}")
        exit(1)

    # Expect deployer to be in the form of "path/to/deployer.py::Deployer"
    # or path.to.deployer::Deployer
    if deployer is None:
        deployer_cls = StandardDeployer
    else:
        try:
            path_to_deployer, deployer_name = deployer.split("::")
            import_route = path_to_deployer.replace("/", ".").removesuffix(".py")
        except ValueError:
            click.echo("Deployer must be in the form of path/to/deployer.py::Deployer or path.to.deployer::Deployer")
            exit(1)

        try:
            module: importlib.ModuleType = importlib.import_module(import_route)
            deployer_cls: Type[Deployer] = getattr(module, deployer_name)
        except ModuleNotFoundError:
            click.echo(f"Could not find deployer module {import_route}")
            exit(1)
        except AttributeError:
            click.echo(f"Could not find deployer {deployer} in module {import_route}")
            exit(1)

    deployer: Deployer = deployer_cls(base, reference)
    deployment: Deployment
    if production:
        deployment = deployer.production()
    else:
        deployment = deployer.development()

    if save:
        deployment.infrastructure.save(
            deployment.infrastructure._block_document_name, overwrite=True
        )
        deployment.storage.save(
            deployment.storage._block_document_name, overwrite=True
        )
    
    if output is not None:
        deployment.to_yaml(output)
    
    if apply:
        deployment.apply()


if __name__ == "__main__":
    cli()
