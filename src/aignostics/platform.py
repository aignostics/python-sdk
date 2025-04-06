"""Service providing platform diagnostics and utilities."""

import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from . import OpenAPISchemaError
from .client import authentication_settings
from .constants import (
    API_ROOT_DEV,
    API_ROOT_PRODUCTION,
    API_ROOT_STAGING,
    __project_name__,
    __project_path__,
    __version__,
)
from .settings import Settings
from .types import JsonType

load_dotenv()


class Platform:
    """Service providing platform diagnostics and utilities."""

    _settings: Settings

    def __init__(self) -> None:
        """Initialize service."""
        self._settings = Settings()  # pyright: ignore[reportCallIssue] - false positive
        self.is_healthy = True

    def healthy(self) -> bool:
        """
        Check if the platform is healthy.

        Returns:
            bool: True if the platform is healthy, False otherwise.
        """
        return self.is_healthy

    def info(self, env: bool = True, filter_secrets: bool = True) -> dict[str, Any]:
        """
        For diagnostics compile info about user and platform environment.

        Returns:
            dict: Info about user and environment, including organisation,
                execution environment, local and remote platform.
        """
        info_dict = {
            "user": {
                "name": "TODO",
                "email": "TODO",
                "id": "TODO",
                "organisation": {
                    "name": "TODO",
                    "id": "TODO",
                    "tier": "TODO",
                },
            },
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
                "settings": {
                    "core": json.loads(self._settings.model_dump_json()),
                    "authentication": json.loads(authentication_settings().model_dump_json()),
                },
            },
            "remote": {
                "platform": {
                    "production": {
                        "API_ROOT": API_ROOT_PRODUCTION,
                    },
                    "staging": {
                        "API_ROOT": API_ROOT_STAGING,
                    },
                    "dev": {
                        "API_ROOT": API_ROOT_DEV,
                    },
                }
            },
        }

        if env:
            if filter_secrets:
                info_dict["local"]["execution"]["env"] = {  # type: ignore[index]
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
                info_dict["local"]["execution"]["env"] = dict(os.environ)  # type: ignore[index]

        return info_dict

    def install(self) -> None:
        """Complete and validate installation of the CLI."""
        # TODO (Helmut, Andreas): Build

    @staticmethod
    def openapi_schema() -> JsonType:
        """
        Get OpenAPI schema of the webservice API provided by the platform.

        Returns:
            dict[str, object]: OpenAPI schema.

        Raises:
            OpenAPISchemaError: If the OpenAPI schema file cannot be found or is not valid JSON.
        """
        schema_path = Path(__file__).parent.parent.parent / "codegen" / "in" / "api.json"
        try:
            with schema_path.open(encoding="utf-8") as f:
                return json.load(f)  # type: ignore[no-any-return]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise OpenAPISchemaError(e) from e
