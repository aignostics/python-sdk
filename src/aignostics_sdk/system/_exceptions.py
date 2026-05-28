"""Exceptions of system module."""


class OpenAPISchemaError(ValueError):
    """Exception raised when OpenAPI schema cannot be loaded."""

    def __init__(self, error: Exception) -> None:
        """Initialize exception with the underlying error."""
        super().__init__(f"Failed to load OpenAPI schema: {error}")
