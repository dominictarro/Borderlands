"""
Module for the CLI tool.
"""

from borderlands.cli.entrypoint import borderlands

from borderlands.cli.blocks import blocks
from borderlands.cli.docs import docs
from borderlands.cli.rds import rds

borderlands.add_command(blocks)
borderlands.add_command(docs)
borderlands.add_command(rds)
