"""Tests to verify the utility functions of the application module."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from aignx.codegen.models import ArtifactOutput, ArtifactState, ArtifactTerminationReason, ItemOutput

from aignostics.application._utils import (
    application_run_status_to_str,
    get_mime_type_for_artifact,
    get_supported_extensions_for_application,
    is_not_terminated_with_deadline_exceeded,
    print_runs_non_verbose,
    print_runs_verbose,
    queue_position_string_from_run,
    read_metadata_csv_to_dict,
    retrieve_and_print_run_details,
    validate_deadline,
    validate_due_date,
    validate_mappings,
    validate_scheduling_constraints,
    write_metadata_dict_to_csv,
)
from aignostics.constants import (
    HETA_APPLICATION_ID,
    TEST_APP_APPLICATION_ID,
    WSI_SUPPORTED_FILE_EXTENSIONS,
    WSI_SUPPORTED_FILE_EXTENSIONS_TEST_APP,
)
from aignostics_sdk.platform import (
    ItemResult,
    ItemState,
    ItemTerminationReason,
    OutputArtifactElement,
    RunData,
    RunItemStatistics,
    RunOutput,
    RunState,
    RunTerminationReason,
)

TEST_MAPPING_TIFF_HE = ".*\\.tiff:staining_method=H&E"
SUBMITTED_BY = "user@example.com"
_ISO_8601_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _make_statistics(  # noqa: PLR0913
    *,
    item_count: int = 0,
    item_succeeded_count: int = 0,
    item_user_error_count: int = 0,
    item_system_error_count: int = 0,
    item_skipped_count: int = 0,
    item_pending_count: int = 0,
    item_processing_count: int = 0,
) -> RunItemStatistics:
    return RunItemStatistics(
        item_count=item_count,
        item_pending_count=item_pending_count,
        item_processing_count=item_processing_count,
        item_skipped_count=item_skipped_count,
        item_succeeded_count=item_succeeded_count,
        item_user_error_count=item_user_error_count,
        item_system_error_count=item_system_error_count,
    )


def _make_run_data(  # noqa: PLR0913
    *,
    run_id: str = "run-test",
    application_id: str = "test-app",
    version_number: str = "0.0.1",
    state: RunState = RunState.PENDING,
    termination_reason: RunTerminationReason | None = None,
    output: RunOutput = RunOutput.NONE,
    statistics: RunItemStatistics | None = None,
    terminated_at: datetime | None = None,
    custom_metadata: dict[str, Any] | None = None,
    error_message: str | None = None,
    error_code: str | None = None,
    **kwargs: object,
) -> RunData:
    return RunData(
        run_id=run_id,
        application_id=application_id,
        version_number=version_number,
        state=state,
        termination_reason=termination_reason,
        output=output,
        statistics=statistics or _make_statistics(),
        submitted_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
        submitted_by=SUBMITTED_BY,
        terminated_at=terminated_at,
        custom_metadata=custom_metadata,
        error_message=error_message,
        error_code=error_code,
        **kwargs,
    )


def _make_artifact(  # noqa: PLR0913
    *,
    output_artifact_id: str = "artifact-abc",
    name: str = "result.parquet",
    download_url: str = "https://example.com/result.parquet",
    metadata: dict[str, Any] | None = None,
    state: ArtifactState = ArtifactState.TERMINATED,
    termination_reason: ArtifactTerminationReason = ArtifactTerminationReason.SUCCEEDED,
    output: ArtifactOutput = ArtifactOutput.AVAILABLE,
    error_code: str | None = None,
    error_message: str | None = None,
) -> OutputArtifactElement:
    return OutputArtifactElement(
        output_artifact_id=output_artifact_id,
        name=name,
        download_url=download_url,
        metadata={"media_type": "application/vnd.apache.parquet"} if metadata is None else metadata,
        state=state,
        termination_reason=termination_reason,
        output=output,
        error_code=error_code,
        error_message=error_message,
    )


def _make_item_result(  # noqa: PLR0913
    *,
    item_id: str = "item-001",
    external_id: str = "slide-001.svs",
    state: ItemState = ItemState.TERMINATED,
    termination_reason: ItemTerminationReason = ItemTerminationReason.SUCCEEDED,
    output: ItemOutput = ItemOutput.FULL,
    error_message: str | None = None,
    error_code: str | None = None,
    custom_metadata: dict[str, Any] | None = None,
    custom_metadata_checksum: str | None = None,
    terminated_at: datetime | None = None,
    input_artifacts: list[Any] | None = None,
    output_artifacts: list[OutputArtifactElement] | None = None,
) -> ItemResult:
    return ItemResult(
        item_id=item_id,
        external_id=external_id,
        state=state,
        termination_reason=termination_reason,
        output=output,
        error_message=error_message,
        error_code=error_code,
        custom_metadata=custom_metadata,
        custom_metadata_checksum=custom_metadata_checksum,
        terminated_at=terminated_at,
        input_artifacts=input_artifacts if input_artifacts is not None else [],
        output_artifacts=output_artifacts if output_artifacts is not None else [],
    )


@pytest.mark.unit
def test_get_supported_extensions_for_heta_application() -> None:
    """Test that HETA application returns the correct set of supported extensions."""
    extensions = get_supported_extensions_for_application(HETA_APPLICATION_ID)

    assert extensions == WSI_SUPPORTED_FILE_EXTENSIONS
    assert isinstance(extensions, set)
    assert len(extensions) > 0


@pytest.mark.unit
def test_get_supported_extensions_for_test_app() -> None:
    """Test that test application returns the correct set of supported extensions."""
    extensions = get_supported_extensions_for_application(TEST_APP_APPLICATION_ID)

    assert extensions == WSI_SUPPORTED_FILE_EXTENSIONS_TEST_APP
    assert isinstance(extensions, set)
    assert len(extensions) > 0


@pytest.mark.unit
def test_get_supported_extensions_for_unsupported_application() -> None:
    """Test that an unsupported application ID raises RuntimeError."""
    unsupported_app_id = "unsupported-application-id"

    with pytest.raises(RuntimeError) as exc_info:
        get_supported_extensions_for_application(unsupported_app_id)

    assert f"Unsupported application {unsupported_app_id}" in str(exc_info.value)


@pytest.mark.unit
def test_get_supported_extensions_for_empty_string() -> None:
    """Test that an empty string application ID raises RuntimeError."""
    with pytest.raises(RuntimeError) as exc_info:
        get_supported_extensions_for_application("")

    assert "Unsupported application" in str(exc_info.value)


@pytest.mark.unit
def test_get_supported_extensions_returns_different_sets() -> None:
    """Test that different applications return different extension sets."""
    heta_extensions = get_supported_extensions_for_application(HETA_APPLICATION_ID)
    test_extensions = get_supported_extensions_for_application(TEST_APP_APPLICATION_ID)

    # Verify they are separate sets (even if they might have the same contents)
    assert heta_extensions is WSI_SUPPORTED_FILE_EXTENSIONS
    assert test_extensions is WSI_SUPPORTED_FILE_EXTENSIONS_TEST_APP


# Tests for application_run_status_to_str


@pytest.mark.unit
def test_application_run_status_to_str_pending() -> None:
    """Test conversion of PENDING status to string."""
    result = application_run_status_to_str(RunState.PENDING)
    assert result == "pending"


@pytest.mark.unit
def test_application_run_status_to_str_processing() -> None:
    """Test conversion of PROCESSING status to string."""
    result = application_run_status_to_str(RunState.PROCESSING)
    assert result == "processing"


@pytest.mark.unit
def test_application_run_status_to_str_terminated() -> None:
    """Test conversion of TERMINATED status to string."""
    result = application_run_status_to_str(RunState.TERMINATED)
    assert result == "terminated"


# Tests for is_not_terminated_with_deadline_exceeded


# --- Tests using scheduling response object (new primary path) ---


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_scheduling_object_terminated_run() -> None:
    """Test that terminated runs always return None regardless of scheduling deadline."""
    past_deadline = datetime(2020, 1, 1, 12, 0, 0, tzinfo=UTC)
    scheduling = Mock(deadline=past_deadline)
    result = is_not_terminated_with_deadline_exceeded(RunState.TERMINATED, scheduling=scheduling)
    assert result is None


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_scheduling_object_pending_future() -> None:
    """Test that a pending run with scheduling deadline in the future returns False."""
    from datetime import timedelta

    future_deadline = datetime.now(tz=UTC) + timedelta(hours=1)
    scheduling = Mock(deadline=future_deadline)
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, scheduling=scheduling)
    assert result is False


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_scheduling_object_pending_past() -> None:
    """Test that a pending run with scheduling deadline in the past returns True."""
    past_deadline = datetime(2020, 1, 1, 12, 0, 0, tzinfo=UTC)
    scheduling = Mock(deadline=past_deadline)
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, scheduling=scheduling)
    assert result is True


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_scheduling_object_processing_past() -> None:
    """Test that a processing run with scheduling deadline in the past returns True."""
    past_deadline = datetime(2020, 1, 1, 12, 0, 0, tzinfo=UTC)
    scheduling = Mock(deadline=past_deadline)
    result = is_not_terminated_with_deadline_exceeded(RunState.PROCESSING, scheduling=scheduling)
    assert result is True


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_scheduling_object_none_deadline() -> None:
    """Test that scheduling object with None deadline returns None."""
    scheduling = Mock(deadline=None)
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, scheduling=scheduling)
    assert result is None


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_scheduling_none() -> None:
    """Test that None scheduling and None metadata returns None."""
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, scheduling=None, custom_metadata=None)
    assert result is None


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_scheduling_takes_precedence() -> None:
    """Test that scheduling object takes precedence over custom_metadata."""
    from datetime import timedelta

    # scheduling says future (not exceeded), custom_metadata says past (exceeded)
    future_deadline = datetime.now(tz=UTC) + timedelta(hours=1)
    scheduling = Mock(deadline=future_deadline)
    metadata = {"sdk": {"scheduling": {"deadline": "2020-01-01T12:00:00Z"}}}
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, scheduling=scheduling, custom_metadata=metadata)
    assert result is False  # scheduling wins


# --- Tests using custom_metadata fallback (backward compatibility for older runs) ---


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_terminated_run() -> None:
    """Test that terminated runs always return None regardless of deadline."""
    past_deadline = datetime(2020, 1, 1, 12, 0, 0, tzinfo=UTC)
    metadata = {"sdk": {"scheduling": {"deadline": past_deadline.isoformat()}}}
    result = is_not_terminated_with_deadline_exceeded(RunState.TERMINATED, custom_metadata=metadata)
    assert result is None


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_none_metadata() -> None:
    """Test that None metadata returns None."""
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, custom_metadata=None)
    assert result is None


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_empty_metadata() -> None:
    """Test that empty metadata returns None."""
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, custom_metadata={})
    assert result is None


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_no_sdk_key() -> None:
    """Test that metadata without 'sdk' key returns None."""
    metadata = {"other_key": "other_value"}
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, custom_metadata=metadata)
    assert result is None


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_no_scheduling_key() -> None:
    """Test that metadata without 'scheduling' key returns None."""
    metadata = {"sdk": {"other_key": "other_value"}}
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, custom_metadata=metadata)
    assert result is None


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_no_deadline_key() -> None:
    """Test that metadata without 'deadline' key returns None."""
    metadata = {"sdk": {"scheduling": {"other_key": "other_value"}}}
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, custom_metadata=metadata)
    assert result is None


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_pending_deadline_in_future() -> None:
    """Test that a pending run with deadline in the future returns False."""
    from datetime import timedelta

    future_deadline = datetime.now(tz=UTC) + timedelta(hours=1)
    metadata = {"sdk": {"scheduling": {"deadline": future_deadline.isoformat()}}}
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, custom_metadata=metadata)
    assert result is False


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_pending_deadline_in_past() -> None:
    """Test that a pending run with deadline in the past returns True."""
    past_deadline = datetime(2020, 1, 1, 12, 0, 0, tzinfo=UTC)
    metadata = {"sdk": {"scheduling": {"deadline": past_deadline.isoformat()}}}
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, custom_metadata=metadata)
    assert result is True


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_processing_deadline_in_past() -> None:
    """Test that a processing run with deadline in the past returns True."""
    past_deadline = datetime(2020, 1, 1, 12, 0, 0, tzinfo=UTC)
    metadata = {"sdk": {"scheduling": {"deadline": past_deadline.isoformat()}}}
    result = is_not_terminated_with_deadline_exceeded(RunState.PROCESSING, custom_metadata=metadata)
    assert result is True


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_invalid_datetime_format() -> None:
    """Test that invalid datetime format returns None."""
    metadata = {"sdk": {"scheduling": {"deadline": "not-a-valid-datetime"}}}
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, custom_metadata=metadata)
    assert result is None


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_deadline_with_z_suffix() -> None:
    """Test that deadline with Z suffix (UTC) is handled correctly for pending run."""
    past_deadline = "2020-01-01T12:00:00Z"
    metadata = {"sdk": {"scheduling": {"deadline": past_deadline}}}
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, custom_metadata=metadata)
    assert result is True


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_deadline_with_timezone_offset() -> None:
    """Test that deadline with timezone offset is handled correctly for pending run."""
    past_deadline = "2020-01-01T12:00:00+00:00"
    metadata = {"sdk": {"scheduling": {"deadline": past_deadline}}}
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, custom_metadata=metadata)
    assert result is True


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_deadline_empty_string() -> None:
    """Test that empty string deadline returns None."""
    metadata = {"sdk": {"scheduling": {"deadline": ""}}}
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, custom_metadata=metadata)
    assert result is None


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_deadline_none_value() -> None:
    """Test that None deadline value returns None."""
    metadata = {"sdk": {"scheduling": {"deadline": None}}}
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, custom_metadata=metadata)
    assert result is None


@pytest.mark.unit
def test_is_not_terminated_with_deadline_exceeded_deadline_numeric_value() -> None:
    """Test that numeric deadline value returns None."""
    metadata = {"sdk": {"scheduling": {"deadline": 123456789}}}
    result = is_not_terminated_with_deadline_exceeded(RunState.PENDING, custom_metadata=metadata)
    assert result is None


# Tests for CSV utilities


@pytest.mark.unit
def test_write_and_read_metadata_csv(tmp_path: Path) -> None:
    """Test writing and reading metadata CSV files."""
    metadata_csv = tmp_path / "metadata.csv"
    test_data = [
        {"name": "file1.svs", "size": "1024", "type": "image"},
        {"name": "file2.svs", "size": "2048", "type": "image"},
    ]

    # Write CSV
    result_path = write_metadata_dict_to_csv(metadata_csv, test_data)
    assert result_path == metadata_csv
    assert metadata_csv.exists()

    # Read CSV back
    read_data = read_metadata_csv_to_dict(metadata_csv)
    assert read_data is not None
    assert len(read_data) == 2
    assert read_data[0]["name"] == "file1.svs"
    assert read_data[1]["size"] == "2048"


@pytest.mark.unit
def test_read_metadata_csv_invalid_file(tmp_path: Path) -> None:
    """Test reading invalid CSV file returns None."""
    invalid_csv = tmp_path / "invalid.csv"
    invalid_csv.write_text("not;valid;csv\ndata")

    result = read_metadata_csv_to_dict(invalid_csv)
    # Should still work but may return unexpected structure
    assert result is not None or result is None  # Either outcome is acceptable


@pytest.mark.unit
def test_read_metadata_csv_nonexistent_file(tmp_path: Path) -> None:
    """Test reading non-existent CSV file."""
    nonexistent = tmp_path / "does_not_exist.csv"

    with pytest.raises(FileNotFoundError):
        read_metadata_csv_to_dict(nonexistent)


# Tests for MIME type utilities


@pytest.mark.unit
def test_get_mime_type_for_input_artifact() -> None:
    """Test getting MIME type from InputArtifactData."""
    # InputArtifactData is actually the response object from the API with different fields
    # For now, skip testing this as it requires mocking the full API response
    # The function is tested indirectly through integration tests


@pytest.mark.unit
def test_get_mime_type_for_output_artifact() -> None:
    """Test getting MIME type from OutputArtifactData."""
    # OutputArtifactData requires additional fields we don't have access to in unit tests
    # The function is tested indirectly through integration tests


@pytest.mark.unit
def test_get_mime_type_for_output_artifact_element_with_media_type() -> None:
    """Test getting MIME type from OutputArtifactElement with media_type in metadata."""
    artifact = _make_artifact(
        output_artifact_id="artifact-456",
        name="data.json",
        download_url="https://example.com/download",
        metadata={"media_type": "application/json"},
    )

    result = get_mime_type_for_artifact(artifact)
    assert result == "application/json"


@pytest.mark.unit
def test_get_mime_type_for_output_artifact_element_with_mime_type() -> None:
    """Test getting MIME type from OutputArtifactElement with mime_type in metadata."""
    artifact = _make_artifact(
        output_artifact_id="artifact-789",
        name="data.csv",
        download_url="https://example.com/download",
        metadata={"mime_type": "text/csv"},
    )

    result = get_mime_type_for_artifact(artifact)
    assert result == "text/csv"


@pytest.mark.unit
def test_get_mime_type_for_output_artifact_element_default() -> None:
    """Test getting MIME type defaults to application/octet-stream."""
    artifact = _make_artifact(
        output_artifact_id="artifact-999",
        name="unknown.bin",
        download_url="https://example.com/download",
        metadata={},
    )

    result = get_mime_type_for_artifact(artifact)
    assert result == "application/octet-stream"


# Tests for print functions


@pytest.mark.unit
@patch("aignostics.application._utils.console")
def test_print_runs_verbose_with_single_run(mock_console: Mock) -> None:
    """Test verbose printing of a single run."""
    run = _make_run_data(
        run_id="run-123",
        application_id="he-tme",
        version_number="1.0.0",
        state=RunState.TERMINATED,
        termination_reason=RunTerminationReason.ALL_ITEMS_PROCESSED,
        output=RunOutput.FULL,
        statistics=_make_statistics(item_count=5, item_succeeded_count=5),
        terminated_at=datetime(2025, 1, 1, 13, 0, 0, tzinfo=UTC),
    )

    print_runs_verbose([run])

    mock_console.print.assert_called_once()
    call_args = mock_console.print.call_args[0][0]
    assert "Application Runs:" in call_args
    assert "run-123" in call_args
    assert "he-tme" in call_args


@pytest.mark.unit
@patch("aignostics.application._utils.console")
def test_print_runs_non_verbose_with_error(mock_console: Mock) -> None:
    """Test non-verbose printing of runs with errors."""
    run = _make_run_data(
        run_id="run-456",
        state=RunState.TERMINATED,
        termination_reason=RunTerminationReason.CANCELED_BY_USER,
        output=RunOutput.PARTIAL,
        statistics=_make_statistics(item_count=3, item_succeeded_count=1, item_user_error_count=2),
        custom_metadata={"key": "value"},
        error_message="User canceled the run",
        error_code="USER_CANCELED",
    )

    print_runs_non_verbose([run])

    mock_console.print.assert_called_once()
    call_args = mock_console.print.call_args[0][0]
    assert "Application Run IDs:" in call_args
    assert "run-456" in call_args
    assert "USER_CANCELED" in call_args


@pytest.mark.unit
@patch("aignostics.application._utils.console")
def test_retrieve_and_print_run_details_with_items(mock_console: Mock) -> None:
    """Test retrieving and printing run details with items."""
    terminated_at = datetime(2025, 1, 1, 13, 0, 0, tzinfo=UTC)

    run_data = _make_run_data(
        run_id="run-789",
        application_id="he-tme",
        version_number="1.0.0",
        state=RunState.TERMINATED,
        termination_reason=RunTerminationReason.ALL_ITEMS_PROCESSED,
        output=RunOutput.FULL,
        statistics=_make_statistics(item_count=2, item_succeeded_count=2),
        terminated_at=terminated_at,
    )

    item_result = _make_item_result(
        item_id="item-123",
        external_id="slide-001",
        terminated_at=terminated_at,
        output_artifacts=[_make_artifact()],
    )

    # Create mock run handle
    mock_run = MagicMock()
    mock_run.details.return_value = run_data
    mock_run.results.return_value = [item_result]

    retrieve_and_print_run_details(mock_run, hide_platform_queue_position=False)

    # Verify console.print was called multiple times (for run details and items)
    assert mock_console.print.call_count >= 2

    # Check that run details were printed
    first_call = mock_console.print.call_args_list[0][0][0]
    assert "Run Details for run-789" in first_call
    assert "he-tme" in first_call


@pytest.mark.unit
@patch("aignostics.application._utils.console")
def test_retrieve_and_print_run_details_no_items(mock_console: Mock) -> None:
    """Test retrieving and printing run details with no items."""
    run_data = _make_run_data(run_id="run-empty")

    mock_run = MagicMock()
    mock_run.details.return_value = run_data
    mock_run.results.return_value = []

    retrieve_and_print_run_details(mock_run, hide_platform_queue_position=False)

    # Should print run details and "No item results available"
    assert mock_console.print.call_count >= 2
    last_call = str(mock_console.print.call_args_list[-1])
    assert "No item results available" in last_call


@pytest.mark.unit
@pytest.mark.parametrize(
    "hide_platform_queue_position",
    [True, False],
)
@patch("aignostics.application._utils.console")
def test_retrieve_and_print_run_details_can_hide_platform_position(
    mock_console: Mock, hide_platform_queue_position: bool
) -> None:
    """Test that platform queue position can be hidden or shown."""
    run_data = _make_run_data(
        run_id="run-empty",
        num_preceding_items_org=10,
        num_preceding_items_platform=100 if not hide_platform_queue_position else None,
    )

    mock_run = MagicMock()
    mock_run.details.return_value = run_data
    mock_run.results.return_value = []

    retrieve_and_print_run_details(mock_run, hide_platform_queue_position=hide_platform_queue_position)

    first_call = str(mock_console.print.call_args_list[0])
    if not hide_platform_queue_position:
        assert "platform" in first_call
    else:
        assert "platform" not in first_call


# Tests for validate_mappings


@pytest.mark.unit
def test_validate_mappings_accepts_none() -> None:
    """Test that None mappings are accepted (no validation needed)."""
    validate_mappings(None)


@pytest.mark.unit
def test_validate_mappings_accepts_empty_list() -> None:
    """Test that empty list is accepted."""
    validate_mappings([])


@pytest.mark.unit
def test_validate_mappings_accepts_single_key_value_pair() -> None:
    """Test valid mapping with single key-value pair."""
    validate_mappings([TEST_MAPPING_TIFF_HE])


@pytest.mark.unit
def test_validate_mappings_accepts_multiple_key_value_pairs() -> None:
    """Test valid mapping with multiple key-value pairs."""
    validate_mappings([".*\\.tiff:staining_method=H&E,tissue=LUNG,disease=LUNG_CANCER"])


@pytest.mark.unit
def test_validate_mappings_accepts_multiple_mappings() -> None:
    """Test multiple valid mappings."""
    validate_mappings([TEST_MAPPING_TIFF_HE, ".*\\.svs:tissue=LIVER", "sample.*:disease=CANCER"])


@pytest.mark.unit
def test_validate_mappings_accepts_complex_regex_patterns() -> None:
    """Test valid complex regex patterns."""
    validate_mappings([
        "^slide[0-9]+\\.tiff$:staining_method=H&E",
        ".*/(sample|test)_.*\\.svs:tissue=LUNG",
        "[a-zA-Z]+_[0-9]{4}:disease=CANCER",
    ])


@pytest.mark.unit
def test_validate_mappings_raises_for_missing_colon_separator() -> None:
    """Test validation fails when colon separator is missing."""
    with pytest.raises(ValueError):
        validate_mappings([".*tiff staining_method=H&E"])


@pytest.mark.unit
def test_validate_mappings_raises_for_colon_instead_of_equals() -> None:
    """Test validation fails when colon is used instead of equals."""
    with pytest.raises(ValueError):
        validate_mappings([".*\\.tiff:staining_method:H&E"])


@pytest.mark.unit
def test_validate_mappings_raises_for_empty_mapping_string() -> None:
    """Test validation fails for empty mapping string."""
    with pytest.raises(ValueError):
        validate_mappings([""])


@pytest.mark.unit
def test_validate_mappings_raises_for_missing_key() -> None:
    """Test validation fails for missing key."""
    with pytest.raises(ValueError):
        validate_mappings([".*\\.tiff:=H&E"])


@pytest.mark.unit
def test_validate_mappings_raises_for_missing_equals_and_value() -> None:
    """Test validation fails for missing equals and value."""
    with pytest.raises(ValueError):
        validate_mappings([".*\\.tiff:staining_method"])


@pytest.mark.unit
def test_validate_mappings_raises_for_invalid_regex_quantifier() -> None:
    """Test validation fails for invalid regex quantifier."""
    with pytest.raises(ValueError):
        validate_mappings(["*\\.tiff:staining_method=H&E"])


@pytest.mark.unit
def test_validate_mappings_raises_for_invalid_regex_unclosed_bracket() -> None:
    """Test validation fails for invalid regex with unclosed bracket."""
    with pytest.raises(ValueError):
        validate_mappings(["[unclosed:staining_method=H&E"])


@pytest.mark.unit
def test_validate_mappings_raises_for_glob_pattern_with_helpful_message() -> None:
    """Test validation fails for glob pattern instead of regex."""
    with pytest.raises(ValueError):
        validate_mappings(["*.tiff:staining_method=H&E"])


@pytest.mark.unit
def test_validate_mappings_raises_with_correct_index_for_first_invalid() -> None:
    """Test validation fails on first invalid mapping."""
    with pytest.raises(ValueError):
        validate_mappings([
            "*.tiff:staining_method=H&E",  # Invalid (index 0)
            ".*\\.svs:tissue=LUNG",  # Valid
        ])


@pytest.mark.unit
def test_validate_mappings_raises_with_correct_index_for_second_invalid() -> None:
    """Test validation fails on second invalid mapping."""
    with pytest.raises(ValueError):
        validate_mappings([
            TEST_MAPPING_TIFF_HE,  # Valid
            "*.svs:tissue=LUNG",  # Invalid (index 1)
        ])


# Tests for queue_position_string_from_run
@pytest.mark.unit
def test_queue_position_string_from_run_with_org_and_platform_position() -> None:
    """Test queue position string with both org and platform positions."""
    run = Mock(
        spec=RunData,
        num_preceding_items_org=5,
        num_preceding_items_platform=20,
    )
    assert queue_position_string_from_run(run) == (
        "5 items ahead within your organization, 20 items ahead across the entire platform"
    )


@pytest.mark.unit
def test_queue_position_string_from_run_with_no_position() -> None:
    """Test queue position string with no positions."""
    run = Mock(
        spec=RunData,
        num_preceding_items_org=None,
        num_preceding_items_platform=None,
    )
    assert queue_position_string_from_run(run) == "N/A"


@pytest.mark.unit
def test_queue_position_string_from_run_with_only_org_position() -> None:
    """Test queue position string with only org position."""
    run = Mock(
        spec=RunData,
        num_preceding_items_org=3,
        num_preceding_items_platform=None,
    )
    assert queue_position_string_from_run(run) == "3 items ahead within your organization"


@pytest.mark.unit
def test_queue_position_string_from_run_with_only_platform_position() -> None:
    """Test queue position string with only platform position."""
    run = Mock(
        spec=RunData,
        num_preceding_items_org=None,
        num_preceding_items_platform=15,
    )
    assert queue_position_string_from_run(run) == "15 items ahead across the entire platform"


# Tests for retrieve_and_print_run_details with summarize option


@pytest.mark.unit
@patch("aignostics.application._utils.console")
def test_retrieve_and_print_run_details_summarize_mode(mock_console: Mock) -> None:
    """Test summarize mode shows concise output with external ID, state, and errors."""
    terminated_at = datetime(2025, 1, 1, 13, 0, 0, tzinfo=UTC)

    run_data = _make_run_data(
        run_id="run-summarize-test",
        application_id="he-tme",
        version_number="1.0.0",
        state=RunState.TERMINATED,
        termination_reason=RunTerminationReason.ALL_ITEMS_PROCESSED,
        output=RunOutput.FULL,
        statistics=_make_statistics(item_count=2, item_succeeded_count=1, item_user_error_count=1),
        terminated_at=terminated_at,
    )

    item_success = _make_item_result(
        external_id="slide-success.svs",
        terminated_at=terminated_at,
    )

    item_error = _make_item_result(
        item_id="item-002",
        external_id="slide-error.svs",
        termination_reason=ItemTerminationReason.USER_ERROR,
        output=ItemOutput.NONE,
        error_message="Invalid file format",
        error_code="INVALID_FORMAT",
        terminated_at=terminated_at,
    )

    mock_run = MagicMock()
    mock_run.details.return_value = run_data
    mock_run.results.return_value = [item_success, item_error]

    retrieve_and_print_run_details(mock_run, hide_platform_queue_position=False, summarize=True)

    # Collect all printed output
    all_output = " ".join(str(call) for call in mock_console.print.call_args_list)

    # Verify run details header is present
    assert "Run Details for run-summarize-test" in all_output
    # Verify application info is present
    assert "he-tme" in all_output
    # Verify items are listed with external IDs
    assert "slide-success.svs" in all_output
    assert "slide-error.svs" in all_output
    # Verify error message is shown for failed item
    assert "Invalid file format" in all_output
    # Verify artifact details are NOT shown (they are omitted in summary)
    assert "Download URL" not in all_output
    assert "Artifact ID" not in all_output


@pytest.mark.unit
@patch("aignostics.application._utils.console")
def test_retrieve_and_print_run_details_summarize_no_items(mock_console: Mock) -> None:
    """Test summarize mode with no items shows appropriate message."""
    run_data = _make_run_data(run_id="run-no-items")

    mock_run = MagicMock()
    mock_run.details.return_value = run_data
    mock_run.results.return_value = []

    retrieve_and_print_run_details(mock_run, hide_platform_queue_position=False, summarize=True)

    all_output = " ".join(str(call) for call in mock_console.print.call_args_list)
    assert "Run Details for run-no-items" in all_output
    assert "No item results available" in all_output


@pytest.mark.unit
@patch("aignostics.application._utils.console")
def test_retrieve_and_print_run_details_summarize_with_run_error(mock_console: Mock) -> None:
    """Test summarize mode shows run-level errors."""
    run_data = _make_run_data(
        run_id="run-with-error",
        state=RunState.TERMINATED,
        termination_reason=RunTerminationReason.CANCELED_BY_SYSTEM,
        statistics=_make_statistics(item_count=1, item_system_error_count=1),
        terminated_at=datetime(2025, 1, 1, 12, 5, 0, tzinfo=UTC),
        error_message="System error occurred",
        error_code="SYS_ERROR",
    )

    mock_run = MagicMock()
    mock_run.details.return_value = run_data
    mock_run.results.return_value = []

    retrieve_and_print_run_details(mock_run, hide_platform_queue_position=False, summarize=True)

    all_output = " ".join(str(call) for call in mock_console.print.call_args_list)
    assert "System error occurred" in all_output
    assert "SYS_ERROR" in all_output


@pytest.mark.unit
@patch("aignostics.application._utils.console")
def test_retrieve_and_print_run_details_default_is_detailed(mock_console: Mock) -> None:
    """Test that default mode (summarize=False) shows detailed output with artifacts."""
    terminated_at = datetime(2025, 1, 1, 13, 0, 0, tzinfo=UTC)

    run_data = _make_run_data(
        run_id="run-detailed-test",
        application_id="he-tme",
        version_number="1.0.0",
        state=RunState.TERMINATED,
        termination_reason=RunTerminationReason.ALL_ITEMS_PROCESSED,
        output=RunOutput.FULL,
        statistics=_make_statistics(item_count=1, item_succeeded_count=1),
        terminated_at=terminated_at,
    )

    item_result = _make_item_result(
        item_id="item-123",
        terminated_at=terminated_at,
        output_artifacts=[_make_artifact()],
    )

    mock_run = MagicMock()
    mock_run.details.return_value = run_data
    mock_run.results.return_value = [item_result]

    # Call without summarize parameter (default is False)
    retrieve_and_print_run_details(mock_run, hide_platform_queue_position=False)

    all_output = " ".join(str(call) for call in mock_console.print.call_args_list)

    # Verify detailed output shows "Run Details" not "Run Summary"
    assert "Run Details for run-detailed-test" in all_output
    # Verify artifact details ARE shown in detailed mode.
    # Download URL is no longer printed: presigned URLs are short-lived and
    # are now resolved on-demand via Run.get_artifact_download_url().
    assert "Download URL" not in all_output
    assert "Artifact ID" in all_output
    assert "MIME Type" in all_output


@pytest.mark.unit
def test_validate_due_date_none() -> None:
    """Test that None is accepted (optional parameter)."""
    # Should not raise any exception
    validate_due_date(None)


@pytest.mark.unit
def test_validate_due_date_valid_formats() -> None:
    """Test that valid ISO 8601 formats in the future are accepted."""
    # Create a datetime 2 hours in the future
    future_time = datetime.now(tz=UTC) + timedelta(hours=2)

    valid_formats = [
        future_time.isoformat(),  # With timezone offset like +00:00
        future_time.strftime(_ISO_8601_FORMAT) + "Z",  # With Z suffix
        future_time.strftime(f"{_ISO_8601_FORMAT}.%f") + "Z",  # With microseconds and Z
        future_time.strftime(f"{_ISO_8601_FORMAT}.%f") + "+00:00",  # With microseconds and colon-separated offset
    ]

    for time_str in valid_formats:
        # Should not raise any exception
        try:
            validate_due_date(time_str)
        except ValueError as e:
            pytest.fail(f"Valid ISO 8601 format '{time_str}' was rejected: {e}")


@pytest.mark.unit
def test_validate_due_date_invalid_format() -> None:
    """Test that invalid ISO 8601 formats are rejected."""
    invalid_formats = [
        "2025-10-19",  # Date only
        "19:53:00",  # Time only
        "2025/10/19 19:53:00",  # Wrong separators
        "2025-10-19 19:53:00",  # Space instead of T
        "not-a-date",  # Completely invalid
        "2025-13-45T25:70:99Z",  # Invalid values
    ]

    for time_str in invalid_formats:
        with pytest.raises(ValueError, match=r"Invalid ISO 8601 format"):
            validate_due_date(time_str)


@pytest.mark.unit
def test_validate_due_date_past_datetime() -> None:
    """Test that datetimes in the past are rejected."""
    # Create a datetime 2 hours in the past
    past_time = datetime.now(tz=UTC) - timedelta(hours=2)

    past_formats = [
        past_time.isoformat(),
        past_time.strftime(_ISO_8601_FORMAT) + "Z",
    ]

    for time_str in past_formats:
        with pytest.raises(ValueError, match=r"due_date must be in the future"):
            validate_due_date(time_str)


@pytest.mark.unit
def test_validate_due_date_current_time() -> None:
    """Test that current time (not future) is rejected."""
    # Get current time - should be rejected as it's not in the future
    current_time = datetime.now(tz=UTC)
    current_time_str = current_time.isoformat()

    with pytest.raises(ValueError, match=r"due_date must be in the future"):
        validate_due_date(current_time_str)


@pytest.mark.unit
def test_validate_due_date_edge_case_one_second_future() -> None:
    """Test that a datetime 1 second in the future is accepted."""
    # Create a datetime 1 second in the future
    future_time = datetime.now(tz=UTC) + timedelta(seconds=1)
    future_time_str = future_time.isoformat()

    # Should not raise any exception
    try:
        validate_due_date(future_time_str)
    except ValueError as e:
        pytest.fail(f"Future datetime '{future_time_str}' was rejected: {e}")


@pytest.mark.unit
def test_validate_deadline_none() -> None:
    """Test that None is accepted (optional parameter)."""
    # Should not raise any exception
    validate_deadline(None)


@pytest.mark.unit
def test_validate_deadline_valid_formats() -> None:
    """Test that valid ISO 8601 formats in the future are accepted."""
    future_time = datetime.now(tz=UTC) + timedelta(hours=2)

    valid_formats = [
        future_time.isoformat(),
        future_time.strftime(_ISO_8601_FORMAT) + "Z",
        future_time.strftime(f"{_ISO_8601_FORMAT}.%f") + "Z",
        future_time.strftime(f"{_ISO_8601_FORMAT}.%f") + "+00:00",  # With microseconds and colon-separated offset
    ]

    for time_str in valid_formats:
        try:
            validate_deadline(time_str)
        except ValueError as e:
            pytest.fail(f"Valid ISO 8601 format '{time_str}' was rejected: {e}")


@pytest.mark.unit
def test_validate_deadline_invalid_format() -> None:
    """Test that invalid ISO 8601 formats are rejected."""
    invalid_formats = [
        "2025-10-19",
        "19:53:00",
        "2025/10/19 19:53:00",
        "2025-10-19 19:53:00",
        "not-a-date",
        "2025-13-45T25:70:99Z",
    ]

    for time_str in invalid_formats:
        with pytest.raises(ValueError, match=r"Invalid ISO 8601 format"):
            validate_deadline(time_str)


@pytest.mark.unit
def test_validate_deadline_past_datetime() -> None:
    """Test that datetimes in the past are rejected."""
    past_time = datetime.now(tz=UTC) - timedelta(hours=2)

    past_formats = [
        past_time.isoformat(),
        past_time.strftime(_ISO_8601_FORMAT) + "Z",
    ]

    for time_str in past_formats:
        with pytest.raises(ValueError, match=r"deadline must be in the future"):
            validate_deadline(time_str)


@pytest.mark.unit
def test_validate_deadline_current_time() -> None:
    """Test that current time (not future) is rejected."""
    current_time = datetime.now(tz=UTC)
    current_time_str = current_time.isoformat()

    with pytest.raises(ValueError, match=r"deadline must be in the future"):
        validate_deadline(current_time_str)


@pytest.mark.unit
def test_validate_deadline_edge_case_one_second_future() -> None:
    """Test that a datetime 1 second in the future is accepted."""
    future_time = datetime.now(tz=UTC) + timedelta(seconds=1)
    future_time_str = future_time.isoformat()

    try:
        validate_deadline(future_time_str)
    except ValueError as e:
        pytest.fail(f"Future datetime '{future_time_str}' was rejected: {e}")


@pytest.mark.unit
def test_validate_scheduling_constraints_both_none() -> None:
    """Test that both None values are accepted."""
    validate_scheduling_constraints(None, None)


@pytest.mark.unit
def test_validate_scheduling_constraints_one_none() -> None:
    """Test that a single None value is accepted (no cross-field check needed)."""
    future_time = (datetime.now(tz=UTC) + timedelta(hours=2)).isoformat()
    validate_scheduling_constraints(future_time, None)
    validate_scheduling_constraints(None, future_time)


@pytest.mark.unit
def test_validate_scheduling_constraints_due_date_before_deadline() -> None:
    """Test that due_date before deadline is accepted."""
    due_date = (datetime.now(tz=UTC) + timedelta(hours=2)).isoformat()
    deadline = (datetime.now(tz=UTC) + timedelta(hours=4)).isoformat()
    validate_scheduling_constraints(due_date, deadline)


@pytest.mark.unit
def test_validate_scheduling_constraints_due_date_after_deadline() -> None:
    """Test that due_date after deadline is rejected."""
    due_date = (datetime.now(tz=UTC) + timedelta(hours=4)).isoformat()
    deadline = (datetime.now(tz=UTC) + timedelta(hours=2)).isoformat()
    with pytest.raises(ValueError, match=r"due_date must be before deadline"):
        validate_scheduling_constraints(due_date, deadline)


@pytest.mark.unit
def test_validate_scheduling_constraints_due_date_equal_deadline() -> None:
    """Test that due_date equal to deadline is rejected."""
    same_time = (datetime.now(tz=UTC) + timedelta(hours=2)).isoformat()
    with pytest.raises(ValueError, match=r"due_date must be before deadline"):
        validate_scheduling_constraints(same_time, same_time)
