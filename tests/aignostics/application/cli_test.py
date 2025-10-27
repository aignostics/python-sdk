"""Tests to verify the CLI functionality of the application module."""

import platform
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import sleep

import pytest
from typer.testing import CliRunner

from aignostics.application import Service as ApplicationService
from aignostics.cli import cli
from aignostics.utils import sanitize_path
from tests.conftest import normalize_output, print_directory_structure
from tests.constants_test import (
    HETA_APPLICATION_ID,
    HETA_APPLICATION_VERSION,
    SPOT_1_EXPECTED_RESULT_FILES,
    SPOT_1_FILENAME,
    SPOT_1_FILESIZE,
    SPOT_1_GS_URL,
    TEST_APPLICATION_ID,
    TEST_APPLICATION_VERSION,
)

MESSAGE_RUN_NOT_FOUND = "Warning: Run with ID '4711' not found"

TEST_APPLICATION_DEADLINE_SECONDS = 60 * 45  # 45 minutes
TEST_APPLICATION_DUE_DATE_SECONDS = 60 * 10  # 10 minutes

HETA_APPLICATION_DUE_DATE_SECONDS = 60 * 60 * 1  # 1 hour
HETA_APPLICATION_DEADLINE_SECONDS = 60 * 60 * 3  # 3 hours


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_cli_application_list_non_verbose(runner: CliRunner, record_property) -> None:
    """Check application list command runs successfully."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    result = runner.invoke(cli, ["application", "list"])
    assert result.exit_code == 0
    assert HETA_APPLICATION_ID in normalize_output(result.output)
    assert TEST_APPLICATION_ID in normalize_output(result.output)


@pytest.mark.e2e
@pytest.mark.scheduled
@pytest.mark.timeout(timeout=60)
def test_cli_application_list_verbose(runner: CliRunner, record_property) -> None:
    """Check application list command runs successfully."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    result = runner.invoke(cli, ["application", "list", "--verbose"])
    assert result.exit_code == 0
    assert HETA_APPLICATION_ID in normalize_output(result.output)
    assert HETA_APPLICATION_VERSION in normalize_output(result.output)
    assert "Artifacts: 1 input(s), 6 output(s)" in normalize_output(result.output)
    assert TEST_APPLICATION_ID in normalize_output(result.output)
    assert TEST_APPLICATION_VERSION in normalize_output(result.output)


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_cli_application_describe_success(runner: CliRunner, record_property) -> None:
    """Check application describe command runs successfully."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    result = runner.invoke(cli, ["application", "describe", HETA_APPLICATION_ID])
    assert result.exit_code == 0


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_cli_application_describe_verbose(runner: CliRunner) -> None:
    """Check application describe command runs successfully."""
    result = runner.invoke(cli, ["application", "describe", HETA_APPLICATION_ID, "--verbose"])
    assert result.exit_code == 0
    assert "tissue_qc:geojson_polygons" in normalize_output(result.output)


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_cli_application_describe_not_found(runner: CliRunner, record_property) -> None:
    """Check application describe command fails as expected on unknown application."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    result = runner.invoke(cli, ["application", "describe", "unknown"])
    assert result.exit_code == 2
    assert "Application with ID 'unknown' not found." in normalize_output(result.output)


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_cli_application_dump_schemata(runner: CliRunner, tmp_path: Path, record_property) -> None:
    """Check application dump schemata works as expected."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    result = runner.invoke(
        cli, ["application", "dump-schemata", HETA_APPLICATION_ID, "--destination", str(tmp_path), "--zip"]
    )
    application_version = ApplicationService().application_version(HETA_APPLICATION_ID)
    application_version = ApplicationService().application_version(HETA_APPLICATION_ID)
    assert result.exit_code == 0
    assert "Zipped 11 files" in normalize_output(result.output)
    zip_file = sanitize_path(
        Path(tmp_path / f"{HETA_APPLICATION_ID}_{application_version.version_number}_schemata.zip")
    )
    assert zip_file.exists(), f"Expected zip file {zip_file} not found"


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_cli_application_run_prepare_upload_submit_fail_on_mpp(
    runner: CliRunner, tmp_path: Path, record_property
) -> None:
    """Check application run prepare command and upload works and submit fails on mpp not supported."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-01")
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
        == "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
        "platform_bucket_url\n"
        f"{source_directory / 'small-pyramidal.dcm'};"
        "EfIIhA==;8.065226874391001;2054;1529;;;;\n"
    )

    # Step 2: Simulate user now upgrading the metadata.csv file, by setting the tissue to "LUNG"
    # and disease to "LUNG_CANCER"
    metadata_csv.write_text(
        "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
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
    assert "Invalid metadata for artifact `whole_slide_image`" in normalize_output(result.stdout)
    assert "8.065226874391001 is greater than" in normalize_output(result.stdout)


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_cli_application_run_upload_fails_on_missing_source(runner: CliRunner, tmp_path: Path, record_property) -> None:
    """Check application run prepare command and upload works and submit fails on mpp not supported."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    metadata_csv = tmp_path / "metadata.csv"
    metadata_csv.write_text(
        "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
        "platform_bucket_url\n"
        "missing.file;"
        "EfIIhA==;8.065226874391001;2054;1529;H&E;LUNG;LUNG_CANCER;\n"
    )

    result = runner.invoke(cli, ["application", "run", "upload", HETA_APPLICATION_ID, str(metadata_csv)])
    assert result.exit_code == 2
    assert "Warning: Source file 'missing.file' (row 0) does not exist" in normalize_output(result.stdout)


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_cli_run_submit_fails_on_application_not_found(runner: CliRunner, tmp_path: Path, record_property) -> None:
    """Check run submit command fails as expected."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    csv_content = "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
    csv_content += "platform_bucket_url\n"
    csv_content += ";5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;gs://bucket/test"
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(
        cli,
        [
            "application",
            "run",
            "submit",
            "wrong",
            str(csv_path),
            "--deadline",
            (datetime.now(tz=UTC) + timedelta(minutes=10)).isoformat(),
        ],
    )

    assert result.exit_code == 2
    assert 'HTTP response body: {"detail":"application not found"}' in normalize_output(result.stdout)
    assert "Warning: Could not find application" in normalize_output(result.stdout)
    assert result.exit_code == 2


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_cli_run_submit_fails_on_unsupported_cloud(runner: CliRunner, tmp_path: Path, record_property) -> None:
    """Check run submit command fails as expected."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    csv_content = "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
    csv_content += "platform_bucket_url\n"
    csv_content += ";5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;aws://bucket/test"
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(
        cli,
        [
            "application",
            "run",
            "submit",
            HETA_APPLICATION_ID,
            str(csv_path),
            "--deadline",
            (datetime.now(tz=UTC) + timedelta(minutes=10)).isoformat(),
        ],
    )

    assert result.exit_code == 2
    assert "Invalid platform bucket URL: 'aws://bucket/test'" in normalize_output(result.stdout)


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_cli_run_submit_fails_on_missing_url(runner: CliRunner, tmp_path: Path, record_property) -> None:
    """Check run submit command fails as expected."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    csv_content = "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
    csv_content += "platform_bucket_url\n"
    csv_content += ";5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;"
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(
        cli,
        [
            "application",
            "run",
            "submit",
            HETA_APPLICATION_ID,
            str(csv_path),
            "--deadline",
            (datetime.now(tz=UTC) + timedelta(minutes=10)).isoformat(),
        ],
    )

    assert result.exit_code == 2
    assert "Invalid platform bucket URL: ''" in normalize_output(result.stdout)


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.flaky(retries=3, delay=5)
@pytest.mark.timeout(timeout=60 * 10)
def test_cli_run_submit_and_describe_and_cancel_and_download_and_delete(  # noqa: PLR0915
    runner: CliRunner, tmp_path: Path, silent_logging, record_property
) -> None:
    """Check run submit command runs successfully."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-02")
    csv_content = "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
    csv_content += "platform_bucket_url\n"
    csv_content += ";5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;gs://bucket/test"
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)
    result = runner.invoke(
        cli,
        [
            "application",
            "run",
            "submit",
            HETA_APPLICATION_ID,
            str(csv_path),
            "--note",
            "note_of_this_complex_test",
            "--tags",
            "cli-test,test_cli_run_submit_and_describe_and_cancel_and_download_and_delete,further-tag",
            "--deadline",
            (datetime.now(tz=UTC) + timedelta(minutes=10)).isoformat(),
            "--validate-only",
        ],
    )
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

    # TODO (Andreas): Causes internal server errors on some runs
    if False:
        # Test that we can find this run by it's note via the query parameter
        list_result = runner.invoke(
            cli,
            [
                "application",
                "run",
                "list",
                "--query",
                "note_of_this_complex_test",
            ],
        )
        assert list_result.exit_code == 0
        list_output = normalize_output(list_result.stdout)
        assert run_id in list_output, f"Run ID '{run_id}' not found when filtering by note via query"

        # Test that we can find this run by it's tag via the query parameter
        list_result = runner.invoke(
            cli,
            [
                "application",
                "run",
                "list",
                "--query",
                "test_cli_run_submit_and_describe_and_cancel_and_download_and_delete",
            ],
        )
        assert list_result.exit_code == 0
        list_output = normalize_output(list_result.stdout)
        assert run_id in list_output, f"Run ID '{run_id}' not found when filtering by tag via query"

        # Test that we cannot find this run by another tag via the query parameter
        list_result = runner.invoke(
            cli,
            [
                "application",
                "run",
                "list",
                "--query",
                "another_tag",
            ],
        )
        assert list_result.exit_code == 0
        list_output = normalize_output(list_result.stdout)
        assert run_id not in list_output, f"Run ID '{run_id}' found when filtering by another tag via query"

        # Test that we can find this run by it's note
        list_result = runner.invoke(
            cli,
            [
                "application",
                "run",
                "list",
                "--note-regex",
                "note_of_this_complex_test",
            ],
        )
        assert list_result.exit_code == 0
        list_output = normalize_output(list_result.stdout)
        assert run_id in list_output, f"Run ID '{run_id}' not found when filtering by note"

        # but not another note
        list_result = runner.invoke(
            cli,
            [
                "application",
                "run",
                "list",
                "--note-regex",
                "other_note",
            ],
        )
        assert list_result.exit_code == 0
        list_output = normalize_output(list_result.stdout)
        assert run_id not in list_output, f"Run ID '{run_id}' found when filtering by other note"

        # Test that we can find this run by one of its tags
        list_result = runner.invoke(
            cli,
            [
                "application",
                "run",
                "list",
                "--tags",
                "test_cli_run_submit_and_describe_and_cancel_and_download_and_delete",
            ],
        )
        assert list_result.exit_code == 0
        list_output = normalize_output(list_result.stdout)
        assert run_id in list_output, f"Run ID '{run_id}' not found when filtering by one tag"

        # but not another tag
        list_result = runner.invoke(
            cli,
            [
                "application",
                "run",
                "list",
                "--tags",
                "other-tag",
            ],
        )
        assert list_result.exit_code == 0
        list_output = normalize_output(list_result.stdout)
        assert run_id not in list_output, f"Run ID '{run_id}' found when filtering by other tag"

        # Test that we can find this run by two of its tags
        list_result = runner.invoke(
            cli,
            [
                "application",
                "run",
                "list",
                "--tags",
                "cli-test,test_cli_run_submit_and_describe_and_cancel_and_download_and_delete",
            ],
        )
        assert list_result.exit_code == 0
        list_output = normalize_output(list_result.stdout)
        assert run_id in list_output, f"Run ID '{run_id}' not found when filtering by two tags"

        # Test that we can find this run by all of its tags
        list_result = runner.invoke(
            cli,
            [
                "application",
                "run",
                "list",
                "--tags",
                "cli-test,test_cli_run_submit_and_describe_and_cancel_and_download_and_delete,further-tag",
            ],
        )
        assert list_result.exit_code == 0
        list_output = normalize_output(list_result.stdout)
        assert run_id in list_output, f"Run ID '{run_id}' not found when filtering by all tags"

        # Test that we cannot find this run by all of its tags and a non-existent tag
        list_result = runner.invoke(
            cli,
            [
                "application",
                "run",
                "list",
                "--tags",
                "cli-test,test_cli_run_submit_and_describe_and_cancel_and_download_and_delete,further-tag,non-existing-tag",
            ],
        )
        assert list_result.exit_code == 0
        list_output = normalize_output(list_result.stdout)
        assert run_id not in list_output, f"Run ID '{run_id}' found when filtering by all tags"

        # Test that we can find this run by all of its tags and it's note
        list_result = runner.invoke(
            cli,
            [
                "application",
                "run",
                "list",
                "--note-regex",
                "note_of_this_complex_test",
                "--tags",
                "cli-test,test_cli_run_submit_and_describe_and_cancel_and_download_and_delete,further-tag",
            ],
        )
        assert list_result.exit_code == 0
        list_output = normalize_output(list_result.stdout)
        assert run_id in list_output, f"Run ID '{run_id}' not found when filtering by all tags and note"

    # Test the describe command with the extracted run ID
    describe_result = runner.invoke(cli, ["application", "run", "describe", run_id])
    assert describe_result.exit_code == 0
    assert f"Run Details for {run_id}" in normalize_output(describe_result.stdout)
    assert "Status (Termination Reason): PENDING" in normalize_output(
        describe_result.stdout
    ) or "Status (Termination Reason): PROCESSING" in normalize_output(describe_result.stdout)
    assert "test_cli_run_submit_and_describe_and_cancel_and_download_and_delete" in normalize_output(
        describe_result.stdout
    )

    # Test the download command spots the run is still running
    download_result = runner.invoke(
        cli, ["application", "run", "result", "download", run_id, str(tmp_path), "--no-wait-for-completion"]
    )
    assert download_result.exit_code == 0
    assert f"Downloaded results of run '{run_id}'" in normalize_output(download_result.stdout)

    # Test the cancel command with the extracted run ID
    cancel_result = runner.invoke(cli, ["application", "run", "cancel", run_id])
    assert cancel_result.exit_code == 0
    assert f"Run with ID '{run_id}' has been canceled." in normalize_output(cancel_result.stdout)

    # Test the describe command with the extracted run ID on canceled run
    describe_result = runner.invoke(cli, ["application", "run", "describe", run_id])
    assert describe_result.exit_code == 0
    assert f"Run Details for {run_id}" in normalize_output(describe_result.stdout)
    assert "Status (Termination Reason): TERMINATED (RunTerminationReason.CANCELED_BY_USER)" in normalize_output(
        describe_result.stdout
    )

    download_result = runner.invoke(cli, ["application", "run", "result", "download", run_id, str(tmp_path)])
    assert download_result.exit_code == 0

    # Verify the download message and path
    assert f"Downloaded results of run '{run_id}'" in normalize_output(download_result.stdout)
    # TODO(andreas): Would also be great to check if it is canceled by user
    assert "status: terminated" in normalize_output(download_result.stdout)

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

    # Test the result delete command with the extracted run ID
    delete_result = runner.invoke(cli, ["application", "run", "result", "delete", run_id])
    assert delete_result.exit_code == 0
    assert f"Results for run with ID '{run_id}' have been deleted." in normalize_output(delete_result.stdout)

    # Test the describe command with the extracted run ID on deleted run
    describe_result = runner.invoke(cli, ["application", "run", "describe", run_id])
    assert describe_result.exit_code == 0
    assert f"Run Details for {run_id}" in normalize_output(describe_result.stdout)
    assert "Status (Termination Reason): TERMINATED (RunTerminationReason.CANCELED_BY_USER)" in normalize_output(
        describe_result.stdout
    )


# TODO(Helmut): Activate when PAPI fixed
#    assert describe_result.exit_code == 2 # noqa: ERA001
#    assert f"Run with id '{run_id}' not found." in normalize_output(describe_result.stdout) # noqa: ERA001


@pytest.mark.e2e
@pytest.mark.scheduled
@pytest.mark.timeout(timeout=60)
def test_cli_run_list_limit_10(runner: CliRunner, record_property) -> None:
    """Check run list command runs successfully."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    result = runner.invoke(cli, ["application", "run", "list", "--limit", "10"])
    assert result.exit_code == 0
    output = normalize_output(result.stdout)
    assert "Application Run IDs:" in output
    # Verify we find a message about the count and that the displayed count is <= 10
    match = re.search(r"Listed '(\d+)' run\(s\)\.", output)
    assert match, "Expected run count message not found"
    displayed_count = int(match.group(1))
    assert displayed_count <= 10, f"Expected listed count to be <= 10, but got {displayed_count}"


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_cli_run_list_verbose_limit_1(runner: CliRunner, record_property) -> None:
    """Check run list command runs successfully."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    result = runner.invoke(cli, ["application", "run", "list", "--verbose", "--limit", "1"])
    assert result.exit_code == 0
    output = normalize_output(result.stdout)
    assert "Application Runs:" in output
    assert "Statistics:" in output
    match = re.search(r"Listed '(\d+)' run\(s\)\.", output)
    assert match, "Expected run count message not found"
    displayed_count = int(match.group(1))
    assert displayed_count == 1, f"Expected listed count to be == 1, but got {displayed_count}"


# TODO(Andreas): This previously failed as invalid run id. Is it expected this now calls the API?
@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_cli_run_describe_invalid_uuid(runner: CliRunner, record_property) -> None:
    """Check run describe command fails as expected on run not found."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    result = runner.invoke(cli, ["application", "run", "describe", "4711"])
    assert result.exit_code == 1
    assert "Error: Failed to retrieve run details for ID '4711'" in normalize_output(result.stdout)


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_cli_run_describe_not_found(runner: CliRunner, record_property) -> None:
    """Check run describe command fails as expected on run not found."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    result = runner.invoke(cli, ["application", "run", "describe", "00000000000000000000000000000000"])
    assert result.exit_code == 2
    assert "Warning: Run with ID '00000000000000000000000000000000' not found." in normalize_output(result.stdout)


@pytest.mark.e2e
def test_cli_run_cancel_invalid_run_id(runner: CliRunner, record_property) -> None:
    """Check run cancel command fails as expected on run not found."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    result = runner.invoke(cli, ["application", "run", "cancel", "4711"])
    assert "Run ID '4711' invalid" in normalize_output(result.stdout)
    assert result.exit_code == 2


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_cli_run_cancel_not_found(runner: CliRunner, record_property) -> None:
    """Check run cancel command fails as expected on run not found."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    result = runner.invoke(cli, ["application", "run", "cancel", "00000000000000000000000000000000"])
    assert "Warning: Run with ID '00000000000000000000000000000000' not found." in normalize_output(result.stdout)
    assert result.exit_code == 2


@pytest.mark.e2e
def test_cli_run_result_download_invalid_uuid(runner: CliRunner, tmp_path: Path, record_property) -> None:
    """Check run result download command fails on invalid uui."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    result = runner.invoke(cli, ["application", "run", "result", "download", "4711", str(tmp_path)])
    assert result.exit_code == 2
    assert "Run ID '4711' invalid" in normalize_output(result.stdout)


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_cli_run_result_download_uuid_not_found(runner: CliRunner, tmp_path: Path, record_property) -> None:
    """Check run result download fails on ID not found."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    result = runner.invoke(
        cli, ["application", "run", "result", "download", "00000000000000000000000000000000", str(tmp_path)]
    )
    assert "Run with ID '00000000000000000000000000000000' not found." in normalize_output(result.stdout)
    assert result.exit_code == 2


# TODO(Andreas): Please check API
@pytest.mark.skip(reason="API currently returns permission denied, not 404")
@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_cli_run_result_delete_not_found(runner: CliRunner, record_property) -> None:
    """Check run result delete command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "result", "delete", "00000000000000000000000000000000"])
    assert "Run with ID '00000000000000000000000000000000' not found." in normalize_output(result.stdout)
    assert result.exit_code == 2


@pytest.mark.integration
def test_cli_run_result_delete_fails_on_no_arg(runner: CliRunner, record_property) -> None:
    """Check run result delete command runs successfully."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    result = runner.invoke(cli, ["application", "run", "result", "delete"])
    assert "Missing argument 'RUN_ID'." in normalize_output(result.stderr)
    assert result.exit_code == 2


# TODO (Helmut): Schedule this run
@pytest.mark.e2e
@pytest.mark.very_long_running
@pytest.mark.timeout(timeout=HETA_APPLICATION_DEADLINE_SECONDS + 60 * 30)
def test_cli_run_execute(runner: CliRunner, tmp_path: Path, record_property) -> None:
    """Check run execution runs e2e."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-03")
    # Step 1: Download the sample file
    result = runner.invoke(
        cli,
        [
            "dataset",
            "aignostics",
            "download",
            SPOT_1_GS_URL,
            str(tmp_path),
        ],
    )

    # Explore what was download
    print_directory_structure(tmp_path, "download")

    # Validate what was downloaded
    assert "Successfully downloaded" in normalize_output(result.stdout)
    assert SPOT_1_FILENAME in normalize_output(result.stdout)
    expected_file = tmp_path / SPOT_1_FILENAME
    assert expected_file.exists(), f"Expected file {expected_file} not found"
    assert expected_file.stat().st_size == SPOT_1_FILESIZE, (
        f"Expected file size {SPOT_1_FILESIZE}, but got {expected_file.stat().st_size}"
    )

    # Validate the download command exited successfully
    assert result.exit_code == 0

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
            "--due-date",
            (datetime.now(tz=UTC) + timedelta(seconds=HETA_APPLICATION_DUE_DATE_SECONDS)).isoformat(),
            "--deadline",
            (datetime.now(tz=UTC) + timedelta(seconds=HETA_APPLICATION_DEADLINE_SECONDS)).isoformat(),
            "--validate-only",
        ],
    )

    # Explore what was download
    print_directory_structure(tmp_path, "execute")

    # Validate no input dir, given we used an external id pointing to a local file
    input_dir = tmp_path / "input"
    assert not input_dir.is_dir(), f"Expected input directory {input_dir} not found"

    # Validate results generated and downloaded
    results_dir = tmp_path / SPOT_1_FILENAME.replace(".tiff", "")
    assert results_dir.is_dir(), f"Expected directory {results_dir} not found"
    files_in_dir = list(results_dir.glob("*"))
    assert len(files_in_dir) == 9, (
        f"Expected 9 files in {results_dir}, but found {len(files_in_dir)}: {[f.name for f in files_in_dir]}"
    )
    print(f"Found files in {results_dir}:")
    for filename, expected_size, tolerance_percent in SPOT_1_EXPECTED_RESULT_FILES:
        file_path = results_dir / filename
        if file_path.exists():
            actual_size = file_path.stat().st_size
            print(f"  {filename}: {actual_size} bytes (expected: {expected_size} ±{tolerance_percent}%)")
        else:
            print(f"  {filename}: NOT FOUND")
    for filename, expected_size, tolerance_percent in SPOT_1_EXPECTED_RESULT_FILES:
        file_path = results_dir / filename
        assert file_path.exists(), f"Expected file {filename} not found"
        actual_size = file_path.stat().st_size
        min_size = expected_size * (100 - tolerance_percent) // 100
        max_size = expected_size * (100 + tolerance_percent) // 100
        assert min_size <= actual_size <= max_size, (
            f"File size for {filename} ({actual_size} bytes) is outside allowed range "
            f"({min_size} to {max_size} bytes, ±{tolerance_percent}% of {expected_size})"
        )

    # Validate the execute command exited successfully
    assert result.exit_code == 0


@pytest.mark.integration
def test_cli_run_update_metadata_invalid_json(runner: CliRunner) -> None:
    """Check run update-metadata command fails with invalid JSON."""
    result = runner.invoke(cli, ["application", "run", "update-metadata", "run-123", "{invalid json}"])
    assert result.exit_code == 1
    assert "Invalid JSON" in result.output


@pytest.mark.integration
def test_cli_run_update_metadata_not_dict(runner: CliRunner) -> None:
    """Check run update-metadata command fails with non-dict JSON."""
    result = runner.invoke(cli, ["application", "run", "update-metadata", "run-123", '["array", "not", "dict"]'])
    assert result.exit_code == 1
    assert "Metadata must be a JSON object" in result.output


@pytest.mark.integration
def test_cli_run_update_item_metadata_invalid_json(runner: CliRunner) -> None:
    """Check run update-item-metadata command fails with invalid JSON."""
    result = runner.invoke(
        cli, ["application", "run", "update-item-metadata", "run-123", "item-ext-id", "{invalid json}"]
    )
    assert result.exit_code == 1
    assert "Invalid JSON" in result.output


@pytest.mark.integration
def test_cli_run_update_item_metadata_not_dict(runner: CliRunner) -> None:
    """Check run update-item-metadata command fails with non-dict JSON."""
    result = runner.invoke(
        cli, ["application", "run", "update-item-metadata", "run-123", "item-ext-id", '["array", "not", "dict"]']
    )
    assert result.exit_code == 1
    assert "Metadata must be a JSON object" in result.output


@pytest.mark.e2e
@pytest.mark.timeout(timeout=120)
@pytest.mark.skipif(
    (platform.system() == "Linux" and platform.machine() in {"aarch64", "arm64"})
    or (platform.system() in {"Darwin", "Windows"}),
    reason="No parallel runners, otherwise race condition on metadata updates",
)
@pytest.mark.sequential
def test_cli_run_dump_and_update_custom_metadata(runner: CliRunner) -> None:
    """Test dumping and updating custom metadata via CLI commands."""
    import json
    import random

    # Step 1: List runs, limit to 1
    result = runner.invoke(cli, ["application", "run", "list", "--limit", "1"])
    assert result.exit_code == 0

    # Check if any runs exist
    if "You did not yet create a run" in result.output:
        pytest.skip("No runs available. Please run tests that submit runs first.")

    # Extract run ID from the output (format: "- <run_id> of <app>...")
    normalized_output = normalize_output(result.output)
    run_id_match = re.search(r"-\s+([a-f0-9\-]{36})\s+of\s+", normalized_output)
    assert run_id_match is not None, f"Could not extract run ID from list output:\n{normalized_output}"
    run_id = run_id_match.group(1)

    # Step 2: Dump custom metadata of run
    result = runner.invoke(cli, ["application", "run", "dump-metadata", run_id])
    assert result.exit_code == 0
    initial_metadata = json.loads(result.stdout)
    # If metadata is None/null, start with empty dict
    if initial_metadata is None:
        initial_metadata = {}
    assert isinstance(initial_metadata, dict), "Custom metadata should be a dictionary"

    # Store initial SDK metadata timestamps for comparison
    initial_created_at = initial_metadata.get("sdk", {}).get("created_at")
    initial_submission_date = initial_metadata.get("sdk", {}).get("submission", {}).get("date")
    initial_updated_at = initial_metadata.get("sdk", {}).get("updated_at")

    # Ensure some time passes to see timestamp changes
    sleep(1)

    # Step 3: Add "random" node with a random number
    random_value = random.randint(1000, 9999)
    updated_metadata = initial_metadata.copy()
    updated_metadata["random"] = random_value

    # Update the custom metadata
    result = runner.invoke(cli, ["application", "run", "update-metadata", run_id, json.dumps(updated_metadata)])
    assert result.exit_code == 0
    assert "Successfully updated custom metadata" in result.output

    # Step 4: Dump metadata again and verify random number appeared
    result = runner.invoke(cli, ["application", "run", "dump-metadata", run_id, "--pretty"])
    assert result.exit_code == 0
    metadata_with_random = json.loads(result.stdout)
    assert "random" in metadata_with_random, "Random field should be present in metadata"
    assert metadata_with_random["random"] == random_value, f"Random value should be {random_value}"

    # Verify SDK metadata timestamps behavior after update
    updated_created_at = metadata_with_random.get("sdk", {}).get("created_at")
    updated_submission_date = metadata_with_random.get("sdk", {}).get("submission", {}).get("date")
    updated_updated_at = metadata_with_random.get("sdk", {}).get("updated_at")

    # created_at and submission.date should NOT change
    # Only check created_at immutability if it was set initially
    if initial_created_at is not None:
        assert updated_created_at == initial_created_at, (
            f"sdk.created_at should not change: {initial_created_at} -> {updated_created_at}"
        )

    if initial_submission_date is not None:
        assert updated_submission_date == initial_submission_date, (
            f"sdk.submission.date should not change: {initial_submission_date} -> {updated_submission_date}"
        )

    # updated_at SHOULD change (be more recent)
    assert updated_updated_at != initial_updated_at, (
        f"sdk.updated_at should change after update: {initial_updated_at} -> {updated_updated_at}"
    )
    assert updated_updated_at > initial_updated_at, (
        f"sdk.updated_at should be more recent: {initial_updated_at} -> {updated_updated_at}"
    )

    # Step 5: Remove the random number
    del updated_metadata["random"]
    result = runner.invoke(cli, ["application", "run", "update-metadata", run_id, json.dumps(updated_metadata)])
    assert result.exit_code == 0
    assert "Successfully updated custom metadata" in result.output

    # Step 6: Dump metadata and validate random element has been removed
    result = runner.invoke(cli, ["application", "run", "dump-metadata", run_id])
    assert result.exit_code == 0
    final_metadata = json.loads(result.stdout)
    assert "random" not in final_metadata, "Random field should have been removed from metadata"

    # Note: We can't compare final_metadata == initial_metadata because the SDK
    # automatically updates some fields (e.g., submission.date, ci.pytest.current_test)
    # when operations are performed. Instead, verify the random field was removed
    # and the structure remains consistent.
    assert isinstance(final_metadata, dict), "Final metadata should be a dictionary"


# TODO(Andreas): Update item metadata returns 404 always
@pytest.mark.skip(reason="Waiting for platform API fix to item metadata endpoint which currently returns 404 always")
@pytest.mark.e2e
@pytest.mark.timeout(timeout=120)
@pytest.mark.skipif(
    (platform.system() == "Linux" and platform.machine() in {"aarch64", "arm64"})
    or (platform.system() in {"Darwin", "Windows"}),
    reason="No parallel runners, otherwise race condition on metadata updates",
)
@pytest.mark.sequential
def test_cli_run_dump_and_update_item_custom_metadata(runner: CliRunner) -> None:  # noqa: PLR0914, PLR0915  # noqa: PLR0914, PLR0915
    """Test dumping and updating item custom metadata via CLI commands."""
    import json
    import random

    # Step 1: List runs, limit to 1
    result = runner.invoke(cli, ["application", "run", "list", "--limit", "1"])
    assert result.exit_code == 0

    # Check if any runs exist
    if "You did not yet create a run" in result.output:
        pytest.skip("No runs available. Please run tests that submit runs first.")

    # Extract run ID from the output (format: "- <run_id> of <app>...")
    normalized_output = normalize_output(result.output)
    run_id_match = re.search(r"-\s+([a-f0-9\-]{36})\s+of\s+", normalized_output)
    assert run_id_match is not None, f"Could not extract run ID from list output:\n{normalized_output}"
    run_id = run_id_match.group(1)

    # Get run details to extract an item's external_id
    result = runner.invoke(cli, ["application", "run", "describe", run_id])
    assert result.exit_code == 0

    normalized_describe = normalize_output(result.output)
    # Match the line after "Item External ID:"
    external_id_match = re.search(r"Item External ID:\s*\n\s*([^\s]+)", normalized_describe)

    if not external_id_match:
        # Try single line format as fallback
        external_id_match = re.search(r"Item External ID:\s*([^\n\s]+)", normalized_describe)

    if not external_id_match:
        pytest.skip("Could not extract item external_id from run. Run may not have items yet.")

    external_id = external_id_match.group(1).strip()
    print(external_id)

    # Step 2: Dump custom metadata of item
    result = runner.invoke(cli, ["application", "run", "dump-item-metadata", run_id, external_id])
    assert result.exit_code == 0
    initial_metadata = json.loads(result.output)
    # If metadata is None/null, start with empty dict
    if initial_metadata is None:
        initial_metadata = {}
    assert isinstance(initial_metadata, dict), "Custom metadata should be a dictionary"

    # Store initial SDK metadata timestamps for comparison
    initial_created_at = initial_metadata.get("sdk", {}).get("created_at")
    initial_updated_at = initial_metadata.get("sdk", {}).get("updated_at")

    # Ensure some time passes to see timestamp changes
    sleep(1)

    # Step 3: Add "random" node with a random number
    random_value = random.randint(1000, 9999)
    updated_metadata = initial_metadata.copy()
    updated_metadata["random"] = random_value

    # Update the custom metadata
    result = runner.invoke(
        cli, ["application", "run", "update-item-metadata", run_id, external_id, json.dumps(updated_metadata)]
    )
    assert result.exit_code == 0
    assert "Successfully updated custom metadata" in result.output

    # Step 4: Dump metadata again and verify random number appeared
    result = runner.invoke(cli, ["application", "run", "dump-item-metadata", run_id, external_id, "--pretty"])
    assert result.exit_code == 0
    metadata_with_random = json.loads(result.output)
    assert "random" in metadata_with_random, "Random field should be present in metadata"
    assert metadata_with_random["random"] == random_value, f"Random value should be {random_value}"

    # Verify SDK metadata timestamps behavior after update
    updated_created_at = metadata_with_random.get("sdk", {}).get("created_at")
    updated_updated_at = metadata_with_random.get("sdk", {}).get("updated_at")

    # created_at should NOT change
    if initial_created_at is not None:
        assert updated_created_at == initial_created_at, (
            f"sdk.created_at should not change: {initial_created_at} -> {updated_created_at}"
        )

    # updated_at SHOULD change (be more recent)
    assert updated_updated_at != initial_updated_at, (
        f"sdk.updated_at should change after update: {initial_updated_at} -> {updated_updated_at}"
    )
    # Step 5: Remove the random numberresult.output)
    assert "random" in metadata_with_random, "Random field should be present in metadata"
    assert metadata_with_random["random"] == random_value, f"Random value should be {random_value}"

    # Step 5: Remove the random number
    del updated_metadata["random"]
    result = runner.invoke(
        cli, ["application", "run", "update-item-metadata", run_id, external_id, json.dumps(updated_metadata)]
    )
    assert result.exit_code == 0
    assert "Successfully updated custom metadata" in result.output

    # Step 6: Dump metadata and validate random element has been removed
    result = runner.invoke(cli, ["application", "run", "dump-item-metadata", run_id, external_id])
    assert result.exit_code == 0
    final_metadata = json.loads(result.output)
    assert "random" not in final_metadata, "Random field should have been removed from metadata"

    # Note: Similar to run metadata, we verify the structure remains consistent
    # rather than doing exact equality comparison due to dynamic fields
    assert isinstance(final_metadata, dict), "Final metadata should be a dictionary"
