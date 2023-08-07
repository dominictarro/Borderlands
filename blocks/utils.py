import asyncio
from collections.abc import Coroutine

from prefect.blocks.core import Block


async def save(block: Block, downstream: list[Coroutine] | None = None):
    """Save a block and its downstream dependencies.

    Args:
        block (Block): The block to save.
        downstream (list[Coroutine], optional): A list of coroutines to run after saving the block. Defaults to None.
    """
    uuid = await block.save(name=block._block_document_name, overwrite=True)
    print(
        f"Saved {block._block_type_slug}/{block._block_document_name} with UUID {uuid}"
    )
    if downstream:
        await asyncio.gather(*downstream)


async def gather(*coros: Coroutine):
    """Run a list of blocks concurrently.

    Args:
        *blocks (Block): The blocks to run.
    """
    await asyncio.gather(*coros)


def run(*coros: Coroutine):
    """Run a list of blocks concurrently.

    Args:
        *blocks (Block): The blocks to run.
    """
    asyncio.run(gather(*coros))
