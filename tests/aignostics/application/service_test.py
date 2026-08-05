"""Tests to verify the service functionality of the application module."""

from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from aignx.codegen.exceptions import ApiException, ForbiddenException
from aignx.codegen.models import SubjectType
from typer.testing import CliRunner

from aignostics.application import Service as ApplicationService
from aignostics.platform import ConcurrencyConflictError, NotFoundException, RunData, RunOutput
from tests.constants_test import (
    HETA_APPLICATION_ID,
    HETA_APPLICATION_VERSION,
    TEST_APPLICATION_VERSION_USE_LATEST_FALLBACK_SKIP,
)


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
    base_time = datetime(2024, 1, 1, tzinfo=UTC)

    run_from_note = MagicMock(spec=RunData)
    run_from_note.run_id = "run-note-123"
    run_from_note.output = RunOutput.FULL
    run_from_note.submitted_at = base_time + timedelta(days=1)

    run_from_tag = MagicMock(spec=RunData)
    run_from_tag.run_id = "run-tag-456"
    run_from_tag.output = RunOutput.FULL
    run_from_tag.submitted_at = base_time + timedelta(days=2)

    run_from_both = MagicMock(spec=RunData)
    run_from_both.run_id = "run-both-789"
    run_from_both.output = RunOutput.FULL
    run_from_both.submitted_at = base_time + timedelta(days=3)

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
    run_from_both.submitted_at = datetime(2024, 1, 1, tzinfo=UTC)

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
    """Test that query parameter respects the limit parameter and returns the newest runs."""
    base_time = datetime(2024, 1, 10, tzinfo=UTC)

    # Note runs are older (days 0..4), tag runs are newer (days 5..9)
    note_runs = []
    for i in range(5):
        run = MagicMock(spec=RunData)
        run.run_id = f"run-note-{i}"
        run.output = RunOutput.FULL
        run.submitted_at = base_time + timedelta(days=i)
        note_runs.append(run)

    tag_runs = []
    for i in range(5):
        run = MagicMock(spec=RunData)
        run.run_id = f"run-tag-{i}"
        run.output = RunOutput.FULL
        run.submitted_at = base_time + timedelta(days=5 + i)
        tag_runs.append(run)

    mock_client = MagicMock()
    mock_runs = MagicMock()
    # API returns newest-first; reverse the lists to simulate that behaviour
    mock_runs.list_data.side_effect = [
        iter(reversed(note_runs)),
        iter(reversed(tag_runs)),
    ]
    mock_client.runs = mock_runs
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    results = service.application_runs(query="test", limit=3)

    # With limit=3 each search stops after 3 items (newest-first).
    # Note search: note-4(day4), note-3(day3), note-2(day2) → stops.
    # Tag search: tag-4(day9), tag-3(day8), tag-2(day7) → stops.
    # After merge+sort+slice: tag-4(9), tag-3(8), tag-2(7) are the 3 newest.
    assert len(results) == 3
    result_ids = {r.run_id for r in results}
    assert result_ids == {"run-tag-2", "run-tag-3", "run-tag-4"}


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_runs_query_tag_search_has_independent_limit(mock_get_client: MagicMock) -> None:
    """Tag search gets its own N-slot budget; a full note search does not starve the tag search."""
    base_time = datetime(2024, 1, 1, tzinfo=UTC)

    # Note search fills its quota of N=3
    note_runs = []
    for i in range(3):
        run = MagicMock(spec=RunData)
        run.run_id = f"run-note-{i}"
        run.output = RunOutput.FULL
        run.submitted_at = base_time + timedelta(days=i)
        note_runs.append(run)

    # Tag search has 3 unique (non-overlapping) newer runs
    tag_runs = []
    for i in range(3):
        run = MagicMock(spec=RunData)
        run.run_id = f"run-tag-{i}"
        run.output = RunOutput.FULL
        run.submitted_at = base_time + timedelta(days=10 + i)
        tag_runs.append(run)

    mock_client = MagicMock()
    mock_runs = MagicMock()
    # API returns newest-first; reverse the lists to simulate that behaviour
    mock_runs.list_data.side_effect = [
        iter(reversed(note_runs)),
        iter(reversed(tag_runs)),
    ]
    mock_client.runs = mock_runs
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    results = service.application_runs(query="test", limit=3)

    # Note search (budget=3): fetches note-2(day2), note-1(day1), note-0(day0) → stops.
    # Tag search (independent budget=3): fetches tag-2(day12), tag-1(day11), tag-0(day10) → stops.
    # After merge+sort+slice: tag-2, tag-1, tag-0 are the 3 newest.
    assert len(results) == 3
    result_ids = {r.run_id for r in results}
    assert result_ids == {"run-tag-0", "run-tag-1", "run-tag-2"}


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_runs_query_sorts_results_by_submitted_at(mock_get_client: MagicMock) -> None:
    """No-limit case: mixed note+tag results are returned newest-first regardless of which search found them."""
    base_time = datetime(2024, 3, 1, tzinfo=UTC)

    run_note = MagicMock(spec=RunData)
    run_note.run_id = "note-recent"
    run_note.output = RunOutput.FULL
    run_note.submitted_at = base_time + timedelta(days=5)

    run_tag_a = MagicMock(spec=RunData)
    run_tag_a.run_id = "tag-middle"
    run_tag_a.output = RunOutput.FULL
    run_tag_a.submitted_at = base_time + timedelta(days=3)

    run_tag_b = MagicMock(spec=RunData)
    run_tag_b.run_id = "tag-oldest"
    run_tag_b.output = RunOutput.FULL
    run_tag_b.submitted_at = base_time + timedelta(days=1)

    mock_client = MagicMock()
    mock_runs = MagicMock()
    mock_runs.list_data.side_effect = [
        iter([run_note]),
        iter([run_tag_a, run_tag_b]),
    ]
    mock_client.runs = mock_runs
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    results = service.application_runs(query="test")

    assert len(results) == 3
    assert results[0].run_id == "note-recent"
    assert results[1].run_id == "tag-middle"
    assert results[2].run_id == "tag-oldest"


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_runs_query_deduplicates_with_independent_budget(mock_get_client: MagicMock) -> None:
    """A run matching both note and tag appears exactly once.

    The duplicate does not consume the tag search's quota — the search continues to find
    the next unique tag-only run.
    """
    base_time = datetime(2024, 4, 1, tzinfo=UTC)

    run_both = MagicMock(spec=RunData)
    run_both.run_id = "run-both"
    run_both.output = RunOutput.FULL
    run_both.submitted_at = base_time + timedelta(days=2)

    run_tag_only = MagicMock(spec=RunData)
    run_tag_only.run_id = "run-tag-only"
    run_tag_only.output = RunOutput.FULL
    run_tag_only.submitted_at = base_time + timedelta(days=1)

    mock_client = MagicMock()
    mock_runs = MagicMock()
    # Tag search sees run_both first (dup, skipped) then run_tag_only (unique)
    mock_runs.list_data.side_effect = [
        iter([run_both]),
        iter([run_both, run_tag_only]),
    ]
    mock_client.runs = mock_runs
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    # limit=1 for tag_runs_dict; the duplicate doesn't consume the slot, so run_tag_only is found
    results = service.application_runs(query="test", limit=1)

    # After merge (run_both + run_tag_only), sort, slice to 1 → newest wins (run_both, day 2)
    assert len(results) == 1
    assert results[0].run_id == "run-both"

    # With limit=2: both should appear, confirming tag search found run_tag_only
    mock_runs.list_data.side_effect = [
        iter([run_both]),
        iter([run_both, run_tag_only]),
    ]
    results_limit2 = ApplicationService().application_runs(query="test", limit=2)
    result_ids = {r.run_id for r in results_limit2}
    assert result_ids == {"run-both", "run-tag-only"}


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
def test_application_runs_tags_single_generates_equality_jsonpath(mock_get_client: MagicMock) -> None:
    """Test that a single tag generates a JSONPath equality expression instead of like_regex."""
    mock_client = MagicMock()
    mock_runs = MagicMock()
    mock_runs.list_data.return_value = iter([])
    mock_client.runs = mock_runs
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    service.application_runs(tags={"experiment-1"})

    call_kwargs = mock_runs.list_data.call_args[1]
    assert call_kwargs["custom_metadata"] == '$.sdk.tags[*] ? (@ == "experiment-1")'


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_runs_tags_multiple_generates_or_equality_jsonpath(mock_get_client: MagicMock) -> None:
    """Test that multiple tags generate a JSONPath OR equality expression."""
    mock_client = MagicMock()
    mock_runs = MagicMock()
    mock_runs.list_data.return_value = iter([])
    mock_client.runs = mock_runs
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    service.application_runs(tags={"alpha", "beta"})

    call_kwargs = mock_runs.list_data.call_args[1]
    custom_metadata = call_kwargs["custom_metadata"]

    # Tags are from a set so order is not guaranteed
    assert custom_metadata.startswith("$.sdk.tags[*] ? (")
    assert custom_metadata.endswith(")")
    assert '@ == "alpha"' in custom_metadata
    assert '@ == "beta"' in custom_metadata
    assert " || " in custom_metadata


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_runs_tags_escapes_quotes_and_backslashes(mock_get_client: MagicMock) -> None:
    """Test that tag values with quotes and backslashes are properly escaped in JSONPath."""
    mock_client = MagicMock()
    mock_runs = MagicMock()
    mock_runs.list_data.return_value = iter([])
    mock_client.runs = mock_runs
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    service.application_runs(tags={'tag"with"quotes', "path\\to\\dir"})

    call_kwargs = mock_runs.list_data.call_args[1]
    custom_metadata = call_kwargs["custom_metadata"]

    # Backslashes escaped first, then quotes
    assert '@ == "tag\\"with\\"quotes"' in custom_metadata
    assert '@ == "path\\\\to\\\\dir"' in custom_metadata


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
    mock_run.update_custom_metadata.assert_called_once_with(
        custom_metadata, custom_metadata_checksum=None, enrich_sdk_metadata=True
    )


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_update_custom_metadata_forwards_checksum(mock_get_client: MagicMock, record_property) -> None:
    """Test that custom_metadata_checksum is forwarded to the platform layer."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-07-01, SWR-APPLICATION-2-17, SPEC-APPLICATION-SERVICE")
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    custom_metadata = {"key": "value"}

    service.application_run_update_custom_metadata("run-123", custom_metadata, custom_metadata_checksum="abc123")

    mock_run.update_custom_metadata.assert_called_once_with(
        custom_metadata, custom_metadata_checksum="abc123", enrich_sdk_metadata=True
    )


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_update_custom_metadata_forwards_enrich_sdk_metadata_false(
    mock_get_client: MagicMock, record_property
) -> None:
    """Test that enrich_sdk_metadata=False is forwarded to the platform layer."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-07-03, SWR-APPLICATION-2-17, SPEC-APPLICATION-SERVICE")
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    custom_metadata = {"key": "value"}

    service.application_run_update_custom_metadata("run-123", custom_metadata, enrich_sdk_metadata=False)

    mock_run.update_custom_metadata.assert_called_once_with(
        custom_metadata, custom_metadata_checksum=None, enrich_sdk_metadata=False
    )


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_update_custom_metadata_static_forwards_enrich_sdk_metadata(
    mock_get_client: MagicMock, record_property
) -> None:
    """Test that the static wrapper forwards enrich_sdk_metadata."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-07-03, SWR-APPLICATION-2-17, SPEC-APPLICATION-SERVICE")
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    ApplicationService.application_run_update_custom_metadata_static(
        "run-123", {"key": "value"}, enrich_sdk_metadata=False
    )

    mock_run.update_custom_metadata.assert_called_once_with(
        {"key": "value"}, custom_metadata_checksum=None, enrich_sdk_metadata=False
    )


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_update_custom_metadata_static_forwards_checksum(
    mock_get_client: MagicMock, record_property
) -> None:
    """Test that the static wrapper forwards custom_metadata_checksum."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-07-01, SWR-APPLICATION-2-17, SPEC-APPLICATION-SERVICE")
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    ApplicationService.application_run_update_custom_metadata_static(
        "run-123", {"key": "value"}, custom_metadata_checksum="abc123"
    )

    mock_run.update_custom_metadata.assert_called_once_with(
        {"key": "value"}, custom_metadata_checksum="abc123", enrich_sdk_metadata=True
    )


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_update_custom_metadata_concurrency_conflict(
    mock_get_client: MagicMock, record_property
) -> None:
    """Test that a 412 ApiException is mapped to ConcurrencyConflictError."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-07-02, SWR-APPLICATION-2-17, SPEC-APPLICATION-SERVICE")
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_run.update_custom_metadata.side_effect = ApiException(
        status=HTTPStatus.PRECONDITION_FAILED, reason="Precondition Failed"
    )
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    service = ApplicationService()

    with pytest.raises(ConcurrencyConflictError):
        service.application_run_update_custom_metadata("run-123", {"key": "value"}, custom_metadata_checksum="stale")

    # ConcurrencyConflictError is a ValueError subclass, so existing callers keep working.
    with pytest.raises(ValueError):
        service.application_run_update_custom_metadata("run-123", {"key": "value"}, custom_metadata_checksum="stale")


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_update_custom_metadata_non_412_api_exception_unchanged(
    mock_get_client: MagicMock, record_property
) -> None:
    """Test that a non-412 ApiException keeps the pre-existing behavior (RuntimeError)."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-07-02, SWR-APPLICATION-2-17, SPEC-APPLICATION-SERVICE")
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_run.update_custom_metadata.side_effect = ApiException(
        status=HTTPStatus.INTERNAL_SERVER_ERROR, reason="Internal Server Error"
    )
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    service = ApplicationService()

    with pytest.raises(RuntimeError):
        service.application_run_update_custom_metadata("run-123", {"key": "value"})


@pytest.mark.unit
def test_concurrency_conflict_error_is_value_error(record_property) -> None:
    """Test that ConcurrencyConflictError subclasses ValueError."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-07-02, SWR-APPLICATION-2-17, SPEC-APPLICATION-SERVICE")
    assert issubclass(ConcurrencyConflictError, ValueError)


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
    mock_run.update_item_custom_metadata.assert_called_once_with(
        "item-ext-id", custom_metadata, custom_metadata_checksum=None, enrich_sdk_metadata=True
    )


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_update_item_custom_metadata_forwards_enrich_sdk_metadata_false(
    mock_get_client: MagicMock, record_property
) -> None:
    """Test that enrich_sdk_metadata=False is forwarded for item metadata updates."""
    record_property(
        "tested-item-id",
        "TC-APPLICATION-CLI-07-03, TC-APPLICATION-CLI-07-06, SWR-APPLICATION-2-17, SPEC-APPLICATION-SERVICE",
    )
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    service = ApplicationService()
    custom_metadata = {"key": "value"}

    service.application_run_update_item_custom_metadata(
        "run-123", "item-ext-id", custom_metadata, enrich_sdk_metadata=False
    )

    mock_run.update_item_custom_metadata.assert_called_once_with(
        "item-ext-id", custom_metadata, custom_metadata_checksum=None, enrich_sdk_metadata=False
    )


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_update_item_custom_metadata_static_forwards_enrich_sdk_metadata(
    mock_get_client: MagicMock, record_property
) -> None:
    """Test that the item static wrapper forwards enrich_sdk_metadata."""
    record_property(
        "tested-item-id",
        "TC-APPLICATION-CLI-07-03, TC-APPLICATION-CLI-07-06, SWR-APPLICATION-2-17, SPEC-APPLICATION-SERVICE",
    )
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    ApplicationService.application_run_update_item_custom_metadata_static(
        "run-123", "item-ext-id", {"key": "value"}, enrich_sdk_metadata=False
    )

    mock_run.update_item_custom_metadata.assert_called_once_with(
        "item-ext-id", {"key": "value"}, custom_metadata_checksum=None, enrich_sdk_metadata=False
    )


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_update_item_custom_metadata_concurrency_conflict(
    mock_get_client: MagicMock, record_property
) -> None:
    """Test that a 412 ApiException for an item update is mapped to ConcurrencyConflictError."""
    record_property(
        "tested-item-id",
        "TC-APPLICATION-CLI-07-02, TC-APPLICATION-CLI-07-06, SWR-APPLICATION-2-17, SPEC-APPLICATION-SERVICE",
    )
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_run.update_item_custom_metadata.side_effect = ApiException(
        status=HTTPStatus.PRECONDITION_FAILED, reason="Precondition Failed"
    )
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    service = ApplicationService()

    with pytest.raises(ConcurrencyConflictError):
        service.application_run_update_item_custom_metadata(
            "run-123", "item-ext-id", {"key": "value"}, custom_metadata_checksum="stale"
        )


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


# ─────────────────────────────────────────────────────────────────────────────
# run sharing service methods
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_organization_grants_success(mock_get_client: MagicMock, record_property: object) -> None:
    """organization_grants delegates to Run.list_share_grants with org filter."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-06-02")
    mock_grant = MagicMock()
    mock_run = MagicMock()
    mock_run.list_share_grants.return_value = iter([mock_grant])
    mock_client = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    result = list(ApplicationService().application_run_organization_grants("run-123"))

    assert result == [mock_grant]
    mock_client.run.assert_called_once_with("run-123")
    mock_run.list_share_grants.assert_called_once()
    call_kwargs = mock_run.list_share_grants.call_args.kwargs
    assert call_kwargs.get("subject_type") is not None
    assert call_kwargs.get("relation") is not None
    assert call_kwargs.get("page_size") == 100


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_organization_grants_not_found(mock_get_client: MagicMock, record_property: object) -> None:
    """organization_grants re-raises NotFoundException."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-06-02")
    mock_run = MagicMock()
    mock_run.list_share_grants.side_effect = NotFoundException("not found")
    mock_client = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    with pytest.raises(NotFoundException, match="not found"):
        list(ApplicationService().application_run_organization_grants("run-123"))


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_organization_grants_error(mock_get_client: MagicMock, record_property: object) -> None:
    """organization_grants wraps unexpected errors in RuntimeError."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-06-02")
    mock_run = MagicMock()
    mock_run.list_share_grants.side_effect = RuntimeError("boom")
    mock_client = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    with pytest.raises(RuntimeError, match="boom"):
        list(ApplicationService().application_run_organization_grants("run-123"))


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_share_tokens_success(mock_get_client: MagicMock, record_property: object) -> None:
    """share_tokens returns only tokens whose grant is still active for the run."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-06-05")
    mock_token = MagicMock()
    mock_token.share_token_id = "token-1"  # noqa: S105

    mock_grant = MagicMock()
    mock_grant.subject_id = "token-1"

    mock_run = MagicMock()
    mock_run.list_share_grants.return_value = iter([mock_grant])

    mock_client = MagicMock()
    mock_client.run.return_value = mock_run
    mock_client.share_tokens.list.return_value = iter([mock_token])
    mock_get_client.return_value = mock_client

    result = list(ApplicationService().application_run_share_tokens("run-123"))

    assert result == [mock_token]
    mock_client.run.assert_called_once_with("run-123")
    mock_client.share_tokens.list.assert_called_once_with(run_id="run-123", page_size=100)
    mock_run.list_share_grants.assert_called_once_with(
        subject_type=SubjectType.SHARE_TOKEN, page_size=100, nocache=True
    )


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_share_tokens_not_found(mock_get_client: MagicMock, record_property: object) -> None:
    """share_tokens re-raises NotFoundException."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-06-05")
    mock_client = MagicMock()
    mock_client.share_tokens.list.side_effect = NotFoundException("not found")
    mock_get_client.return_value = mock_client

    with pytest.raises(NotFoundException, match="not found"):
        list(ApplicationService().application_run_share_tokens("run-123"))


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_share_with_organization_explicit_org(
    mock_get_client: MagicMock, record_property: object
) -> None:
    """share_with_organization calls grant_access with the given org_id."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-06-01")
    mock_grant = MagicMock()
    mock_run = MagicMock()
    mock_run.grant_access.return_value = mock_grant
    mock_client = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    result = ApplicationService().application_run_share_with_organization("run-123", organization_id="org-abc")

    assert result is mock_grant
    mock_client.me.assert_not_called()
    mock_run.grant_access.assert_called_once()


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_share_with_organization_defaults_to_own_org(
    mock_get_client: MagicMock, record_property: object
) -> None:
    """share_with_organization fetches own org_id when none is provided."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-06-01")
    mock_grant = MagicMock()
    mock_run = MagicMock()
    mock_run.grant_access.return_value = mock_grant
    mock_me = MagicMock()
    mock_me.organization.id = "own-org"
    mock_client = MagicMock()
    mock_client.run.return_value = mock_run
    mock_client.me.return_value = mock_me
    mock_get_client.return_value = mock_client

    result = ApplicationService().application_run_share_with_organization("run-123", organization_id=None)

    assert result is mock_grant
    mock_client.me.assert_called_once()


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_share_with_organization_not_found(mock_get_client: MagicMock, record_property: object) -> None:
    """share_with_organization re-raises NotFoundException."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-06-01")
    mock_run = MagicMock()
    mock_run.grant_access.side_effect = NotFoundException("not found")
    mock_client = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    with pytest.raises(NotFoundException, match="not found"):
        ApplicationService().application_run_share_with_organization("run-123", organization_id="org-abc")


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_unshare_with_organization_revokes_grants(
    mock_get_client: MagicMock, record_property: object
) -> None:
    """unshare_with_organization revokes all matching grants."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-06-03")
    mock_grant = MagicMock()
    mock_run = MagicMock()
    mock_run.list_share_grants.return_value = iter([mock_grant])
    mock_me = MagicMock()
    mock_me.organization.id = "own-org"
    mock_client = MagicMock()
    mock_client.run.return_value = mock_run
    mock_client.me.return_value = mock_me
    mock_get_client.return_value = mock_client

    ApplicationService().application_run_unshare_with_organization("run-123", organization_id=None)

    mock_grant.revoke.assert_called_once()


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_unshare_with_organization_not_found(
    mock_get_client: MagicMock, record_property: object
) -> None:
    """unshare_with_organization re-raises NotFoundException."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-06-03")
    mock_run = MagicMock()
    mock_run.list_share_grants.side_effect = NotFoundException("not found")
    mock_client = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    with pytest.raises(NotFoundException, match="not found"):
        ApplicationService().application_run_unshare_with_organization("run-123", organization_id="org-abc")


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_create_share_token_success(mock_get_client: MagicMock, record_property: object) -> None:
    """create_share_token creates a token and grants it access to the run."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-06-04")
    mock_token = MagicMock()
    mock_token.share_token_id = "tok-001"  # noqa: S105
    mock_run = MagicMock()
    mock_client = MagicMock()
    mock_client.share_tokens.create.return_value = mock_token
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    result = ApplicationService().application_run_create_share_token("run-123")

    assert result is mock_token
    mock_client.share_tokens.create.assert_called_once_with(expires_at=None)
    mock_run.grant_access.assert_called_once()


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_create_share_token_with_expiry(mock_get_client: MagicMock, record_property: object) -> None:
    """create_share_token passes expiry datetime through to ShareTokens.create."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-06-04")
    mock_token = MagicMock()
    mock_run = MagicMock()
    mock_client = MagicMock()
    mock_client.share_tokens.create.return_value = mock_token
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    expiry = datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC)
    ApplicationService().application_run_create_share_token("run-123", expires_at=expiry)

    mock_client.share_tokens.create.assert_called_once_with(expires_at=expiry)


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_create_share_token_not_found(mock_get_client: MagicMock, record_property: object) -> None:
    """create_share_token re-raises NotFoundException."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-06-04")
    mock_client = MagicMock()
    mock_client.share_tokens.create.side_effect = NotFoundException("not found")
    mock_get_client.return_value = mock_client

    with pytest.raises(NotFoundException, match="not found"):
        ApplicationService().application_run_create_share_token("run-123")


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_revoke_share_token_success(mock_get_client: MagicMock, record_property: object) -> None:
    """revoke_share_token finds the grant on the run and revokes it."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-06-06")
    mock_grant = MagicMock()
    mock_run = MagicMock()
    mock_run.list_share_grants.return_value = iter([mock_grant])
    mock_client = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    ApplicationService().application_run_revoke_share_token("run-123", "tok-001")

    call_kw = mock_run.list_share_grants.call_args.kwargs
    assert call_kw["subject_type"].value == "share_token"
    assert call_kw["subject_id"] == "tok-001"
    mock_grant.revoke.assert_called_once()


@pytest.mark.unit
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_revoke_share_token_not_found(mock_get_client: MagicMock, record_property: object) -> None:
    """revoke_share_token raises NotFoundException when no grant exists for the token."""
    record_property("tested-item-id", "TC-APPLICATION-CLI-06-06")
    mock_run = MagicMock()
    mock_run.list_share_grants.return_value = iter([])
    mock_client = MagicMock()
    mock_client.run.return_value = mock_run
    mock_get_client.return_value = mock_client

    with pytest.raises(NotFoundException, match="No grant found"):
        ApplicationService().application_run_revoke_share_token("run-123", "tok-missing")


@pytest.mark.unit
def test_application_run_download_reraises_forbidden(tmp_path, record_property: object) -> None:
    """A 403 from run.details() propagates as ForbiddenException, not wrapped into RuntimeError.

    Guards the CLI's share-token 'access denied' handler: the download path must not
    swallow ForbiddenException into RuntimeError via its generic ApiException branch.
    """
    record_property("tested-item-id", "PYSDK-145")
    mock_run = MagicMock()
    mock_run.details.side_effect = ForbiddenException(status=403, reason="Forbidden")

    with (
        patch.object(ApplicationService, "application_run", return_value=mock_run),
        pytest.raises(ForbiddenException),
    ):
        ApplicationService().application_run_download("run-id", tmp_path, share_token="s3cr3t")  # noqa: S106


@pytest.mark.unit
@patch("aignostics.application._service.Run.for_run_id")
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_empty_share_token_uses_oauth_path(
    mock_get_client: MagicMock, mock_for_run_id: MagicMock, record_property: object
) -> None:
    """An empty --share-token is normalized to None and takes the normal authenticated path."""
    record_property("tested-item-id", "PYSDK-145")

    ApplicationService().application_run("run-id", share_token="")

    mock_get_client.return_value.run.assert_called_once_with("run-id")
    mock_for_run_id.assert_not_called()


@pytest.mark.unit
@patch("aignostics.application._service.Run.for_run_id")
@patch("aignostics.application._service.Service._get_platform_client")
def test_application_run_with_share_token_uses_share_token_path(
    mock_get_client: MagicMock, mock_for_run_id: MagicMock, record_property: object
) -> None:
    """A non-empty share token takes the Run.for_run_id path and is forwarded verbatim."""
    record_property("tested-item-id", "PYSDK-145")

    ApplicationService().application_run("run-id", share_token="s3cr3t")  # noqa: S106

    mock_for_run_id.assert_called_once_with("run-id", share_token="s3cr3t")  # noqa: S106
    mock_get_client.return_value.run.assert_not_called()
