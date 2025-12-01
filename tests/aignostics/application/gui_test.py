"""Tests to verify the GUI functionality of the application module."""

import platform
import re
import sys
import tempfile
from asyncio import sleep
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from nicegui.testing import User
from typer.testing import CliRunner

from aignostics.application import Service
from aignostics.application._gui._page_application_run_describe import RESULTS_PAGE_SIZE
from aignostics.cli import cli
from tests.conftest import assert_notified, normalize_output, print_directory_structure
from tests.constants_test import (
    HETA_APPLICATION_ID,
    HETA_APPLICATION_VERSION,
    SPOT_0_EXPECTED_RESULT_FILES,
    SPOT_0_FILENAME,
    SPOT_0_FILESIZE,
    SPOT_0_GS_URL,
)

if TYPE_CHECKING:
    from nicegui import ui


@pytest.mark.e2e
@pytest.mark.skipif(
    platform.system() == "Darwin" and platform.machine() == "arm64" and sys.version_info >= (3, 13),
    reason="GUI tests unstable on macOS Apple Silicon with Python 3.13 (GitHub Actions runner architecture issues)",
)
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
@pytest.mark.skipif(
    platform.system() == "Darwin" and platform.machine() == "arm64" and sys.version_info >= (3, 13),
    reason="GUI tests unstable on macOS Apple Silicon with Python 3.13 (GitHub Actions runner architecture issues)",
)
@pytest.mark.flaky(retries=2, delay=5, only_on=[AssertionError])
@pytest.mark.timeout(timeout=60 * 2)
@pytest.mark.parametrize(
    ("application_id", "application_name", "expected_text"),
    [
        (
            "he-tme",
            "Atlas H&E-TME",
            "The Atlas H&E TME is an AI application",
        ),
        (
            "test-app",
            "test-app",  # TODO(Helmut): Check in with Ari
            "This is the test application with two algorithms",
        ),
    ],
)
async def test_gui_home_to_application(  # noqa: PLR0913, PLR0917
    user: User, application_id: str, application_name: str, expected_text: str, silent_logging: None, record_property
) -> None:
    """Test that the user sees the specific application page with expected content."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE, SPEC-GUI-SERVICE")
    await user.open("/")
    await user.should_see(application_name, retries=100)
    user.find(marker=f"SIDEBAR_APPLICATION:{application_id}").click()
    await user.should_see(expected_text, retries=300)


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
        latest_version_number = application.versions[0].number if application.versions else None
        assert latest_version_number is not None, f"No versions found for application {HETA_APPLICATION_ID}"

        # Submit run
        csv_content = (
            "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
        )
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
                "test_gui_cli_submit_to_run_result_delete",
                "--tags",
                "test_gui_cli_submit_to_run_result_delete",
                "--deadline",
                (datetime.now(tz=UTC) + timedelta(minutes=5)).isoformat(),
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
            f"Run of {application.application_id} ({latest_version_number})",
            retries=100,
        )
        await user.should_see(
            f"Application: {application.application_id} ({latest_version_number})",
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
                    "gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff",
                    str(tmp_path),
                ],
            )
            assert result.exit_code == 0
            assert "Successfully downloaded" in normalize_output(result.stdout)
            assert "9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff" in normalize_output(result.stdout)
            expected_file = Path(tmp_path) / "9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
            assert expected_file.exists(), f"Expected file {expected_file} not found"
            assert expected_file.stat().st_size == 14681750

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
            user.find(marker="BUTTON_APPLICATION_VERSION_NEXT").click()

            # Check the file picker opens and closes
            await user.should_see("Select the folder with the whole slide images you want to analyze then click Next")
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
            time_deadline: ui.time = user.find(marker="TIME_DEADLINE").elements.pop()
            time_deadline.value = (datetime.now().astimezone() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M")

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
@pytest.mark.timeout(timeout=60 * 5)
@pytest.mark.sequential  # Helps on Linux with image analysis step otherwise timing out
async def test_gui_run_download(  # noqa: PLR0915
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

        # Step 3: Select Data
        download_run_button: ui.button = user.find(marker="DIALOG_BUTTON_DOWNLOAD_RUN").elements.pop()
        assert not download_run_button.enabled, "Download button should be disabled before selecting target"
        await user.should_see(marker="BUTTON_DOWNLOAD_DESTINATION_DATA", retries=100)
        user.find(marker="BUTTON_DOWNLOAD_DESTINATION_DATA").click()

        # Step 3: Trigger Download
        await sleep(2)  # Wait a bit for button state to update so we can click
        download_run_button: ui.button = user.find(marker="DIALOG_BUTTON_DOWNLOAD_RUN").elements.pop()
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
        assert len(files_in_results_dir) == 9, (
            f"Expected 9 files in {results_dir}, but found {len(files_in_results_dir)}: "
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


@pytest.mark.integration
@pytest.mark.sequential
@pytest.mark.skipif(
    platform.system() == "Darwin" and platform.machine() == "arm64" and sys.version_info >= (3, 13),
    reason="GUI tests unstable on macOS Apple Silicon with Python 3.13 (GitHub Actions runner architecture issues)",
)
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

    # Find a run with fewer items than RESULTS_PAGE_SIZE
    runs = Service().application_runs(
        application_id=HETA_APPLICATION_ID,
        application_version=HETA_APPLICATION_VERSION,
        has_output=True,
        limit=20,
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
@pytest.mark.skipif(
    platform.system() == "Darwin" and platform.machine() == "arm64" and sys.version_info >= (3, 13),
    reason="GUI tests unstable on macOS Apple Silicon with Python 3.13 (GitHub Actions runner architecture issues)",
)
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
