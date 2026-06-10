"""Tests to verify the GUI functionality of the application module."""

import contextlib
import re
import tempfile
from asyncio import sleep, to_thread
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from aignostics.application import Service
from aignostics.application._gui._page_application_run_describe import (
    RESULTS_PAGE_SIZE,
    _resolve_artifact_url_and_invoke,
    _resolve_artifact_url_or_notify,
)
from aignostics.cli import cli
from nicegui.testing import User
from typer.testing import CliRunner

from aignostics import WSI_SUPPORTED_FILE_EXTENSIONS
from tests.conftest import assert_notified, assert_parquet_geojson_parity, normalize_output, print_directory_structure
from tests.constants_test import (
    HETA_APPLICATION_ID,
    HETA_APPLICATION_VERSION,
    PIPELINE_GPU_TYPE,
    SPOT_0_EXPECTED_RESULT_FILES,
    SPOT_0_FILENAME,
    SPOT_0_FILESIZE,
    SPOT_0_GS_URL,
    SPOT_1_FILENAME,
    SPOT_1_FILESIZE,
    SPOT_1_GS_URL,
)

if TYPE_CHECKING:
    from nicegui import ui


@pytest.mark.e2e
@pytest.mark.flaky(retries=2, delay=5, only_on=[AssertionError])
@pytest.mark.timeout(timeout=30)
async def test_gui_index(user: User, silent_logging, record_property) -> None:
    """Test that the user sees the index page, and sees the intro."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE, SPEC-GUI-SERVICE")
    # hello world
    await user.open("/")
    await user.should_see("Atlas H&E-TME", retries=100)
    await user.should_see("Download Datasets")


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.flaky(retries=2, delay=5, only_on=[AssertionError])
@pytest.mark.timeout(timeout=60 * 5)
@pytest.mark.sequential
async def test_gui_cli_submit_to_run_result_delete(
    user: User,
    runner: CliRunner,
    silent_logging: None,
    record_property,
) -> None:
    """Test that the user can submit a run via the CLI up to deleting the run results."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE, SPEC-GUI-SERVICE")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        application = Service().application(HETA_APPLICATION_ID)

        # Submit run
        csv_content = (
            "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
        )
        csv_content += "platform_bucket_url\n"
        csv_content += ";5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;gs://bucket/test"
        csv_path = tmp_path / "dummy.csv"
        csv_path.write_text(csv_content)
        result = await to_thread(
            runner.invoke,
            cli,
            [
                "application",
                "run",
                "submit",
                HETA_APPLICATION_ID,
                str(csv_path),
                "--application-version",
                HETA_APPLICATION_VERSION,
                "--note",
                "test_gui_cli_submit_to_run_result_delete",
                "--tags",
                "test_gui_cli_submit_to_run_result_delete",
                "--deadline",
                (datetime.now(tz=UTC) + timedelta(minutes=5)).isoformat(),
                "--gpu-type",
                PIPELINE_GPU_TYPE,
            ],
        )
        assert result.exit_code == 0

        # Extract the run ID from the output
        output = normalize_output(result.output)
        # Strip ANSI escape codes before matching
        ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
        output_clean = ansi_escape.sub("", output)
        run_id_match = re.search(r"Submitted run with id '([0-9a-f-]+)' for '", output_clean)
        assert run_id_match is not None, f"Could not extract run ID from output: {output}"
        run_id = run_id_match.group(1)

        # Run shown in he GUI
        await user.open("/")
        await user.should_see("Applications")
        await user.should_see(marker="SIDEBAR_APPLICATION:he-tme", retries=100)
        await user.should_see("Atlas H&E-TME", retries=100)
        await user.should_see("Runs")
        await user.should_see(content=HETA_APPLICATION_ID, marker="LABEL_RUN_APPLICATION:0", retries=250)
        await user.should_see(content=HETA_APPLICATION_VERSION, marker="LABEL_RUN_APPLICATION:0", retries=100)

        # Navigate to the extracted run ID
        await user.open(f"/application/run/{run_id}")
        await user.should_see(
            f"Run of {application.application_id} ({HETA_APPLICATION_VERSION})",
            retries=100,
        )
        await user.should_see(
            f"Application: {application.application_id} ({HETA_APPLICATION_VERSION})",
            retries=100,
        )
        try:
            await user.should_see("PENDING", retries=100)
        except AssertionError:
            await user.should_see("PROCESSING", retries=100)
        await user.should_see("test_gui_cli_submit_to_run_result_delete", retries=100)
        await user.should_see(marker="BUTTON_APPLICATION_RUN_CANCEL")
        user.find(marker="BUTTON_APPLICATION_RUN_CANCEL").click()
        await assert_notified(user, f"Canceling application run with id '{run_id}' ...")
        await assert_notified(user, "Application run cancelled!")

        # Check user sees refreshed run page and run is cancelled
        await user.should_see("CANCELED_BY_USER", retries=100)

        # ... and user can delete run
        await user.should_see(marker="BUTTON_APPLICATION_RUN_RESULT_DELETE", retries=100)

        # Have user delete run
        user.find(marker="BUTTON_APPLICATION_RUN_RESULT_DELETE").click()
        await assert_notified(user, f"Deleting results of application run with id '{run_id}' ...")
        await assert_notified(user, "Application run deleted!")

        # Assert user was auto-navigated to Homepage
        await user.should_see("Welcome", retries=500)


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.flaky(retries=1, delay=5)
@pytest.mark.timeout(timeout=60 * 10)
@pytest.mark.sequential
async def test_gui_download_dataset_via_application_to_run_cancel_to_find_back(  # noqa: PLR0915
    user: User, runner: CliRunner, silent_logging: None, record_property
) -> None:
    """Test that the user can download a dataset via the application page and cancel the run, then find it back."""
    record_property("tested-item-id", "TC-APPLICATION-GUI-04, SPEC-GUI-SERVICE")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        with patch(
            "aignostics.application._gui._page_application_describe.Path.home",
            return_value=tmp_path,
        ):
            # Download example wsi
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
            assert result.exit_code == 0
            assert "Successfully downloaded" in normalize_output(result.stdout)
            assert SPOT_1_FILENAME in normalize_output(result.stdout)
            expected_file = Path(tmp_path) / SPOT_1_FILENAME
            assert expected_file.exists(), f"Expected file {expected_file} not found"
            assert expected_file.stat().st_size == SPOT_1_FILESIZE

            # Open the GUI and navigate to Atlas H&E-TME application
            await user.open("/")
            await user.should_see("Applications")
            await user.should_see("Atlas H&E-TME", retries=100)
            await user.should_see(marker="SIDEBAR_APPLICATION:he-tme", retries=100)
            user.find(marker="SIDEBAR_APPLICATION:he-tme").click()
            await sleep(5)
            await user.should_see("The Atlas H&E TME is an AI application", retries=100)

            # Check the latest application version is shown and select it
            application = Service().application("he-tme")
            latest_application_version = application.versions[0] if application.versions else None
            assert latest_application_version is not None, "No application versions found for he-tme"
            await user.should_see(latest_application_version.number)
            with contextlib.suppress(AssertionError):
                # Click force checkbox if system is unhealthy (checkbox only appears when unhealthy)
                user.find(marker="CHECKBOX_FORCE").click()
            user.find(marker="BUTTON_APPLICATION_VERSION_NEXT").click()

            # Check the file picker opens and closes
            await user.should_see("Select the folder with the whole slide images you want to analyze then click Next")
            await user.should_see(f"Supported formats: {', '.join(sorted(WSI_SUPPORTED_FILE_EXTENSIONS))}")
            user.find(marker="BUTTON_WSI_SELECT_DATA").click()
            await user.should_see("Ok")
            await user.should_see("Cancel")
            user.find(marker="BUTTON_WSI_SELECT_CUSTOM").click()
            await user.should_see("Ok")
            await user.should_see("Cancel")
            user.find(marker="BUTTON_FILEPICKER_CANCEL").click()
            await assert_notified(user, "You did not make a selection")

            # Select the home directory and trigger metadata generation
            user.find(marker="BUTTON_PYTEST_HOME").click()
            await user.should_see(f"Selected folder {tmp_path!s} to analyze.")
            await assert_notified(user, f"You chose directory {tmp_path!s}.")
            user.find(marker="BUTTON_WSI_NEXT").click()
            await assert_notified(user, "Finding WSIs and generating metadata", wait_seconds=5)
            await assert_notified(user, "Found 1 slides for analysis", wait_seconds=120)
            await sleep(10)

            # Generate remaining metadata, going to upload UI
            await user.should_see(
                "The Launchpad has found all compatible slide files in your selected folder.",
                retries=100,
            )

            user.find(marker="BUTTON_PYTEST_META").click()
            await assert_notified(user, "Your metadata is now valid! Feel free to continue to the next step.")
            user.find(marker="BUTTON_METADATA_NEXT").click()
            await assert_notified(user, "Metadata captured.")

            # Navigate through Notes and Tags step
            await user.should_see("Note (optional)", retries=100)
            user.find("TEXTAREA_NOTE").type("test_gui_download_dataset_via_application_to_run_cancel:note").trigger(
                "keydown.enter"
            )

            await user.should_see("Tags (optional, press Enter to add)")
            tags_input: ui.input_chips = user.find(marker="INPUT_TAGS").elements.pop()
            tags_input.value = ["test_gui_tag1", "test_gui_tag2"]

            user.find(marker="BUTTON_NOTES_AND_TAGS_NEXT").click()

            # Navigate through Scheduling step
            await user.should_see("Soft Due Date", retries=100)
            await user.should_see("The platform will try to complete the run before this time", retries=100)

            await user.should_see("Hard Deadline")
            await user.should_see("The platform might cancel the run if not completed by this time.", retries=100)
            time_due_date: ui.time = user.find(marker="TIME_DUE_DATE").elements.pop()
            time_due_date.value = (datetime.now().astimezone() + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
            time_deadline: ui.time = user.find(marker="TIME_DEADLINE").elements.pop()
            time_deadline.value = (datetime.now().astimezone() + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M")

            user.find(marker="BUTTON_SCHEDULING_NEXT").click()
            await assert_notified(user, "Prepared upload UI.")

            # Now on Submission step
            await user.should_see("Upload and submit your 1 slide(s) for analysis.", retries=100)

            # Trigger upload and submission
            await user.should_see(marker="BUTTON_SUBMISSION_UPLOAD")
            button_submission_upload: ui.button = user.find(marker="BUTTON_SUBMISSION_UPLOAD").elements.pop()
            assert button_submission_upload.enabled, "Upload button should be enabled"
            user.find(marker="BUTTON_SUBMISSION_UPLOAD").click()
            await assert_notified(user, "Uploading whole slide images to Aignostics Platform ...", 10)
            button_submission_upload: ui.button = user.find(marker="BUTTON_SUBMISSION_UPLOAD").elements.pop()
            assert not button_submission_upload.enabled, "Upload button should be disabled after click"
            await assert_notified(user, "Upload to Aignostics Platform completed.", wait_seconds=60)
            await assert_notified(user, "Submitting application run ...")
            await assert_notified(user, "Application run submitted with id", wait_seconds=30)

            # Check user is redirected to the run page and run is running
            await sleep(5)
            await user.should_see(f"Run of he-tme ({latest_application_version.number})", retries=200)
            try:
                await user.should_see("PENDING", retries=100)
            except AssertionError:
                await user.should_see("PROCESSING", retries=100)

            code_run_metadata: ui.code = user.find(marker="CODE_RUN_METADATA").elements.pop()
            metadata_text = code_run_metadata.props["content"]
            # extract run id, with metadata text containing Run ID: '{run_data.run_id}'
            run_id_match = re.search(r"Run ID: ([0-9a-f-]+)", metadata_text)
            assert run_id_match is not None, f"Could not extract run ID from metadata: {metadata_text}"
            run_id = run_id_match.group(1)

            # Check user can cancel run
            await user.should_see(marker="BUTTON_APPLICATION_RUN_CANCEL", retries=100)
            user.find(marker="BUTTON_APPLICATION_RUN_CANCEL").click()
            await assert_notified(user, "Canceling application run with id")
            await assert_notified(user, "Application run cancelled!", wait_seconds=20)

            # Check user sees refreshed run page and run is cancelled
            await user.should_see("CANCELED_BY_USER", retries=200)

            # Check the tags were saved correctly
            await user.should_see("test_gui_download_dataset_via_application_to_run_cancel:note", retries=100)
            await user.should_see("test_gui_tag1", retries=100)
            await user.should_see("test_gui_tag2", retries=100)

            # Click on a tag to go to the homagepage with filtered runs
            user.find("test_gui_tag1").click()
            await sleep(10)

            # Check. user is on the homepage and the run filter is set to the tag clicked
            user.should_see("Welcome to the Aignostics Launchpad")
            user.should_see("test_gui_tag1", marker="INPUT_RUNS_FILTER_NOTE_OR_TAGS")

            # Check the first run is the one we created
            user.should_see(marker=f"SIDEBAR_RUN_ITEM:0:{run_id}")


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.flaky(retries=1, delay=5)
@pytest.mark.timeout(timeout=60 * 10)
@pytest.mark.sequential  # Helps on Linux with image analysis step otherwise timing out
async def test_gui_run_download(  # noqa: PLR0914, PLR0915
    user: User, runner: CliRunner, tmp_path: Path, silent_logging: None, record_property
) -> None:
    """Test that the user can download a run result via the GUI."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE, SPEC-GUI-SERVICE")
    with patch(
        "aignostics.application._gui._page_application_run_describe.get_user_data_directory",
        return_value=tmp_path,
    ):
        # Find run
        runs = Service().application_runs(
            application_id=HETA_APPLICATION_ID,
            application_version=HETA_APPLICATION_VERSION,
            external_id=SPOT_0_GS_URL,
            tags=["scheduled"],
            has_output=True,
            limit=1,
        )
        if not runs:
            message = f"No matching runs found for application {HETA_APPLICATION_ID} ({HETA_APPLICATION_VERSION}). "
            message += "This test requires the scheduled test test_application_runs_heta_version passing first."
            pytest.skip(message)

        run_id = runs[0].run_id

        # Explore run
        run = Service().application_run(run_id).details()
        print(
            f"Found existing run: {run.run_id}\n"
            f"application: {run.application_id} ({run.version_number})\n"
            f"status: {run.state}, output: {run.output}\n"
            f"submitted at: {run.submitted_at}, terminated at: {run.terminated_at}\n"
            f"statistics: {run.statistics!r}\n",
            f"custom_metadata: {run.custom_metadata!r}\n",
        )
        # Step 1: Go to latest completed run
        await user.open(f"/application/run/{run.run_id}")
        await user.should_see(f"Run {run.run_id}", retries=100)
        await user.should_see(
            f"Run of {run.application_id} ({run.version_number})",
            retries=100,
        )

        # Step 2: Open Result Download dialog
        await user.should_see(marker="BUTTON_DOWNLOAD_RUN", retries=100)
        user.find(marker="BUTTON_DOWNLOAD_RUN").click()

        # Step 3: Check download button is initially disabled, then select Data folder
        download_run_button: ui.button = user.find(marker="DIALOG_BUTTON_DOWNLOAD_RUN").elements.pop()
        assert not download_run_button.enabled, "Download button should be disabled before selecting target"
        await user.should_see(marker="BUTTON_DOWNLOAD_DESTINATION_DATA", retries=100)
        user.find(marker="BUTTON_DOWNLOAD_DESTINATION_DATA").click()
        await assert_notified(user, "Using Launchpad results directory")

        # Step 4: Trigger Download - wait for button to be enabled
        download_run_button = user.find(marker="DIALOG_BUTTON_DOWNLOAD_RUN").elements.pop()
        assert download_run_button.enabled, "Download button should be enabled after selecting target"
        user.find(marker="DIALOG_BUTTON_DOWNLOAD_RUN").click()
        await assert_notified(user, "Downloading ...")

        # Check: Download completed
        await assert_notified(user, "Download completed.", 60 * 4)
        print_directory_structure(tmp_path, "downloaded_run")

        # Check for directory layout as expected
        run_dir = tmp_path / run.run_id
        assert run_dir.is_dir(), f"Expected run directory {run_dir} not found"

        subdirs = [d for d in run_dir.iterdir() if d.is_dir()]
        assert len(subdirs) == 2, f"Expected two subdirectories in {run_dir}, but found {len(subdirs)}"

        input_dir = run_dir / "input"
        assert input_dir.is_dir(), f"Expected input directory {input_dir} not found"

        results_dir = run_dir / SPOT_0_FILENAME.replace(".tiff", "")
        assert results_dir.is_dir(), f"Expected run results directory {results_dir} not found"

        # Check for input file having been downloaded
        input_file = input_dir / SPOT_0_FILENAME
        assert input_file.exists(), f"Expected input file {input_file} not found"
        assert input_file.stat().st_size == SPOT_0_FILESIZE, (
            f"Expected input file size {SPOT_0_FILESIZE}, but got {input_file.stat().st_size}"
        )

        # Check for files in the results directory
        files_in_results_dir = list(results_dir.glob("*"))
        expected_count = len(SPOT_0_EXPECTED_RESULT_FILES)
        assert len(files_in_results_dir) == expected_count, (
            f"Expected {expected_count} files in {results_dir}, but found {len(files_in_results_dir)}: "
            f"{[f.name for f in files_in_results_dir]}"
        )

        print(f"Found files in {results_dir}:")
        for filename, expected_size, tolerance_percent in SPOT_0_EXPECTED_RESULT_FILES:
            file_path = results_dir / filename
            if file_path.exists():
                actual_size = file_path.stat().st_size
                print(f"  {filename}: {actual_size} bytes (expected: {expected_size} ±{tolerance_percent}%)")
            else:
                print(f"  {filename}: NOT FOUND")
        for filename, expected_size, tolerance_percent in SPOT_0_EXPECTED_RESULT_FILES:
            file_path = results_dir / filename
            assert file_path.exists(), f"Expected file {filename} not found"
            actual_size = file_path.stat().st_size
            min_size = expected_size * (100 - tolerance_percent) // 100
            max_size = expected_size * (100 + tolerance_percent) // 100
            assert min_size <= actual_size <= max_size, (
                f"File size for {filename} ({actual_size} bytes) is outside allowed range "
                f"({min_size} to {max_size} bytes, ±{tolerance_percent}% of {expected_size})"
            )

        # Validate parquet <-> GeoJSON parity: area for segmentation, count for cell classification.
        assert_parquet_geojson_parity(results_dir)


@pytest.mark.integration
@pytest.mark.sequential
@pytest.mark.flaky(retries=2, delay=5, only_on=[AssertionError])
@pytest.mark.timeout(timeout=60)
async def test_gui_run_results_pagination_show_more_button_hidden_when_few_results(
    user: User, silent_logging: None, record_property
) -> None:
    """Test that the 'Show more' button is hidden when there are fewer results than the page size.

    Raises:
        AssertionError: If the button is visible when it shouldn't be.
    """
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE, SPEC-GUI-SERVICE")

    # Find a run with fewer items than RESULTS_PAGE_SIZE.
    # Omit has_output so the server-side filter is applied without client-side pagination:
    # item_count already acts as a proxy (runs with no output show item_count=0 and fail
    # the 0 < item_count <= RESULTS_PAGE_SIZE check below).
    runs = Service().application_runs(
        application_id=HETA_APPLICATION_ID,
        application_version=HETA_APPLICATION_VERSION,
        limit=5,
    )

    # Find a run with few enough items
    run_with_few_items = None
    for run in runs:
        if 0 < run.statistics.item_count <= RESULTS_PAGE_SIZE:
            run_with_few_items = run
            print(f"Found run {run.run_id} with {run.statistics.item_count} items for pagination test.")
            break

    if run_with_few_items is None:
        pytest.skip(
            f"No runs found with 1-{RESULTS_PAGE_SIZE} items for {HETA_APPLICATION_ID} ({HETA_APPLICATION_VERSION})"
        )

    # Navigate to the run page
    await user.open(f"/application/run/{run_with_few_items.run_id}")
    await user.should_see(f"Run {run_with_few_items.run_id}", retries=100)

    # Wait for results to load
    await sleep(3)

    # Verify "Show more" button is NOT visible (element should not exist in DOM)
    await user.should_not_see(marker="BUTTON_SHOW_MORE_RESULTS", retries=10)


@pytest.mark.integration
@pytest.mark.long_running
@pytest.mark.sequential
@pytest.mark.flaky(retries=2, delay=5, only_on=[AssertionError])
@pytest.mark.timeout(timeout=120)
async def test_gui_run_results_pagination_show_more(user: User, silent_logging: None, record_property) -> None:
    """Test pagination 'Show more' button visibility and functionality.

    Verifies:
    1. Button is visible when there are more results than RESULTS_PAGE_SIZE
    2. Button shows correct remaining count
    3. Clicking button loads more results and updates the count
    4. Button is hidden when all results are loaded
    """
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE, SPEC-GUI-SERVICE")

    # Find a run with more items than RESULTS_PAGE_SIZE
    runs = Service().application_runs(
        application_id=HETA_APPLICATION_ID,
        application_version=HETA_APPLICATION_VERSION,
        has_output=True,
        limit=10,
    )

    # Find a run with enough items to test pagination (need at least 2 pages)
    run_with_many_items = None
    for run in runs:
        if run.statistics.item_count > RESULTS_PAGE_SIZE:
            run_with_many_items = run
            print(f"Found run {run.run_id} with {run.statistics.item_count} items for pagination test.")
            break

    if run_with_many_items is None:
        pytest.skip(
            f"No runs found with more than {RESULTS_PAGE_SIZE} items for "
            f"{HETA_APPLICATION_ID} ({HETA_APPLICATION_VERSION})"
        )

    total_items = run_with_many_items.statistics.item_count

    # Navigate to the run page
    await user.open(f"/application/run/{run_with_many_items.run_id}")
    await user.should_see(f"Run {run_with_many_items.run_id}", retries=100)

    # Verify "Show more" button is visible with correct initial count
    await user.should_see(marker="BUTTON_SHOW_MORE_RESULTS", retries=100)
    initial_remaining = total_items - RESULTS_PAGE_SIZE
    await user.should_see(f"Show more ({initial_remaining} remaining)", retries=100)

    # Click "Show more" button
    user.find(marker="BUTTON_SHOW_MORE_RESULTS").click()

    # Wait for loading to complete
    await sleep(5)

    # After loading more, the remaining count should decrease
    new_remaining = total_items - (2 * RESULTS_PAGE_SIZE)
    if new_remaining > 0:
        # Button should still be visible with updated count
        await user.should_see(f"Show more ({new_remaining} remaining)", retries=100)
    else:
        # All items loaded - button should be hidden
        await user.should_not_see(marker="BUTTON_SHOW_MORE_RESULTS", retries=20)


# ---------------------------------------------------------------------------
# _resolve_artifact_url_or_notify — module-level GUI helper
# ---------------------------------------------------------------------------

_PATCH_NICEGUI_RUN_IO_BOUND = "aignostics.application._gui._page_application_run_describe.nicegui_run.io_bound"
_PATCH_UI_NOTIFY = "aignostics.application._gui._page_application_run_describe.ui.notify"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_resolve_artifact_url_or_notify_returns_url_on_success() -> None:
    """Happy path: io_bound succeeds → helper returns the URL, no notify is shown."""
    fake_run = MagicMock()
    fake_button = MagicMock()
    presigned_url = "https://storage.example.com/file?sig=abc"

    with (
        patch(_PATCH_NICEGUI_RUN_IO_BOUND, new_callable=AsyncMock, return_value=presigned_url) as mock_io_bound,
        patch(_PATCH_UI_NOTIFY) as mock_notify,
    ):
        result = await _resolve_artifact_url_or_notify(fake_run, "art-123", fake_button)

    assert result == presigned_url
    mock_io_bound.assert_awaited_once_with(fake_run.get_artifact_download_url, "art-123")
    mock_notify.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_resolve_artifact_url_or_notify_returns_none_and_notifies_on_exception() -> None:
    """Failure path: io_bound raises → helper notifies user with warning, returns None.

    This is the principled-error-handling path for the GUI. Without it, the
    NiceGUI click handler would surface the exception as a dev-console traceback,
    not as a user-friendly notification — and the loading state would stay
    forever stuck on the button.
    """
    fake_run = MagicMock()
    fake_button = MagicMock()

    with (
        patch(
            _PATCH_NICEGUI_RUN_IO_BOUND,
            new_callable=AsyncMock,
            side_effect=RuntimeError("SAMIA returned 503"),
        ) as mock_io_bound,
        patch(_PATCH_UI_NOTIFY) as mock_notify,
    ):
        result = await _resolve_artifact_url_or_notify(fake_run, "art-123", fake_button)

    assert result is None
    mock_io_bound.assert_awaited_once()
    mock_notify.assert_called_once()
    # The notify call carries the failure detail and is a user-friendly warning.
    notify_args, notify_kwargs = mock_notify.call_args
    assert "SAMIA returned 503" in notify_args[0]
    assert notify_kwargs["type"] == "warning"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_resolve_artifact_url_or_notify_toggles_button_loading_state_on_success() -> None:
    """The loading prop must be both added before and removed after a successful resolve.

    A button left in loading state after a successful URL fetch is a classic UI
    bug — the user sees a spinner forever. The ``finally`` block in the helper
    must run on both the success and the exception paths; this test pins the
    success path; the next test pins the exception path.
    """
    fake_run = MagicMock()
    fake_button = MagicMock()

    with (
        patch(_PATCH_NICEGUI_RUN_IO_BOUND, new_callable=AsyncMock, return_value="https://x"),
        patch(_PATCH_UI_NOTIFY),
    ):
        await _resolve_artifact_url_or_notify(fake_run, "art-1", fake_button)

    fake_button.props.assert_any_call(add="loading")
    fake_button.props.assert_any_call(remove="loading")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_resolve_artifact_url_or_notify_toggles_button_loading_state_on_exception() -> None:
    """The loading prop must be removed even when the URL resolve raises."""
    fake_run = MagicMock()
    fake_button = MagicMock()

    with (
        patch(_PATCH_NICEGUI_RUN_IO_BOUND, new_callable=AsyncMock, side_effect=RuntimeError("boom")),
        patch(_PATCH_UI_NOTIFY),
    ):
        await _resolve_artifact_url_or_notify(fake_run, "art-1", fake_button)

    fake_button.props.assert_any_call(add="loading")
    fake_button.props.assert_any_call(remove="loading")


# ---------------------------------------------------------------------------
# _resolve_artifact_url_and_invoke — composition helper used by every per-artifact button
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.asyncio
async def test_resolve_artifact_url_and_invoke_calls_on_success_with_url() -> None:
    """When URL resolution succeeds, on_success is invoked exactly once with the URL.

    This is the composition path used by every per-artifact button in the run
    page (TIFF preview, CSV preview, browser download). Pinning the call shape
    means a future refactor cannot accidentally pass the wrong argument or
    skip the success branch.
    """
    fake_run = MagicMock()
    fake_button = MagicMock()
    on_success = Mock()
    presigned_url = "https://storage.example.com/file?sig=xyz"

    with patch(_PATCH_NICEGUI_RUN_IO_BOUND, new_callable=AsyncMock, return_value=presigned_url):
        await _resolve_artifact_url_and_invoke(fake_run, "art-1", fake_button, on_success)

    on_success.assert_called_once_with(presigned_url)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_resolve_artifact_url_and_invoke_short_circuits_on_resolution_failure() -> None:
    """When URL resolution fails, on_success must NOT be called.

    The user has already been notified via ui.notify by the inner helper;
    invoking on_success with None would either crash (e.g. webbrowser.open(None))
    or open a dialog with no content. Pinning the short-circuit.
    """
    fake_run = MagicMock()
    fake_button = MagicMock()
    on_success = Mock()

    with (
        patch(_PATCH_NICEGUI_RUN_IO_BOUND, new_callable=AsyncMock, side_effect=RuntimeError("nope")),
        patch(_PATCH_UI_NOTIFY),  # notify is called but we don't assert on it here
    ):
        await _resolve_artifact_url_and_invoke(fake_run, "art-1", fake_button, on_success)

    on_success.assert_not_called()
