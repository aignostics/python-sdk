"""Service of Aignostics Python SDK."""

import os

from dotenv import load_dotenv

from .models import Echo, Utterance
from .settings import Language, Settings

load_dotenv()
THE_VAR = os.getenv("THE_VAR", "not defined")


class Service:
    """Service of Aignostics Python SDK."""

    _settings: Settings

    def __init__(self) -> None:
        """Initialize service."""
        self._settings = Settings()  # pyright: ignore[reportCallIssue] - false positive
        self.is_healthy = True

    def healthy(self) -> bool:
        """
        Check if the service is healthy.

        Returns:
            bool: True if the service is healthy, False otherwise.
        """
        return self.is_healthy

    def info(self) -> str:
        """
        Get info about configuration of service.

        Returns:
            str: Service configuration.
        """
        return self._settings.model_dump_json()

    def get_hello_world(self) -> str:
        """
        Get a hello world message.

        Returns:
            str: Hello world message.
        """
        match self._settings.language:
            case Language.GERMAN:
                return "Hallo, Welt!"
            case _:
                return "Hello, world!"

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
