"""
Entrypoint for scripts.
"""

import click


@click.group()
def cli():
    """Tool for managing the project."""


@cli.command()
def docs():
    """Generate docs for the datasets."""
    from src.borderlands.definitions import media_inventory, oryx
    from src.scripts.docs import update_dataset_docs

    for dataset in (oryx, media_inventory):
        update_dataset_docs(dataset)


if __name__ == "__main__":
    cli()
