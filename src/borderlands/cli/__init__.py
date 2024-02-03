"""
Module for the CLI tool.
"""

from borderlands.cli.entrypoint import borderlands
from borderlands.cli.docs import docs

borderlands.add_command(docs)
