"""Service of Aignostics Python SDK."""

import json
from pathlib import Path

from dotenv import load_dotenv

from . import OpenAPISchemaError
from .settings import Settings

load_dotenv()


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

    @staticmethod
    def openapi_schema() -> dict:
        """
        Get OpenAPI schema.

        Returns:
            dict: OpenAPI schema.

        Raises:
            OpenAPISchemaError: If the OpenAPI schema file cannot be found or is not valid JSON.
        """
        schema_path = Path(__file__).parent.parent.parent / "schema" / "api.json"
        try:
            with schema_path.open(encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise OpenAPISchemaError(e) from e
