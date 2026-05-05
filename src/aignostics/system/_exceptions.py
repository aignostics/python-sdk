"""Exceptions of system module."""


class OpenAPISchemaError(ValueError):
    """Exception raised when OpenAPI schema cannot be loaded."""

    def __init__(self, error: Exception) -> None:
        """Initialize exception with the underlying error."""
        super().__init__(f"Failed to load OpenAPI schema: {error}")


class ConcurrencyConflictError(ValueError):
    """Raised when an optimistic concurrency precondition (HTTP 412) fails.

    Subclasses ValueError so existing ``except ValueError`` callers still catch it,
    while callers that need to distinguish a conflict from a bad-ID error can use
    ``except ConcurrencyConflictError``.
    """
