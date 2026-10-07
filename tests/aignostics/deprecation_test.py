"""Tests for the deprecation notice that the SDK shows on import."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from aignostics.constants import DEPRECATION_NOTICE

ENV_WITHOUT_PYTEST_FLAG = {key: value for key, value in os.environ.items() if key != "PYTEST_RUNNING_AIGNOSTICS"}


def _import_in_library_mode() -> subprocess.CompletedProcess[str]:
    """Import aignostics in a fresh Python process, outside of pytest mode.

    Returns:
        subprocess.CompletedProcess[str]: The completed process with captured output.
    """
    return subprocess.run(
        [sys.executable, "-W", "always::FutureWarning", "-c", "import aignostics"],
        capture_output=True,
        text=True,
        check=False,
        shell=False,
        encoding="utf-8",
        env=ENV_WITHOUT_PYTEST_FLAG,
    )


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_import_in_library_mode_emits_future_warning() -> None:
    """Import in library mode emits a FutureWarning with the deprecation notice."""
    result = _import_in_library_mode()

    assert result.returncode == 0, result.stderr
    assert f"FutureWarning: {DEPRECATION_NOTICE}" in result.stderr


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_import_in_library_mode_logs_deprecation_warning() -> None:
    """Import in library mode writes the deprecation notice as a WARNING log line."""
    result = _import_in_library_mode()

    assert result.returncode == 0, result.stderr
    log_lines = [line for line in result.stderr.splitlines() if "FutureWarning" not in line]
    assert any("WARNING" in line and DEPRECATION_NOTICE in line for line in log_lines), result.stderr


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_cli_mode_shows_notice_once_without_future_warning() -> None:
    """The CLI shows the deprecation notice once on stderr, without a log line or a FutureWarning."""
    script_name = "aignostics.exe" if sys.platform == "win32" else "aignostics"
    cli_script = Path(sys.executable).parent / script_name

    result = subprocess.run(
        [str(cli_script), "system", "--help"],
        capture_output=True,
        text=True,
        check=False,
        shell=False,
        encoding="utf-8",
        env=ENV_WITHOUT_PYTEST_FLAG,
    )

    assert result.returncode == 0, result.stderr
    assert result.stderr.count(DEPRECATION_NOTICE) == 1, result.stderr
    assert "WARNING" not in result.stderr
    assert "FutureWarning" not in result.stderr


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_import_in_child_process_shows_no_notice(tmp_path: Path) -> None:
    """A child process that imports aignostics does not repeat the deprecation notice."""
    script = tmp_path / "spawn_child.py"
    script.write_text(
        "import multiprocessing\n"
        "\n"
        "\n"
        "def child() -> None:\n"
        "    import aignostics  # noqa: F401\n"
        "\n"
        '    print("CHILD_IMPORTED", flush=True)\n'
        "\n"
        "\n"
        'if __name__ == "__main__":\n'
        '    process = multiprocessing.get_context("spawn").Process(target=child)\n'
        "    process.start()\n"
        "    process.join()\n"
        "    raise SystemExit(process.exitcode)\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-W", "always::FutureWarning", str(script)],
        capture_output=True,
        text=True,
        check=False,
        shell=False,
        encoding="utf-8",
        env=ENV_WITHOUT_PYTEST_FLAG,
    )

    assert result.returncode == 0, result.stderr
    assert "CHILD_IMPORTED" in result.stdout
    assert DEPRECATION_NOTICE not in result.stderr
