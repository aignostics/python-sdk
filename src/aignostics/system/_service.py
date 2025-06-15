"""System service."""

import json
import os
import platform
import re
import sys
import typing as t
from http import HTTPStatus
from pathlib import Path
from socket import AF_INET, SOCK_DGRAM, socket
from typing import Any, NotRequired, TypedDict
from urllib.request import getproxies

from dotenv import set_key as dotenv_set_key
from dotenv import unset_key as dotenv_unset_key
from pydantic_settings import BaseSettings
from requests import get

from ..utils import (  # noqa: TID252
    UNHIDE_SENSITIVE_INFO,
    BaseService,
    Health,
    __env__,
    __env_file__,
    __project_name__,
    __project_path__,
    __repository_url__,
    __version__,
    get_logger,
    get_process_info,
    load_settings,
    locate_subclasses,
)
from ._exceptions import OpenAPISchemaError
from ._settings import Settings

logger = get_logger(__name__)

JsonValue: t.TypeAlias = str | int | float | list["JsonValue"] | t.Mapping[str, "JsonValue"] | None
JsonType: t.TypeAlias = list[JsonValue] | t.Mapping[str, JsonValue]

# Note: There is multiple measurements and network calls
MEASURE_INTERVAL_SECONDS = 2
NETWORK_TIMEOUT = 5
IPIFY_URL = "https://api.ipify.org"


class RuntimeDict(TypedDict, total=False):
    """Type for runtime information dictionary."""

    environment: str
    username: str
    process: dict[str, Any]
    host: dict[str, Any]
    python: dict[str, Any]
    environ: dict[str, str]


class InfoDict(TypedDict, total=False):
    """Type for the info dictionary."""

    package: dict[str, Any]
    runtime: RuntimeDict
    settings: dict[str, Any]
    __extra__: NotRequired[dict[str, Any]]


class Service(BaseService):
    """System service."""

    _settings: Settings

    def __init__(self) -> None:
        """Initialize service."""
        super().__init__(Settings)

    @staticmethod
    def _is_healthy() -> bool:
        """Check if the service itself is healthy.

        Returns:
            bool: True if the service is healthy, False otherwise.
        """
        return True

    @staticmethod
    def _determine_network_health() -> Health:
        """Determine we can reach a well known and secure endpoint.

        - Checks if health endpoint is reachable and returns 200 OK
        - Uses requests library for a direct connection check without authentication

        Returns:
            Health: The healthiness of the network connection via basic unauthenticated request.
        """
        try:
            response = get(
                url=IPIFY_URL,
                headers={"User-Agent": f"aignostics-python-sdk/{__version__}"},
                timeout=NETWORK_TIMEOUT,
            )

            if response.status_code != HTTPStatus.OK:
                logger.error("'%s' returned '%s'", IPIFY_URL, response.status_code)
                return Health(
                    status=Health.Code.DOWN,
                    reason=f"'{IPIFY_URL}' returned status '{response.status_code}'",
                )
        except Exception as e:
            message = f"Issue reaching {IPIFY_URL}: {e}"
            logger.exception(message)
            return Health(status=Health.Code.DOWN, reason=message)

        return Health(status=Health.Code.UP)

    @staticmethod
    def health_static() -> Health:
        """Determine health of the system.

        - This method is static and does not require an instance of the service.
        - It is used to determine the health of the system without needing to pass the service.

        Returns:
            Health: The health of the system.
        """
        return Service().health()

    def health(self) -> Health:
        """Determine aggregate health of the system.

        - Health exposed by implementations of BaseService in other
            modules is automatically included into the health tree.
        - See utils/_health.py:Health for an explanation of the health tree.

        Returns:
            Health: The aggregate health of the system.
        """
        components: dict[str, Health] = {}
        for service_class in locate_subclasses(BaseService):
            if service_class is not Service:
                components[f"{service_class.__module__}.{service_class.__name__}"] = service_class().health()
        components["network"] = self._determine_network_health()

        # Set the system health status based on is_healthy attribute
        status = Health.Code.UP if self._is_healthy() else Health.Code.DOWN
        reason = None if self._is_healthy() else "System marked as unhealthy"
        return Health(status=status, components=components, reason=reason)

    def is_token_valid(self, token: str) -> bool:
        """Check if the presented token is valid.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        logger.info(token)
        if not self._settings.token:
            logger.warning("Token is not set in settings.")
            return False
        return token == self._settings.token.get_secret_value()

    @staticmethod
    def _get_public_ipv4(timeout: int = NETWORK_TIMEOUT) -> str | None:
        """Get the public IPv4 address of the system.

        Args:
            timeout (int): Timeout for the request in seconds.

        Returns:
            str: The public IPv4 address.
        """
        try:
            response = get(url=IPIFY_URL, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            message = f"Failed to get public IP: {e}"
            logger.exception(message)
            return None

    @staticmethod
    def _get_local_ipv4() -> str | None:
        """Get the local IPv4 address of the system.

        Returns:
            str: The local IPv4 address.
        """
        try:
            with socket(AF_INET, SOCK_DGRAM) as connection:
                connection.connect((".".join(str(1) for _ in range(4)), 53))
                return str(connection.getsockname()[0])
        except Exception as e:
            message = f"Failed to get local IP: {e}"
            logger.exception(message)
            return None

    @staticmethod
    def _is_secret_key(key: str) -> bool:
        """Determine if a key name indicates it contains secret information.

        This function uses two different matching strategies:
        1. Word boundary matching for terms like "id" and "auth" to avoid false positives
        2. Simple string matching for unambiguous secret terms like "token", "key", "secret", "password"

        Args:
            key: The key name to check

        Returns:
            bool: True if the key likely contains secret information
        """
        key_lower = key.lower()

        # Terms that require word boundary matching to avoid false positives
        # (e.g., "id" shouldn't match "valid" or "middle")
        word_boundary_terms = ["id"]

        # Terms that can use simple string matching as they're unambiguous
        string_match_terms = [
            "auth",
            "bearer",
            "cert",
            "credential",
            "hash",
            "jwt",
            "key",
            "nonce",
            "oauth",
            "password",
            "private",
            "salt",
            "secret",
            "seed",
            "session",
            "signature",
            "token",
        ]

        # Check word boundary terms using regex
        for term in word_boundary_terms:
            # Use regex to match word boundaries (non-alphanumeric characters)
            pattern = rf"(?:^|[^a-zA-Z]){re.escape(term)}(?:[^a-zA-Z]|$)"
            if re.search(pattern, key_lower):
                return True  # Check simple string match terms
        return any(term in key_lower for term in string_match_terms)

    @staticmethod
    def info(include_environ: bool = False, mask_secrets: bool = True) -> dict[str, Any]:  # type: ignore[override]
        """
        Get info about configuration of service.

        - Runtime information is automatically compiled.
        - Settings are automatically aggregated from all implementations of
            Pydantic BaseSettings in this package.
        - Info exposed by implementations of BaseService in other modules is
            automatically included into the info dict.

        Args:
            include_environ (bool): Whether to include environment variables in the info.
            mask_secrets (bool): Whether to mask information in environment variables identified as secrets

        Returns:
            dict[str, Any]: Service configuration.
        """
        import psutil  # noqa: PLC0415
        from uptime import boottime, uptime  # noqa: PLC0415

        bootdatetime = boottime()
        vmem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        cpu_percent = psutil.cpu_percent(interval=MEASURE_INTERVAL_SECONDS)
        cpu_times_percent = psutil.cpu_times_percent(interval=MEASURE_INTERVAL_SECONDS)
        cpu_freq = None
        try:
            cpu_freq = psutil.cpu_freq()
        except RuntimeError:
            logger.warning("Failed to get CPU frequency.")  # Happens on macOS VM on GHA

        rtn: InfoDict = {
            "package": {
                "version": __version__,
                "name": __project_name__,
                "repository": __repository_url__,
                "local": __project_path__,
            },
            "runtime": {
                "environment": __env__,
                "username": psutil.Process().username(),
                "process": {
                    "command_line": " ".join(sys.argv),
                    "entry_point": sys.argv[0] if sys.argv else None,
                    "process_info": json.loads(get_process_info().model_dump_json()),
                },
                "host": {
                    "os": {
                        "platform": platform.platform(),
                        "system": platform.system(),
                        "release": platform.release(),
                        "version": platform.version(),
                    },
                    "machine": {
                        "cpu": {
                            "percent": cpu_percent,
                            "load_avg": psutil.getloadavg(),
                            "user": cpu_times_percent.user,
                            "system": cpu_times_percent.system,
                            "idle": cpu_times_percent.idle,
                            "arch": platform.machine(),
                            "processor": platform.processor(),
                            "count": os.cpu_count(),
                            "frequency": {
                                "current": cpu_freq.current if cpu_freq else None,
                                "min": cpu_freq.min if cpu_freq else None,
                                "max": cpu_freq.max if cpu_freq else None,
                            },
                        },
                        "memory": {
                            "percent": vmem.percent,
                            "total": vmem.total,
                            "available": vmem.available,
                            "used": vmem.used,
                            "free": vmem.free,
                        },
                        "swap": {
                            "percent": swap.percent,
                            "total": swap.total,
                            "used": swap.used,
                            "free": swap.free,
                        },
                    },
                    "network": {
                        "hostname": platform.node(),
                        "local_ipv4": Service._get_local_ipv4(),
                        "public_ipv4": Service._get_public_ipv4(),
                        "proxies": getproxies(),
                        "requests_ca_bundle": os.getenv("REQUESTS_CA_BUNDLE"),
                    },
                    "uptime": {
                        "seconds": uptime(),
                        "boottime": bootdatetime.isoformat() if bootdatetime else None,
                    },
                },
                "python": {
                    "version": platform.python_version(),
                    "compiler": platform.python_compiler(),
                    "implementation": platform.python_implementation(),
                    "sys.path": sys.path,
                    "interpreter_path": sys.executable,
                },
            },
            "settings": {},
        }

        runtime = rtn["runtime"]
        if include_environ:
            if mask_secrets:
                runtime["environ"] = {
                    k: "*********" if Service._is_secret_key(k) else v for k, v in sorted(os.environ.items())
                }
            else:
                runtime["environ"] = dict(sorted(os.environ.items()))

        settings: dict[str, Any] = {}
        for settings_class in locate_subclasses(BaseSettings):
            settings_instance = load_settings(settings_class)
            env_prefix = settings_instance.model_config.get("env_prefix", "")
            settings_dict = json.loads(
                settings_instance.model_dump_json(context={UNHIDE_SENSITIVE_INFO: not mask_secrets})
            )
            for key, value in settings_dict.items():
                flat_key = f"{env_prefix}{key}".upper()
                settings[flat_key] = value
        rtn["settings"] = {k: settings[k] for k in sorted(settings)}

        # Convert the TypedDict to a regular dict before adding dynamic service keys
        result_dict: dict[str, Any] = dict(rtn)

        for service_class in locate_subclasses(BaseService):
            if service_class is not Service:
                service = service_class()
                result_dict[service.key()] = service.info(mask_secrets=mask_secrets)

        logger.info("Service info: %s", result_dict)
        return result_dict

    @staticmethod
    def openapi_schema() -> JsonType:
        """
        Get OpenAPI schema of the webservice API provided by the platform.

        Returns:
            dict[str, object]: OpenAPI schema.

        Raises:
            OpenAPISchemaError: If the OpenAPI schema file cannot be found or is not valid JSON.
        """
        schema_path = Path(__file__).parent.parent.parent.parent / "codegen" / "in" / "api.json"
        try:
            with schema_path.open(encoding="utf-8") as f:
                return json.load(f)  # type: ignore[no-any-return]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise OpenAPISchemaError(e) from e

    @staticmethod
    def _get_env_files_paths() -> list[Path]:
        """Get the paths of the environment files.

        Returns:
            list[Path]: List of environment file paths.
        """
        return __env_file__

    @staticmethod
    def dotenv_get(key: str) -> str | None:
        """Get value of key in environment.

        Args:
            key (str): The key to add.

        Returns:
            str | None: The value of the key if it exists, None otherwise.
        """
        return os.getenv(key, None)

    @staticmethod
    def dotenv_set(key: str, value: str) -> None:
        """Set key-value pair in primary .env file, unset in alternative .env files.

        Args:
            key (str): The key to add.
            value (str): The value to add.

        Raises:
            ValueError: If the primary .env file does not exist.

        """
        Service.dotenv_unset(key)

        dotenv_path = Service._get_env_files_paths()[0]  # Primary .env file
        if not dotenv_path.is_file():
            message = f"Primary .env file '{dotenv_path!s}' does not exist, canceling update of .env files"
            logger.error(message)
            raise ValueError(message)

        dotenv_set_key(dotenv_path=str(dotenv_path.resolve()), key_to_set=key, value_to_set=value, quote_mode="auto")
        os.environ[key] = value

    @staticmethod
    def dotenv_unset(key: str) -> int:
        """Unset key-value pair in all .env files.

        Args:
            key (str): The key to remove.

        Returns:
            int: The number of times the key has been removed across files.
        """
        removed_count = 0
        for dotenv_path in Service._get_env_files_paths():
            if not dotenv_path.is_file():
                message = f"File '{dotenv_path!s}' does not exist, skipping update"
                logger.debug(message)
                continue
            dotenv_unset_key(dotenv_path=str(dotenv_path.resolve()), key_to_unset=key, quote_mode="auto")
        os.environ.pop(key, None)
        return removed_count

    @staticmethod
    def remote_diagnostics_enabled() -> bool:
        """Check if remote diagnostics are enabled.

        Returns:
            bool: True if remote diagnostics are enabled, False otherwise.
        """
        return (
            Service.dotenv_get(f"{__project_name__.upper()}_SENTRY_ENABLED") == "1"
            and Service.dotenv_get(f"{__project_name__.upper()}_LOGFIRE_ENABLED") == "1"
        )

    @staticmethod
    def remote_diagnostics_enable() -> None:
        """Enable remote diagnostics via Sentry and Logfire. Data stored in EU data centers.

        Raises:
            ValueError: If the environment variable cannot be set.
        """
        Service.dotenv_set(f"{__project_name__.upper()}_SENTRY_ENABLED", "1")
        Service.dotenv_set(f"{__project_name__.upper()}_LOGFIRE_ENABLED", "1")

    @staticmethod
    def remote_diagnostics_disable() -> None:
        """Disable remote diagnostics."""
        Service.dotenv_unset(f"{__project_name__.upper()}_SENTRY_ENABLED")
        Service.dotenv_unset(f"{__project_name__.upper()}_LOGFIRE_ENABLED")

    @staticmethod
    def http_proxy_enable(
        host: str,
        port: int,
        scheme: str,
        ssl_cert_file: str | None = None,
        no_ssl_verify: bool = False,
    ) -> None:
        """Enable HTTP proxy.

        Args:
            host (str): The host of the proxy server.
            port (int): The port of the proxy server.
            scheme (str): The scheme of the proxy server (e.g., "http", "https").
            ssl_cert_file (str | None): Path to the SSL certificate file, if any.
            no_ssl_verify (bool): Whether to disable SSL verification

        Raises:
            ValueError: If both 'ssl_cert_file' and 'ssl_disable_verify' are set.
        """
        url = f"{scheme}://{host}:{port}"
        Service.dotenv_set("HTTP_PROXY", url)
        Service.dotenv_set("HTTPS_PROXY", url)
        if ssl_cert_file is not None and no_ssl_verify:
            message = "Cannot set both 'ssl_cert_file' and 'ssl_disable_verify'. Please choose one."
            logger.warning(message)
            raise ValueError(message)
        if no_ssl_verify:
            Service.dotenv_set("SSL_NO_VERIFY", "1")
            Service.dotenv_set("SSL_CERT_FILE", "")
            Service.dotenv_set("REQUESTS_CA_BUNDLE", "")
            Service.dotenv_set("CURL_CA_BUNDLE", "")
        else:
            Service.dotenv_unset("SSL_NO_VERIFY")
            Service.dotenv_unset("SSL_CERT_FILE")
            Service.dotenv_unset("REQUESTS_CA_BUNDLE")
            Service.dotenv_unset("CURL_CA_BUNDLE")
            if ssl_cert_file:
                file = Path(ssl_cert_file).resolve()
                if not file.is_file():
                    message = f"SSL certificate file '{ssl_cert_file}' does not exist."
                    logger.warning(message)
                    raise ValueError(message)
                Service.dotenv_set("SSL_CERT_FILE", str(ssl_cert_file))
                Service.dotenv_set("REQUESTS_CA_BUNDLE", str(ssl_cert_file))
                Service.dotenv_set("CURL_CA_BUNDLE", str(ssl_cert_file))

    @staticmethod
    def http_proxy_disable() -> None:
        """Disable HTTP proxy."""
        Service.dotenv_unset("HTTP_PROXY")
        Service.dotenv_unset("HTTPS_PROXY")
        Service.dotenv_unset("SSL_CERT_FILE")
        Service.dotenv_unset("SSL_NO_VERIFY")
        Service.dotenv_unset("REQUESTS_CA_BUNDLE")
        Service.dotenv_unset("CURL_CA_BUNDLE")
