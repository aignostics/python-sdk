"""Tests for download utility functions in the application module."""

import base64
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import crc32c
import pytest
import requests

from aignostics.application._download import (
    _resolve_artifact_url,
    download_available_items,
    download_file_with_progress,
    download_item_artifact,
    download_url_to_file_with_progress,
    extract_filename_from_url,
)
from aignostics.application._models import DownloadProgress, DownloadProgressState

_PATCH_DOWNLOAD_ITEM_ARTIFACT = "aignostics.application._download.download_item_artifact"
_OLD_SIGNED_URL = "https://old-signed-url.com/file"
_ERROR_403_FORBIDDEN = "403 Forbidden"


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


@pytest.fixture
def patched_item_and_run() -> Generator[tuple[MagicMock, MagicMock], None, None]:
    """Fixture providing patched ItemState/ItemOutput enums and a mock run with one configurable artifact.

    Yields:
        tuple[MagicMock, MagicMock]: The mock run and its single mock artifact.
            Tests configure artifact attributes (output_artifact_id, download_url, metadata) as needed.
    """
    mock_artifact = MagicMock()
    mock_item = MagicMock()
    mock_item.external_id = "slide-1"
    mock_item.state = "TERMINATED"
    mock_item.output = "FULL"
    mock_item.output_artifacts = [mock_artifact]

    with (
        patch("aignostics.application._download.ItemState") as mock_item_state,
        patch("aignostics.application._download.ItemOutput") as mock_item_output,
    ):
        mock_item_state.TERMINATED = "TERMINATED"
        mock_item_output.FULL = "FULL"

        mock_run = MagicMock()
        mock_run.run_id = "run-123"
        mock_run.results.return_value = [mock_item]

        yield mock_run, mock_artifact


@pytest.mark.unit
def test_download_available_items_calls_url_resolver(
    tmp_path: Path, patched_item_and_run: tuple[MagicMock, MagicMock]
) -> None:
    """Test that download_available_items uses the get_artifact_download_url callback.

    Verifies that when a callback is provided, it is called with (run_id, artifact_id)
    and the resolved URL is passed to download_item_artifact.
    """
    mock_run, mock_artifact = patched_item_and_run
    mock_artifact.output_artifact_id = "artifact-xyz"
    mock_artifact.name = "result"
    mock_artifact.metadata = {"checksum_base64_crc32c": "AAAA", "checksum_crc32c": ""}

    resolved_url = "https://storage.googleapis.com/presigned"
    mock_url_resolver = MagicMock(return_value=resolved_url)

    with patch(_PATCH_DOWNLOAD_ITEM_ARTIFACT) as mock_download:
        download_available_items(
            progress=DownloadProgress(),
            application_run=mock_run,
            destination_directory=tmp_path,
            downloaded_items=set(),
            get_artifact_download_url=mock_url_resolver,
        )

        mock_url_resolver.assert_called_once_with("run-123", "artifact-xyz")
        mock_download.assert_called_once()
        assert mock_download.call_args[0][2] == resolved_url  # artifact_download_url is 3rd positional arg


@pytest.mark.unit
def test_download_available_items_falls_back_to_download_url(
    tmp_path: Path, patched_item_and_run: tuple[MagicMock, MagicMock]
) -> None:
    """Test that download_available_items falls back to artifact.download_url when no callback.

    Verifies the deprecated fallback path when get_artifact_download_url is None.
    """
    mock_run, mock_artifact = patched_item_and_run
    mock_artifact.output_artifact_id = "artifact-xyz"
    mock_artifact.name = "result"
    mock_artifact.download_url = _OLD_SIGNED_URL
    mock_artifact.metadata = {"checksum_base64_crc32c": "AAAA"}

    with patch(_PATCH_DOWNLOAD_ITEM_ARTIFACT) as mock_download:
        download_available_items(
            progress=DownloadProgress(),
            application_run=mock_run,
            destination_directory=tmp_path,
            downloaded_items=set(),
            get_artifact_download_url=None,
        )

        mock_download.assert_called_once()
        assert mock_download.call_args[0][2] == _OLD_SIGNED_URL


@pytest.mark.unit
def test_download_available_items_skips_when_no_url_available(
    tmp_path: Path, patched_item_and_run: tuple[MagicMock, MagicMock]
) -> None:
    """Test that download_available_items skips artifacts with no URL available.

    When get_artifact_download_url is None and artifact.download_url is also None,
    the artifact should be skipped.
    """
    mock_run, mock_artifact = patched_item_and_run
    mock_artifact.output_artifact_id = None
    mock_artifact.download_url = None

    with patch(_PATCH_DOWNLOAD_ITEM_ARTIFACT) as mock_download:
        download_available_items(
            progress=DownloadProgress(),
            application_run=mock_run,
            destination_directory=tmp_path,
            downloaded_items=set(),
            get_artifact_download_url=None,
        )

        mock_download.assert_not_called()


@pytest.mark.unit
def test_download_item_artifact_uses_provided_url(tmp_path: Path) -> None:
    """Test that download_item_artifact uses the explicitly provided artifact_download_url."""
    mock_artifact = MagicMock()
    mock_artifact.name = "cell_classification"
    mock_artifact.metadata = {"checksum_base64_crc32c": "AAAA"}

    progress = DownloadProgress()
    artifact_url = "https://storage.googleapis.com/presigned-url"

    with (
        patch("aignostics.application._download.get_file_extension_for_artifact", return_value=".csv"),
        patch("aignostics.application._download.download_file_with_progress") as mock_download,
    ):
        download_item_artifact(
            progress=progress,
            artifact=mock_artifact,
            artifact_download_url=artifact_url,
            destination_directory=tmp_path,
        )

        mock_download.assert_called_once()
        call_args = mock_download.call_args[0]
        assert call_args[0] is progress
        assert call_args[1] == artifact_url
        assert call_args[3] == "AAAA"


@pytest.mark.unit
def test_resolve_artifact_url_uses_new_endpoint() -> None:
    """Test that _resolve_artifact_url calls get_artifact_download_url when output_artifact_id is set."""
    mock_artifact = MagicMock()
    mock_artifact.output_artifact_id = "artifact-abc"
    mock_artifact.download_url = None

    resolver = MagicMock(return_value="https://new-endpoint.com/presigned")
    result = _resolve_artifact_url(mock_artifact, "run-123", resolver)

    assert result == "https://new-endpoint.com/presigned"
    resolver.assert_called_once_with("run-123", "artifact-abc")


@pytest.mark.unit
def test_resolve_artifact_url_falls_back_to_download_url_on_error() -> None:
    """Test that _resolve_artifact_url falls back to download_url when the new endpoint raises."""
    mock_artifact = MagicMock()
    mock_artifact.output_artifact_id = "artifact-abc"
    mock_artifact.download_url = _OLD_SIGNED_URL

    resolver = MagicMock(side_effect=RuntimeError(_ERROR_403_FORBIDDEN))
    result = _resolve_artifact_url(mock_artifact, "run-123", resolver)

    assert result == _OLD_SIGNED_URL


@pytest.mark.unit
def test_resolve_artifact_url_reraises_when_no_fallback_available() -> None:
    """Test that _resolve_artifact_url re-raises if the endpoint fails and download_url is absent."""
    mock_artifact = MagicMock()
    mock_artifact.output_artifact_id = "artifact-abc"
    mock_artifact.download_url = None

    resolver = MagicMock(side_effect=RuntimeError(_ERROR_403_FORBIDDEN))

    with pytest.raises(RuntimeError, match=_ERROR_403_FORBIDDEN):
        _resolve_artifact_url(mock_artifact, "run-123", resolver)


@pytest.mark.unit
def test_download_available_items_skips_already_downloaded_items(
    tmp_path: Path, patched_item_and_run: tuple[MagicMock, MagicMock]
) -> None:
    """Test that items already in downloaded_items are skipped without downloading."""
    mock_run, mock_artifact = patched_item_and_run
    mock_artifact.output_artifact_id = "artifact-xyz"

    with patch(_PATCH_DOWNLOAD_ITEM_ARTIFACT) as mock_download:
        download_available_items(
            progress=DownloadProgress(),
            application_run=mock_run,
            destination_directory=tmp_path,
            downloaded_items={"slide-1"},  # "slide-1" is already downloaded
            get_artifact_download_url=None,
        )

        mock_download.assert_not_called()


@pytest.mark.unit
def test_download_available_items_with_create_subdirectory_per_item(
    tmp_path: Path, patched_item_and_run: tuple[MagicMock, MagicMock]
) -> None:
    """Test that a subdirectory is created per item when create_subdirectory_per_item=True."""
    mock_run, mock_artifact = patched_item_and_run
    mock_artifact.output_artifact_id = "artifact-xyz"

    with patch(_PATCH_DOWNLOAD_ITEM_ARTIFACT):
        download_available_items(
            progress=DownloadProgress(),
            application_run=mock_run,
            destination_directory=tmp_path,
            downloaded_items=set(),
            create_subdirectory_per_item=True,
            get_artifact_download_url=None,
        )

    # Item external_id is "slide-1", stem is "slide-1"
    assert (tmp_path / "slide-1").is_dir()


@pytest.mark.unit
def test_download_url_to_file_with_progress_network_error(tmp_path: Path) -> None:
    """Test that network (non-HTTP) errors are wrapped in RuntimeError."""
    url = "https://example.com/slide.tiff"
    destination = tmp_path / "slide.tiff"
    progress = DownloadProgress()

    with patch("aignostics.application._download.requests.get") as mock_get:
        mock_get.side_effect = requests.ConnectionError("Network unreachable")

        with pytest.raises(RuntimeError, match="Network error downloading"):
            download_url_to_file_with_progress(progress, url, destination)

    assert not destination.exists()


@pytest.mark.unit
def test_download_item_artifact_no_checksum_raises(tmp_path: Path) -> None:
    """Test that ValueError is raised when no checksum metadata is found for an artifact."""
    mock_artifact = MagicMock()
    mock_artifact.name = "result.csv"
    mock_artifact.metadata = {}  # No checksum fields

    with pytest.raises(ValueError, match="No checksum metadata found"):
        download_item_artifact(
            progress=DownloadProgress(),
            artifact=mock_artifact,
            artifact_download_url="https://example.com/result.csv",
            destination_directory=tmp_path,
        )


@pytest.mark.unit
def test_download_item_artifact_file_exists_correct_checksum_skips_download(tmp_path: Path) -> None:
    """Test that download is skipped when the file already exists with the correct CRC32C checksum."""
    test_content = b"test file content for checksum"
    artifact_path = tmp_path / "result.csv"
    artifact_path.write_bytes(test_content)

    hasher = crc32c.CRC32CHash()
    hasher.update(test_content)
    correct_checksum = base64.b64encode(hasher.digest()).decode("ascii")

    mock_artifact = MagicMock()
    mock_artifact.name = "result"
    mock_artifact.metadata = {"checksum_base64_crc32c": correct_checksum}

    with (
        patch("aignostics.application._download.get_file_extension_for_artifact", return_value=".csv"),
        patch("aignostics.application._download.download_file_with_progress") as mock_download,
    ):
        download_item_artifact(
            progress=DownloadProgress(),
            artifact=mock_artifact,
            artifact_download_url="https://example.com/result.csv",
            destination_directory=tmp_path,
        )

    mock_download.assert_not_called()


@pytest.mark.unit
def test_download_file_with_progress_success(tmp_path: Path) -> None:
    """Test that download_file_with_progress downloads a file and verifies its CRC32C checksum."""
    signed_url = "https://example.com/artifact.csv"
    artifact_path = tmp_path / "result.csv"
    file_content = b"test artifact content for crc32c"

    hasher = crc32c.CRC32CHash()
    hasher.update(file_content)
    expected_checksum = base64.b64encode(hasher.digest()).decode("ascii")

    progress = DownloadProgress()
    progress.artifact = MagicMock()
    progress.artifact.name = "result"
    progress.item_external_id = "slide-1"

    with patch("aignostics.application._download.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_response.raise_for_status = Mock()
        mock_response.headers = {"content-length": str(len(file_content))}
        mock_response.iter_content = Mock(return_value=[file_content])
        mock_get.return_value = mock_response

        download_file_with_progress(
            progress=progress,
            signed_url=signed_url,
            artifact_path=artifact_path,
            metadata_checksum=expected_checksum,
        )

    assert artifact_path.exists()
    assert artifact_path.read_bytes() == file_content


@pytest.mark.unit
def test_download_file_with_progress_checksum_mismatch_removes_file_and_raises(tmp_path: Path) -> None:
    """Test that a CRC32C checksum mismatch causes the file to be removed and raises ValueError."""
    signed_url = "https://example.com/artifact.csv"
    artifact_path = tmp_path / "result.csv"
    file_content = b"test artifact content"
    wrong_checksum = "AAAAAAAAAAAAAAAA=="

    progress = DownloadProgress()
    progress.artifact = MagicMock()
    progress.artifact.name = "result"
    progress.item_external_id = "slide-1"

    with patch("aignostics.application._download.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_response.raise_for_status = Mock()
        mock_response.headers = {"content-length": str(len(file_content))}
        mock_response.iter_content = Mock(return_value=[file_content])
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Checksum mismatch"):
            download_file_with_progress(
                progress=progress,
                signed_url=signed_url,
                artifact_path=artifact_path,
                metadata_checksum=wrong_checksum,
            )

    assert not artifact_path.exists()
