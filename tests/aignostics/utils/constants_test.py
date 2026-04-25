"""Tests for constants module."""

import re

import pytest

from aignostics.utils import __python_version__, __version__


@pytest.mark.unit
def test_python_version_format(record_property) -> None:
    """Test that __python_version__ returns a clean semver-like version string.

    The version should be in format X.Y.Z (e.g., 3.14.3) without build info,
    compiler details, or other metadata that sys.version includes.
    """
    record_property("tested-item-id", "SPEC-UTILS-CONSTANTS")

    # Should match semver-like pattern: X.Y or X.Y.Z
    version_pattern = re.compile(r"^\d+\.\d+(\.\d+)?$")

    assert version_pattern.match(__python_version__), (
        f"__python_version__ should be a clean version string like '3.14.3', got '{__python_version__}'"
    )


@pytest.mark.unit
def test_python_version_no_build_info(record_property) -> None:
    """Test that __python_version__ does not contain build metadata.

    sys.version includes extra info like '(main, Dec 2 2025, 22:17:19) [Clang 21.1.4]'
    which should NOT be present in __python_version__.
    """
    record_property("tested-item-id", "SPEC-UTILS-CONSTANTS")

    # These are common patterns found in sys.version but NOT wanted in __python_version__
    unwanted_patterns = [
        "(",  # Build date info
        ")",
        "[",  # Compiler info like [Clang 21.1.4]
        "]",
        "GCC",
        "Clang",
        "MSC",
    ]

    for pattern in unwanted_patterns:
        assert pattern not in __python_version__, (
            f"__python_version__ should not contain '{pattern}', got '{__python_version__}'"
        )


@pytest.mark.unit
def test_version_is_string(record_property) -> None:
    """Test that __version__ and __python_version__ are strings."""
    record_property("tested-item-id", "SPEC-UTILS-CONSTANTS")

    assert isinstance(__version__, str), f"__version__ should be a string, got {type(__version__)}"
    assert isinstance(__python_version__, str), f"__python_version__ should be a string, got {type(__python_version__)}"
