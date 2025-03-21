"""Service of Aignostics Python SDK's."""

import os

from dotenv import load_dotenv

from aignostics.models import Echo, Utterance

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

    @staticmethod
    def echo(utterance: Utterance) -> Echo:
        """
        Loudly echo utterance.

        Args:
            utterance (Utterance): The utterance to echo.

        Returns:
            Echo: The loudly echoed utterance.

        Raises:
            ValueError: If the utterance is empty or contains only whitespace.
        """
        return Echo(text=utterance.text.upper())
