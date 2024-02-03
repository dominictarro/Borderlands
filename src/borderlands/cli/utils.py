"""
Utility functions for the CLI.
"""

from typing import TYPE_CHECKING, Callable

import click

if TYPE_CHECKING:
    from prefect.blocks.core import Block


def save(block: "Block", downstream: list[Callable] | None = None):
    """Save a block and its downstream dependencies.

    Args:
        block (Block): The block to save.
        downstream (list[Coroutine], optional): A list of coroutines to run after saving the block. Defaults to None.
    """
    uuid = block.save(name=block._block_document_name, overwrite=True)
    click.echo(
        f"Saved {block._block_type_slug}/{block._block_document_name} with UUID {uuid}"
    )
    if downstream:
        for fn in downstream:
            if not callable(fn):
                raise ValueError(f"{fn} is not callable.")
            fn()
