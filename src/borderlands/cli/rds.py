"""
Module to manage RDS assets.
"""

import os

import click


@click.group()
def rds():
    """Manage RDS assets."""
    pass


@click.group()
def tables():
    """Manage RDS tables."""
    pass


rds.add_command(tables)


@tables.command()
@click.option(
    "--credentials",
    "-c",
    default="database-credentials-admin",
    type=str,
    help="Credentials with permission to create the table.",
)
def equipment_loss(credentials: str):
    """Create the EquipmentLoss table."""

    os.environ["LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN"] = "1"

    from prefect_sqlalchemy import DatabaseCredentials

    from borderlands.models import EquipmentLoss

    credentials: DatabaseCredentials = DatabaseCredentials.load(credentials)
    engine = credentials.get_engine()

    EquipmentLoss.metadata.create_all(engine.engine, checkfirst=True)
