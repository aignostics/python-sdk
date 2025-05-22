"""Tests to verify the CLI functionality of the appliction module."""

import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli

MESSAGE_NOT_YET_IMPLEMENTED = "NOT YET IMPLEMENTED"
MESSAGE_RUN_NOT_FOUND = "Warning: Run with ID '4711' not found"

APPLICATION_VERSION_ID = "he-tme:v0.50.0"


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


def test_cli_application_list(runner: CliRunner) -> None:
    """Check application list command runs successfully."""
    result = runner.invoke(cli, ["application", "list"])
    assert result.exit_code == 0
    assert "he-tme" in result.output
    assert "test-app" in result.output


def test_cli_application_list_verbose(runner: CliRunner) -> None:
    """Check application list command runs successfully."""
    result = runner.invoke(cli, ["application", "list", "--verbose"])
    assert result.exit_code == 0
    assert "he-tme" in result.output
    assert "Artifacts: 1 input(s), 6 output(s)" in result.output
    assert "test-app" in result.output


def test_cli_application_describe(runner: CliRunner) -> None:
    """Check application describe command runs successfully."""
    result = runner.invoke(cli, ["application", "describe", "he-tme"])
    assert result.exit_code == 0
    assert "tissue_qc:geojson_polygons" in result.output


def test_cli_application_describe_not_found(runner: CliRunner) -> None:
    """Check application describe command fails as expected on unknown upplication."""
    result = runner.invoke(cli, ["application", "describe", "unknown"])
    assert result.exit_code == 0
    assert "Application with ID 'unknown' not found." in result.output


def test_cli_application_run_prepare_upload_submit_fail_on_mpp(runner: CliRunner, tmp_path: Path) -> None:
    """Check application run prepare command and upload works and submit fails on mpp not supported."""
    # Step 1: Prepare the file, by scanning for wsi and generating metadata
    source_directory = Path(__file__).parent.parent.parent / "resources" / "run"
    metadata_csv = tmp_path / "metadata.csv"
    result = runner.invoke(
        cli, ["application", "run", "prepare", APPLICATION_VERSION_ID, str(metadata_csv), str(source_directory)]
    )
    assert result.exit_code == 0
    assert metadata_csv.exists()
    assert (
        metadata_csv.read_text() == "reference;source;checksum_crc32c;mpp;width;height;staining;tissue_type;disease;"
        "file_size_human;file_upload_progress;platform_bucket_url\n"
        f"small-pyramidal;{source_directory / 'small-pyramidal.dcm'};"
        "EfIIhA==;8.065226874391001;2054;1529;H&E;;;0.00 GB;0.0;\n"
    )

    # Step 2: Simulate user now upading the metadata.csv file, byt setting the tissue_type and disease to "lung"
    metadata_csv.write_text(
        "reference;source;checksum_crc32c;mpp;width;height;staining;tissue_type;disease;"
        "file_size_human;file_upload_progress;platform_bucket_url\n"
        f"small-pyramidal;{source_directory / 'small-pyramidal.dcm'};"
        "EfIIhA==;8.065226874391001;2054;1529;H&E;lung;lung;0.00 GB;0.0;\n"
    )

    # Step 3: Upload the file to the platform
    result = runner.invoke(cli, ["application", "run", "upload", APPLICATION_VERSION_ID, str(metadata_csv)])
    assert result.exit_code == 0
    assert "Upload completed." in result.output

    # Step 3: Submit the run from the metadata file
    result = runner.invoke(cli, ["application", "run", "submit", APPLICATION_VERSION_ID, str(metadata_csv)])
    assert result.exit_code == 0
    assert "Invalid metadata for artifact `user_slide`" in result.output
    assert "8.065226874391001 is greater than" in result.output


def test_cli_application_run_upload_fails_on_missing_source(runner: CliRunner, tmp_path: Path) -> None:
    """Check application run prepare command and upload works and submit fails on mpp not supported."""
    metadata_csv = tmp_path / "metadata.csv"
    metadata_csv.write_text(
        "reference;source;checksum_crc32c;mpp;width;height;staining;tissue_type;disease;"
        "file_size_human;file_upload_progress;platform_bucket_url\n"
        "small-pyramidal;missing.file;"
        "EfIIhA==;8.065226874391001;2054;1529;H&E;lung;lung;0.00 GB;0.0;\n"
    )

    result = runner.invoke(cli, ["application", "run", "upload", APPLICATION_VERSION_ID, str(metadata_csv)])
    assert result.exit_code == 0
    assert "Warning: Source file 'missing.file' (row 0) does not exist" in result.output


def test_cli_run_submit_fails_on_application_not_found(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command fails as expected."""
    csv_content = "reference;source;checksum_crc32c;mpp;width;height;staining;tissue_type;disease;"
    csv_content += "file_size_human;file_upload_progress;platform_bucket_url\n"
    csv_content += ";;5onqtA==;0.26268186053789266;7447;7196;H&E;lung;lung;;;gs://bucket/test"
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(cli, ["application", "run", "submit", "wrong:v0.45.0", str(csv_path)])

    assert result.exit_code == 0
    assert "Error: Failed to create run for application version" in result.output


def test_cli_run_submit_fails_on_unsupported_cloud(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command fails as expected."""
    csv_content = "reference;source;checksum_crc32c;mpp;width;height;staining;tissue_type;disease;"
    csv_content += "file_size_human;file_upload_progress;platform_bucket_url\n"
    csv_content += ";;5onqtA==;0.26268186053789266;7447;7196;H&E;lung;lung;;;aws://bucket/test"
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(cli, ["application", "run", "submit", APPLICATION_VERSION_ID, str(csv_path)])

    assert result.exit_code == 0
    assert "Invalid platform bucket URL: 'aws://bucket/test'" in result.output


def test_cli_run_submit_fails_on_missing_url(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command fails as expected."""
    csv_content = "reference;source;checksum_crc32c;mpp;width;height;staining;tissue_type;disease;"
    csv_content += "file_size_human;file_upload_progress;platform_bucket_url\n"
    csv_content += ";;5onqtA==;0.26268186053789266;7447;7196;H&E;lung;lung;;;"
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(cli, ["application", "run", "submit", APPLICATION_VERSION_ID, str(csv_path)])

    assert result.exit_code == 0
    assert "Invalid platform bucket URL: ''" in result.output


def test_cli_run_submit_and_describe_and_cancel_and_download(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command runs successfully."""
    csv_content = "reference;source;checksum_crc32c;mpp;width;height;staining;tissue_type;disease;"
    csv_content += "file_size_human;file_upload_progress;platform_bucket_url\n"
    csv_content += ";;5onqtA==;0.26268186053789266;7447;7196;H&E;lung;lung;;;gs://bucket/test"
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(cli, ["application", "run", "submit", APPLICATION_VERSION_ID, str(csv_path)])

    assert result.exit_code == 0
    assert re.search(
        r"submitted run with id 'Application run `[0-9a-f-]+`:\s+running, 1 items - \(1/0/0\)", result.output
    ), f"Output '{result.output}' doesn't match expected pattern"

    # Extract run ID from the output
    run_id_match = re.search(r"submitted run with id 'Application run `([0-9a-f-]+)`", result.output)
    assert run_id_match, "Failed to extract run ID from output"
    run_id = run_id_match.group(1)

    # Test the describe command with the extracted run ID
    describe_result = runner.invoke(cli, ["application", "run", "describe", run_id])
    assert describe_result.exit_code == 0
    assert f"Run Details for {run_id}" in describe_result.output
    assert "Status: running" in describe_result.output

    # Test the cancel command with the extracted run ID
    cancel_result = runner.invoke(cli, ["application", "run", "cancel", run_id])
    assert cancel_result.exit_code == 0
    assert f"Run with ID '{run_id}' has been canceled." in cancel_result.output

    # Test the describe command with the extracted run ID on canceled run
    describe_result = runner.invoke(cli, ["application", "run", "describe", run_id])
    assert describe_result.exit_code == 0
    assert f"Run Details for {run_id}" in describe_result.output
    assert "Status: canceled_user" in describe_result.output

    download_result = runner.invoke(cli, ["application", "run", "result", "download", run_id, str(tmp_path)])
    assert download_result.exit_code == 0

    # Verify the download message and path
    expected_message = f"Downloaded results for run with ID '{run_id}' to"
    assert expected_message in download_result.output

    # More robust path verification - normalize paths and check if the destination path is mentioned in the output
    normalized_tmp_path = str(Path(tmp_path).resolve())
    normalized_output = download_result.output.replace("\n", "").replace(" ", "")
    normalized_path_in_output = normalized_tmp_path.replace(" ", "")

    assert normalized_path_in_output in normalized_output, (
        f"Expected path '{normalized_tmp_path}' not found in output: '{download_result.output}'"
    )

    download_result = runner.invoke(cli, ["application", "run", "result", "download", run_id, "/4711"])
    assert download_result.exit_code == 0
    assert "Failed to create destination directory '/4711'" in download_result.output


def test_cli_run_list_limit_10(runner: CliRunner) -> None:
    """Check run list command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "list", "--limit", "10"])
    assert result.exit_code == 0
    assert "Application Run IDs:" in result.output
    # Verify we find a message about the count and that the displayed count is <= 10
    match = re.search(r"Found \d+ application runs, displayed (\d+)\.", result.output)
    assert match, "Expected run count message not found"
    displayed_count = int(match.group(1))
    assert displayed_count <= 10, f"Expected displayed count to be <= 10, but got {displayed_count}"


def test_cli_run_list_verbose_limit_1(runner: CliRunner) -> None:
    """Check run list command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "list", "--verbose", "--limit", "1"])
    assert result.exit_code == 0
    assert "Application Runs:" in result.output
    assert "Item Status Counts:" in result.output
    assert re.search(r"Found \d+ application runs, displayed 1\.", result.output), (
        "Expected run count message not found"
    )


def test_cli_run_describe_invalid_uuid(runner: CliRunner) -> None:
    """Check run describe command fails as expected on run not found."""
    result = runner.invoke(cli, ["application", "run", "describe", "4711"])
    assert result.exit_code == 0
    assert "Error: Failed to retrieve run details for ID '4711'" in result.output


def test_cli_run_describe_not_found(runner: CliRunner) -> None:
    """Check run describe command fails as expected on run not found."""
    result = runner.invoke(cli, ["application", "run", "describe", "00000000000000000000000000000000"])
    assert result.exit_code == 0
    assert "Warning: Run with ID '00000000000000000000000000000000' not found." in result.output


def test_cli_run_cancel_invalid_run_id(runner: CliRunner) -> None:
    """Check run cancel command fails as expected on run not found."""
    result = runner.invoke(cli, ["application", "run", "cancel", "4711"])
    assert result.exit_code == 0
    assert "Failed to cancel run with ID '4711'" in result.output


def test_cli_run_cancel_not_found(runner: CliRunner) -> None:
    """Check run cancel command fails as expected on run not found."""
    result = runner.invoke(cli, ["application", "run", "cancel", "00000000000000000000000000000000"])
    assert result.exit_code == 0
    assert "Warning: Run with ID '00000000000000000000000000000000' not found." in result.output


def test_cli_run_result_describe(runner: CliRunner) -> None:
    """Check run result describe command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "result", "describe"])
    assert result.exit_code == 0
    assert MESSAGE_NOT_YET_IMPLEMENTED in result.output


def test_cli_run_result_download_invalid_uuid(runner: CliRunner, tmp_path: Path) -> None:
    """Check run result download command fails on invalid uui."""
    result = runner.invoke(cli, ["application", "run", "result", "download", "4711", str(tmp_path)])
    assert result.exit_code == 0
    assert "Failed to download results for run with ID '4711'" in result.output


def test_cli_run_result_download_uuid_not_found(runner: CliRunner, tmp_path: Path) -> None:
    """Check run result download fails on uuid not found."""
    result = runner.invoke(
        cli, ["application", "run", "result", "download", "00000000000000000000000000000000", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "Warning: Run with ID '00000000000000000000000000000000' not found." in result.output


def test_cli_run_result_delete(runner: CliRunner) -> None:
    """Check run result delete command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "result", "delete"])
    assert result.exit_code == 0
    assert MESSAGE_NOT_YET_IMPLEMENTED in result.output
