"""Tests to verify the CLI functionality of the bucket module."""

import json
import os
import uuid
from pathlib import Path

from typer.testing import CliRunner

from aignostics.cli import cli
from tests.conftest import normalize_output

MESSAGE_NOT_YET_IMPLEMENTED = "NOT YET IMPLEMENTED"


def test_cli_bucket_flow(runner: CliRunner, tmpdir) -> None:  # noqa: C901, PLR0912, PLR0915
    """E2E flow testing all bucket CLI commands.

    1. Creates 9 files with 2 sub directories in tmpdir, with total file size of 1MB
    2. Uploads tmpdir to bucket using bucket upload command, prefix is {username}/test/
    3. Executes bucket find command and finds 9 files
    4. Downloads the files in a subdir of tmpdir using the download command, and they match content wise
    5. Check that purge would delete at least 9 files
    6. Deletes the 9 files using the delete command
    7. No longer finds any of the 9 files
    8. Tries to delete a file that does not exist and gets "Object with key '{file}' not found message
    """
    import re

    import psutil

    # Get username for path verification
    the_uuid = str(uuid.uuid4())[:8]  # Use first 8 characters of a random UUID
    username = psutil.Process().username()
    test_prefix = f"{the_uuid}/{username}/test-cli"

    # Step 1: Create test files in the temporary directory
    # Create directories
    dir1 = Path(tmpdir) / "dir1"
    dir2 = Path(tmpdir) / "dir2"
    dir1.mkdir()
    dir2.mkdir()

    # Create 9 files (3 in root, 3 in dir1, 3 in dir2) with total size of ~1MB
    created_files = []

    # Create 3 files in the root directory
    for i in range(1, 4):
        file_path = Path(tmpdir) / f"file{i}.txt"
        # Write approximately 111KB to each file to total ~1MB across 9 files
        file_path.write_bytes(os.urandom(111 * 1024))
        created_files.append(file_path)

    # Create 3 files in dir1
    for i in range(4, 7):
        file_path = dir1 / f"file{i}.txt"
        file_path.write_bytes(os.urandom(111 * 1024))
        created_files.append(file_path)

    # Create 3 files in dir2
    for i in range(7, 10):
        file_path = dir2 / f"file{i}.txt"
        file_path.write_bytes(os.urandom(111 * 1024))
        created_files.append(file_path)

    # Step 2: Upload the directory to bucket
    result = runner.invoke(cli, ["bucket", "upload", str(tmpdir), "--destination-prefix", test_prefix])
    assert result.exit_code == 0
    assert "All files uploaded successfully!" in result.output

    # Step 3: Find the uploaded files
    result = runner.invoke(cli, ["bucket", "find"])
    assert result.exit_code == 0

    # Verify all 9 files are found
    for i in range(1, 10):
        assert f"file{i}.txt" in result.output

    result = runner.invoke(cli, ["bucket", "find", "--detail"])
    assert result.exit_code == 0

    # Verify all 9 files are found
    for i in range(1, 10):
        if i <= 3:
            file_path = f"{test_prefix}/file{i}.txt"
        elif i <= 6:
            file_path = f"{test_prefix}/dir1/file{i}.txt"
        else:
            file_path = f"{test_prefix}/dir2/file{i}.txt"
        assert file_path in result.output.replace("\\\\", "\\")

    # Step 4: Download the files to a subdirectory and verify they match content-wise
    result = runner.invoke(
        cli, ["bucket", "download", test_prefix.replace("\\\\", "\\"), "--destination", tmpdir / "downloaded"]
    )
    assert result.exit_code == 0
    assert "Summary: 9 downloaded, 0 failed, 9 total" in result.output

    # Verify downloaded files match original files content-wise
    for i, original_file in enumerate(created_files, 1):
        # Determine the relative path structure
        if i <= 9:
            downloaded_file = tmpdir / "downloaded" / f"file{i}.txt"
            assert downloaded_file.exists(), f"Downloaded file {downloaded_file} does not exist"
            # Convert LocalPath to bytes for comparison
            original_content = Path(original_file).read_bytes()
            downloaded_content = downloaded_file.read_binary()
            assert original_content == downloaded_content, f"Content mismatch for file{i}.txt"

    # Step 5: Purge dry run
    result = runner.invoke(cli, ["bucket", "purge", "--dry-run"])
    assert result.exit_code == 0
    pattern = r"Would purge bucket by deleting (\d+) object\(s\)"
    match = re.search(pattern, normalize_output(result.stdout))
    assert match is not None, f"Expected purge message not found in output: {normalize_output(result.stdout)}"
    object_count = int(match.group(1))
    assert object_count > 9, f"Expected more than 9 objects to be purged, but found {object_count}"

    # Step 6: Delete the files one by one
    for i in range(1, 10):
        if i <= 3:
            file_path = f"{test_prefix}/file{i}.txt"
        elif i <= 6:
            file_path = f"{test_prefix}/dir1/file{i}.txt"
        else:
            file_path = f"{test_prefix}/dir2/file{i}.txt"
        result = runner.invoke(cli, ["bucket", "delete", file_path, "--what-is-key", "--no-dry-run"])
        assert result.exit_code == 0
        assert f"Deleted 1 object(s) matching ['{file_path}']" in normalize_output(result.stdout)

    # Step 7: Verify the files are no longer found
    result = runner.invoke(cli, ["bucket", "find"])
    assert result.exit_code == 0
    for i in range(1, 10):
        if i <= 3:
            file_path = f"{test_prefix}/file{i}.txt"
        elif i <= 6:
            file_path = f"{test_prefix}/dir1/file{i}.txt"
        else:
            file_path = f"{test_prefix}/dir2/file{i}.txt"
        assert file_path not in normalize_output(result.stdout).replace("\\\\", "\\")

    # Step 8: Try to delete a file that doesn't exist
    non_existent_file = f"{test_prefix}/file1.txt"
    result = runner.invoke(cli, ["bucket", "delete", non_existent_file, "--what-is-key", "--no-dry-run"])
    assert result.exit_code == 0
    assert f"No objects found matching pattern ['{non_existent_file}']" in normalize_output(result.stdout)


def test_cli_bucket_purge(runner: CliRunner) -> None:
    """Check bucket purge command runs successfully."""
    result = runner.invoke(cli, ["bucket", "purge", "--dry-run"])
    assert result.exit_code == 0


def test_cli_bucket_info_settings(runner: CliRunner) -> None:
    """Check settings in system info with proper defaults."""
    result = runner.invoke(cli, ["system", "info"])
    assert result.exit_code == 0

    # Parse the JSON output
    output_data = json.loads(result.output)

    # Verify the bucket settings defaults
    assert output_data["bucket"]["settings"]["protocol"] == "gs"
    assert output_data["bucket"]["settings"]["region_name"] == "EUROPE-WEST3"
    assert output_data["bucket"]["settings"]["name"].startswith("aignostics-platform")
    assert output_data["bucket"]["settings"]["upload_signed_url_expiration_seconds"] == 7200
    assert output_data["bucket"]["settings"]["download_signed_url_expiration_seconds"] == 604800
    assert output_data["bucket"]["settings"]["hmac_access_key_id"] == "**********"
    assert output_data["bucket"]["settings"]["hmac_secret_access_key"] == "**********"  # noqa: S105
