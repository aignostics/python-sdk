"""
Utility functions for the Aignostics client resources.

This module provides helper functions for working with the Aignostics API, including
pagination utilities to handle API responses that span multiple pages. These utility
functions are designed to be used internally by the SDK's resource classes.
"""

from collections.abc import Callable, Iterator
from typing import TypeVar

from aignx.codegen.exceptions import NotFoundException

T = TypeVar("T")

PAGE_SIZE = 20


def paginate(func: Callable[..., list[T]], *args: object, page_size: int = PAGE_SIZE, **kwargs: object) -> Iterator[T]:
    """
    A generator function that handles pagination for API calls.

    This function takes a callable that returns a list of items and handles pagination
    by repeatedly calling the function with increasing page numbers until either
    a page returns fewer items than the requested page size or a NotFoundException is raised.

    Args:
        func (Callable[..., list[T]]): The function to paginate, which should accept page and page_size parameters.
        *args: Positional arguments to pass to the function.
        page_size (int): The number of items to request per page
        **kwargs: Keyword arguments to pass to the function.

    Raises:
        ValueError: If page_size is 0 or negative.

    Yields:
        Individual items from all pages.

    Example:
        >>> def list_items(page=1, page_size=20):
        ...     # Returns a full page on page 1, fewer items on page 2 (signals last page)
        ...     return [f"item_{i}" for i in range(page_size if page == 1 else 5)]
        >>> items = list(paginate(list_items))
        >>> print(len(items))
        25
    """
    # Credit: fix contributed by external community contributor @alekseevpavel04
    # (https://github.com/aignostics/python-sdk/pull/444)
    if page_size <= 0:
        message = f"page_size must be a positive integer, got {page_size}"
        raise ValueError(message)
    page = 1
    while True:
        try:
            results = func(*args, page=page, page_size=page_size, **kwargs)
            if not results:
                break
            yield from results
            if len(results) < page_size:
                break
            page += 1
        except NotFoundException:
            break  # We've paginated beyond the last page
