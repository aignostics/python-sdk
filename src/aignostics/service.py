"""Service of Aignostics Python SDK."""

import os

from dotenv import load_dotenv

load_dotenv()
THE_VAR = os.getenv("THE_VAR", "not defined")


class Service:
    """Service of Aignostics Python SDK."""

    def __init__(self) -> None:
        """Initialize service."""
        self.is_healthy = True

    @staticmethod
    def get_hello_world() -> str:
        """
        Get a hello world message.

        Returns:
            str: Hello world message.
        """
        return f"Hello, world! The value of THE_VAR is {THE_VAR}"

    def healthy(self) -> bool:
        """
        Check if the service is healthy.

        Returns:
            bool: True if the service is healthy, False otherwise.
        """
        return self.is_healthy
