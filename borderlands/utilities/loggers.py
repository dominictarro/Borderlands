"""
Module for Prefect logging.
"""
import logging

from prefect.logging import get_run_logger


def get_prefect_or_default_logger(
    __default: logging.Logger | str | None = None,
) -> logging.Logger:
    """Gets the Prefect logger if the global context is set. Returns the
    `__default` or root logger if not.
    """
    try:
        return get_run_logger()
    except RuntimeError:
        if isinstance(__default, str):
            return logging.getLogger(__default)
        return __default or logging.getLogger()


if __name__ == "__main__":
    import doctest

    doctest.testmod()
