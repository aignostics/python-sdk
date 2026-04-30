"""Tests to verify the CLI functionality of the application module."""

import contextlib
import json
import platform
import re
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import sleep
from unittest.mock import MagicMock, patch

import pytest
from loguru import logger
from tenacity import Retrying, retry, stop_after_attempt, wait_exponential
from typer.testing import CliRunner

from aignostics.application import Service as ApplicationService
from aignostics.cli import cli
from aignostics.platform import LIST_APPLICATION_RUNS_MAX_PAGE_SIZE
from aignostics.utils import Health, sanitize_path
from tests.conftest import normalize_output, print_directory_structure
from tests.constants_test import (
    HETA_APPLICATION_ID,
    HETA_APPLICATION_VERSION,
    PIPELINE_GPU_TYPE,
    SPOT_0_CRC32C,
    SPOT_0_FILENAME,
    SPOT_0_GS_URL,
    SPOT_0_HEIGHT,
    SPOT_0_RESOLUTION_MPP,
    SPOT_0_WIDTH,
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
HETA_APPLICATION_DEADLINE_SECONDS = 60 * 60 * 4  # 4 hours

RUN_CSV_FILENAME = "run.csv"

DOCUMENT_OUTPUT_DESCRIPTION_PDF = "output_description.pdf"
DOCUMENT_MODEL_CARD_PDF = "model_card.pdf"
DOCUMENT_MISSING_PDF = "missing.pdf"
APPLICATION_CLI_CLIENT_PATCH_TARGET = "aignostics.application._cli.Client"

# Stub values reused across the document CLI tests.
DOCUMENT_TEST_FAILURE_MESSAGE = "kaboom"  # canonical exception body for unexpected-failure paths
DOCUMENT_LATEST_VERSION_NUMBER = "1.0.0"
DOCUMENT_ERROR_CODE_NOT_FOUND = "not_found"  # JSON-error contract: missing resource
DOCUMENT_ERROR_CODE_FAILED = "failed"  # JSON-error contract: unexpected failure

# Full SPOT_0 CSV - single source of truth for all run submissions in this test file.
CSV_CONTENT_SPOT0 = (
    "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;"
    "staining_method;tissue;disease;platform_bucket_url\n"
    f"{SPOT_0_FILENAME};{SPOT_0_CRC32C};{SPOT_0_RESOLUTION_MPP};{SPOT_0_WIDTH};{SPOT_0_HEIGHT}"
    f";H&E;LUNG;LUNG_CANCER;{SPOT_0_GS_URL}"
)

# Source directory for `prepare` tests (contains small-pyramidal.dcm).
PREPARE_SOURCE_DIR = Path(__file__).parent.parent.parent / "resources" / "run"


@contextlib.contextmanager
def submitted_run(
    runner: CliRunner,
    tmp_path: Path,
    csv_content: str,
    application_id: str = HETA_APPLICATION_ID,
    extra_args: list[str] | None = None,
) -> Generator[str, None, None]:
    """Context manager that submits a run, yields its ID, then cancels it on exit.

    Submits an application run via the CLI, yields the extracted run ID to the caller,
    and attempts to cancel the run on exit. Cancellation failures are logged but do not
    raise, so test assertions are never masked by cleanup errors.

    A 5-minute deadline is automatically appended unless ``extra_args`` already contains
    ``--deadline``.

    Args:
        runner: Typer CliRunner to invoke CLI commands.
        tmp_path: Temporary directory used to write the CSV file.
        csv_content: Full CSV content (header + rows) for the run submission.
        application_id: Application ID to submit against. Defaults to HETA_APPLICATION_ID.
        extra_args: Additional CLI arguments forwarded to the ``submit`` command,
            e.g. ``["--tags", "my-tag", "--deadline", "..."]``.

    Yields:
        The run ID string extracted from the submission output.

    Raises:
        AssertionError: If the submit command fails or the run ID cannot be extracted.
    """
    csv_path = tmp_path / "run.csv"
    csv_path.write_text(csv_content)

    extra = list(extra_args or [])
    if "--deadline" not in extra:
        extra += ["--deadline", (datetime.now(tz=UTC) + timedelta(minutes=5)).isoformat()]

    args = ["application", "run", "submit", application_id, str(csv_path), *extra]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, f"Run submission failed (exit {result.exit_code}):\n{result.stdout}"

    output = normalize_output(result.stdout)
    run_id_match = re.search(r"Submitted run with id '([0-9a-f-]+)' for '", output)
    assert run_id_match, f"Could not extract run ID from submission output:\n{output}"
    run_id = run_id_match.group(1)

    try:
        yield run_id
    finally:
        cancel_result = runner.invoke(cli, ["application", "run", "cancel", run_id])
        if cancel_result.exit_code != 0:
            logger.warning(
                "Failed to cancel run '{}' during cleanup (exit {}): {}",
                run_id,
                cancel_result.exit_code,
                normalize_output(cancel_result.stdout),
            )


def _cancel_run_if_submitted(runner: CliRunner, output: str) -> None:
    """Cancel any run that was unexpectedly created, for use in error-path cleanup.

    Args:
        runner: Typer CliRunner to invoke CLI commands.
        output: stdout from the submit invocation to search for a run ID.
    """
    run_id_match = re.search(r"Submitted run with id '([0-9a-f-]+)' for '", normalize_output(output))
    if run_id_match:
        cancel_result = runner.invoke(cli, ["application", "run", "cancel", run_id_match.group(1)])
        if cancel_result.exit_code != 0:
            logger.warning(
                "Defensive cancel of run '{}' failed (exit {}): {}",
                run_id_match.group(1),
                cancel_result.exit_code,
                normalize_output(cancel_result.stdout),
            )


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
    source_directory = PREPARE_SOURCE_DIR
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
    result = runner.invoke(cli, ["application", "run", "upload", HETA_APPLICATION_ID, str(metadata_csv), "--force"])
    assert "Upload completed." in normalize_output(result.stdout)
    assert result.exit_code == 0

    # Step 3: Submit the run from the metadata file
    result = runner.invoke(cli, ["application", "run", "submit", HETA_APPLICATION_ID, str(metadata_csv), "--force"])
    try:
        assert result.exit_code == 2
        assert "Invalid metadata for artifact `whole_slide_image`" in normalize_output(result.stdout)
        assert "8.065226874391001 is greater than" in normalize_output(result.stdout)
    finally:
        _cancel_run_if_submitted(runner, result.stdout)


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

    result = runner.invoke(cli, ["application", "run", "upload", HETA_APPLICATION_ID, str(metadata_csv), "--force"])
    assert result.exit_code == 2
    assert "Warning: Source file 'missing.file' (row 0) does not exist" in normalize_output(result.stdout)


@pytest.mark.e2e
@pytest.mark.timeout(timeout=10)
@patch("aignostics.application._cli.SystemService.health_static")
def test_cli_run_submit_fails_when_system_unhealthy_and_no_force(
    mock_health: MagicMock, runner: CliRunner, tmp_path: Path
) -> None:
    """Check run submit command exits with code 1 when system is unhealthy and --force is not used."""
    mock_health.return_value = Health(
        status=Health.Code.DOWN,
        reason="Simulated unhealthy system for testing",
    )
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
        ],
    )
    try:
        assert result.exit_code == 1
    finally:
        _cancel_run_if_submitted(runner, result.stdout)


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
@patch("aignostics.application._cli.SystemService.health_static")
def test_cli_run_submit_succeeds_when_system_degraded_and_no_force(
    mock_health: MagicMock, runner: CliRunner, tmp_path: Path
) -> None:
    """Check run submit command succeeds when system is degraded and --force is not used."""
    mock_health.return_value = Health(
        status=Health.Code.DEGRADED,
        reason="Simulated degraded system for testing",
    )
    with submitted_run(runner, tmp_path, CSV_CONTENT_SPOT0):
        pass  # submission success is asserted by the context manager


@pytest.mark.e2e
@pytest.mark.timeout(timeout=10)
@patch("aignostics.application._cli.SystemService.health_static")
def test_cli_run_upload_fails_when_system_unhealthy_and_no_force(
    mock_health: MagicMock, runner: CliRunner, tmp_path: Path
) -> None:
    """Check run upload command exits with code 1 when system is unhealthy and --force is not used."""
    mock_health.return_value = Health(
        status=Health.Code.DOWN,
        reason="Simulated unhealthy system for testing",
    )
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
            "upload",
            HETA_APPLICATION_ID,
            str(csv_path),
        ],
    )

    assert result.exit_code == 1


@pytest.mark.e2e
@pytest.mark.timeout(timeout=10)
@patch("aignostics.application._cli.SystemService.health_static")
def test_cli_run_execute_fails_when_system_unhealthy_and_no_force(
    mock_health: MagicMock, runner: CliRunner, tmp_path: Path
) -> None:
    """Check run execute command exits with code 1 when system is unhealthy and --force is not used."""
    mock_health.return_value = Health(
        status=Health.Code.DOWN,
        reason="Simulated unhealthy system for testing",
    )
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
            "execute",
            HETA_APPLICATION_ID,
            str(csv_path),
            str(tmp_path),
        ],
    )

    assert result.exit_code == 1


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
            "--force",
        ],
    )
    try:
        assert result.exit_code == 2
        assert 'HTTP response body: {"detail":"application not found"}' in normalize_output(result.stdout)
        assert "Warning: Could not find application" in normalize_output(result.stdout)
        assert result.exit_code == 2
    finally:
        _cancel_run_if_submitted(runner, result.stdout)


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
            "--force",
        ],
    )
    try:
        assert result.exit_code == 2
        assert "Invalid platform bucket URL: 'aws://bucket/test'" in normalize_output(result.stdout)
    finally:
        _cancel_run_if_submitted(runner, result.stdout)


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
            "--force",
        ],
    )
    try:
        assert result.exit_code == 2
        assert "Invalid platform bucket URL: ''" in normalize_output(result.stdout)
    finally:
        _cancel_run_if_submitted(runner, result.stdout)


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.flaky(retries=3, delay=5)
@pytest.mark.timeout(timeout=60 * 10)
@pytest.mark.skipif(
    (platform.system() == "Linux" and platform.machine() in {"aarch64", "arm64"})
    or (platform.system() in {"Darwin", "Windows"}),
    reason=(
        "Only run on Linux x86_64 / GitHub Actions ubuntu-latest to avoid creating unnecessary load on the platform."
    ),
)
def test_cli_run_submit_and_describe_and_cancel_and_download_and_delete(  # noqa: PLR0915
    runner: CliRunner, tmp_path: Path, silent_logging, record_property
) -> None:
    """Check run submit command runs successfully."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-02")
    with submitted_run(
        runner,
        tmp_path,
        CSV_CONTENT_SPOT0,
        extra_args=[
            "--note",
            "note_of_this_complex_test",
            "--tags",
            "cli-test,test_cli_run_submit_and_describe_and_cancel_and_download_and_delete,further-tag",
            "--deadline",
            (datetime.now(tz=UTC) + timedelta(minutes=10)).isoformat(),
            "--onboard-to-aignostics-portal",
            "--gpu-type",
            PIPELINE_GPU_TYPE,
            "--force",
        ],
    ) as run_id:
        # Test that we can find this run by it's note via the query parameter
        list_result = runner.invoke(
            cli,
            [
                "application",
                "run",
                "list",
                "--query",
                "note_of_this_complex_test",
                "--limit",
                str(LIST_APPLICATION_RUNS_MAX_PAGE_SIZE),
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
                "--limit",
                str(LIST_APPLICATION_RUNS_MAX_PAGE_SIZE),
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
                "--limit",
                str(LIST_APPLICATION_RUNS_MAX_PAGE_SIZE),
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
                "--limit",
                str(LIST_APPLICATION_RUNS_MAX_PAGE_SIZE),
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
                "--limit",
                str(LIST_APPLICATION_RUNS_MAX_PAGE_SIZE),
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
                "--limit",
                str(LIST_APPLICATION_RUNS_MAX_PAGE_SIZE),
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
                "--limit",
                str(LIST_APPLICATION_RUNS_MAX_PAGE_SIZE),
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
                "--limit",
                str(LIST_APPLICATION_RUNS_MAX_PAGE_SIZE),
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
                "--limit",
                str(LIST_APPLICATION_RUNS_MAX_PAGE_SIZE),
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
                "--limit",
                str(LIST_APPLICATION_RUNS_MAX_PAGE_SIZE),
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
                "--limit",
                str(LIST_APPLICATION_RUNS_MAX_PAGE_SIZE),
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
        assert "Queue Position:" in normalize_output(describe_result.stdout)
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

        # More robust path verification - normalize paths and check if destination path is mentioned in output
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
            assert f"Failed to create destination directory '/4711/{run_id}'" in normalize_output(
                download_result.stdout
            )

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


@pytest.mark.unit
def test_cli_run_list_for_organization(runner: CliRunner) -> None:
    """Check run list command passes --for-organization to service and shows org-specific empty message."""
    with patch.object(ApplicationService, "application_runs", return_value=[]) as mock_method:
        result = runner.invoke(cli, ["application", "run", "list", "--for-organization", "org-123"])
        assert result.exit_code == 0
        mock_method.assert_called_once()
        assert mock_method.call_args[1]["for_organization"] == "org-123"
        output = normalize_output(result.stdout)
        assert "No runs found for organization 'org-123'" in output


@pytest.mark.unit
def test_cli_run_list_forbidden_with_organization(runner: CliRunner) -> None:
    """Check ForbiddenException with --for-organization shows org-specific access denied message."""
    from aignx.codegen.exceptions import ForbiddenException

    with patch.object(
        ApplicationService, "application_runs", side_effect=ForbiddenException(status=403, reason="Forbidden")
    ):
        result = runner.invoke(cli, ["application", "run", "list", "--for-organization", "secret-org"])
        assert result.exit_code == 2
        output = normalize_output(result.stdout)
        assert "Access denied" in output
        assert "secret-org" in output


@pytest.mark.unit
def test_cli_run_list_forbidden_without_organization(runner: CliRunner) -> None:
    """Check ForbiddenException without --for-organization shows generic access denied message."""
    from aignx.codegen.exceptions import ForbiddenException

    with patch.object(
        ApplicationService, "application_runs", side_effect=ForbiddenException(status=403, reason="Forbidden")
    ):
        result = runner.invoke(cli, ["application", "run", "list"])
        assert result.exit_code == 2
        output = normalize_output(result.stdout)
        assert "Access denied: you are not authorized to list runs." in output


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


@pytest.mark.integration
def test_cli_run_describe_json_includes_items(runner: CliRunner) -> None:
    """Check run describe --format=json includes items in output."""
    from aignx.codegen.models import (
        ItemOutput,
        ItemResultReadResponse,
        ItemState,
        ItemTerminationReason,
        RunItemStatistics,
        RunOutput,
        RunReadResponse,
        RunState,
        RunTerminationReason,
    )

    mock_run_data = RunReadResponse(
        run_id="test-run-id-123",
        application_id="test-app",
        version_number="1.0.0",
        state=RunState.TERMINATED,
        output=RunOutput.FULL,
        termination_reason=RunTerminationReason.ALL_ITEMS_PROCESSED,
        error_code=None,
        error_message=None,
        statistics=RunItemStatistics(
            item_count=1,
            item_pending_count=0,
            item_processing_count=0,
            item_user_error_count=0,
            item_system_error_count=0,
            item_skipped_count=0,
            item_succeeded_count=1,
        ),
        custom_metadata=None,
        submitted_at=datetime(2025, 1, 1, tzinfo=UTC),
        submitted_by="test-user",
        terminated_at=datetime(2025, 1, 1, 0, 5, tzinfo=UTC),
    )

    mock_item = ItemResultReadResponse(
        item_id="item-id-456",
        external_id="slide-001.svs",
        custom_metadata={"key": "value"},
        state=ItemState.TERMINATED,
        output=ItemOutput.FULL,
        termination_reason=ItemTerminationReason.SUCCEEDED,
        error_message=None,
        error_code=None,
        input_artifacts=[],
        output_artifacts=[],
    )

    mock_user_info = MagicMock()
    mock_user_info.is_internal_user = False

    mock_run_handle = MagicMock()
    mock_run_handle.details.return_value = mock_run_data
    mock_run_handle.results.return_value = iter([mock_item])

    with (
        patch("aignostics.application._cli.PlatformService.get_user_info", return_value=mock_user_info),
        patch("aignostics.application._cli.Service") as mock_service_cls,
    ):
        mock_service_cls.return_value.application_run.return_value = mock_run_handle

        result = runner.invoke(cli, ["application", "run", "describe", "test-run-id-123", "--format", "json"])

    assert result.exit_code == 0, f"Command failed with output: {result.stdout}"
    output_data = json.loads(result.stdout)

    # Verify run-level fields are present
    assert output_data["run_id"] == "test-run-id-123"
    assert output_data["application_id"] == "test-app"

    # Verify items are included
    assert "items" in output_data, "JSON output must include 'items' key"
    assert len(output_data["items"]) == 1
    item = output_data["items"][0]
    assert item["item_id"] == "item-id-456"
    assert item["external_id"] == "slide-001.svs"
    assert item["custom_metadata"] == {"key": "value"}
    assert item["state"] == "TERMINATED"
    assert item["termination_reason"] == "SUCCEEDED"


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


# TODO (Helmut): Run this test on a schedule when the GPU ressourcing situation and PAPI pipeline reliabilty improved
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
            str(tmp_path / RUN_CSV_FILENAME),
            str(tmp_path),
            "--application-version",
            HETA_APPLICATION_VERSION,
            "--mapping",
            ".*\\.tiff:staining_method=H&E,tissue=LUNG,disease=LUNG_CANCER",
            "--no-create-subdirectory-for-run",
            "--due-date",
            (datetime.now(tz=UTC) + timedelta(seconds=HETA_APPLICATION_DUE_DATE_SECONDS)).isoformat(),
            "--deadline",
            (datetime.now(tz=UTC) + timedelta(seconds=HETA_APPLICATION_DEADLINE_SECONDS)).isoformat(),
            "--force",
        ],
    )

    # Validate the download command exited successfully
    assert result.exit_code == 0

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
def test_cli_run_execute_invalid_mapping_format(runner: CliRunner, tmp_path: Path) -> None:
    """Check execute command fails with invalid mapping format."""
    result = runner.invoke(
        cli,
        [
            "application",
            "run",
            "execute",
            HETA_APPLICATION_ID,
            str(tmp_path / RUN_CSV_FILENAME),
            str(tmp_path),
            "--mapping",
            ".*\\.tiff:staining_method:H&E",  # Wrong: colon instead of equals
            "--force",  # Skip health check; we're testing argument validation only
        ],
    )
    assert result.exit_code != 0
    assert "Invalid mapping" in result.output
    assert "should be in format" in result.output


@pytest.mark.integration
def test_cli_run_execute_invalid_regex_pattern(runner: CliRunner, tmp_path: Path) -> None:
    """Check execute command fails with invalid regex pattern."""
    result = runner.invoke(
        cli,
        [
            "application",
            "run",
            "execute",
            HETA_APPLICATION_ID,
            str(tmp_path / RUN_CSV_FILENAME),
            str(tmp_path),
            "--mapping",
            "*.tiff:staining_method=H&E",  # Wrong: glob pattern, not regex
            "--force",  # Skip health check; we're testing argument validation only
        ],
    )
    assert result.exit_code != 0
    assert "Invalid mapping" in result.output
    assert "invalid regex pattern" in result.output


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
@pytest.mark.timeout(timeout=180)
@pytest.mark.sequential
def test_cli_run_dump_and_update_custom_metadata(runner: CliRunner, tmp_path: Path) -> None:
    """Test dumping and updating custom metadata via CLI commands."""
    import json
    import random

    unique_tag = f"test_metadata_{datetime.now(tz=UTC).timestamp()}"
    with submitted_run(runner, tmp_path, CSV_CONTENT_SPOT0, extra_args=["--tags", unique_tag, "--force"]) as run_id:
        # Step 1: Dump initial custom metadata of run
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

        # Step 2: Add "random" node with a random number
        random_value = random.randint(1000, 9999)
        updated_metadata = initial_metadata.copy()
        updated_metadata["random"] = random_value

        # Update the custom metadata
        result = runner.invoke(cli, ["application", "run", "update-metadata", run_id, json.dumps(updated_metadata)])
        assert result.exit_code == 0
        assert "Successfully updated custom metadata" in result.output

        # Step 3: Dump metadata again with retry to handle read-replica lag after write
        metadata_with_random: dict = {}
        for attempt in Retrying(wait=wait_exponential(multiplier=2, max=10), stop=stop_after_attempt(5)):
            with attempt:
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

        # Step 4: Remove the random number
        del updated_metadata["random"]
        result = runner.invoke(cli, ["application", "run", "update-metadata", run_id, json.dumps(updated_metadata)])
        assert result.exit_code == 0
        assert "Successfully updated custom metadata" in result.output

        # Step 5: Dump metadata and validate random element removed, with retry for read-replica lag
        final_metadata: dict = {}
        for attempt in Retrying(wait=wait_exponential(multiplier=2, max=10), stop=stop_after_attempt(5)):
            with attempt:
                result = runner.invoke(cli, ["application", "run", "dump-metadata", run_id])
                assert result.exit_code == 0
                final_metadata = json.loads(result.stdout)
                assert "random" not in final_metadata, "Random field should have been removed from metadata"

        # Note: We can't compare final_metadata == initial_metadata because the SDK
        # automatically updates some fields (e.g., submission.date, ci.pytest.current_test)
        # when operations are performed. Instead, verify the random field was removed
        # and the structure remains consistent.
        assert isinstance(final_metadata, dict), "Final metadata should be a dictionary"


@pytest.mark.e2e
@pytest.mark.timeout(timeout=240)
@pytest.mark.sequential
def test_cli_run_dump_and_update_item_custom_metadata(runner: CliRunner, tmp_path: Path) -> None:  # noqa: PLR0915
    """Test dumping and updating item custom metadata via CLI commands."""
    import json
    import random

    unique_tag = f"test_item_metadata_{datetime.now(tz=UTC).timestamp()}"
    # CSV_CONTENT_SPOT0 uses SPOT_0_FILENAME as external_id, which the describe output surfaces
    # as "Item External ID: `...`" — the get_external_id() helper below captures it dynamically.
    with submitted_run(runner, tmp_path, CSV_CONTENT_SPOT0, extra_args=["--tags", unique_tag]) as run_id:
        # Wait for items to appear in the run (describe until external_id is available)
        @retry(wait=wait_exponential(multiplier=1, max=15), stop=stop_after_attempt(8))
        def get_external_id() -> str:
            describe_result = runner.invoke(cli, ["application", "run", "describe", run_id])
            assert describe_result.exit_code == 0, f"describe failed: {describe_result.output}"
            normalized = normalize_output(describe_result.output)
            match = re.search(r"Item External ID:\s*`([^`]+)`", normalized)
            if not match:
                msg = "No item external_id available in run yet"
                raise RuntimeError(msg)
            return match.group(1).strip()

        external_id = get_external_id()

        # Step 1: Dump initial custom metadata of item
        result = runner.invoke(cli, ["application", "run", "dump-item-metadata", run_id, external_id])
        assert result.exit_code == 0
        initial_metadata = json.loads(result.stdout)
        # If metadata is None/null, start with empty dict
        if initial_metadata is None:
            initial_metadata = {}
        assert isinstance(initial_metadata, dict), "Custom metadata should be a dictionary"

        # Store initial SDK metadata timestamps for comparison
        initial_created_at = initial_metadata.get("sdk", {}).get("created_at")
        initial_updated_at = initial_metadata.get("sdk", {}).get("updated_at")

        # Ensure some time passes to see timestamp changes
        sleep(1)

        # Step 2: Add "random" node with a random number
        random_value = random.randint(1000, 9999)
        updated_metadata = initial_metadata.copy()
        updated_metadata["random"] = random_value

        # Update the custom metadata
        result = runner.invoke(
            cli, ["application", "run", "update-item-metadata", run_id, external_id, json.dumps(updated_metadata)]
        )
        assert result.exit_code == 0
        assert "Successfully updated custom metadata" in result.output

        # Step 3: Dump metadata again with retry to handle read-replica lag after write
        metadata_with_random: dict = {}
        for attempt in Retrying(wait=wait_exponential(multiplier=2, max=10), stop=stop_after_attempt(5)):
            with attempt:
                result = runner.invoke(
                    cli, ["application", "run", "dump-item-metadata", run_id, external_id, "--pretty"]
                )
                assert result.exit_code == 0
                metadata_with_random = json.loads(result.stdout)
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

        # Step 4: Remove the random number
        del updated_metadata["random"]
        result = runner.invoke(
            cli, ["application", "run", "update-item-metadata", run_id, external_id, json.dumps(updated_metadata)]
        )
        assert result.exit_code == 0
        assert "Successfully updated custom metadata" in result.output

        # Step 5: Dump metadata and validate random element removed, with retry for read-replica lag
        final_metadata: dict = {}
        for attempt in Retrying(wait=wait_exponential(multiplier=2, max=10), stop=stop_after_attempt(5)):
            with attempt:
                result = runner.invoke(cli, ["application", "run", "dump-item-metadata", run_id, external_id])
                assert result.exit_code == 0
                final_metadata = json.loads(result.stdout)
                assert "random" not in final_metadata, "Random field should have been removed from metadata"

        # Note: Similar to run metadata, we verify the structure remains consistent
        # rather than doing exact equality comparison due to dynamic fields
        assert isinstance(final_metadata, dict), "Final metadata should be a dictionary"


@retry(wait=wait_exponential(multiplier=2, max=10), stop=stop_after_attempt(5))
def list_runs_by_tag(tag: str, runner: CliRunner, expected_count: int = 1) -> list[dict]:
    """List runs filtered by tag. Returns list of runs.

    Retries to handle eventual consistency.

    Args:
        runner: CliRunner to use.
        tag: Tag to filter runs by.
        expected_count: Minimum number of runs expected (default: 1).

    Raises:
        RuntimeError: If listing runs fails or expected count not met.
    """
    list_result = runner.invoke(
        cli,
        [
            "application",
            "run",
            "list",
            "--tags",
            tag,
            "--format",
            "json",
        ],
    )
    if list_result.exit_code != 0:
        msg = f"List runs by tag '{tag}' failed"
        raise RuntimeError(msg)
    runs_data = json.loads(list_result.stdout)
    if len(runs_data) < expected_count:
        msg = f"Expected at least {expected_count} run(s) with tag '{tag}', but found {len(runs_data)}"
        raise RuntimeError(msg)
    return runs_data


@pytest.mark.e2e
@pytest.mark.timeout(timeout=180)
def test_cli_json_format_and_cancel_by_filter_with_dry_run(  # noqa: PLR0915, PLR0914
    runner: CliRunner, tmp_path: Path, silent_logging, record_property
) -> None:
    """Test JSON output format for application/run commands and cancel-by-filter with dry-run mode.

    This test comprehensively validates:
    1. JSON format for application list/describe commands
    2. JSON format for run list/describe commands
    3. Run filtering by tags
    4. cancel-by-filter command with multiple filters (tags, application_id, application_version)
    5. Dry-run mode (preview without canceling)
    6. Actual cancellation and state transitions (PENDING/PROCESSING → TERMINATED)
    7. Termination reason verification (CANCELED_BY_USER)
    """
    record_property("tested-item-id", "TC-APPLICATION-CLI-JSON-FORMAT-AND-CANCEL-BY-FILTER")

    # Step 1: Test application list with JSON format
    app_list_result = runner.invoke(
        cli,
        [
            "application",
            "list",
            "--format",
            "json",
        ],
    )
    assert app_list_result.exit_code == 0
    apps_data = json.loads(app_list_result.stdout)
    assert isinstance(apps_data, list), "Application list JSON output should be a list"
    assert len(apps_data) > 0, "Should have at least one application"

    # Find HETA application in the list
    heta_found = False
    for app in apps_data:
        if app["application_id"] == HETA_APPLICATION_ID:
            heta_found = True
            assert "name" in app
            assert "latest_version" in app
            break
    assert heta_found, f"Application '{HETA_APPLICATION_ID}' should be in the list"

    # Step 2: Test application describe with JSON format
    app_describe_result = runner.invoke(
        cli,
        [
            "application",
            "describe",
            HETA_APPLICATION_ID,
            "--format",
            "json",
        ],
    )
    assert app_describe_result.exit_code == 0
    app_details = json.loads(app_describe_result.stdout)
    assert isinstance(app_details, dict), "Application describe JSON output should be a dictionary"
    assert app_details["application_id"] == HETA_APPLICATION_ID
    assert "name" in app_details
    assert "versions" in app_details
    assert "description" in app_details

    # Step 3: Submit a run with custom tag
    unique_tag = f"test_json_format_{datetime.now(tz=UTC).timestamp()}"

    with submitted_run(
        runner,
        tmp_path,
        CSV_CONTENT_SPOT0,
        extra_args=["--tags", unique_tag, "--note", "Testing JSON format output", "--gpu-type", PIPELINE_GPU_TYPE],
    ) as run_id:
        # Step 4: List runs with JSON format and filter by tag
        runs_data = list_runs_by_tag(unique_tag, runner, expected_count=1)

        # Step 5: Parse JSON output and verify structure
        assert isinstance(runs_data, list), "JSON output should be a list"
        assert len(runs_data) > 0, "Should find at least one run with the unique tag"

        # Step 6: Find our run in the JSON output
        run_found = False
        for run in runs_data:
            if run["run_id"] == run_id:
                run_found = True

                # Verify basic structure
                assert "application_id" in run
                assert run["application_id"] == HETA_APPLICATION_ID
                assert "version_number" in run
                assert "state" in run
                assert "custom_metadata" in run

                # Verify custom metadata contains SDK metadata with tags
                custom_metadata = run["custom_metadata"]
                assert "sdk" in custom_metadata, "SDK metadata should be present"
                assert "tags" in custom_metadata["sdk"], "Tags should be in SDK metadata"
                assert unique_tag in custom_metadata["sdk"]["tags"], f"Tag '{unique_tag}' should be in tags"

                # Verify note is in SDK metadata
                assert "note" in custom_metadata["sdk"], "Note should be in SDK metadata"
                assert custom_metadata["sdk"]["note"] == "Testing JSON format output"

                break

        assert run_found, f"Run with ID '{run_id}' not found in JSON output"

        # Step 7: Test run describe with JSON format
        describe_result = runner.invoke(
            cli,
            ["application", "run", "describe", run_id, "--format", "json"],
        )
        assert describe_result.exit_code == 0

        # Parse and verify describe JSON output
        describe_data = json.loads(describe_result.stdout)
        assert isinstance(describe_data, dict), "Describe JSON output should be a dictionary"
        assert describe_data["run_id"] == run_id, "Run ID should match"
        assert describe_data["application_id"] == HETA_APPLICATION_ID, "Application ID should match"
        assert "custom_metadata" in describe_data, "Should have custom_metadata field"
        assert "sdk" in describe_data["custom_metadata"], "Should have SDK metadata"
        assert unique_tag in describe_data["custom_metadata"]["sdk"]["tags"], "Tag should be in SDK metadata"
        assert describe_data["custom_metadata"]["sdk"]["note"] == "Testing JSON format output", "Note should match"

        # Step 8: Test empty result with JSON format
        empty_result = runner.invoke(
            cli,
            ["application", "run", "list", "--tags", "non_existent_tag_12345", "--format", "json"],
        )
        assert empty_result.exit_code == 0
        empty_runs = json.loads(empty_result.stdout)
        assert isinstance(empty_runs, list), "Empty JSON output should be a list"
        assert len(empty_runs) == 0, "Should return empty list for non-existent tag"

        # Step 9: Submit a second run with same tags for testing cancel-by-filter
        with submitted_run(
            runner,
            tmp_path,
            CSV_CONTENT_SPOT0,
            extra_args=[
                "--tags",
                unique_tag,
                "--note",
                "Testing JSON format output - run 2",
                "--gpu-type",
                PIPELINE_GPU_TYPE,
            ],
        ) as run_id_2:
            # Wait for both runs to appear in the list (handles eventual consistency)
            list_runs_by_tag(unique_tag, runner, expected_count=2)

            # Step 10: Test dry-run mode - verify it shows what would be canceled without actually canceling
            logger.info("Step 10: Testing dry-run mode for cancel-by-filter")

            # First get the application version from the first run
            app_version_result = runner.invoke(
                cli,
                ["application", "run", "describe", run_id, "--format", "json"],
            )
            assert app_version_result.exit_code == 0, f"Failed to describe run: {app_version_result.stdout}"
            run_details = json.loads(app_version_result.stdout)
            app_version = run_details["version_number"]

            # Test dry-run mode
            dry_run_result = runner.invoke(
                cli,
                [
                    "application",
                    "run",
                    "cancel-by-filter",
                    "--tags",
                    unique_tag,
                    "--application-id",
                    HETA_APPLICATION_ID,
                    "--application-version",
                    app_version,
                    "--dry-run",
                ],
            )
            assert dry_run_result.exit_code == 0, f"Dry-run failed: {dry_run_result.stdout}"
            assert "Would cancel 2 run(s)" in dry_run_result.stdout
            logger.info("Dry-run output:\n{}", dry_run_result.stdout)

            # Step 11: Verify runs are NOT canceled after dry-run by describing them
            logger.info("Step 11: Verifying runs are NOT canceled after dry-run")
            for idx, rid in enumerate([run_id, run_id_2], 1):
                describe_result = runner.invoke(cli, ["application", "run", "describe", rid, "--format", "json"])
                assert describe_result.exit_code == 0, f"Failed to describe run {idx}: {describe_result.stdout}"
                described_run = json.loads(describe_result.stdout)
                # Verify run is still in original state (PENDING or PROCESSING, not TERMINATED)
                assert described_run["state"] in {
                    "PENDING",
                    "PROCESSING",
                }, f"Run {idx} was unexpectedly canceled during dry-run"
                logger.info("Run {} still active after dry-run (state: {})", idx, described_run["state"])

            # Step 12: Actually cancel runs using cancel-by-filter with all three filters
            logger.info("Step 12: Canceling runs by filter (tags, application_id, application_version)")
            cancel_by_filter_result = runner.invoke(
                cli,
                [
                    "application",
                    "run",
                    "cancel-by-filter",
                    "--tags",
                    unique_tag,
                    "--application-id",
                    HETA_APPLICATION_ID,
                    "--application-version",
                    app_version,
                ],
            )
            assert cancel_by_filter_result.exit_code == 0
            assert "Successfully canceled 2 run(s)" in cancel_by_filter_result.stdout
            logger.info("Successfully canceled both runs using cancel-by-filter")

            # Step 13: Verify runs ARE canceled by describing them again
            # Use retry to handle read-replica lag and slow API responses after cancel.
            logger.info("Step 13: Verifying runs ARE canceled after actual cancel")
            for idx, rid in enumerate([run_id, run_id_2], 1):
                for attempt in Retrying(
                    wait=wait_exponential(multiplier=2, min=1, max=15),
                    stop=stop_after_attempt(5),
                    reraise=True,
                ):
                    with attempt:
                        describe_result = runner.invoke(
                            cli, ["application", "run", "describe", rid, "--format", "json"]
                        )
                        assert describe_result.exit_code == 0, (
                            f"Failed to describe run {idx} after cancel: {describe_result.stdout}"
                        )
                        described_run = json.loads(describe_result.stdout)
                        # Verify run is now TERMINATED
                        assert described_run["state"] == "TERMINATED", (
                            f"Run {idx} was not canceled, state: {described_run['state']}"
                        )
                        # termination_reason is a top-level field, not nested under output
                        assert described_run["termination_reason"] == "CANCELED_BY_USER", (
                            f"Run {idx} has unexpected termination reason: {described_run.get('termination_reason')}"
                        )
                        logger.info("Run {} successfully canceled (state: TERMINATED, reason: CANCELED_BY_USER)", idx)


# ----------------------------------------------------------------------------------
# Application version document CLI tests (TC-APPLICATION-CLI-05)
# ----------------------------------------------------------------------------------


def _make_document_stub(name: str = DOCUMENT_OUTPUT_DESCRIPTION_PDF) -> MagicMock:
    """Create a stub ApplicationVersionDocument with realistic field values."""
    stub = MagicMock()
    stub.id = "11111111-1111-1111-1111-111111111111"
    stub.name = name
    stub.mime_type = "application/pdf"  # NOSONAR python:S1192: standard MIME type literal is clearer than a constant
    stub.visibility = "public"
    stub.created_at = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    stub.updated_at = datetime(2026, 1, 2, 12, 0, tzinfo=UTC)
    stub.model_dump.return_value = {
        "id": stub.id,
        "name": stub.name,
        "mime_type": stub.mime_type,
        "visibility": stub.visibility,
        "created_at": stub.created_at.isoformat(),
        "updated_at": stub.updated_at.isoformat(),
    }
    return stub


@pytest.mark.unit
def test_cli_application_version_document_list_success(runner: CliRunner, record_property) -> None:
    """`application version document list` prints document metadata."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-01")
    fake_documents = MagicMock()
    fake_documents.list.return_value = [
        _make_document_stub(DOCUMENT_OUTPUT_DESCRIPTION_PDF),
        _make_document_stub(DOCUMENT_MODEL_CARD_PDF),
    ]
    fake_client = MagicMock()
    latest_version = MagicMock()
    latest_version.number = DOCUMENT_LATEST_VERSION_NUMBER
    fake_client.applications.versions.latest.return_value = latest_version
    fake_client.applications.versions.documents.return_value = fake_documents

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(cli, ["application", "version", "document", "list", "heta"])

    assert result.exit_code == 0
    output = normalize_output(result.output)
    assert DOCUMENT_OUTPUT_DESCRIPTION_PDF in output
    assert DOCUMENT_MODEL_CARD_PDF in output
    assert "application/pdf" in output  # NOSONAR python:S1192: standard MIME type literal is clearer than a constant
    fake_client.applications.versions.documents.assert_called_once_with("heta", DOCUMENT_LATEST_VERSION_NUMBER)


@pytest.mark.unit
def test_cli_application_version_document_describe_success(runner: CliRunner, record_property) -> None:
    """`application version document describe` prints metadata for a single document."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-02")
    fake_documents = MagicMock()
    fake_documents.details.return_value = _make_document_stub(DOCUMENT_OUTPUT_DESCRIPTION_PDF)
    fake_client = MagicMock()
    fake_client.applications.versions.documents.return_value = fake_documents

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(
            cli,
            ["application", "version", "document", "describe", "heta:1.0.0", DOCUMENT_OUTPUT_DESCRIPTION_PDF],
        )

    assert result.exit_code == 0
    output = normalize_output(result.output)
    assert DOCUMENT_OUTPUT_DESCRIPTION_PDF in output
    assert "application/pdf" in output  # NOSONAR python:S1192: standard MIME type literal is clearer than a constant
    # Explicit version supplied via "heta:1.0.0", so latest() should NOT be called.
    fake_client.applications.versions.latest.assert_not_called()
    fake_client.applications.versions.documents.assert_called_once_with("heta", DOCUMENT_LATEST_VERSION_NUMBER)
    fake_documents.details.assert_called_once_with(DOCUMENT_OUTPUT_DESCRIPTION_PDF)


@pytest.mark.unit
def test_cli_application_version_document_describe_not_found(runner: CliRunner, record_property) -> None:
    """`application version document describe` exits 2 with a clear message on 404."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-03")
    from aignx.codegen.exceptions import NotFoundException as ApiNotFound

    fake_documents = MagicMock()
    fake_documents.details.side_effect = ApiNotFound(status=404, reason="Not Found")
    fake_client = MagicMock()
    latest_version = MagicMock()
    latest_version.number = DOCUMENT_LATEST_VERSION_NUMBER
    fake_client.applications.versions.latest.return_value = latest_version
    fake_client.applications.versions.documents.return_value = fake_documents

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(
            cli,
            ["application", "version", "document", "describe", "heta", DOCUMENT_MISSING_PDF],
        )

    assert result.exit_code == 2
    output = normalize_output(result.output)
    assert f"Document '{DOCUMENT_MISSING_PDF}' not found for application version 'heta'." in output


@pytest.mark.unit
def test_cli_application_version_document_download_success(runner: CliRunner, tmp_path: Path, record_property) -> None:
    """`application version document download` writes the file and prints the destination."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-04")
    fake_documents = MagicMock()
    expected_path = tmp_path / DOCUMENT_OUTPUT_DESCRIPTION_PDF
    fake_documents.download_to_path.return_value = expected_path
    fake_client = MagicMock()
    latest_version = MagicMock()
    latest_version.number = DOCUMENT_LATEST_VERSION_NUMBER
    fake_client.applications.versions.latest.return_value = latest_version
    fake_client.applications.versions.documents.return_value = fake_documents

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(
            cli,
            [
                "application",
                "version",
                "document",
                "download",
                "heta",
                DOCUMENT_OUTPUT_DESCRIPTION_PDF,
                "--output",
                str(tmp_path),
            ],
        )

    assert result.exit_code == 0
    output = normalize_output(result.output)
    assert str(expected_path) in output
    fake_documents.download_to_path.assert_called_once()
    args, _ = fake_documents.download_to_path.call_args
    assert args[0] == DOCUMENT_OUTPUT_DESCRIPTION_PDF


@pytest.mark.unit
def test_cli_application_version_document_list_json_success(runner: CliRunner, record_property) -> None:
    """`application version document list --format json` emits a JSON array of documents."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-01")
    fake_documents = MagicMock()
    fake_documents.list.return_value = [
        _make_document_stub(DOCUMENT_OUTPUT_DESCRIPTION_PDF),
        _make_document_stub(DOCUMENT_MODEL_CARD_PDF),
    ]
    fake_client = MagicMock()
    latest_version = MagicMock()
    latest_version.number = DOCUMENT_LATEST_VERSION_NUMBER
    fake_client.applications.versions.latest.return_value = latest_version
    fake_client.applications.versions.documents.return_value = fake_documents

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(cli, ["application", "version", "document", "list", "heta", "--format", "json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert isinstance(payload, list)
    assert len(payload) == 2
    assert payload[0]["name"] == DOCUMENT_OUTPUT_DESCRIPTION_PDF
    assert payload[1]["name"] == DOCUMENT_MODEL_CARD_PDF
    assert (
        payload[0]["mime_type"] == "application/pdf"
    )  # NOSONAR python:S1192: standard MIME type literal is clearer than a constant


@pytest.mark.unit
def test_cli_application_version_document_list_json_empty(runner: CliRunner, record_property) -> None:
    """`application version document list --format json` emits an empty array when none attached."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-01")
    fake_documents = MagicMock()
    fake_documents.list.return_value = []
    fake_client = MagicMock()
    latest_version = MagicMock()
    latest_version.number = DOCUMENT_LATEST_VERSION_NUMBER
    fake_client.applications.versions.latest.return_value = latest_version
    fake_client.applications.versions.documents.return_value = fake_documents

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(cli, ["application", "version", "document", "list", "heta", "--format", "json"])

    assert result.exit_code == 0
    assert json.loads(result.stdout) == []


@pytest.mark.unit
def test_cli_application_version_document_list_resolve_not_found_text(runner: CliRunner, record_property) -> None:
    """`application version document list` exits 2 when no versions exist (text format)."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-01")
    fake_client = MagicMock()
    # `latest()` returning None triggers `_resolve_documents` to raise NotFoundException.
    fake_client.applications.versions.latest.return_value = None

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(cli, ["application", "version", "document", "list", "heta"])

    assert result.exit_code == 2
    output = normalize_output(result.output)
    assert "No release documents found" in output
    assert "'heta'" in output


@pytest.mark.unit
def test_cli_application_version_document_list_resolve_not_found_json(runner: CliRunner, record_property) -> None:
    """`application version document list --format json` emits structured error on 404."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-01")
    fake_client = MagicMock()
    fake_client.applications.versions.latest.return_value = None

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(cli, ["application", "version", "document", "list", "heta", "--format", "json"])

    assert result.exit_code == 2
    payload = json.loads(result.stderr)
    assert payload["error"] == DOCUMENT_ERROR_CODE_NOT_FOUND
    assert "heta" in payload["message"]


@pytest.mark.unit
def test_cli_application_version_document_list_failed_text(runner: CliRunner, record_property) -> None:
    """`application version document list` exits 1 with an error message on unexpected failure."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-01")
    fake_documents = MagicMock()
    fake_documents.list.side_effect = RuntimeError(DOCUMENT_TEST_FAILURE_MESSAGE)
    fake_client = MagicMock()
    latest_version = MagicMock()
    latest_version.number = DOCUMENT_LATEST_VERSION_NUMBER
    fake_client.applications.versions.latest.return_value = latest_version
    fake_client.applications.versions.documents.return_value = fake_documents

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(cli, ["application", "version", "document", "list", "heta"])

    assert result.exit_code == 1
    output = normalize_output(result.output)
    assert "Failed to list release documents for 'heta'" in output
    assert DOCUMENT_TEST_FAILURE_MESSAGE in output


@pytest.mark.unit
def test_cli_application_version_document_list_failed_json(runner: CliRunner, record_property) -> None:
    """`application version document list --format json` emits structured error on failure."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-01")
    fake_documents = MagicMock()
    fake_documents.list.side_effect = RuntimeError(DOCUMENT_TEST_FAILURE_MESSAGE)
    fake_client = MagicMock()
    latest_version = MagicMock()
    latest_version.number = DOCUMENT_LATEST_VERSION_NUMBER
    fake_client.applications.versions.latest.return_value = latest_version
    fake_client.applications.versions.documents.return_value = fake_documents

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(cli, ["application", "version", "document", "list", "heta", "--format", "json"])

    assert result.exit_code == 1
    payload = json.loads(result.stderr)
    assert payload["error"] == DOCUMENT_ERROR_CODE_FAILED
    assert DOCUMENT_TEST_FAILURE_MESSAGE in payload["message"]


@pytest.mark.unit
def test_cli_application_version_document_describe_json_success(runner: CliRunner, record_property) -> None:
    """`application version document describe --format json` emits a single JSON object."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-02")
    fake_documents = MagicMock()
    fake_documents.details.return_value = _make_document_stub(DOCUMENT_OUTPUT_DESCRIPTION_PDF)
    fake_client = MagicMock()
    fake_client.applications.versions.documents.return_value = fake_documents

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(
            cli,
            [
                "application",
                "version",
                "document",
                "describe",
                "heta:1.0.0",
                DOCUMENT_OUTPUT_DESCRIPTION_PDF,
                "--format",
                "json",
            ],
        )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["name"] == DOCUMENT_OUTPUT_DESCRIPTION_PDF
    assert (
        payload["mime_type"] == "application/pdf"
    )  # NOSONAR python:S1192: standard MIME type literal is clearer than a constant
    assert payload["visibility"] == "public"


@pytest.mark.unit
def test_cli_application_version_document_describe_resolve_not_found_text(runner: CliRunner, record_property) -> None:
    """`describe` exits 2 when the application version cannot be resolved (text format)."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-03")
    fake_client = MagicMock()
    fake_client.applications.versions.latest.return_value = None

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(
            cli,
            ["application", "version", "document", "describe", "heta", DOCUMENT_OUTPUT_DESCRIPTION_PDF],
        )

    assert result.exit_code == 2
    output = normalize_output(result.output)
    assert "Application version 'heta' is unavailable." in output


@pytest.mark.unit
def test_cli_application_version_document_describe_resolve_not_found_json(runner: CliRunner, record_property) -> None:
    """`describe --format json` emits structured error when version cannot be resolved."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-03")
    fake_client = MagicMock()
    fake_client.applications.versions.latest.return_value = None

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(
            cli,
            [
                "application",
                "version",
                "document",
                "describe",
                "heta",
                DOCUMENT_OUTPUT_DESCRIPTION_PDF,
                "--format",
                "json",
            ],
        )

    assert result.exit_code == 2
    payload = json.loads(result.stderr)
    assert payload["error"] == DOCUMENT_ERROR_CODE_NOT_FOUND
    assert "heta" in payload["message"]


@pytest.mark.unit
def test_cli_application_version_document_describe_not_found_json(runner: CliRunner, record_property) -> None:
    """`describe --format json` emits structured error when the document is missing."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-03")
    from aignx.codegen.exceptions import NotFoundException as ApiNotFound

    fake_documents = MagicMock()
    fake_documents.details.side_effect = ApiNotFound(status=404, reason="Not Found")
    fake_client = MagicMock()
    latest_version = MagicMock()
    latest_version.number = DOCUMENT_LATEST_VERSION_NUMBER
    fake_client.applications.versions.latest.return_value = latest_version
    fake_client.applications.versions.documents.return_value = fake_documents

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(
            cli,
            [
                "application",
                "version",
                "document",
                "describe",
                "heta",
                DOCUMENT_MISSING_PDF,
                "--format",
                "json",
            ],
        )

    assert result.exit_code == 2
    payload = json.loads(result.stderr)
    assert payload["error"] == DOCUMENT_ERROR_CODE_NOT_FOUND
    assert DOCUMENT_MISSING_PDF in payload["message"]


@pytest.mark.unit
def test_cli_application_version_document_describe_failed_text(runner: CliRunner, record_property) -> None:
    """`describe` exits 1 with an error message on an unexpected failure (text format)."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-03")
    fake_documents = MagicMock()
    fake_documents.details.side_effect = RuntimeError(DOCUMENT_TEST_FAILURE_MESSAGE)
    fake_client = MagicMock()
    latest_version = MagicMock()
    latest_version.number = DOCUMENT_LATEST_VERSION_NUMBER
    fake_client.applications.versions.latest.return_value = latest_version
    fake_client.applications.versions.documents.return_value = fake_documents

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(
            cli,
            ["application", "version", "document", "describe", "heta", DOCUMENT_OUTPUT_DESCRIPTION_PDF],
        )

    assert result.exit_code == 1
    output = normalize_output(result.output)
    assert "Failed to describe release document" in output
    assert DOCUMENT_TEST_FAILURE_MESSAGE in output


@pytest.mark.unit
def test_cli_application_version_document_describe_failed_json(runner: CliRunner, record_property) -> None:
    """`describe --format json` emits structured error on an unexpected failure."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-03")
    fake_documents = MagicMock()
    fake_documents.details.side_effect = RuntimeError(DOCUMENT_TEST_FAILURE_MESSAGE)
    fake_client = MagicMock()
    latest_version = MagicMock()
    latest_version.number = DOCUMENT_LATEST_VERSION_NUMBER
    fake_client.applications.versions.latest.return_value = latest_version
    fake_client.applications.versions.documents.return_value = fake_documents

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(
            cli,
            [
                "application",
                "version",
                "document",
                "describe",
                "heta",
                DOCUMENT_OUTPUT_DESCRIPTION_PDF,
                "--format",
                "json",
            ],
        )

    assert result.exit_code == 1
    payload = json.loads(result.stderr)
    assert payload["error"] == DOCUMENT_ERROR_CODE_FAILED
    assert DOCUMENT_TEST_FAILURE_MESSAGE in payload["message"]


@pytest.mark.unit
def test_cli_application_version_document_download_resolve_not_found(
    runner: CliRunner, tmp_path: Path, record_property
) -> None:
    """`download` exits 2 when the application version cannot be resolved."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-04")
    fake_client = MagicMock()
    fake_client.applications.versions.latest.return_value = None

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(
            cli,
            [
                "application",
                "version",
                "document",
                "download",
                "heta",
                DOCUMENT_OUTPUT_DESCRIPTION_PDF,
                "--output",
                str(tmp_path),
            ],
        )

    assert result.exit_code == 2
    output = normalize_output(result.output)
    assert "Application version 'heta' is unavailable." in output


@pytest.mark.unit
def test_cli_application_version_document_download_not_found(
    runner: CliRunner, tmp_path: Path, record_property
) -> None:
    """`download` exits 2 with a clear message when the document does not exist."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-04")
    from aignx.codegen.exceptions import NotFoundException as ApiNotFound

    fake_documents = MagicMock()
    fake_documents.download_to_path.side_effect = ApiNotFound(status=404, reason="Not Found")
    fake_client = MagicMock()
    latest_version = MagicMock()
    latest_version.number = DOCUMENT_LATEST_VERSION_NUMBER
    fake_client.applications.versions.latest.return_value = latest_version
    fake_client.applications.versions.documents.return_value = fake_documents

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(
            cli,
            [
                "application",
                "version",
                "document",
                "download",
                "heta",
                DOCUMENT_MISSING_PDF,
                "--output",
                str(tmp_path),
            ],
        )

    assert result.exit_code == 2
    output = normalize_output(result.output)
    assert f"Document '{DOCUMENT_MISSING_PDF}' not found for application version 'heta'." in output


@pytest.mark.unit
def test_cli_application_version_document_download_failed(runner: CliRunner, tmp_path: Path, record_property) -> None:
    """`download` exits 1 with an error message on an unexpected failure."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-05-04")
    fake_documents = MagicMock()
    fake_documents.download_to_path.side_effect = RuntimeError(DOCUMENT_TEST_FAILURE_MESSAGE)
    fake_client = MagicMock()
    latest_version = MagicMock()
    latest_version.number = DOCUMENT_LATEST_VERSION_NUMBER
    fake_client.applications.versions.latest.return_value = latest_version
    fake_client.applications.versions.documents.return_value = fake_documents

    with patch(APPLICATION_CLI_CLIENT_PATCH_TARGET, return_value=fake_client):
        result = runner.invoke(
            cli,
            [
                "application",
                "version",
                "document",
                "download",
                "heta",
                DOCUMENT_OUTPUT_DESCRIPTION_PDF,
                "--output",
                str(tmp_path),
            ],
        )

    assert result.exit_code == 1
    output = normalize_output(result.output)
    assert "Failed to download release document" in output
    assert DOCUMENT_TEST_FAILURE_MESSAGE in output
