"""
This module provides utility functions to support the Aignostics client operations.

It includes helpers for file operations, checksum verification, and Google Cloud Storage
interactions.

These utilities primarily handle file operations, data integrity, and cloud storage
interactions to support the main client functionality.
"""

import base64
import contextlib
import datetime
import re
import tempfile
import typing as t
from collections.abc import Generator
from pathlib import Path
from typing import IO, Any

import google_crc32c
import requests
from aignx.codegen.models import InputArtifactReadResponse as InputArtifactData
from aignx.codegen.models import OutputArtifactReadResponse as OutputArtifactData
from aignx.codegen.models import OutputArtifactResultReadResponse as OutputArtifactElement
from tqdm.auto import tqdm

EIGHT_MB = 8_388_608
SIGNED_DOWNLOAD_URL_EXPIRES_SECONDS_DEFAULT = 6 * 60 * 60  # 6 hours


def mime_type_to_file_ending(mime_type: str) -> str:
    """Converts a MIME type to an appropriate file extension.

    Args:
        mime_type (str): The MIME type string to convert.

    Returns:
        str: The corresponding file extension including the dot.

    Raises:
        ValueError: If the MIME type is not recognized.
    """
    if mime_type == "image/png":
        return ".png"
    if mime_type == "image/tiff":
        return ".tiff"
    if mime_type == "application/vnd.apache.parquet":
        return ".parquet"
    if mime_type in {"application/geo+json", "application/json"}:
        return ".json"
    if mime_type == "text/csv":
        return ".csv"
    msg = f"Unknown mime type: {mime_type}"
    raise ValueError(msg)


def get_mime_type_for_artifact(artifact: OutputArtifactData | InputArtifactData | OutputArtifactElement) -> str:
    """Get the MIME type for a given artifact.

    Args:
        artifact (OutputArtifact | InputArtifact | OutputArtifactElement): The artifact to get the MIME type for.

    Returns:
        str: The MIME type of the artifact.
    """
    if isinstance(artifact, InputArtifactData):
        return str(artifact.mime_type)
    if isinstance(artifact, OutputArtifactData):
        return str(artifact.mime_type)
    metadata = artifact.metadata or {}
    return str(metadata.get("media_type", metadata.get("mime_type", "application/octet-stream")))


def download_file(signed_url: str, file_path: str, verify_checksum: str) -> None:
    """Downloads a file from a signed URL and verifies its integrity.

    Args:
        signed_url (str): The signed URL to download the file from.
        file_path (str): The local path where the file should be saved.
        verify_checksum (str): The expected CRC32C checksum in base64 encoding.

    Raises:
        ValueError: If the downloaded file's checksum doesn't match the expected value.
        requests.HTTPError: If the download request fails.
    """
    checksum = google_crc32c.Checksum()  # type: ignore[no-untyped-call]
    with requests.get(signed_url, stream=True, timeout=60) as stream:
        stream.raise_for_status()
        with open(file_path, mode="wb") as file:
            total_size = int(stream.headers.get("content-length", 0))
            progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)
            for chunk in stream.iter_content(chunk_size=EIGHT_MB):
                if chunk:
                    file.write(chunk)
                    checksum.update(chunk)  # type: ignore[no-untyped-call]
                    progress_bar.update(len(chunk))
            progress_bar.close()
    downloaded_file = base64.b64encode(checksum.digest()).decode("ascii")  # type: ignore[no-untyped-call]
    if downloaded_file != verify_checksum:
        msg = f"Checksum mismatch: {downloaded_file} != {verify_checksum}"
        raise ValueError(msg)


def generate_signed_url(url: str, expires_seconds: int = SIGNED_DOWNLOAD_URL_EXPIRES_SECONDS_DEFAULT) -> str:
    """Generates a signed URL for a Google Cloud Storage object.

    Args:
        url (str): The fully qualified bucket URL (e.g. gs://bucket/path/to/object).
        expires_seconds (int): The number of seconds the signed URL should be valid for.

    Returns:
        str: A signed URL that can be used to download the object.

    Raises:
        ValueError: If the GS path is invalid or the blob doesn't exist.
    """
    from google.cloud import storage  # noqa: PLC0415, lazy loading for performance

    pattern = r"gs://(?P<bucket_name>[^/]+)/(?P<path>.*)"
    m = re.fullmatch(pattern, url)
    if not m:
        msg = "Invalid google storage URI"
        raise ValueError(msg)
    bucket_name = m.group("bucket_name")
    path = m.group("path")

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(path)
    if not blob.exists():
        msg = f"Blob does not exist: {url}"
        raise ValueError(msg)

    return t.cast(
        "str",
        blob.generate_signed_url(expiration=datetime.timedelta(seconds=expires_seconds), method="GET", version="v4"),
    )


def calculate_file_crc32c(file: Path) -> str:
    """Calculates the CRC32C checksum of a file.

    Args:
        file (Path): Path to the file to calculate the checksum for.

    Returns:
        str: The CRC32C checksum in base64 encoding.
    """
    checksum = google_crc32c.Checksum()  # type: ignore[no-untyped-call]
    with open(file, mode="rb") as f:
        for _ in checksum.consume(f, EIGHT_MB):  # type: ignore[no-untyped-call]
            pass
    return base64.b64encode(checksum.digest()).decode("ascii")  # type: ignore[no-untyped-call]


@contextlib.contextmanager
def download_temporarily(signed_url: str, verify_checksum: str) -> Generator[IO[bytes], Any, None]:
    """Downloads a file to a temporary location and provides file handle.

    Args:
        signed_url (str): The signed URL to download the file from.
        verify_checksum (str): The expected CRC32C checksum in base64 encoding.

    Yields:
        IO[bytes]: File handle to the downloaded temporary file.

    Raises:
        ValueError: If the downloaded file's checksum doesn't match the expected value.
        requests.HTTPError: If the download request fails.
    """
    with tempfile.NamedTemporaryFile() as file:
        download_file(signed_url, file.name, verify_checksum)
        yield file
