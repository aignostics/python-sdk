"""Tests to verify the CLI functionality of the appliction module."""

import platform
import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from aignostics.application import Service as ApplicationService
from aignostics.cli import cli
from aignostics.utils import sanitize_path
from tests.conftest import normalize_output, print_directory_structure

MESSAGE_NOT_YET_IMPLEMENTED = "NOT YET IMPLEMENTED"
MESSAGE_RUN_NOT_FOUND = "Warning: Run with ID '4711' not found"

HETA_APPLICATION_ID = "he-tme"
TEST_APPLICATION_ID = "test-app"


def test_cli_application_list(runner: CliRunner) -> None:
    """Check application list command runs successfully."""
    result = runner.invoke(cli, ["application", "list"])
    assert result.exit_code == 0
    assert HETA_APPLICATION_ID in normalize_output(result.output)
    assert TEST_APPLICATION_ID in normalize_output(result.output)


def test_cli_application_list_verbose(runner: CliRunner) -> None:
    """Check application list command runs successfully."""
    result = runner.invoke(cli, ["application", "list", "--verbose"])
    assert result.exit_code == 0
    assert HETA_APPLICATION_ID in normalize_output(result.output)
    assert "Artifacts: 1 input(s), 6 output(s)" in normalize_output(result.output)
    assert TEST_APPLICATION_ID in normalize_output(result.output)


def test_cli_application_describe(runner: CliRunner) -> None:
    """Check application describe command runs successfully."""
    result = runner.invoke(cli, ["application", "describe", HETA_APPLICATION_ID])
    assert result.exit_code == 0
    assert "tissue_qc:geojson_polygons" in normalize_output(result.output)


def test_cli_application_describe_not_found(runner: CliRunner) -> None:
    """Check application describe command fails as expected on unknown upplication."""
    result = runner.invoke(cli, ["application", "describe", "unknown"])
    assert result.exit_code == 2
    assert "Application with ID 'unknown' not found." in normalize_output(result.output)


def test_cli_application_dump_schemata(runner: CliRunner, tmp_path: Path) -> None:
    """Check application dump schemata works as expected."""
    result = runner.invoke(
        cli, ["application", "dump-schemata", HETA_APPLICATION_ID, "--destination", str(tmp_path), "--zip"]
    )
    application_version = ApplicationService().application_version(HETA_APPLICATION_ID, True)
    assert result.exit_code == 0
    assert "Zipped 11 files" in normalize_output(result.output)
    zip_file = sanitize_path(Path(tmp_path / f"{application_version.application_version_id}_schemata.zip"))
    assert zip_file.exists(), f"Expected zip file {zip_file} not found"


def test_cli_application_run_prepare_upload_submit_fail_on_mpp(runner: CliRunner, tmp_path: Path) -> None:
    """Check application run prepare command and upload works and submit fails on mpp not supported."""
    # Step 1: Prepare the file, by scanning for wsi and generating metadata
    source_directory = Path(__file__).parent.parent.parent / "resources" / "run"
    metadata_csv = tmp_path / "metadata.csv"
    result = runner.invoke(
        cli, ["application", "run", "prepare", HETA_APPLICATION_ID, str(metadata_csv), str(source_directory)]
    )
    assert result.exit_code == 0
    assert metadata_csv.exists()
    assert (
        metadata_csv.read_text()
        == "reference;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
        "platform_bucket_url\n"
        f"{source_directory / 'small-pyramidal.dcm'};"
        "EfIIhA==;8.065226874391001;2054;1529;;;;\n"
    )

    # Step 2: Simulate user now upading the metadata.csv file, by setting the tissue to "LUNG"
    # and disease to "LUNG_CANCER"
    metadata_csv.write_text(
        "reference;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
        "platform_bucket_url\n"
        f"{source_directory / 'small-pyramidal.dcm'};"
        "EfIIhA==;8.065226874391001;2054;1529;H&E;LUNG;LUNG_CANCER;\n"
    )

    # Step 3: Upload the file to the platform
    result = runner.invoke(cli, ["application", "run", "upload", HETA_APPLICATION_ID, str(metadata_csv)])
    assert "Upload completed." in normalize_output(result.stdout)
    assert result.exit_code == 0

    # Step 3: Submit the run from the metadata file
    result = runner.invoke(cli, ["application", "run", "submit", HETA_APPLICATION_ID, str(metadata_csv)])
    assert result.exit_code == 2
    assert "Invalid metadata for artifact `user_slide`" in normalize_output(result.stdout)
    assert "8.065226874391001 is greater than" in normalize_output(result.stdout)


def test_cli_application_run_upload_fails_on_missing_source(runner: CliRunner, tmp_path: Path) -> None:
    """Check application run prepare command and upload works and submit fails on mpp not supported."""
    metadata_csv = tmp_path / "metadata.csv"
    metadata_csv.write_text(
        "reference;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
        "platform_bucket_url\n"
        "missing.file;"
        "EfIIhA==;8.065226874391001;2054;1529;H&E;LUNG;LUNG_CANCER;\n"
    )

    result = runner.invoke(cli, ["application", "run", "upload", HETA_APPLICATION_ID, str(metadata_csv)])
    assert result.exit_code == 2
    assert "Warning: Source file 'missing.file' (row 0) does not exist" in normalize_output(result.stdout)


def test_cli_run_submit_fails_on_application_not_found(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command fails as expected."""
    csv_content = "reference;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
    csv_content += "platform_bucket_url\n"
    csv_content += ";5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;gs://bucket/test"
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(cli, ["application", "run", "submit", "wrong:v1.2.3", str(csv_path)])

    assert result.exit_code == 1
    assert "Error: Failed to create run for application version" in normalize_output(result.stdout)


def test_cli_run_submit_fails_on_unsupported_cloud(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command fails as expected."""
    csv_content = "reference;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
    csv_content += "platform_bucket_url\n"
    csv_content += ";5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;aws://bucket/test"
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(cli, ["application", "run", "submit", HETA_APPLICATION_ID, str(csv_path)])

    assert result.exit_code == 2
    assert "Invalid platform bucket URL: 'aws://bucket/test'" in normalize_output(result.stdout)


def test_cli_run_submit_fails_on_missing_url(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command fails as expected."""
    csv_content = "reference;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
    csv_content += "platform_bucket_url\n"
    csv_content += ";5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;"
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(cli, ["application", "run", "submit", HETA_APPLICATION_ID, str(csv_path)])

    assert result.exit_code == 2
    assert "Invalid platform bucket URL: ''" in normalize_output(result.stdout)


def test_cli_run_submit_and_describe_and_cancel_and_download(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command runs successfully."""
    csv_content = "reference;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
    csv_content += "platform_bucket_url\n"
    csv_content += ";5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;gs://bucket/test"
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(cli, ["application", "run", "submit", HETA_APPLICATION_ID, str(csv_path)])
    output = normalize_output(result.stdout)
    assert re.search(
        r"Submitted run with id '[0-9a-f-]+' for '",
        output,
    ), f"Output '{output}' doesn't match expected pattern"
    assert result.exit_code == 0

    # Extract run ID from the output
    run_id_match = re.search(r"Submitted run with id '([0-9a-f-]+)' for '", output)
    assert run_id_match, f"Failed to extract run ID from output '{output}'"
    run_id = run_id_match.group(1)

    # Test the describe command with the extracted run ID
    describe_result = runner.invoke(cli, ["application", "run", "describe", run_id])
    assert describe_result.exit_code == 0
    assert f"Run Details for {run_id}" in normalize_output(describe_result.stdout)
    assert "Status: RUNNING" in normalize_output(describe_result.stdout)

    # Test the download command spots the run is still running
    download_result = runner.invoke(
        cli, ["application", "run", "result", "download", run_id, str(tmp_path), "--no-wait-for-completion"]
    )
    assert download_result.exit_code == 0
    assert f"Downloaded results of run '{run_id}'" in normalize_output(download_result.stdout)
    assert "status: running on plat" in normalize_output(download_result.stdout)

    # Test the cancel command with the extracted run ID
    cancel_result = runner.invoke(cli, ["application", "run", "cancel", run_id])
    assert cancel_result.exit_code == 0
    assert f"Run with ID '{run_id}' has been canceled." in normalize_output(cancel_result.stdout)

    # Test the describe command with the extracted run ID on canceled run
    describe_result = runner.invoke(cli, ["application", "run", "describe", run_id])
    assert describe_result.exit_code == 0
    assert f"Run Details for {run_id}" in normalize_output(describe_result.stdout)
    assert "Status: CANCELED_USER" in normalize_output(describe_result.stdout)

    download_result = runner.invoke(cli, ["application", "run", "result", "download", run_id, str(tmp_path)])
    assert download_result.exit_code == 0

    # Verify the download message and path
    assert f"Downloaded results of run '{run_id}'" in normalize_output(download_result.stdout)
    assert "status: canceled by user." in normalize_output(download_result.stdout)

    # More robust path verification - normalize paths and check if the destination path is mentioned in the output
    normalized_tmp_path = str(Path(tmp_path).resolve())
    normalized_output = normalize_output(download_result.stdout).replace(" ", "")
    normalized_path_in_output = normalized_tmp_path.replace(" ", "")

    assert normalized_path_in_output in normalized_output, (
        f"Expected path '{normalized_tmp_path}' not found in output: '{download_result.output}'"
    )

    download_result = runner.invoke(cli, ["application", "run", "result", "download", run_id, "/4711"])
    if platform.system() == "Windows":
        assert download_result.exit_code == 0
    else:
        assert download_result.exit_code == 2
        assert f"Failed to create destination directory '/4711/{run_id}'" in normalize_output(download_result.stdout)


def test_cli_run_list_limit_10(runner: CliRunner) -> None:
    """Check run list command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "list", "--limit", "10"])
    assert result.exit_code == 0
    output = normalize_output(result.stdout)
    assert "Application Run IDs:" in output
    # Verify we find a message about the count and that the displayed count is <= 10
    match = re.search(r"Listed '(\d+)' run\(s\)\.", output)
    assert match, "Expected run count message not found"
    displayed_count = int(match.group(1))
    assert displayed_count <= 10, f"Expected listed count to be <= 10, but got {displayed_count}"


def test_cli_run_list_verbose_limit_1(runner: CliRunner) -> None:
    """Check run list command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "list", "--verbose", "--limit", "1"])
    assert result.exit_code == 0
    output = normalize_output(result.stdout)
    assert "Application Runs:" in output
    assert "Item Status Counts:" in output
    match = re.search(r"Listed '(\d+)' run\(s\)\.", output)
    assert match, "Expected run count message not found"
    displayed_count = int(match.group(1))
    assert displayed_count == 1, f"Expected listed count to be == 1, but got {displayed_count}"


def test_cli_run_describe_invalid_uuid(runner: CliRunner) -> None:
    """Check run describe command fails as expected on run not found."""
    result = runner.invoke(cli, ["application", "run", "describe", "4711"])
    assert result.exit_code == 1
    assert "Error: Failed to retrieve run details for ID '4711'" in normalize_output(result.stdout)


def test_cli_run_describe_not_found(runner: CliRunner) -> None:
    """Check run describe command fails as expected on run not found."""
    result = runner.invoke(cli, ["application", "run", "describe", "00000000000000000000000000000000"])
    assert result.exit_code == 2
    assert "Warning: Run with ID '00000000000000000000000000000000' not found." in normalize_output(result.stdout)


def test_cli_run_cancel_invalid_run_id(runner: CliRunner) -> None:
    """Check run cancel command fails as expected on run not found."""
    result = runner.invoke(cli, ["application", "run", "cancel", "4711"])
    assert result.exit_code == 1
    assert "Failed to cancel run with ID '4711'" in normalize_output(result.stdout)


def test_cli_run_cancel_not_found(runner: CliRunner) -> None:
    """Check run cancel command fails as expected on run not found."""
    result = runner.invoke(cli, ["application", "run", "cancel", "00000000000000000000000000000000"])
    assert result.exit_code == 2
    assert "Warning: Run with ID '00000000000000000000000000000000' not found." in normalize_output(result.stdout)


def test_cli_run_result_download_invalid_uuid(runner: CliRunner, tmp_path: Path) -> None:
    """Check run result download command fails on invalid uui."""
    result = runner.invoke(cli, ["application", "run", "result", "download", "4711", str(tmp_path)])
    assert result.exit_code == 2
    assert "Run ID '4711' invalid" in normalize_output(result.stdout)


def test_cli_run_result_download_uuid_not_found(runner: CliRunner, tmp_path: Path) -> None:
    """Check run result download fails on uuid not found."""
    result = runner.invoke(
        cli, ["application", "run", "result", "download", "00000000000000000000000000000000", str(tmp_path)]
    )
    assert result.exit_code == 1
    assert "Failed to download results of run with ID '00000000000000000000000000000000'" in result.output.replace(
        "\n", ""
    )


def test_cli_run_result_delete(runner: CliRunner) -> None:
    """Check run result delete command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "result", "delete"])
    assert result.exit_code == 1
    assert MESSAGE_NOT_YET_IMPLEMENTED in normalize_output(result.stdout)


@pytest.mark.long_running
def test_cli_run_execute(runner: CliRunner, tmp_path: Path) -> None:
    """Check run execution runs e2e."""
    # Step 1: Download the sample file
    result = runner.invoke(
        cli,
        [
            "dataset",
            "aignostics",
            "download",
            "gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff",
            str(tmp_path),
        ],
    )
    print_directory_structure(tmp_path, "download")
    assert result.exit_code == 0
    assert "Successfully downloaded" in result.stdout.replace("\n", "")
    assert "9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff" in result.stdout.replace("\n", "")
    expected_file = tmp_path / "9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
    assert expected_file.exists(), f"Expected file {expected_file} not found"
    assert expected_file.stat().st_size == 14681750

    # Step 2: Execute the run, i.e. prepare, amend, upload, submit and download the results
    result = runner.invoke(
        cli,
        [
            "application",
            "run",
            "execute",
            HETA_APPLICATION_ID,
            str(tmp_path / "run.csv"),
            str(tmp_path),
            ".*\\.tiff:staining_method=H&E,tissue=LUNG,disease=LUNG_CANCER",
            "--no-create-subdirectory-for-run",
        ],
    )
    print_directory_structure(tmp_path, "execute")
    assert result.exit_code == 0
    item_out_dir = tmp_path / "9375e3ed-28d2-4cf3-9fb9-8df9d11a6627"
    assert item_out_dir.is_dir(), f"Expected directory {item_out_dir} not found"
    files_in_dir = list(item_out_dir.glob("*"))
    assert len(files_in_dir) == 9, (
        f"Expected 9 files in {item_out_dir}, but found {len(files_in_dir)}: {[f.name for f in files_in_dir]}"
    )
    expected_files = [
        ("tissue_segmentation_csv_class_information.csv", 342, 10),
        ("cell_classification_geojson_polygons.json", 16058196, 10),
        ("readout_generation_cell_readouts.csv", 2234724, 10),
        ("tissue_qc_csv_class_information.csv", 232, 10),
        ("tissue_segmentation_geojson_polygons.json", 270932, 10),
        ("tissue_qc_geojson_polygons.json", 180522, 10),
        ("tissue_qc_segmentation_map_image.tiff", 464908, 10),
        ("readout_generation_slide_readouts.csv", 348957, 10),
        ("tissue_segmentation_segmentation_map_image.tiff", 521530, 10),
    ]
    for filename, expected_size, tolerance_percent in expected_files:
        file_path = item_out_dir / filename
        assert file_path.exists(), f"Expected file {filename} not found"
        actual_size = file_path.stat().st_size
        min_size = expected_size * (100 - tolerance_percent) // 100
        max_size = expected_size * (100 + tolerance_percent) // 100
        assert min_size <= actual_size <= max_size, (
            f"File size for {filename} ({actual_size} bytes) is outside allowed range "
            f"({min_size} to {max_size} bytes, ±{tolerance_percent}% of {expected_size})"
        )
