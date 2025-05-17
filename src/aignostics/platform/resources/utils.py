"""
Utility functions for the Aignostics client resources.

This module provides helper functions for working with the Aignostics API, including
pagination utilities to handle API responses that span multiple pages. These utility
functions are designed to be used internally by the SDK's resource classes.
"""

from collections.abc import Callable, Iterator
from typing import TypeVar

T = TypeVar("T")

PAGE_SIZE = 20


def paginate(func: Callable[..., list[T]], *args, **kwargs) -> Iterator[T]:  # type: ignore[no-untyped-def]
    """
    A decorator to paginate a function that returns a list of items.

    Args:
        func: The function to paginate.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Yields:
        T: The items from the paginated function.
    """
    page = 1
    while True:
        results = func(*args, page=page, page_size=PAGE_SIZE, **kwargs)
        yield from results
        if len(results) < PAGE_SIZE:
            break
        page += 1


def paginate_flex(func: Callable[..., list[T]], page_size: int = PAGE_SIZE, *args, **kwargs) -> Iterator[T]:  # type: ignore[no-untyped-def]
    """
    A decorator to paginate a function that returns a list of items.

    Args:
        func: The function to paginate.
        page_size (int): The number of items per page.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Yields:
        T: The items from the paginated function.
    """
    page = 1
    while True:
        results = func(*args, page=page, page_size=page_size, **kwargs)
        yield from results
        if len(results) < page_size:
            break
        page += 1
