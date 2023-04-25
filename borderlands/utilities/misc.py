"""
Utility classes and methods.
"""
from __future__ import annotations

import string
from typing import Callable, List


ALPHANUMERICS = string.ascii_letters + string.digits


def parse_alphabet_items(
        text: str,
        alphabet: str = ALPHANUMERICS,
        exclude: bool = False
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
    tail_pointer_logic: Callable[[str], bool] = lambda char: (
            char not in alphabet)
    head_pointer_logic: Callable[[str], bool] = lambda char: (
            char in alphabet)

    # Switch head and tail pointer checks if excluding
    if exclude:
        tail_pointer_logic, head_pointer_logic = (
                head_pointer_logic, tail_pointer_logic)

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


def series_splitter(text: str, delimiter: str = ',') -> List[str]:
    """Splits a string list with or without an Oxford comma (delimiter).

    :param text:    Comma separated list
    :return:        A list of the series's items

    >>> series_splitter("a, b, c, and d")
    >>> ['a', 'b', 'c', 'd']

    >>> series_splitter("a, b, c or d")
    >>> ['a', 'b', 'c', 'd']
    """
    items = [item.strip() for item in text.split(f"{delimiter} ")]

    for conjunction in ('and', 'nor', 'but', 'or',):
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
