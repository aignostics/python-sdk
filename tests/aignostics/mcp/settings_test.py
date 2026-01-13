"""Tests for MCP settings module."""

from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

import pytest

from aignostics.mcp._settings import (
    DEFAULT_CACHE_DIR,
    DEFAULT_ENVIRONMENT,
    ENV_API_ROOTS,
    Environment,
    configure_environment,
    get_cache_dir,
    get_readout_cache_path,
    get_readouts_dir,
)

# =============================================================================
# Environment Enum Tests
# =============================================================================


@pytest.mark.unit
def test_environment_enum_values() -> None:
    """Test that Environment enum has expected values."""
    assert Environment.PRODUCTION == "production"
    assert Environment.STAGING == "staging"


@pytest.mark.unit
def test_env_api_roots_has_all_environments() -> None:
    """Test that ENV_API_ROOTS has entries for all environments."""
    for env in Environment:
        assert env in ENV_API_ROOTS


@pytest.mark.unit
def test_default_environment_is_production() -> None:
    """Test that default environment is production."""
    assert DEFAULT_ENVIRONMENT == Environment.PRODUCTION


# =============================================================================
# get_readouts_dir Tests
# =============================================================================


@pytest.mark.unit
def test_get_readouts_dir_returns_default_when_env_not_set() -> None:
    """Test that default directory is returned when env var not set."""
    with mock.patch.dict(os.environ, {}, clear=True):
        os.environ.pop("AIGNOSTICS_MCP_READOUTS_DIR", None)
        result = get_readouts_dir()
        assert result == DEFAULT_CACHE_DIR


@pytest.mark.unit
def test_get_readouts_dir_returns_env_var_when_set() -> None:
    """Test that env var value is returned when set."""
    custom_dir = "/custom/readouts/dir"
    with mock.patch.dict(os.environ, {"AIGNOSTICS_MCP_READOUTS_DIR": custom_dir}):
        result = get_readouts_dir()
        assert result == Path(custom_dir)


# =============================================================================
# configure_environment Tests
# =============================================================================


@pytest.mark.unit
def test_configure_environment_uses_existing_env_var() -> None:
    """Test that existing AIGNOSTICS_API_ROOT is preserved."""
    existing_url = "https://custom.api.example.com"
    with mock.patch.dict(os.environ, {"AIGNOSTICS_API_ROOT": existing_url}):
        result = configure_environment()
        assert result == existing_url


@pytest.mark.unit
def test_configure_environment_sets_production_by_default() -> None:
    """Test that production API root is set when no env var exists."""
    with mock.patch.dict(os.environ, {}, clear=True):
        os.environ.pop("AIGNOSTICS_API_ROOT", None)
        result = configure_environment()
        assert result == ENV_API_ROOTS[Environment.PRODUCTION]
        assert os.environ["AIGNOSTICS_API_ROOT"] == ENV_API_ROOTS[Environment.PRODUCTION]


@pytest.mark.unit
def test_configure_environment_sets_staging_when_specified() -> None:
    """Test that staging API root is set when specified."""
    with mock.patch.dict(os.environ, {}, clear=True):
        os.environ.pop("AIGNOSTICS_API_ROOT", None)
        result = configure_environment(Environment.STAGING)
        assert result == ENV_API_ROOTS[Environment.STAGING]


# =============================================================================
# get_cache_dir Tests
# =============================================================================


@pytest.mark.unit
def test_get_cache_dir_creates_directory(tmp_path: Path) -> None:
    """Test that cache directory is created if it doesn't exist."""
    custom_dir = tmp_path / "test_cache"
    assert not custom_dir.exists()

    with mock.patch.dict(os.environ, {"AIGNOSTICS_MCP_READOUTS_DIR": str(custom_dir)}):
        result = get_cache_dir()
        assert result == custom_dir
        assert custom_dir.exists()


# =============================================================================
# get_readout_cache_path Tests
# =============================================================================


@pytest.mark.unit
def test_get_readout_cache_path_returns_correct_path_for_slide(tmp_path: Path) -> None:
    """Test that correct path is returned for slide readouts."""
    run_id = "test-run-123"
    with mock.patch.dict(os.environ, {"AIGNOSTICS_MCP_READOUTS_DIR": str(tmp_path)}):
        result = get_readout_cache_path(run_id, "slide")
        expected = tmp_path / run_id / "slide_readouts.csv"
        assert result == expected


@pytest.mark.unit
def test_get_readout_cache_path_returns_correct_path_for_cell(tmp_path: Path) -> None:
    """Test that correct path is returned for cell readouts."""
    run_id = "test-run-456"
    with mock.patch.dict(os.environ, {"AIGNOSTICS_MCP_READOUTS_DIR": str(tmp_path)}):
        result = get_readout_cache_path(run_id, "cell")
        expected = tmp_path / run_id / "cell_readouts.csv"
        assert result == expected


@pytest.mark.unit
def test_get_readout_cache_path_creates_run_directory(tmp_path: Path) -> None:
    """Test that run-specific directory is created."""
    run_id = "new-run-789"
    run_dir = tmp_path / run_id
    assert not run_dir.exists()

    with mock.patch.dict(os.environ, {"AIGNOSTICS_MCP_READOUTS_DIR": str(tmp_path)}):
        get_readout_cache_path(run_id, "cell")
        assert run_dir.exists()
