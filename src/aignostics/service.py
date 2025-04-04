"""Service of Aignostics Python SDK."""

import json
import os
import platform
import sys
from pathlib import Path

from dotenv import load_dotenv

from . import OpenAPISchemaError
from .constants import __project_name__, __project_path__, __version__
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

    def info(self, env: bool = True, filter_secrets: bool = True) -> dict:
        """
        For diagnostics compile info about local and remote environment.

        Returns:
            dict: Info about local and remote environment
        """
        info_dict = {
            "local": {
                "sdk": {
                    "version": __version__,
                    "name": __project_name__,
                    "path": __project_path__,
                },
                "execution": {
                    "interpreter_path": sys.executable,
                    "command_line": " ".join(sys.argv),
                    "entry_point": sys.argv[0] if sys.argv else None,
                },
                "platform": {
                    "os": {
                        "system": platform.system(),
                        "release": platform.release(),
                        "version": platform.version(),
                        "machine": platform.machine(),
                        "processor": platform.processor(),
                    },
                    "python": {
                        "version": platform.python_version(),
                        "compiler": platform.python_compiler(),
                        "implementation": platform.python_implementation(),
                    },
                },
                "settings": self._settings.model_dump_json(),
            },
            "remote": {
                "dev": {
                    "url": "https://api.dev.aignostics.com",
                },
                "staging": {
                    "url": "https://api.staging.aignostics.com",
                },
                "production": {
                    "url": "https://api.aignostics.com",
                },
            },
        }

        if env:
            if filter_secrets:
                info_dict["local"]["execution"]["env"] = {
                    k: v
                    for k, v in os.environ.items()
                    if not (
                        "token" in k.lower()
                        or "key" in k.lower()
                        or "secret" in k.lower()
                        or "password" in k.lower()
                        or "auth" in k.lower()
                    )
                }
            else:
                info_dict["local"]["execution"]["env"] = dict(os.environ)

        return info_dict

    @staticmethod
    def openapi_schema() -> dict:
        """
        Get OpenAPI schema.

        Returns:
            dict: OpenAPI schema.

        Raises:
            OpenAPISchemaError: If the OpenAPI schema file cannot be found or is not valid JSON.
        """
        schema_path = Path(__file__).parent.parent.parent / "codegen" / "in" / "api.json"
        try:
            with schema_path.open(encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise OpenAPISchemaError(e) from e
