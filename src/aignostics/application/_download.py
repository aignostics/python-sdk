"""Download helper functions for application run results."""

import base64
from collections.abc import Callable
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

import google_crc32c
import requests
from loguru import logger

from aignostics.platform import ItemOutput, ItemState, Run, generate_signed_url
from aignostics.utils import sanitize_path_component

from ._models import DownloadProgress, DownloadProgressState
from ._utils import get_file_extension_for_artifact

# Download chunk sizes
APPLICATION_RUN_FILE_READ_CHUNK_SIZE = 1024 * 1024 * 1024  # 1GB
APPLICATION_RUN_DOWNLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB


def extract_filename_from_url(url: str) -> str:
    """Extract a filename from a URL robustly.

    Args:
        url (str): The URL to extract filename from.

    Returns:
        str: The extracted filename, sanitized for use as a path component.

    Examples:
        >>> extract_filename_from_url("gs://bucket/path/to/file.tiff")
        'file.tiff'
        >>> extract_filename_from_url("https://example.com/slides/sample.svs?token=abc")
        'sample.svs'
        >>> extract_filename_from_url("https://example.com/download/")
        'download'
    """
    # Parse the URL and extract the path component
    parsed = urlparse(url)
    # Use PurePosixPath since URLs always use forward slashes
    path = PurePosixPath(parsed.path)

    # Get the last component (name) of the path
    # If path ends with /, .name will be empty, so use the parent's name
    filename = path.name or path.parent.name

    # If still empty (e.g., root path), use a default
    if not filename:
        filename = "download"

    # Sanitize the filename to ensure it's safe for filesystem use
    return sanitize_path_component(filename)


def download_url_to_file_with_progress(
    progress: DownloadProgress,
    url: str,
    destination_path: Path,
    download_progress_queue: Any | None = None,  # noqa: ANN401
    download_progress_callable: Callable | None = None,  # type: ignore[type-arg]
) -> Path:
    """Download a file from a URL (gs://, http://, or https://) with progress tracking.

    Args:
        progress (DownloadProgress): Progress tracking object for GUI or CLI updates.
        url (str): The URL to download from (supports gs://, http://, https://).
        destination_path (Path): The local file path to save to.
        download_progress_queue (Any | None): Queue for GUI progress updates.
        download_progress_callable (Callable | None): Callback for CLI progress updates.

    Returns:
        Path: The path to the downloaded file.

    Raises:
        ValueError: If the URL is invalid.
        RuntimeError: If the download fails.
    """
    logger.trace("Downloading URL '{}' to '{}' with progress tracking", url, destination_path)

    # Initialize progress tracking
    progress.status = DownloadProgressState.DOWNLOADING_INPUT
    progress.input_slide_url = url
    progress.input_slide_path = destination_path
    progress.input_slide_downloaded_size = 0
    progress.input_slide_downloaded_chunk_size = 0
    progress.input_slide_size = None
    update_progress(progress, download_progress_callable, download_progress_queue)

    # Generate download URL (convert gs:// to signed URL, use http(s):// directly)
    if url.startswith("gs://"):
        download_url = generate_signed_url(url)
    elif url.startswith(("http://", "https://")):
        download_url = url
    else:
        msg = f"Unsupported URL scheme: {url}. Only gs://, http://, and https:// are supported."
        raise ValueError(msg)

    destination_path.parent.mkdir(parents=True, exist_ok=True)

    # Download with progress tracking
    try:
        response = requests.get(download_url, stream=True, timeout=60)
        response.raise_for_status()

        progress.input_slide_size = int(response.headers.get("content-length", 0))
        update_progress(progress, download_progress_callable, download_progress_queue)

        with destination_path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=APPLICATION_RUN_DOWNLOAD_CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
                    progress.input_slide_downloaded_chunk_size = len(chunk)
                    progress.input_slide_downloaded_size += progress.input_slide_downloaded_chunk_size
                    update_progress(progress, download_progress_callable, download_progress_queue)

        logger.debug("Downloaded URL '{}' to '{}'", url, destination_path)
        return destination_path
    except requests.HTTPError as e:
        msg = f"HTTP error downloading '{url}': {e}"
        logger.warning(msg)
        raise RuntimeError(msg) from e
    except requests.RequestException as e:
        msg = f"Network error downloading '{url}': {e}"
        logger.warning(msg)
        raise RuntimeError(msg) from e


def update_progress(
    progress: DownloadProgress,
    download_progress_callable: Callable | None = None,  # type: ignore[type-arg]
    download_progress_queue: Any | None = None,  # noqa: ANN401
) -> None:
    """Update download progress via callback or queue.

    Args:
        progress (DownloadProgress): Progress tracking object to send.
        download_progress_callable (Callable | None): Optional callback function.
        download_progress_queue (Any | None): Optional queue for progress updates.
    """
    if download_progress_callable:
        download_progress_callable(progress)
    if download_progress_queue:
        download_progress_queue.put_nowait(progress)


def download_available_items(  # noqa: PLR0913, PLR0917
    progress: DownloadProgress,
    application_run: Run,
    destination_directory: Path,
    downloaded_items: set[str],
    create_subdirectory_per_item: bool = False,
    download_progress_queue: Any | None = None,  # noqa: ANN401
    download_progress_callable: Callable | None = None,  # type: ignore[type-arg]
) -> None:
    """Download items that are available and not yet downloaded.

    Args:
        progress (DownloadProgress): Progress tracking object for GUI or CLI updates.
        application_run (Run): The application run object.
        destination_directory (Path): Directory to save files.
        downloaded_items (set): Set of already downloaded item external ids.
        create_subdirectory_per_item (bool): Whether to create a subdirectory for each item.
        download_progress_queue (Queue | None): Queue for GUI progress updates.
        download_progress_callable (Callable | None): Callback for CLI progress updates.
    """
    items = list(application_run.results())
    progress.item_count = len(items)
    for item_index, item in enumerate(items):
        if item.external_id in downloaded_items:
            continue

        if item.state == ItemState.TERMINATED and item.output == ItemOutput.FULL:
            progress.status = DownloadProgressState.DOWNLOADING
            progress.item_index = item_index
            progress.item = item
            progress.item_external_id = item.external_id

            progress.artifact_count = len(item.output_artifacts)
            update_progress(progress, download_progress_callable, download_progress_queue)

            if create_subdirectory_per_item:
                path = Path(item.external_id)
                stem_name = path.stem
                try:
                    # Handle case where path might be relative to destination
                    rel_path = path.relative_to(destination_directory)
                    stem_name = rel_path.stem
                except ValueError:
                    # Not a subfolder - just use the stem
                    pass
                item_directory = destination_directory / stem_name
            else:
                item_directory = destination_directory
            item_directory.mkdir(exist_ok=True)

            for artifact_index, artifact in enumerate(item.output_artifacts):
                progress.artifact_index = artifact_index
                progress.artifact = artifact
                update_progress(progress, download_progress_callable, download_progress_queue)

                download_item_artifact(
                    progress,
                    artifact,
                    item_directory,
                    item.external_id if not create_subdirectory_per_item else "",
                    download_progress_queue,
                    download_progress_callable,
                )

            downloaded_items.add(item.external_id)


def download_item_artifact(  # noqa: PLR0913, PLR0917
    progress: DownloadProgress,
    artifact: Any,  # noqa: ANN401
    destination_directory: Path,
    prefix: str = "",
    download_progress_queue: Any | None = None,  # noqa: ANN401
    download_progress_callable: Callable | None = None,  # type: ignore[type-arg]
) -> None:
    """Download an artifact of a result item with progress tracking.

    Args:
        progress (DownloadProgress): Progress tracking object for GUI or CLI updates.
        artifact (Any): The artifact to download.
        destination_directory (Path): Directory to save the file.
        prefix (str): Prefix for the file name, if needed.
        download_progress_queue (Queue | None): Queue for GUI progress updates.
        download_progress_callable (Callable | None): Callback for CLI progress updates.

    Raises:
        ValueError: If
            no checksum metadata is found for the artifact.
        requests.HTTPError: If the download fails.
    """
    metadata = artifact.metadata or {}
    metadata_checksum = metadata.get("checksum_base64_crc32c", "") or metadata.get("checksum_crc32c", "")
    if not metadata_checksum:
        message = f"No checksum metadata found for artifact {artifact.name}"
        logger.error(message)
        raise ValueError(message)

    artifact_path = (
        destination_directory
        / f"{prefix}{sanitize_path_component(artifact.name)}{get_file_extension_for_artifact(artifact)}"
    )

    if artifact_path.exists():
        checksum = google_crc32c.Checksum()  # type: ignore[no-untyped-call]
        with open(artifact_path, "rb") as f:
            while chunk := f.read(APPLICATION_RUN_FILE_READ_CHUNK_SIZE):
                checksum.update(chunk)  # type: ignore[no-untyped-call]
        existing_checksum = base64.b64encode(checksum.digest()).decode("ascii")  # type: ignore[no-untyped-call]
        if existing_checksum == metadata_checksum:
            logger.trace("File {} already exists with correct checksum", artifact_path)
            return

    download_file_with_progress(
        progress,
        artifact.download_url,
        artifact_path,
        metadata_checksum,
        download_progress_queue,
        download_progress_callable,
    )


def download_file_with_progress(  # noqa: PLR0913, PLR0917
    progress: DownloadProgress,
    signed_url: str,
    artifact_path: Path,
    metadata_checksum: str,
    download_progress_queue: Any | None = None,  # noqa: ANN401
    download_progress_callable: Callable | None = None,  # type: ignore[type-arg]
) -> None:
    """Download a file with progress tracking support.

    Args:
        progress (DownloadProgress): Progress tracking object for GUI or CLI updates.
        signed_url (str): The signed URL to download from.
        artifact_path (Path): Path to save the file.
        metadata_checksum (str): Expected CRC32C checksum in base64.
        download_progress_queue (Any | None): Queue for GUI progress updates.
        download_progress_callable (Callable | None): Callback for CLI progress updates.

    Raises:
        ValueError: If
            checksum verification fails.
        requests.HTTPError: If download fails.
    """
    logger.trace(
        "Downloading artifact '{}' to '{}' with expected checksum '{}' for item with external id '{}'",
        progress.artifact.name if progress.artifact else "unknown",
        artifact_path,
        metadata_checksum,
        progress.item_external_id or "unknown",
    )
    progress.artifact_download_url = signed_url
    progress.artifact_path = artifact_path
    progress.artifact_downloaded_size = 0
    progress.artifact_downloaded_chunk_size = 0
    progress.artifact_size = None
    update_progress(progress, download_progress_callable, download_progress_queue)

    checksum = google_crc32c.Checksum()  # type: ignore[no-untyped-call]

    with requests.get(signed_url, stream=True, timeout=60) as stream:
        stream.raise_for_status()
        progress.artifact_size = int(stream.headers.get("content-length", 0))
        update_progress(progress, download_progress_callable, download_progress_queue)
        with open(artifact_path, mode="wb") as file:
            for chunk in stream.iter_content(chunk_size=APPLICATION_RUN_DOWNLOAD_CHUNK_SIZE):
                if chunk:
                    file.write(chunk)
                    checksum.update(chunk)  # type: ignore[no-untyped-call]
                    progress.artifact_downloaded_chunk_size = len(chunk)
                    progress.artifact_downloaded_size += progress.artifact_downloaded_chunk_size
                    update_progress(progress, download_progress_callable, download_progress_queue)

    downloaded_checksum = base64.b64encode(checksum.digest()).decode("ascii")  # type: ignore[no-untyped-call]
    if downloaded_checksum != metadata_checksum:
        artifact_path.unlink()  # Remove corrupted file
        msg = f"Checksum mismatch for {artifact_path}: {downloaded_checksum} != {metadata_checksum}"
        logger.error(msg)
        raise ValueError(msg)
