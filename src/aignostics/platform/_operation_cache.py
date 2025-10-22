"""Operation caching utilities for the Aignostics Platform client.

This module provides caching functionality for API operations to reduce redundant calls
and improve performance. It includes cache management, key generation, and a decorator
for automatic caching of function results with configurable time-to-live (TTL).

The caching mechanism:
- Caches operation results based on authentication tokens and function parameters
- Respects TTL (time-to-live) for cached values
- Automatically invalidates cache when tokens change
- Supports selective cache clearing by function
"""

import hashlib
import time
import typing as t
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

from ._authentication import get_token

# Cache storage for operation results
_operation_cache: dict[str, tuple[Any, float]] = {}

# Type variables for the cached_operation decorator
P = ParamSpec("P")
T = TypeVar("T")


def operation_cache_clear(func: Callable[..., Any] | list[Callable[..., Any]] | None = None) -> int:
    """Clears the operation cache, optionally filtering by function(s).

    Args:
        func (Callable | list[Callable] | None): If provided, only clear cache entries
            for the specified function(s). Can be:
            - A callable (function/method)
            - A list of callables
            - None to clear all cache entries

    Returns:
        int: Number of cache entries removed.
    """
    removed_count = 0

    if func is None:
        # Remove all cache entries
        removed_count = len(_operation_cache)
        _operation_cache.clear()
    else:
        # Normalize input to a list of function qualified names
        func_list = func if isinstance(func, list) else [func]
        func_qualified_names = [f.__qualname__ for f in func_list]

        # Remove entries matching any of the function qualified names
        keys_to_remove = [key for key in _operation_cache if any(name in key for name in func_qualified_names)]

        for key in keys_to_remove:
            del _operation_cache[key]
            removed_count += 1

    return removed_count


def cache_key(func_qualified_name: str, *args: object, **kwargs: object) -> str:
    """Generates a cache key based on the function name and parameters.

    Args:
        func_qualified_name (str): The qualified name of the function being cached (e.g., 'ClassName.func1').
        *args: Positional arguments to the function.
        **kwargs: Keyword arguments to the function.

    Returns:
        str: A unique cache key.
    """
    return f"{func_qualified_name}:{args}:{sorted(kwargs.items())}"


def cache_key_with_token(token: str, func_qualified_name: str, *args: object, **kwargs: object) -> str:
    """Generates a cache key based on the token, function name, and parameters.

    Args:
        token (str): The authentication token.
        func_qualified_name (str): The qualified name of the function being cached (e.g., 'ClassName.func1').
        *args: Positional arguments to the function.
        **kwargs: Keyword arguments to the function.

    Returns:
        str: A unique cache key.
    """
    token_hash = hashlib.sha256((token or "").encode()).hexdigest()[:16]
    return f"{token_hash}:{func_qualified_name}:{args}:{sorted(kwargs.items())}"


def cached_operation(
    ttl: int, *, use_token: bool = True, instance_attrs: tuple[str, ...] | None = None
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Caches the result of a function call for a specified time-to-live (TTL).

    Args:
        ttl (int): Time-to-live for the cache in seconds.
        use_token (bool): If True, includes the authentication token in the cache key.
            This is useful for Client methods that should cache per-user.
            When use_token is True and no instance_attrs are specified, the 'self'
            argument is excluded from the cache key to enable cache sharing across instances.
        instance_attrs (tuple[str, ...] | None): Instance attributes to include in the cache key.
            This is useful for instance methods where caching should be per-instance based on
            specific attributes (e.g., 'run_id' for Run.details()).

    Returns:
        Callable: A decorator that caches the function result.
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Build cache key components
            cache_args: tuple[object, ...] = args

            # Get qualified name (including class name if it's a method)
            func_qualified_name = func.__qualname__

            # If instance_attrs specified, extract them from self (args[0])
            if instance_attrs and args:
                instance = args[0]
                instance_values = tuple(getattr(instance, attr) for attr in instance_attrs)
                cache_args = instance_values + args[1:]

            if use_token:
                key = cache_key_with_token(get_token(True), func_qualified_name, *cache_args, **kwargs)
            else:
                key = cache_key(func_qualified_name, *cache_args, **kwargs)

            if key in _operation_cache:
                result, expiry = _operation_cache[key]
                if time.time() < expiry:
                    return t.cast("T", result)
                del _operation_cache[key]

            result = func(*args, **kwargs)
            _operation_cache[key] = (result, time.time() + ttl)
            return result

        return wrapper

    return decorator
