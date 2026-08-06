"""Exceptions of platform module."""

from __future__ import annotations


class ConcurrencyConflictError(ValueError):
    """Raised when an optimistic concurrency precondition (HTTP 412) fails.

    Subclasses ValueError so existing ``except ValueError`` callers still catch it,
    while callers that need to distinguish a conflict from a bad-ID error can use
    ``except ConcurrencyConflictError``.
    """
