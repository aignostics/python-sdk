"""Tests to verify the CLI functionality of the QuPath module."""

import json
import platform
import re
from pathlib import Path

import psutil
import pytest
from typer.testing import CliRunner

from aignostics.cli import cli
from aignostics.qupath import QUPATH_VERSION
from tests.conftest import normalize_output


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.skipif(
    platform.system() == "Linux" and platform.machine() in {"aarch64", "arm64"},
    reason="QuPath is not supported on ARM64 Linux",
)
@pytest.mark.flaky(retries=3, delay=5, only_on=[AssertionError])
@pytest.mark.timeout(timeout=60 * 10)
@pytest.mark.sequential
def test_cli_install_and_uninstall(runner: CliRunner, qupath_save_restore: None) -> None:
    """Check (un)install works for Windows, Mac and Linux package."""
    # Test installation and uninstallation on different platforms
    if platform.system() == "Windows":
        platforms_to_test = [
            {"system": "Windows"},
        ]
    else:
        platforms_to_test = [
            {"system": "Windows"},
            {"system": "Linux"},
            {"system": "Darwin", "machine": "amd64"},
            {"system": "Darwin", "machine": "arm64"},
        ]

    for platform_config in platforms_to_test:
        install_args = ["qupath", "install", "--platform-system", platform_config["system"]]
        uninstall_args = ["qupath", "uninstall", "--platform-system", platform_config["system"]]
        if "machine" in platform_config:
            install_args.extend(["--platform-machine", platform_config["machine"]])
            uninstall_args.extend(["--platform-machine", platform_config["machine"]])

        result = runner.invoke(cli, install_args)
        assert f"QuPath v{QUPATH_VERSION} installed successfully" in normalize_output(result.output)
        assert result.exit_code == 0

        result = runner.invoke(cli, uninstall_args)
        assert "QuPath uninstalled successfully." in normalize_output(result.output)
        assert result.exit_code == 0


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.skipif(
    platform.system() == "Linux" and platform.machine() in {"aarch64", "arm64"},
    reason="QuPath is not supported on ARM64 Linux",
)
@pytest.mark.flaky(retries=3, delay=5, only_on=[AssertionError])
@pytest.mark.timeout(timeout=60 * 10)
@pytest.mark.sequential
def test_cli_install_launch_project_annotations_headless(
    runner: CliRunner, tmpdir, qupath_teardown, qupath_save_restore: None
) -> None:
    """Check (un)install, launching headless, creating project and adding annotations works."""
    # Step 1: System info determines QuPath is not installed
    result = runner.invoke(cli, ["system", "info"])
    output_data = json.loads(result.stdout)
    assert output_data["qupath"]["app"]["path"] is None
    assert output_data["qupath"]["app"]["version"] is None
    assert result.exit_code == 0

    # Step 2: Check QuPath install succeeds
    result = runner.invoke(cli, ["qupath", "install"])
    assert f"QuPath v{QUPATH_VERSION} installed successfully" in normalize_output(result.output)
    assert result.exit_code == 0

    # Step 3: Check QuPath can now launch successfully
    result = runner.invoke(cli, ["system", "info"])
    output_data = json.loads(result.stdout)
    assert output_data["qupath"]["app"]["path"] is not None
    assert output_data["qupath"]["app"]["version"]["version"] == QUPATH_VERSION
    assert result.exit_code == 0

    # Step 4: Check repeated QuPath install succeeds (idempotent operation)
    result = runner.invoke(cli, ["qupath", "install"])
    assert f"QuPath v{QUPATH_VERSION} installed successfully" in normalize_output(result.output)
    assert result.exit_code == 0

    if platform.system() in {"Linux", "Darwin"}:
        # Step 5: Create QuPath project and add image
        project_dir = Path(tmpdir) / "qupath_project"
        small_pyramidal_dcm = Path(__file__).parent.parent.parent / "resources" / "run" / "small-pyramidal.dcm"
        result = runner.invoke(cli, ["qupath", "add", str(project_dir), str(small_pyramidal_dcm)])
        assert f"Added '1' images to project '{project_dir}'." in normalize_output(result.output)
        assert project_dir.exists(), f"Project directory {project_dir} was not created"
        assert project_dir.parent == Path(tmpdir), f"Project directory {project_dir} is not a subdirectory of {tmpdir}"

        # Step 6: Annotate project with polygons
        cells_json = Path(__file__).parent.parent.parent / "resources" / "cells_broken.json"
        result = runner.invoke(cli, ["qupath", "annotate", str(project_dir), str(small_pyramidal_dcm), str(cells_json)])
        assert "Failed to add images to project: parse error: premature EOF" in normalize_output(result.output)
        assert result.exit_code == 1

    # Step 7: Uninstall QuPath
    result = runner.invoke(cli, ["qupath", "uninstall"])
    assert "QuPath uninstalled successfully." in normalize_output(result.output)
    assert result.exit_code == 0

    # Step 8: Check QuPath info fails if not installed
    result = runner.invoke(cli, ["system", "info"])
    output_data = json.loads(result.stdout)
    assert output_data["qupath"]["app"]["path"] is None
    assert output_data["qupath"]["app"]["version"] is None
    assert result.exit_code == 0


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.skipif(
    platform.system() == "Linux" and platform.machine() in {"aarch64", "arm64"},
    reason="QuPath is not supported on ARM64 Linux",
)
@pytest.mark.flaky(retries=3, delay=5, only_on=[AssertionError])
@pytest.mark.timeout(timeout=60 * 10)
@pytest.mark.sequential
def test_cli_install_and_launch_ui(runner: CliRunner, qupath_teardown, qupath_save_restore: None) -> None:
    """Check (un)install and launching UI versin of QuPath works."""
    # Step 1: Check QuPath launch fails if not installed
    result = runner.invoke(cli, ["qupath", "launch"])
    assert "QuPath is not installed. Use 'uvx aignostics qupath install' to install it." in normalize_output(
        result.output
    )
    assert result.exit_code == 2

    # Step 2: Check QuPath install succeeds
    result = runner.invoke(cli, ["qupath", "install"])
    assert f"QuPath v{QUPATH_VERSION} installed successfully" in normalize_output(result.output)
    assert result.exit_code == 0

    # Step 3: Check QuPath can now launch successfully
    result = runner.invoke(cli, ["qupath", "launch"])
    assert "QuPath launched successfully" in normalize_output(result.output)
    assert result.exit_code == 0
    pid_match = re.search(r"QuPath launched successfully with process id '(\d+)'.", normalize_output(result.output))
    assert pid_match is not None, "PID not found in launch output"
    pid = int(pid_match.group(1))
    assert psutil.Process(pid).is_running(), f"QuPath process wit pid '{pid}' is not running as expected."

    # Step 4: Check we list the process via the CLI
    result = runner.invoke(cli, ["qupath", "processes", "--json"])
    assert f'"pid": {pid},' in normalize_output(result.output)
    assert result.exit_code == 0
    result = runner.invoke(cli, ["qupath", "processes"])
    assert "Process ID" in normalize_output(result.output)
    assert f"{pid}" in normalize_output(result.output)
    assert result.exit_code == 0

    # Step 5: Terminate via CLI
    result = runner.invoke(cli, ["qupath", "terminate"])
    output = normalize_output(result.output)
    terminate_match = re.search(r"Terminated (\d+) running QuPath processes?\.", output)
    assert terminate_match is not None, f"Expected termination message not found in output: {output}"
    terminated_count = int(terminate_match.group(1))
    assert terminated_count >= 1, f"Expected at least 1 terminated process, but got {terminated_count}"
    assert result.exit_code == 0

    # Step 6: Check QuPath install succeeds (idempotent operation)
    result = runner.invoke(cli, ["qupath", "install"])
    assert f"QuPath v{QUPATH_VERSION} installed successfully" in normalize_output(result.output)
    assert result.exit_code == 0

    # Step 7: Uninstall QuPath
    result = runner.invoke(cli, ["qupath", "uninstall"])
    assert "QuPath uninstalled successfully." in normalize_output(result.output)
    assert result.exit_code == 0

    # Step 8: Check QuPath launch fails if not installed
    result = runner.invoke(cli, ["qupath", "launch"])
    assert "QuPath is not installed. Use 'uvx aignostics qupath install' to install it." in normalize_output(
        result.output
    )
    assert result.exit_code == 2
