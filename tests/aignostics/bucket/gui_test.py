"""Tests to verify the GUI functionality of the bucket module."""

import os
from asyncio import sleep
from pathlib import Path

import pytest
from nicegui.testing import User
from typer.testing import CliRunner

from aignostics.cli import cli
from aignostics.utils import gui_register_pages


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


async def test_gui_bucket_shows(user: User) -> None:
    """Test that the user sees the dataset page."""
    gui_register_pages()
    await user.open("/bucket")
    await user.should_see("The bucket is securely hosted on Google Cloud in EU")


async def test_gui_bucket_flow(user: User, runner: CliRunner, tmpdir) -> None:
    """E2E flow testing all bucket CLI commands.

    1. Creates 1 file in a subdir of size 100kb
    2. Uploads tmpdir to bucket using bucket upload command, prefix is {username}/test/
    3. Checks the file is there using find comand
    5. Deletes the files using the GUI
    6. Checks the file is no longer there using the find command
    """
    import psutil

    # Step 1: Create file
    username = psutil.Process().username()
    test_prefix = f"{username}/test-gui"
    dir1 = Path(tmpdir) / "dir1"
    dir1.mkdir()
    file_path = dir1 / "file.txt"
    file_path.write_bytes(os.urandom(100 * 1024))

    # Step 2: Upload file
    result = runner.invoke(cli, ["bucket", "upload", str(tmpdir), "--destination-prefix", test_prefix])
    assert result.exit_code == 0
    assert "All files uploaded successfully!" in result.output

    # Step 3: Check the file is there
    result = runner.invoke(cli, ["bucket", "find"])
    assert result.exit_code == 0
    assert f"{test_prefix}/dir1/file.txt" in result.output

    # Step 4: Check the GUI
    gui_register_pages()
    await user.open("/bucket")
    await user.should_see("The bucket is securely hosted on Google Cloud in EU")

    grid = user.find(marker="GRID_BUCKET")
    grid_item = grid.elements.pop()
    # Check if any item in rowData contains the file path in its key
    row_data = grid_item.options["rowData"]
    assert any(f"{test_prefix}/dir1/file.txt" in item.get("key", "") for item in row_data), (
        f"File path not found in grid data: {row_data}"
    )

    # Step 5: Delete the files using GUI
    delete_button = user.find(marker="BUTTON_DELETE_OBJECTS")
    delete_button_item = delete_button.elements.pop()
    assert not delete_button_item.enabled
    delete_button_item.enable()
    assert delete_button_item.enabled

    async def mocked_get_selected_rows():  # noqa: RUF029
        # Need to keep it as async since it's mocking an async method
        return [{"key": f"{test_prefix}/dir1/file.txt"}]

    assert grid_item.get_selected_rows is not None
    grid_item.get_selected_rows = mocked_get_selected_rows

    # Click the delete button to trigger the deletion
    user.find(marker="BUTTON_DELETE_OBJECTS").click()

    # Step 6: Verify file is no longer there
    found = True
    for _ in range(10):
        result = runner.invoke(cli, ["bucket", "find"])
        assert result.exit_code == 0
        found = f"{test_prefix}/dir1/file.txt" in result.output
        if not found:
            break
        await sleep(1)

    assert not found, "File was not deleted successfully"
