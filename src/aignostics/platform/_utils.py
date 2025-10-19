"""
This module provides utility functions to support the Aignostics client operations.

It includes helpers for file operations, checksum verification, Google Cloud Storage
interactions, and operation caching.

These utilities primarily handle file operations, data integrity, cloud storage
interactions, and caching to support the main client functionality.
"""

import base64
import contextlib
import datetime
import hashlib
import re
import tempfile
import time
import typing as t
from collections.abc import Callable, Generator
from pathlib import Path
from typing import IO, Any, ParamSpec, TypeVar

import google_crc32c
import requests
from aignx.codegen.models import InputArtifact as InputArtifactData
from aignx.codegen.models import OutputArtifact as OutputArtifactData
from aignx.codegen.models import OutputArtifactResultReadResponse as OutputArtifactElement
from tqdm.auto import tqdm

from aignostics.platform._authentication import get_token

EIGHT_MB = 8_388_608
SIGNED_DOWNLOAD_URL_EXPIRES_SECONDS_DEFAULT = 6 * 60 * 60  # 6 hours

# Cache storage for operation results
_operation_cache: dict[str, tuple[Any, float]] = {}

# Type variables for the cached_operation decorator
P = ParamSpec("P")
T = TypeVar("T")


def cache_key(method_name: str, *args: object, **kwargs: object) -> str:
    """Generates a cache key based on the method name and parameters.

    Args:
        method_name (str): The name of the method being cached.
        *args: Positional arguments to the method.
        **kwargs: Keyword arguments to the method.

    Returns:
        str: A unique cache key.
    """
    params = f"{args}:{sorted(kwargs.items())}"
    return f"{method_name}:{params}"


def cache_key_with_token(token: str, method_name: str, *args: object, **kwargs: object) -> str:
    """Generates a cache key based on the token, method name, and parameters.

    Args:
        token (str): The authentication token.
        method_name (str): The name of the method being cached.
        *args: Positional arguments to the method.
        **kwargs: Keyword arguments to the method.

    Returns:
        str: A unique cache key.
    """
    token_hash = hashlib.sha256((token or "").encode()).hexdigest()[:16]
    params = f"{args}:{sorted(kwargs.items())}"
    return f"{token_hash}:{method_name}:{params}"


def cached_operation(
    ttl: int, *, use_token: bool = True, instance_attrs: tuple[str, ...] | None = None
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Caches the result of a method call for a specified time-to-live (TTL).

    Args:
        ttl (int): Time-to-live for the cache in seconds.
        use_token (bool): If True, includes the authentication token in the cache key.
            This is useful for Client methods that should cache per-user.
            When use_token is True and no instance_attrs are specified, the 'self'
            argument is excluded from the cache key to enable cache sharing across instances.
        instance_attrs (tuple[str, ...] | None): Instance attributes to include in the cache key.
            This is useful for instance methods where caching should be per-instance based on
            specific attributes (e.g., 'run_id' for Run.details()).

    Returns:
        Callable: A decorator that caches the method result.
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Build cache key components
            cache_args: tuple[object, ...] = args

            # If instance_attrs specified, extract them from self (args[0])
            if instance_attrs and args:
                instance = args[0]
                instance_values = tuple(getattr(instance, attr) for attr in instance_attrs)
                # Replace self with instance attribute values in cache key
                cache_args = instance_values + args[1:]
            elif use_token and args:
                # When using token-based caching without instance_attrs,
                # skip 'self' to enable cache sharing across instances
                cache_args = args[1:]

            if use_token:
                token = get_token(True)
                key = cache_key_with_token(token, func.__name__, *cache_args, **kwargs)
            else:
                key = cache_key(func.__name__, *cache_args, **kwargs)

            if key in _operation_cache:
                value, expiry = _operation_cache[key]
                if time.time() < expiry:
                    return t.cast("T", value)
                del _operation_cache[key]

            result = func(*args, **kwargs)
            _operation_cache[key] = (result, time.time() + ttl)
            return result

        return wrapper

    return decorator


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
