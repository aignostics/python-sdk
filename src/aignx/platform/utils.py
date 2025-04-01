import base64
import contextlib
import datetime
import re
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import IO, Any

import google_crc32c
import requests
from google.cloud import storage
from tqdm.auto import tqdm

EIGHT_MB = 8_388_608


def mime_type_to_file_ending(mime_type: str) -> str:
    """
    Convert a mime type to a file ending.
    """
    if mime_type == "image/png":
        return ".png"
    if mime_type == "image/tiff":
        return ".tiff"
    if mime_type == "application/vnd.apache.parquet":
        return ".parquet"
    if mime_type == "application/geo+json" or mime_type == "application/json":
        return ".json"
    if mime_type == "text/csv":
        return ".csv"
    raise ValueError(f"Unknown mime type: {mime_type}")


def _download_file(signed_url: str, file_path: str, verify_checksum: str) -> None:
    checksum = google_crc32c.Checksum()
    with requests.get(signed_url, stream=True) as stream:
        stream.raise_for_status()
        with open(file_path, "wb") as file:
            total_size = int(stream.headers.get("content-length", 0))
            progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)
            for chunk in stream.iter_content(chunk_size=EIGHT_MB):
                if chunk:
                    file.write(chunk)
                    checksum.update(chunk)
                    progress_bar.update(len(chunk))
            progress_bar.close()
    downloaded_file = base64.b64encode(checksum.digest()).decode("ascii")
    if downloaded_file != verify_checksum:
        raise ValueError(f"Checksum mismatch: {downloaded_file} != {verify_checksum}")


def _generate_signed_url(fully_qualified_gs_path: str):
    pattern = r"gs://(?P<bucket_name>[^/]+)/(?P<path>.*)"
    m = re.fullmatch(pattern, fully_qualified_gs_path)
    if not m:
        raise ValueError("Invalid google storage URI")
    bucket_name = m.group(1)
    path = m.group(2)

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(path)
    if not blob.exists():
        raise ValueError(f"Blob does not exist: {fully_qualified_gs_path}")

    url = blob.generate_signed_url(
        expiration=datetime.timedelta(hours=1),
        method="GET",
        version="v4"
    )
    return url


def _calculate_file_crc32c(file: Path) -> str:
    checksum = google_crc32c.Checksum()
    with open(file, "rb") as file:
        for _ in checksum.consume(file, EIGHT_MB):
            pass
    return base64.b64encode(checksum.digest()).decode("ascii")


@contextlib.contextmanager
def download_temporarily(signed_url: str, verify_checksum: str) -> Generator[IO[bytes], Any, None]:
    with tempfile.NamedTemporaryFile() as file:
        _download_file(signed_url, file.name, verify_checksum)
        yield file
