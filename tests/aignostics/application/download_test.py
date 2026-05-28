"""Tests for download utility functions in the application module."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from aignostics.application._download import (
    download_available_items,
    download_item_artifact,
    download_url_to_file_with_progress,
    extract_filename_from_url,
)
from aignostics.application._models import DownloadProgress, DownloadProgressState
from aignostics_sdk.platform import ArtifactOutput


@pytest.mark.unit
def test_extract_filename_from_url_gs() -> None:
    """Test filename extraction from gs:// URLs."""
    assert extract_filename_from_url("gs://bucket/path/to/file.tiff") == "file.tiff"
    assert extract_filename_from_url("gs://bucket/file.svs") == "file.svs"
    assert extract_filename_from_url("gs://bucket/path/to/folder/image.dcm") == "image.dcm"


@pytest.mark.unit
def test_extract_filename_from_url_https() -> None:
    """Test filename extraction from https:// URLs."""
    assert extract_filename_from_url("https://example.com/slides/sample.svs") == "sample.svs"
    assert extract_filename_from_url("https://example.com/path/to/image.tiff") == "image.tiff"
    # URL with query parameters
    assert extract_filename_from_url("https://example.com/download/file.svs?token=abc123") == "file.svs"


@pytest.mark.unit
def test_extract_filename_from_url_http() -> None:
    """Test filename extraction from http:// URLs."""
    assert extract_filename_from_url("http://example.com/image.tiff") == "image.tiff"
    assert extract_filename_from_url("http://server.com/data/slides/sample.dcm") == "sample.dcm"


@pytest.mark.unit
def test_extract_filename_from_url_edge_cases() -> None:
    """Test filename extraction from URLs with edge cases."""
    # Trailing slash
    assert extract_filename_from_url("https://example.com/folder/") == "folder"
    # Root path
    assert extract_filename_from_url("https://example.com/") == "download"
    # Multiple extensions
    assert extract_filename_from_url("gs://bucket/file.tar.gz") == "file.tar.gz"
    # No extension
    assert extract_filename_from_url("https://example.com/myfile") == "myfile"


@pytest.mark.unit
def test_download_url_to_file_with_progress_gs_url_success(tmp_path: Path) -> None:
    """Test successful download from gs:// URL with progress tracking via callable."""
    gs_url = "gs://test-bucket/path/to/input.tiff"
    signed_url = "https://storage.googleapis.com/signed-url"
    destination = tmp_path / "input.tiff"
    file_content = b"test file content for progress tracking"

    progress = DownloadProgress()
    progress_updates = []

    def progress_callback(p: DownloadProgress) -> None:
        progress_updates.append({
            "status": p.status,
            "input_slide_path": p.input_slide_path,
            "input_slide_url": p.input_slide_url,
            "input_slide_size": p.input_slide_size,
            "input_slide_downloaded_size": p.input_slide_downloaded_size,
            "input_slide_downloaded_chunk_size": p.input_slide_downloaded_chunk_size,
        })

    with patch("aignostics.application._download.generate_signed_url") as mock_generate_signed_url:
        mock_generate_signed_url.return_value = signed_url

        with patch("aignostics.application._download.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.headers = {"content-length": str(len(file_content))}
            mock_response.iter_content = Mock(return_value=[file_content])
            mock_get.return_value = mock_response

            # Call the function with progress tracking
            result = download_url_to_file_with_progress(
                progress, gs_url, destination, download_progress_callable=progress_callback
            )

            # Verify the result
            assert result == destination
            assert destination.exists()
            assert destination.read_bytes() == file_content

            # Verify progress updates
            assert len(progress_updates) >= 3  # Initial, size update, chunk update

            # Check initial update
            assert progress_updates[0]["status"] == DownloadProgressState.DOWNLOADING_INPUT
            assert progress_updates[0]["input_slide_url"] == gs_url
            assert progress_updates[0]["input_slide_path"] == destination
            assert progress_updates[0]["input_slide_size"] is None
            assert progress_updates[0]["input_slide_downloaded_size"] == 0

            # Check size update
            assert progress_updates[1]["input_slide_size"] == len(file_content)

            # Check final chunk update
            assert progress_updates[-1]["input_slide_downloaded_size"] == len(file_content)
            assert progress_updates[-1]["input_slide_downloaded_chunk_size"] == len(file_content)


@pytest.mark.unit
def test_download_url_to_file_with_progress_queue(tmp_path: Path) -> None:
    """Test download with progress tracking via queue."""
    gs_url = "gs://test-bucket/input.tiff"
    signed_url = "https://storage.googleapis.com/signed-url"
    destination = tmp_path / "input.tiff"
    file_content = b"test content"

    progress = DownloadProgress()
    progress_queue = Mock()
    progress_queue.put_nowait = Mock()  # Mock the put_nowait method

    with patch("aignostics.application._download.generate_signed_url") as mock_generate_signed_url:
        mock_generate_signed_url.return_value = signed_url

        with patch("aignostics.application._download.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.headers = {"content-length": str(len(file_content))}
            mock_response.iter_content = Mock(return_value=[file_content])
            mock_get.return_value = mock_response

            # Call with queue
            download_url_to_file_with_progress(progress, gs_url, destination, download_progress_queue=progress_queue)

            # Verify queue was called with progress
            assert progress_queue.put_nowait.call_count >= 3

            # Verify final state
            assert progress.status == DownloadProgressState.DOWNLOADING_INPUT
            assert progress.input_slide_downloaded_size == len(file_content)


@pytest.mark.unit
def test_download_url_to_file_with_progress_chunked(tmp_path: Path) -> None:
    """Test progress tracking with multiple chunks."""
    gs_url = "gs://test-bucket/large-input.tiff"
    signed_url = "https://storage.googleapis.com/signed-url"
    destination = tmp_path / "large-input.tiff"
    chunks = [b"chunk1", b"chunk2", b"chunk3", b"chunk4"]
    total_size = sum(len(c) for c in chunks)

    progress = DownloadProgress()
    progress_updates = []

    def progress_callback(p: DownloadProgress) -> None:
        progress_updates.append(p.input_slide_downloaded_size)

    with patch("aignostics.application._download.generate_signed_url") as mock_generate_signed_url:
        mock_generate_signed_url.return_value = signed_url

        with patch("aignostics.application._download.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.headers = {"content-length": str(total_size)}
            mock_response.iter_content = Mock(return_value=chunks)
            mock_get.return_value = mock_response

            # Call the function
            download_url_to_file_with_progress(
                progress, gs_url, destination, download_progress_callable=progress_callback
            )

            # Verify progressive size updates
            assert progress_updates[0] == 0  # Initial
            assert progress_updates[1] == 0  # After size header
            # Each chunk updates the total
            assert progress_updates[2] == len(chunks[0])
            assert progress_updates[3] == len(chunks[0]) + len(chunks[1])
            assert progress_updates[4] == len(chunks[0]) + len(chunks[1]) + len(chunks[2])
            assert progress_updates[5] == total_size  # Final


@pytest.mark.unit
def test_download_url_to_file_with_progress_http_error(tmp_path: Path) -> None:
    """Test that HTTP errors are wrapped in RuntimeError."""
    gs_url = "gs://test-bucket/missing.tiff"
    signed_url = "https://storage.googleapis.com/signed-url"
    destination = tmp_path / "missing.tiff"

    progress = DownloadProgress()

    with patch("aignostics.application._download.generate_signed_url") as mock_generate_signed_url:
        mock_generate_signed_url.return_value = signed_url

        with patch("aignostics.application._download.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status = Mock(side_effect=requests.HTTPError("404 Not Found"))
            mock_get.return_value = mock_response

            # Verify that RuntimeError is raised (wrapping HTTPError)
            with pytest.raises(RuntimeError, match="HTTP error downloading"):
                download_url_to_file_with_progress(progress, gs_url, destination)

            # Verify file was not created
            assert not destination.exists()


@pytest.mark.unit
def test_download_url_to_file_with_progress_normalized_values(tmp_path: Path) -> None:
    """Test that DownloadProgress computes normalized progress correctly for input slides."""
    gs_url = "gs://test-bucket/input.tiff"
    signed_url = "https://storage.googleapis.com/signed-url"
    destination = tmp_path / "input.tiff"
    file_size = 1000
    chunks = [b"x" * 250, b"x" * 250, b"x" * 250, b"x" * 250]  # 4 chunks of 250 bytes

    progress = DownloadProgress()
    progress.item_count = 5  # 5 items total
    progress.item_index = 2  # Processing 3rd item

    normalized_values = []

    def progress_callback(p: DownloadProgress) -> None:
        # Capture all updates
        normalized_values.append({
            "has_size": p.input_slide_size is not None,
            "downloaded": p.input_slide_downloaded_size,
            "item_progress": p.item_progress_normalized,
            "artifact_progress": p.artifact_progress_normalized,
        })

    with patch("aignostics.application._download.generate_signed_url") as mock_generate_signed_url:
        mock_generate_signed_url.return_value = signed_url

        with patch("aignostics.application._download.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.headers = {"content-length": str(file_size)}
            mock_response.iter_content = Mock(return_value=chunks)
            mock_get.return_value = mock_response

            # Call the function
            download_url_to_file_with_progress(
                progress, gs_url, destination, download_progress_callable=progress_callback
            )

            # Verify we have updates
            assert len(normalized_values) >= 6  # Initial, size, 4 chunks

            # Item progress should always be (item_index + 1) / item_count = 3/5 = 0.6
            for val in normalized_values:
                assert val["item_progress"] == 0.6

            # Find updates with size information (after size header is read)
            sized_updates = [v for v in normalized_values if v["has_size"]]
            assert len(sized_updates) >= 4  # Size update + 4 chunks

            # Verify artifact progress increases correctly
            # First sized update should be at 0% (size just set, no data yet)
            assert sized_updates[0]["artifact_progress"] == 0.0
            assert sized_updates[0]["downloaded"] == 0

            # After first chunk: 250/1000 = 0.25
            assert sized_updates[1]["artifact_progress"] == 0.25
            assert sized_updates[1]["downloaded"] == 250

            # After second chunk: 500/1000 = 0.5
            assert sized_updates[2]["artifact_progress"] == 0.5
            assert sized_updates[2]["downloaded"] == 500

            # After third chunk: 750/1000 = 0.75
            assert sized_updates[3]["artifact_progress"] == 0.75
            assert sized_updates[3]["downloaded"] == 750

            # After fourth chunk: 1000/1000 = 1.0
            assert sized_updates[4]["artifact_progress"] == 1.0
            assert sized_updates[4]["downloaded"] == 1000


@pytest.mark.unit
def test_download_url_to_file_with_progress_https_url_success(tmp_path: Path) -> None:
    """Test successful download from https:// URL (no signed URL generation needed)."""
    https_url = "https://example.com/path/to/input.tiff"
    destination = tmp_path / "input.tiff"
    file_content = b"test file content from https"

    progress = DownloadProgress()
    progress_updates = []

    def progress_callback(p: DownloadProgress) -> None:
        progress_updates.append({
            "status": p.status,
            "input_slide_url": p.input_slide_url,
            "input_slide_downloaded_size": p.input_slide_downloaded_size,
        })

    with patch("aignostics.application._download.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.headers = {"content-length": str(len(file_content))}
        mock_response.iter_content = Mock(return_value=[file_content])
        mock_get.return_value = mock_response

        # Call the function (should not call generate_signed_url for https://)
        result = download_url_to_file_with_progress(
            progress, https_url, destination, download_progress_callable=progress_callback
        )

        # Verify the result
        assert result == destination
        assert destination.exists()
        assert destination.read_bytes() == file_content

        # Verify requests.get was called with the https URL directly (no signed URL conversion)
        mock_get.assert_called_once_with(https_url, stream=True, timeout=60)

        # Verify progress updates
        assert len(progress_updates) >= 3
        assert progress_updates[0]["status"] == DownloadProgressState.DOWNLOADING_INPUT
        assert progress_updates[0]["input_slide_url"] == https_url


@pytest.mark.unit
def test_download_url_to_file_with_progress_http_url_success(tmp_path: Path) -> None:
    """Test successful download from http:// URL (no signed URL generation needed)."""
    http_url = "http://example.com/input.tiff"
    destination = tmp_path / "input.tiff"
    file_content = b"test file content from http"

    progress = DownloadProgress()

    with patch("aignostics.application._download.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.headers = {"content-length": str(len(file_content))}
        mock_response.iter_content = Mock(return_value=[file_content])
        mock_get.return_value = mock_response

        # Call the function
        result = download_url_to_file_with_progress(progress, http_url, destination)

        # Verify the result
        assert result == destination
        assert destination.exists()
        assert destination.read_bytes() == file_content

        # Verify requests.get was called with the http URL directly
        mock_get.assert_called_once_with(http_url, stream=True, timeout=60)


@pytest.mark.unit
def test_download_url_to_file_with_progress_unsupported_scheme(tmp_path: Path) -> None:
    """Test that unsupported URL schemes raise ValueError."""
    ftp_url = "ftp://example.com/file.tiff"
    destination = tmp_path / "file.tiff"
    progress = DownloadProgress()

    # Verify that ValueError is raised for unsupported schemes
    with pytest.raises(ValueError, match="Unsupported URL scheme"):
        download_url_to_file_with_progress(progress, ftp_url, destination)

    # Verify file was not created
    assert not destination.exists()


@pytest.mark.unit
def test_download_url_to_file_with_progress_https_with_chunked(tmp_path: Path) -> None:
    """Test https:// download with multiple chunks and progress tracking."""
    https_url = "https://example.com/large-file.tiff"
    destination = tmp_path / "large-file.tiff"
    chunks = [b"chunk1", b"chunk2", b"chunk3"]
    total_size = sum(len(c) for c in chunks)

    progress = DownloadProgress()
    progress_updates = []

    def progress_callback(p: DownloadProgress) -> None:
        progress_updates.append(p.input_slide_downloaded_size)

    with patch("aignostics.application._download.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.headers = {"content-length": str(total_size)}
        mock_response.iter_content = Mock(return_value=chunks)
        mock_get.return_value = mock_response

        # Call the function
        download_url_to_file_with_progress(
            progress, https_url, destination, download_progress_callable=progress_callback
        )

        # Verify progressive size updates
        assert progress_updates[0] == 0  # Initial
        assert progress_updates[1] == 0  # After size header
        assert progress_updates[2] == len(chunks[0])
        assert progress_updates[3] == len(chunks[0]) + len(chunks[1])
        assert progress_updates[4] == total_size  # Final

        # Verify direct URL was used (no signed URL generation)
        mock_get.assert_called_once_with(https_url, stream=True, timeout=60)


# ---------------------------------------------------------------------------
# download_item_artifact / download_available_items: AVAILABLE-gating + URL flow
# ---------------------------------------------------------------------------


_PRESIGNED_URL = "https://storage.googleapis.com/bucket/file?sig=abc"
# Patch _download.get_file_extension_for_artifact (NOT _utils.*) — the function
# is imported by name into _download, so re-binding it on _utils does nothing.
# Copilot called this out on PR #478 (comments #3 + #4).
_PATCH_GET_EXT = "aignostics.application._download.get_file_extension_for_artifact"
_PATCH_DOWNLOAD_FILE_WITH_PROGRESS = "aignostics.application._download.download_file_with_progress"


def _mock_artifact(
    *,
    output_artifact_id: str = "art-1",
    name: str = "result",
    output: ArtifactOutput = ArtifactOutput.AVAILABLE,
    metadata: dict | None = None,
) -> MagicMock:
    """Build a mock OutputArtifactResultReadResponse for tests."""
    artifact = MagicMock()
    artifact.output_artifact_id = output_artifact_id
    artifact.name = name
    artifact.output = output
    artifact.metadata = metadata if metadata is not None else {"checksum_base64_crc32c": "AAAA"}
    return artifact


@pytest.mark.unit
def test_download_item_artifact_resolves_fresh_url_per_call(tmp_path: Path) -> None:
    """download_item_artifact must call run.get_artifact_download_url(artifact_id).

    The deprecated artifact.download_url field is no longer consulted; every
    download resolves a fresh, short-lived URL via the /file endpoint. This
    test pins that behavior.
    """
    artifact = _mock_artifact()
    run = MagicMock()
    run.get_artifact_download_url.return_value = _PRESIGNED_URL

    with (
        patch(_PATCH_GET_EXT, return_value=".csv"),
        patch(_PATCH_DOWNLOAD_FILE_WITH_PROGRESS) as mock_download,
    ):
        download_item_artifact(
            progress=DownloadProgress(),
            run=run,
            artifact=artifact,
            destination_directory=tmp_path,
        )

    run.get_artifact_download_url.assert_called_once_with("art-1")
    # download_file_with_progress was handed the fresh URL, not anything from artifact
    mock_download.assert_called_once()
    assert mock_download.call_args.args[1] == _PRESIGNED_URL


@pytest.mark.unit
def test_download_item_artifact_skips_when_local_checksum_matches(tmp_path: Path) -> None:
    """If the artifact already exists locally with the right checksum, skip.

    Critical: do NOT call run.get_artifact_download_url in this branch — the
    presigned URL request hits SAMIA, and skipping it shortens resume cycles
    and reduces backend load.
    """
    import base64

    import crc32c as crc32c_lib  # local import keeps the test name space tight

    content = b"hello, slide"
    artifact_path = tmp_path / "result.csv"
    artifact_path.write_bytes(content)

    h = crc32c_lib.CRC32CHash()
    h.update(content)
    correct_checksum = base64.b64encode(h.digest()).decode("ascii")

    artifact = _mock_artifact(metadata={"checksum_base64_crc32c": correct_checksum})
    run = MagicMock()

    with (
        patch(_PATCH_GET_EXT, return_value=".csv"),
        patch(_PATCH_DOWNLOAD_FILE_WITH_PROGRESS) as mock_download,
    ):
        download_item_artifact(
            progress=DownloadProgress(),
            run=run,
            artifact=artifact,
            destination_directory=tmp_path,
        )

    run.get_artifact_download_url.assert_not_called()
    mock_download.assert_not_called()


@pytest.mark.unit
def test_download_item_artifact_raises_when_no_checksum(tmp_path: Path) -> None:
    """Empty metadata -> ValueError, before any URL is requested."""
    artifact = _mock_artifact(metadata={})
    run = MagicMock()

    with pytest.raises(ValueError, match="No checksum metadata"):
        download_item_artifact(
            progress=DownloadProgress(),
            run=run,
            artifact=artifact,
            destination_directory=tmp_path,
        )

    run.get_artifact_download_url.assert_not_called()


@pytest.mark.unit
def test_download_available_items_skips_non_available_artifacts(tmp_path: Path) -> None:
    """Artifacts with output != AVAILABLE are skipped.

    Per Dima on PR #478: the /file endpoint does NOT return a presigned URL for
    artifacts that aren't AVAILABLE. Calling it for a NONE artifact would fail
    the whole download. This test pins the guard.
    """
    from aignostics_sdk.platform import ItemOutput, ItemState

    available = _mock_artifact(output_artifact_id="art-ok", output=ArtifactOutput.AVAILABLE)
    none_artifact = _mock_artifact(output_artifact_id="art-skip", output=ArtifactOutput.NONE)

    item = MagicMock()
    item.external_id = "slide-1"
    item.state = ItemState.TERMINATED
    item.output = ItemOutput.FULL
    item.output_artifacts = [available, none_artifact]

    run = MagicMock()
    run.run_id = "run-xyz"
    run.results.return_value = [item]

    with patch("aignostics.application._download.download_item_artifact") as mock_dia:
        download_available_items(
            progress=DownloadProgress(),
            application_run=run,
            destination_directory=tmp_path,
            downloaded_items=set(),
        )

    # Only the AVAILABLE artifact triggered a download
    assert mock_dia.call_count == 1
    forwarded_artifact = mock_dia.call_args.args[2]
    assert forwarded_artifact.output_artifact_id == "art-ok"


@pytest.mark.unit
def test_download_available_items_passes_run_to_download_item_artifact(tmp_path: Path) -> None:
    """download_item_artifact is called with the Run instance as the second positional arg.

    download_item_artifact needs the Run handle to call get_artifact_download_url,
    so the calling site must pass it through. Pinning the call shape keeps the
    contract explicit.
    """
    from aignostics_sdk.platform import ItemOutput, ItemState

    artifact = _mock_artifact()
    item = MagicMock()
    item.external_id = "slide-1"
    item.state = ItemState.TERMINATED
    item.output = ItemOutput.FULL
    item.output_artifacts = [artifact]

    run = MagicMock()
    run.run_id = "run-xyz"
    run.results.return_value = [item]

    with patch("aignostics.application._download.download_item_artifact") as mock_dia:
        download_available_items(
            progress=DownloadProgress(),
            application_run=run,
            destination_directory=tmp_path,
            downloaded_items=set(),
        )

    # Args order matches def download_item_artifact(progress, run, artifact, ...)
    forwarded_progress, forwarded_run, forwarded_artifact, *_ = mock_dia.call_args.args
    assert forwarded_run is run
    assert forwarded_artifact is artifact
    assert isinstance(forwarded_progress, DownloadProgress)
