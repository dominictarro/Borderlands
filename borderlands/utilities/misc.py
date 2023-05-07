"""
Utility classes and methods.
"""
from __future__ import annotations

import datetime
import string
from typing import Callable, List

ALPHANUMERICS = string.ascii_letters + string.digits


def parse_alphabet_items(
    text: str, alphabet: str = ALPHANUMERICS, exclude: bool = False
) -> List[str]:
    """Parses substrings whose characters are found in `alphabet`.

    :param text:        Text to iterate
    :param alphabet:    Characters to look for
    :param exclude:     Parse substrings whose characters are **not** found\
        in `alphabet`
    :return:            Section of `text` where all characters are found in\
        `alphabet`

    >>> parse_alphabet_items("one, two three, four")
    >>> ['one', 'two', 'three', 'four']

    >>> parse_alphabet_items("12, 34a 5b6 7", alphabet=string.digits)
    >>> ['12', '34', '5', '6', '7']
    """
    tail_pointer_logic: Callable[[str], bool] = lambda char: (char not in alphabet)
    head_pointer_logic: Callable[[str], bool] = lambda char: (char in alphabet)

    # Switch head and tail pointer checks if excluding
    if exclude:
        tail_pointer_logic, head_pointer_logic = (
            head_pointer_logic,
            tail_pointer_logic,
        )

    items: List[str] = []
    tail, head = 0, 0
    while True:
        # Increment for characters not in alphabet
        # Exclude: Increment for characters in alphabet
        while tail < len(text) and tail_pointer_logic(text[tail]):
            tail += 1

        # Terminate parsing if at end
        if tail >= len(text):
            break

        # Start of item
        head = tail
        # Increment for characters in alphabet
        # Exclude: Increment for characters not in alphabet
        while head < len(text) and head_pointer_logic(text[head]):
            head += 1

        # Add substring to list
        items.append(text[tail:head])

        # Continue loop at next character
        tail = head + 1
    return items


def series_splitter(text: str, delimiter: str = ",") -> List[str]:
    """Splits a string list with or without an Oxford comma (delimiter).

    :param text:    Comma separated list
    :return:        A list of the series's items

    >>> series_splitter("a, b, c, and d")
    >>> ['a', 'b', 'c', 'd']

    >>> series_splitter("a, b, c or d")
    >>> ['a', 'b', 'c', 'd']
    """
    items = [item.strip() for item in text.split(f"{delimiter} ")]

    for conjunction in (
        "and",
        "nor",
        "but",
        "or",
    ):
        if items[-1].startswith(f"{conjunction} "):
            # Oxford comma case
            items[-1] = items[-1].removeprefix(f"{conjunction} ")
        elif f" {conjunction} " in items[-1]:
            item = items.pop(-1)
            items.extend([_item.strip() for _item in item.split(f" {conjunction} ")])
        else:
            # try another conjunction
            continue
        # conjunction found, go no further
        break
    return items


def build_datetime_key(dt: datetime.datetime, unit: str = "hour") -> str:
    """Builds a datetime key in the format `year=YYYY/month=MM/day=DD/hour=HH/`.
    Can limit the `unit` to

    - `year`
    - `month`
    - `day`
    - `hour`
    - `minute`
    - `second`

    :param dt:  Datetime to build key for
    :return:    Datetime key

    >>> build_datetime_key(datetime.datetime(2021, 1, 1, 0, 0))
    >>> 'year=2021/month=01/day=01/hour=00'

    >>> build_datetime_key(datetime.datetime(2021, 1, 1, 0, 0), granularity="day")
    >>> 'year=2021/month=01/day=01'
    """
    # position, format
    UNIT = {
        "year": (1, "%04d"),
        "month": (2, "%02d"),
        "day": (3, "%02d"),
        "hour": (4, "%02d"),
        "minute": (5, "%02d"),
        "second": (6, "%02d"),
    }
    if unit not in UNIT:
        raise ValueError(f"Unit must be one of {tuple(UNIT.keys())!r}")

    # Build key
    key = ""
    for u, (p, f) in sorted(UNIT.items(), key=lambda x: x[1][0]):
        if p > UNIT[unit][0]:
            break
        key += f"{u}={f % getattr(dt, u)}"
        
        if p < UNIT[unit][0]:
            key += "/"
    return key
