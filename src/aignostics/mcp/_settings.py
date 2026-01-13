"""Settings for the MCP server."""

from __future__ import annotations

import os
from enum import StrEnum
from pathlib import Path


class Environment(StrEnum):
    """Platform environment options."""

    PRODUCTION = "production"
    STAGING = "staging"


# Environment API roots
ENV_API_ROOTS = {
    Environment.PRODUCTION: "https://platform.aignostics.com",
    Environment.STAGING: "https://platform-staging.aignostics.com",
}

DEFAULT_ENVIRONMENT = Environment.PRODUCTION

# Default cache directory for downloaded readouts
# Can be overridden via AIGNOSTICS_MCP_READOUTS_DIR environment variable
DEFAULT_CACHE_DIR = Path.home() / "aignostics_readouts"


def get_readouts_dir() -> Path:
    """Get the readouts directory from environment or use default.

    The directory can be configured via AIGNOSTICS_MCP_READOUTS_DIR.
    Default is ~/aignostics_readouts (visible in home directory).

    Returns:
        Path to the readouts directory.
    """
    env_dir = os.environ.get("AIGNOSTICS_MCP_READOUTS_DIR")
    if env_dir:
        return Path(env_dir)
    return DEFAULT_CACHE_DIR


def configure_environment(env: Environment | None = None) -> str:
    """Configure the SDK to use the specified environment.

    Args:
        env: Environment to use. If None, uses AIGNOSTICS_API_ROOT env var
             or defaults to production.

    Returns:
        The configured API root URL.
    """
    if env is None:
        # Check if already configured via environment
        existing = os.environ.get("AIGNOSTICS_API_ROOT")
        if existing:
            return existing
        env = DEFAULT_ENVIRONMENT

    api_root = ENV_API_ROOTS[env]
    os.environ["AIGNOSTICS_API_ROOT"] = api_root
    return api_root


def get_cache_dir() -> Path:
    """Get the cache directory, creating it if needed.

    Returns:
        Path to the MCP cache directory.
    """
    cache_dir = get_readouts_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_readout_cache_path(run_id: str, readout_type: str) -> Path:
    """Get the cache path for a specific readout file.

    Args:
        run_id: The run ID.
        readout_type: Type of readout ('slide' or 'cell').

    Returns:
        Path to the cached readout file.
    """
    cache_dir = get_cache_dir() / run_id
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{readout_type}_readouts.csv"
