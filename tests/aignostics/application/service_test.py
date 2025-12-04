"""Tests to verify the service functionality of the application module."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pydicom
import pytest
from typer.testing import CliRunner

from aignostics.application import Service as ApplicationService
from aignostics.application._utils import validate_due_date
from aignostics.platform import NotFoundException, RunData, RunOutput
from tests.constants_test import (
    HETA_APPLICATION_ID,
    HETA_APPLICATION_VERSION,
    TEST_APPLICATION_VERSION_USE_LATEST_FALLBACK_SKIP,
)


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
        future_time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",  # With Z suffix
        future_time.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z",  # With microseconds and Z
        future_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),  # With microseconds and timezone
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
        past_time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
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


@pytest.mark.e2e
def test_application_version_valid_semver_formats(runner: CliRunner) -> None:
    """Test that valid semver formats are accepted."""
    from aignostics.application import Service as ApplicationService

    service = ApplicationService()

    # These should work if the application exists
    valid_formats = [
        "test-app:v1.0.0",
        "test-app:v1.2.3",
        "test-app:v10.20.30",
        "test-app:v1.1.2-prerelease+meta",
        "test-app:v1.1.2+meta",
        "test-app:v1.1.2+meta-valid",
        "test-app:v1.0.0-alpha",
        "test-app:v1.0.0-beta",
        "test-app:v1.0.0-alpha.beta",
        "test-app:v1.0.0-alpha.1",
        "test-app:v1.0.0-alpha0.beta",
        "test-app:v1.0.0-alpha.alpha",
        "test-app:v1.0.0-alpha+metadata",
        "test-app:v1.0.0-rc.1+meta",
    ]

    for version_id in valid_formats:
        try:
            service.application_version(version_id)
        except ValueError as e:
            pytest.fail(f"Valid semver format '{version_id}' was rejected: {e}")
        except NotFoundException:
            pytest.skip(f"Application '{version_id.split(':')[0]}' not found, skipping test for this version format.")


@pytest.mark.unit
def test_application_version_invalid_semver_formats(runner: CliRunner, record_property) -> None:
    """Test that invalid semver formats are rejected with ValueError."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    from aignostics.application import Service as ApplicationService

    service = ApplicationService()

    invalid_application_versions = [
        "test-app:v1.0.0",  # legacy format
        "bla",  # not semver
    ]

    for application_version in invalid_application_versions:
        with pytest.raises(ValueError, match=r"not compliant with semantic versioning"):
            service.application_version("test-app", application_version)


@pytest.mark.e2e
@pytest.mark.skipif(
    TEST_APPLICATION_VERSION_USE_LATEST_FALLBACK_SKIP,
    reason="Skipping test that uses 'latest' application version if so configured for given platform environment.",
)
def test_application_version_use_latest_fallback(runner: CliRunner, record_property) -> None:
    """Test that latest version works and tested."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    service = ApplicationService()

    try:
        app_version = service.application_version(HETA_APPLICATION_ID)
        assert app_version is not None
        assert app_version.version_number == HETA_APPLICATION_VERSION
    except NotFoundException as e:
        if "No versions found for application" in str(e):
            pass  # This is expected behavior
    except ValueError as e:
        pytest.fail(f"Unexpected error: {e}")

    with pytest.raises(ValueError, match=r"not compliant with semantic versioning"):
        service.application_version(HETA_APPLICATION_ID, "invalid-format")


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60 * 2)
def test_application_versions_are_unique(runner: CliRunner) -> None:
    """Check that application versions are unique (currently fails due to backend bug)."""
    # Get all applications
    service = ApplicationService()
    applications = service.applications()

    # Check each application for duplicate versions
    for app in applications:
        versions = service.application_versions(app.application_id)

        # Extract version numbers
        version_numbers = [v.version_number for v in versions]

        # Check for duplicates
        unique_versions = set(version_numbers)
        assert len(version_numbers) == len(unique_versions), (
            f"Application '{app.application_id}' has duplicate versions. "
            f"Found {len(version_numbers)} versions but only {len(unique_versions)} unique: {version_numbers}"
        )


@pytest.mark.unit
def test_application_runs_query_with_note_regex_raises() -> None:
    """Test that using query with note_regex raises ValueError."""
    service = ApplicationService()

    with pytest.raises(ValueError, match=r"Cannot use 'query' parameter together with 'note_regex' parameter"):
        service.application_runs(query="test", note_regex="test.*")


@pytest.mark.unit
def test_application_runs_query_with_tags_raises() -> None:
    """Test that using query with tags raises ValueError."""
    service = ApplicationService()

    with pytest.raises(ValueError, match=r"Cannot use 'query' parameter together with 'tags' parameter"):
        service.application_runs(query="test", tags={"tag1", "tag2"})


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_runs_query_searches_note_and_tags(mock_get_client: MagicMock) -> None:
    """Test that query parameter searches both note and tags with union semantics."""
    # Create mock runs
    run_from_note = MagicMock(spec=RunData)
    run_from_note.run_id = "run-note-123"
    run_from_note.output = RunOutput.FULL

    run_from_tag = MagicMock(spec=RunData)
    run_from_tag.run_id = "run-tag-456"
    run_from_tag.output = RunOutput.FULL

    run_from_both = MagicMock(spec=RunData)
    run_from_both.run_id = "run-both-789"
    run_from_both.output = RunOutput.FULL

    # Mock the platform client to return different runs for note and tag searches
    mock_client = MagicMock()
    mock_runs = MagicMock()

    # First call returns runs matching note, second call returns runs matching tags
    mock_runs.list_data.side_effect = [
        iter([run_from_note, run_from_both]),  # Note search results
        iter([run_from_tag]),  # Tag search results (run_from_both already in note results, so not added)
    ]

    mock_client.runs = mock_runs
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    results = service.application_runs(query="test")

    # Verify we got union of both searches (3 unique runs)
    assert len(results) == 3
    assert run_from_note in results
    assert run_from_tag in results
    assert run_from_both in results

    # Verify that list_data was called twice (once for note, once for tags)
    assert mock_runs.list_data.call_count == 2

    # Verify the custom_metadata parameters contain the escaped query with case insensitive flag
    calls = mock_runs.list_data.call_args_list
    note_call_kwargs = calls[0][1]
    tag_call_kwargs = calls[1][1]

    assert "custom_metadata" in note_call_kwargs
    assert "$.sdk.note" in note_call_kwargs["custom_metadata"]
    assert 'like_regex "test"' in note_call_kwargs["custom_metadata"]
    assert 'flag "i"' in note_call_kwargs["custom_metadata"]

    assert "custom_metadata" in tag_call_kwargs
    assert "$.sdk.tags" in tag_call_kwargs["custom_metadata"]
    assert 'like_regex "test"' in tag_call_kwargs["custom_metadata"]
    assert 'flag "i"' in tag_call_kwargs["custom_metadata"]


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_runs_query_deduplicates_results(mock_get_client: MagicMock) -> None:
    """Test that query parameter deduplicates runs that match both note and tags."""
    # Create mock run that matches both searches
    run_from_both = MagicMock(spec=RunData)
    run_from_both.run_id = "run-both-123"
    run_from_both.output = RunOutput.FULL

    # Mock the platform client to return the same run from both searches
    mock_client = MagicMock()
    mock_runs = MagicMock()

    # Both searches return the same run
    mock_runs.list_data.side_effect = [
        iter([run_from_both]),  # Note search results
        iter([run_from_both]),  # Tag search results (should be deduplicated)
    ]

    mock_client.runs = mock_runs
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    results = service.application_runs(query="test")

    # Verify we only got one run (deduplicated)
    assert len(results) == 1
    assert results[0].run_id == "run-both-123"


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_runs_query_respects_limit(mock_get_client: MagicMock) -> None:
    """Test that query parameter respects the limit parameter."""
    # Create mock runs
    runs = []
    for i in range(10):
        run = MagicMock(spec=RunData)
        run.run_id = f"run-{i}"
        run.output = RunOutput.FULL
        runs.append(run)

    # Mock the platform client to return many runs
    mock_client = MagicMock()
    mock_runs = MagicMock()

    # Note search returns 5 runs, tag search returns 5 runs
    mock_runs.list_data.side_effect = [
        iter(runs[:5]),  # Note search results
        iter(runs[5:]),  # Tag search results
    ]

    mock_client.runs = mock_runs
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    results = service.application_runs(query="test", limit=3)

    # Verify we only got 3 runs despite having 10 total
    assert len(results) == 3


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_runs_query_escapes_special_characters(mock_get_client: MagicMock) -> None:
    """Test that query parameter properly escapes special regex characters."""
    # Mock the platform client
    mock_client = MagicMock()
    mock_runs = MagicMock()
    mock_runs.list_data.side_effect = [
        iter([]),  # Note search results
        iter([]),  # Tag search results
    ]
    mock_client.runs = mock_runs
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    # Use query with special characters that need escaping
    service.application_runs(query='test"value\\path')

    # Verify the custom_metadata parameters contain properly escaped query
    calls = mock_runs.list_data.call_args_list
    note_call_kwargs = calls[0][1]
    tag_call_kwargs = calls[1][1]

    # Check that double quotes and backslashes are properly escaped
    assert 'test\\"value\\\\path' in note_call_kwargs["custom_metadata"]
    assert 'test\\"value\\\\path' in tag_call_kwargs["custom_metadata"]


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_update_custom_metadata_success(mock_get_client: MagicMock) -> None:
    """Test successful update of run custom metadata."""
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    custom_metadata = {"key": "value", "tags": ["tag1", "tag2"]}

    # Should not raise any exception
    service.application_run_update_custom_metadata("run-123", custom_metadata)

    # Verify the run() method was called with correct run_id
    mock_client.run.assert_called_once_with("run-123")
    # Verify the update_custom_metadata method was called with correct arguments
    mock_run.update_custom_metadata.assert_called_once_with(custom_metadata)


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_update_custom_metadata_not_found(mock_get_client: MagicMock) -> None:
    """Test update metadata with non-existent run."""
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_run.update_custom_metadata.side_effect = NotFoundException("Run not found")
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    service = ApplicationService()

    with pytest.raises(NotFoundException, match="not found"):
        service.application_run_update_custom_metadata("invalid-run-id", {"key": "value"})


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_update_item_custom_metadata_success(mock_get_client: MagicMock) -> None:
    """Test successful update of item custom metadata."""
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    custom_metadata = {"key": "value", "note": "test note"}

    # Should not raise any exception
    service.application_run_update_item_custom_metadata("run-123", "item-ext-id", custom_metadata)

    # Verify the run() method was called with correct run_id
    mock_client.run.assert_called_once_with("run-123")
    # Verify the update_item_custom_metadata method was called with correct arguments
    mock_run.update_item_custom_metadata.assert_called_once_with("item-ext-id", custom_metadata)


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_update_item_custom_metadata_not_found(mock_get_client: MagicMock) -> None:
    """Test update item metadata with non-existent run or item."""
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_run.update_item_custom_metadata.side_effect = NotFoundException("Item not found")
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    service = ApplicationService()

    with pytest.raises(NotFoundException, match="not found"):
        service.application_run_update_item_custom_metadata("run-123", "invalid-item-id", {"key": "value"})


@pytest.fixture
def dicom_factory() -> Callable[..., pydicom.Dataset]:
    """Factory fixture for creating DICOM datasets with custom parameters.

    The nested function returns a factory that lets us create multiple DICOMs
    with different parameters in each test (e.g., different pyramid UIDs,
    resolutions, and image types).
    """

    def _create_dicom(
        pyramid_uid: str | None,
        rows: int,
        cols: int,
        sop_class_uid: str = "1.2.840.10008.5.1.4.1.1.77.1.6",  # VL WSI by default
        image_type: list[str] | None = None,
    ) -> pydicom.Dataset:
        """Create a minimal but valid DICOM dataset for WSI.

        Args:
            pyramid_uid: The pyramid UID (None for standalone images)
            rows: Total image rows (TotalPixelMatrixRows) for the full WSI
            cols: Total image columns (TotalPixelMatrixColumns) for the full WSI
            sop_class_uid: SOP Class UID (defaults to VL WSI)
            image_type: Optional ImageType attribute

        Returns:
            A valid pydicom Dataset for whole slide imaging
        """
        ds = pydicom.Dataset()

        # File Meta Information
        ds.file_meta = pydicom.Dataset()
        ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        ds.file_meta.MediaStorageSOPClassUID = sop_class_uid
        ds.file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()

        # Required DICOM attributes
        ds.SOPInstanceUID = pydicom.uid.generate_uid()
        ds.SOPClassUID = sop_class_uid
        ds.StudyInstanceUID = pydicom.uid.generate_uid()
        ds.SeriesInstanceUID = pydicom.uid.generate_uid()
        ds.Modality = "SM"

        # Tile dimensions (typically 256x256 for WSI)
        ds.Rows = 256
        ds.Columns = 256

        # CRITICAL: Total image dimensions for whole slide imaging
        # These represent the full image size and are what differentiate pyramid levels
        ds.TotalPixelMatrixRows = rows
        ds.TotalPixelMatrixColumns = cols

        # Add PyramidUID if provided (optional for standalone images)
        if pyramid_uid:
            ds.PyramidUID = pyramid_uid

        # Add ImageType if provided
        if image_type:
            ds.ImageType = image_type

        return ds

    return _create_dicom


@pytest.mark.unit
def test_select_dicom_pyramid_single_file(
    tmp_path: Path,
    dicom_factory: Callable[..., pydicom.Dataset],
) -> None:
    """Test that single DICOM files with PyramidUID are included."""
    ds = dicom_factory("1.2.3.4.5", 1024, 1024, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file = tmp_path / "test.dcm"
    ds.save_as(dcm_file, write_like_original=False)

    included = ApplicationService._select_dicom_files_to_process(tmp_path)
    assert len(included) == 1
    assert dcm_file in included


@pytest.mark.unit
def test_select_dicom_pyramid_standalone_no_pyramid_uid(
    tmp_path: Path,
    dicom_factory: Callable[..., pydicom.Dataset],
) -> None:
    """Test that standalone DICOM files without PyramidUID are included."""
    ds = dicom_factory(None, 1024, 1024)  # No PyramidUID, no ImageType Value 3
    dcm_file = tmp_path / "test.dcm"
    ds.save_as(dcm_file, write_like_original=False)

    included = ApplicationService._select_dicom_files_to_process(tmp_path)
    assert len(included) == 1
    assert dcm_file in included


@pytest.mark.unit
def test_select_dicom_pyramid_multi_file(tmp_path: Path, dicom_factory: Callable[..., pydicom.Dataset]) -> None:
    """Test that for multi-file DICOM pyramid, only the highest resolution file is kept."""
    pyramid_uid = "1.2.3.4.5"

    # Create low resolution DICOM file (smallest pyramid level)
    ds_low = dicom_factory(pyramid_uid, 512, 512, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file_low = tmp_path / "test_low.dcm"
    ds_low.save_as(dcm_file_low, write_like_original=False)

    # Create medium resolution DICOM file
    ds_med = dicom_factory(pyramid_uid, 1024, 1024, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file_med = tmp_path / "test_med.dcm"
    ds_med.save_as(dcm_file_med, write_like_original=False)

    # Create high resolution DICOM file (base layer - highest resolution)
    ds_high = dicom_factory(pyramid_uid, 2048, 2048, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file_high = tmp_path / "test_high.dcm"
    ds_high.save_as(dcm_file_high, write_like_original=False)

    # Select files to process
    included = ApplicationService._select_dicom_files_to_process(tmp_path)

    # Should include only 1 file (the highest resolution)
    assert len(included) == 1
    assert dcm_file_high in included
    assert dcm_file_low not in included
    assert dcm_file_med not in included


@pytest.mark.unit
def test_select_dicom_pyramid_multiple_pyramids(tmp_path: Path, dicom_factory: Callable[..., pydicom.Dataset]) -> None:
    """Test that files from different pyramids are not filtered against each other."""
    # Pyramid 1 - two files (pyramid with 2 levels)
    ds1_low = dicom_factory("1.2.3.4.5", 512, 512, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file1_low = tmp_path / "pyramid1_low.dcm"
    ds1_low.save_as(dcm_file1_low, write_like_original=False)

    ds1_high = dicom_factory("1.2.3.4.5", 1024, 1024, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file1_high = tmp_path / "pyramid1_high.dcm"
    ds1_high.save_as(dcm_file1_high, write_like_original=False)

    # Pyramid 2 - single file (standalone, single level)
    ds2 = dicom_factory("6.7.8.9.0", 512, 512, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file2 = tmp_path / "pyramid2.dcm"
    ds2.save_as(dcm_file2, write_like_original=False)

    included = ApplicationService._select_dicom_files_to_process(tmp_path)

    # Should include 2 files: highest from pyramid 1 and single from pyramid 2
    assert len(included) == 2
    assert dcm_file1_high in included
    assert dcm_file2 in included
    assert dcm_file1_low not in included


@pytest.mark.unit
def test_select_dicom_exclude_non_wsi(
    tmp_path: Path,
    dicom_factory: Callable[..., pydicom.Dataset],
) -> None:
    """Test that non-WSI DICOM files (e.g., segmentations) are excluded."""
    # Create a segmentation storage DICOM
    ds_seg = dicom_factory(
        "1.2.3.4.5",
        1024,
        1024,
        sop_class_uid="1.2.840.10008.5.1.4.1.1.66.4",  # Segmentation Storage
        image_type=["DERIVED", "PRIMARY", "VOLUME"],
    )
    dcm_file_seg = tmp_path / "segmentation.dcm"
    ds_seg.save_as(dcm_file_seg, write_like_original=False)

    # Create a valid WSI
    ds_wsi = dicom_factory("1.2.3.4.5", 1024, 1024, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file_wsi = tmp_path / "wsi.dcm"
    ds_wsi.save_as(dcm_file_wsi, write_like_original=False)

    included = ApplicationService._select_dicom_files_to_process(tmp_path)

    # Should include only the WSI file
    assert len(included) == 1
    assert dcm_file_wsi in included
    assert dcm_file_seg not in included


@pytest.mark.unit
def test_select_dicom_exclude_non_volumes(
    tmp_path: Path,
    dicom_factory: Callable[..., pydicom.Dataset],
) -> None:
    """Test that non-volume images are excluded."""
    # Create a thumbnail
    ds_thumb = dicom_factory(
        "1.2.3.4.5",
        256,
        256,
        image_type=["DERIVED", "PRIMARY", "THUMBNAIL", "RESAMPLED"],
    )
    dcm_file_thumb = tmp_path / "thumbnail.dcm"
    ds_thumb.save_as(dcm_file_thumb, write_like_original=False)

    # Create a regular WSI image
    ds_wsi = dicom_factory(
        "1.2.3.4.5",
        1024,
        1024,
        image_type=["DERIVED", "PRIMARY", "VOLUME", "NONE"],
    )
    dcm_file_wsi = tmp_path / "wsi.dcm"
    ds_wsi.save_as(dcm_file_wsi, write_like_original=False)

    included = ApplicationService._select_dicom_files_to_process(tmp_path)

    # Should include only the VOLUME image
    assert len(included) == 1
    assert dcm_file_wsi in included
    assert dcm_file_thumb not in included


@pytest.mark.unit
def test_select_dicom_no_image_type_value_3(
    tmp_path: Path,
    dicom_factory: Callable[..., pydicom.Dataset],
) -> None:
    """Test that files without ImageType Value 3 are included as standalone."""
    # Create file with only 2 ImageType values
    ds = dicom_factory("1.2.3.4.5", 1024, 1024, image_type=["DERIVED", "PRIMARY"])
    dcm_file = tmp_path / "no_value3.dcm"
    ds.save_as(dcm_file, write_like_original=False)

    included = ApplicationService._select_dicom_files_to_process(tmp_path)

    # Should include as standalone (no Value 3 to check)
    assert len(included) == 1
    assert dcm_file in included


@pytest.mark.unit
def test_select_dicom_mixed_scenario(
    tmp_path: Path,
    dicom_factory: Callable[..., pydicom.Dataset],
) -> None:
    """Test complex scenario with multiple pyramids, thumbnails, and segmentations."""
    # Pyramid 1: 2 levels (keep highest)
    ds1_low = dicom_factory("pyramid1", 512, 512, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file1_low = tmp_path / "p1_low.dcm"
    ds1_low.save_as(dcm_file1_low, write_like_original=False)

    ds1_high = dicom_factory("pyramid1", 2048, 2048, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file1_high = tmp_path / "p1_high.dcm"
    ds1_high.save_as(dcm_file1_high, write_like_original=False)

    # Thumbnail for pyramid 1 (exclude)
    ds1_thumb = dicom_factory("pyramid1", 256, 256, image_type=["DERIVED", "PRIMARY", "THUMBNAIL"])
    dcm_file1_thumb = tmp_path / "p1_thumb.dcm"
    ds1_thumb.save_as(dcm_file1_thumb, write_like_original=False)

    # Segmentation file (exclude)
    ds_seg = dicom_factory("pyramid1", 2048, 2048, sop_class_uid="1.2.840.10008.5.1.4.1.1.66.4")
    dcm_file_seg = tmp_path / "seg.dcm"
    ds_seg.save_as(dcm_file_seg, write_like_original=False)

    # Standalone WSI without PyramidUID (keep)
    ds_standalone = dicom_factory(None, 1024, 1024, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file_standalone = tmp_path / "standalone.dcm"
    ds_standalone.save_as(dcm_file_standalone, write_like_original=False)

    included = ApplicationService._select_dicom_files_to_process(tmp_path)

    # Should include: high-res from pyramid1, standalone
    assert len(included) == 2
    assert dcm_file1_high in included
    assert dcm_file_standalone in included
    # Should exclude: low-res, thumbnail, segmentation
    assert dcm_file1_low not in included
    assert dcm_file1_thumb not in included
    assert dcm_file_seg not in included
