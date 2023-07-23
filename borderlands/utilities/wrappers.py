"""Utility wrappers for functions."""
import functools

import polars as pl
from prefecto.logging import get_prefect_or_default_logger


def force_lazyframe(func):
    """Converts function output from a `DataFrame` to a `LazyFrame` if it is not already a `LazyFrame`."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Converts function output from a `DataFrame` to a `LazyFrame` if it is not already a `LazyFrame`."""
        df = func(*args, **kwargs)
        return df.lazy() if isinstance(df, pl.DataFrame) else df

    return wrapper


def inject_default_logger(func):
    """Injects a default logger into the function if it is not already present."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Injects a default logger into the function if it is not already present."""
        if "logger" not in kwargs:
            kwargs["logger"] = get_prefect_or_default_logger()
        return func(*args, **kwargs)

    return wrapper
