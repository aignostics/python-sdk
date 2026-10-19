"""Tests for constants module."""

import re

import pytest

from aignostics.utils import __python_version__, __version__
from aignostics.utils._constants import _is_cli_mode


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


@pytest.mark.unit
@pytest.mark.parametrize(
    "argv",
    [
        ["/home/user/.venv/bin/aignostics", "system", "info"],
        ["/home/user/.cache/uv/archive-v0/abc/bin/aignostics", "launchpad"],
        [r"D:\a\python-sdk\.venv\Scripts\aignostics.exe", "system", "--help"],
        [r"C:\Program Files\Aignostics\AIGNOSTICS.EXE"],
        ["/Applications/aignostics.app/Contents/MacOS/aignostics"],
        ["/usr/bin/python3", "aignostics", "system", "info"],
        ["/home/user/sdk/gui_watch.py"],
        ["/usr/bin/python3", "gui_watch.py"],
    ],
)
def test_is_cli_mode_detects_cli(argv: list[str], record_property) -> None:
    """The CLI, the Windows console script, the native app and the GUI watcher run in CLI mode."""
    record_property("tested-item-id", "SPEC-UTILS-CONSTANTS")

    assert _is_cli_mode(argv)


@pytest.mark.unit
@pytest.mark.parametrize(
    "argv",
    [
        [],
        [""],
        ["-c"],
        ["/home/user/notebook.py"],
        [r"C:\Users\user\analysis.py"],
        ["/usr/bin/python3", "my_aignostics_script.py"],
        ["/home/user/.venv/bin/pytest", "tests"],
        ["/home/user/my-aignostics"],
    ],
)
def test_is_cli_mode_rejects_library_use(argv: list[str], record_property) -> None:
    """Scripts, notebooks and other tools that import the SDK do not run in CLI mode."""
    record_property("tested-item-id", "SPEC-UTILS-CONSTANTS")

    assert not _is_cli_mode(argv)
