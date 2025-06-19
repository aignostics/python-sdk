"""Service of the bucket module."""

import hashlib
import re
from collections.abc import Callable, Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import humanize
import requests
from pydantic import BaseModel, computed_field

if TYPE_CHECKING:
    from botocore.client import BaseClient

from aignostics.utils import UNHIDE_SENSITIVE_INFO, BaseService, Health, get_logger, get_user_data_directory

from ._settings import Settings

BUCKET_PROTOCOL = "gs"
SIGNATURE_VERSION = "s3v4"
ENDPOINT_URL_DEFAULT = "https://storage.googleapis.com"

UPLOAD_CHUNK_SIZE = 1024 * 1024
DOWNLOAD_CHUNK_SIZE = 1024 * 1024 * 10
ETAG_CHUNK_SIZE = 1024 * 1024 * 100

logger = get_logger(__name__)


class DownloadProgress(BaseModel):
    overall_total: int
    overall_downloaded: int
    overall_failed: int

    @computed_field  # type: ignore[prop-decorator]
    @property
    def overall_processed(self) -> int:
        return self.overall_failed + self.overall_downloaded

    @computed_field  # type: ignore[prop-decorator]
    @property
    def overall_current(self) -> int:
        return min(self.overall_total, self.overall_processed + 1)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def overall_progress_normalized(self) -> float:
        if self.overall_total == 0:
            return 0.0
        return float(self.overall_processed) / float(self.overall_total)

    current_file_key: str
    current_file_downloaded: int
    current_file_size: int

    @computed_field  # type: ignore[prop-decorator]
    @property
    def current_file_progress_normalized(self) -> float:
        if self.current_file_size == 0:
            return 0.0
        return float(self.current_file_downloaded) / float(self.current_file_size)


class DownloadResult(BaseModel):
    downloaded: list[Path]
    failed: list[str]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def downloaded_count(self) -> int:
        return len(self.downloaded)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def failed_count(self) -> int:
        return len(self.failed)

    @property
    def total_count(self) -> int:
        return self.downloaded_count + self.failed_count


class Service(BaseService):
    """Service of the bucket module."""

    _settings: Settings

    def __init__(self) -> None:
        """Initialize service."""
        super().__init__(Settings)

    def info(self, mask_secrets: bool = True) -> dict[str, Any]:
        """Determine info of this service.

        Args:
            mask_secrets (bool): If True, mask sensitive information in the output.

        Returns:
            dict[str,Any]: The info of this service.
        """
        return {"settings": self._settings.model_dump(context={UNHIDE_SENSITIVE_INFO: not mask_secrets})}

    def health(self) -> Health:  # noqa: PLR6301
        """Determine health of this service.

        Returns:
            Health: The health of the service.
        """
        return Health(
            status=Health.Code.UP,
            components={},
        )

    def _get_s3_client(self, endpoint_url: str = ENDPOINT_URL_DEFAULT) -> "BaseClient":
        """Get a Boto3 S3 client instance for cloud bucket on Aignostics Platform.

        Args:
            endpoint_url (str): The endpoint URL for the S3 service.

        Returns:
            BaseClient: A Boto3 S3 client instance.
        """
        from boto3 import Session  # noqa: PLC0415
        from botocore.client import Config  # noqa: PLC0415

        # https://www.kmp.tw/post/accessgcsusepythonboto3/
        session = Session(
            aws_access_key_id=self._settings.hmac_access_key_id.get_secret_value(),
            aws_secret_access_key=self._settings.hmac_secret_access_key.get_secret_value(),
            region_name=self._settings.region_name,
        )
        return session.client("s3", endpoint_url=endpoint_url, config=Config(signature_version=SIGNATURE_VERSION))

    @staticmethod
    def get_bucket_protocol() -> str:
        """Get the bucket protocol.

        Returns:
            str: The bucket protocol.
        """
        return BUCKET_PROTOCOL

    def get_bucket_name(self) -> str:
        """Get the bucket name.

        Returns:
            str: The bucket name.
        """
        return self._settings.name

    def create_signed_upload_url(self, object_key: str, bucket_name: str | None = None) -> str:
        """Generates a signed URL to upload a Google Cloud Storage object.

        Args:
            object_key (str): The key of the object to generate a signed URL for.
            bucket_name (str): The name of the bucket to generate a signed URL for.
                If None, use the default bucket.

        Returns:
            str: A signed URL that can be used to upload to the bucket and key.
        """
        url = self._get_s3_client().generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": self._settings.name if bucket_name is None else bucket_name, "Key": object_key},
            ExpiresIn=self._settings.upload_signed_url_expiration_seconds,
        )
        return cast("str", url)

    def _upload_file(
        self, source_path: Path, object_key: str, callback: Callable[[int, Path], None] | None = None
    ) -> bool:
        """Upload a file to the bucket using a signed URL.

        Args:
            source_path (Path): Path of the local file to upload.
            object_key (str): Key to use for the uploaded object.
            callback (Callable[[int, int], None] | None): Optional callback function for upload progress.
                Function receives bytes_read and total_bytes parameters.

        Returns:
            bool: True if upload was successful, False otherwise.
        """
        logger.debug("Uploading file '%s' to object key '%s'", source_path, object_key)
        if not source_path.is_file():
            logger.error("Source path '%s' is not a file", source_path)
            return False

        signed_url = self.create_signed_upload_url(object_key)

        try:
            with open(source_path, "rb") as f:

                def read_in_chunks() -> Generator[bytes, None, None]:
                    while True:
                        chunk = f.read(UPLOAD_CHUNK_SIZE)
                        if not chunk:
                            break
                        if callback:
                            callback(len(chunk), source_path)
                        yield chunk

                response = requests.put(
                    signed_url,
                    data=read_in_chunks(),
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=60,
                )
                response.raise_for_status()

            logger.info("Successfully uploaded '%s' to object key '%s'", source_path, object_key)
            return True

        except (OSError, requests.RequestException):
            logger.exception("Error uploading file '%s' to object key '%s'", source_path, object_key)
            return False

    def upload(
        self,
        source_path: Path,
        destination_prefix: str,
        callback: Callable[[int, Path], None] | None = None,
    ) -> dict[str, list[str]]:
        """Upload a file or directory to the bucket.

        Args:
            source_path (Path): Path to file or directory to upload.
            destination_prefix (str): Prefix for object keys (e.g. username).
            callback (Callable[[int, int], None] | None): Optional callback function for upload progress.
                Function receives bytes_read and total_bytes parameters.

        Returns:
            dict[str, list[str]]: Dict with 'success' and 'failed' lists containing object keys.
        """
        results: dict[str, list[str]] = {"success": [], "failed": []}

        destination_prefix = destination_prefix.rstrip("/")

        if source_path.is_file():
            object_key = f"{destination_prefix}/{source_path.name}"
            if self._upload_file(source_path, object_key, callback):
                results["success"].append(object_key)
            else:
                results["failed"].append(object_key)

        elif source_path.is_dir():
            for file_path in source_path.glob("**/*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(source_path).as_posix()
                    object_key = f"{destination_prefix}/{rel_path}"

                    if self._upload_file(file_path, object_key, callback):
                        results["success"].append(object_key)
                    else:
                        results["failed"].append(object_key)
        else:
            logger.error("Source path '%s' is neither a file nor directory", source_path)

        return results

    @staticmethod
    def find_static(
        what: list[str] | None = None,
        what_is_key: bool = False,
        detail: bool = False,
        include_signed_urls: bool = False,
    ) -> list[str | dict[str, Any]]:
        """List objects recursively in the bucket, static method version.

        Args:
            what (list[str] | None): Patterns or keys to match object keys against - all if not specified.
            what_is_key (bool): If True, treat the pattern as a key, else as a regex.
            detail (bool): If True, return detailed information including object type, else return only paths.
            include_signed_urls (bool): If True, include signed download URLs in the results.

        Returns:
            list[Union[str, dict[str, Any]]]: List of objects in the bucket with optional detail.

        Raises:
            ValueError: If the provided regex pattern is invalid.
        """
        return Service().find(what, what_is_key, detail, include_signed_urls)

    def find(  # noqa: C901
        self,
        what: list[str] | None,
        what_is_key: bool = False,
        detail: bool = False,
        include_signed_urls: bool = False,
    ) -> list[str | dict[str, Any]]:
        """List objects recursively in the bucket, with optional pattern matching.

        Args:
            what (list[str] | None): Patterns or keys to match object keys against - all if not specified.
            what_is_key (bool): If True, treat entries in what as exact keys, else as regex patterns.
            detail (bool): If True, return detailed information including object type, else return only paths.
            include_signed_urls (bool): If True, include signed download URLs in the results.

        Returns:
            list[Union[str, dict[str, Any]]]: List of objects in the bucket with optional detail.

        Raises:
            ValueError: If any provided regex pattern is invalid.
        """
        if not what:
            what = [".*"]  # Default to match all objects if no patterns provided

        # Normalize keys by removing bucket prefix if present (when treating as exact keys)
        if what_is_key:
            bucket_prefix = f"{self._settings.name}/"
            what = [key.removeprefix(bucket_prefix) for key in what]

        compiled_patterns: list[re.Pattern[str]] = []
        if not what_is_key:
            for pattern in what:
                try:
                    compiled_patterns.append(re.compile(pattern))
                except re.error as e:
                    msg = f"Invalid regex pattern '{pattern}': {e}"
                    logger.warning(msg)
                    raise ValueError(msg) from e

        s3c = self._get_s3_client()
        paginator = s3c.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=self._settings.name)

        result: list[str | dict[str, Any]] = []

        for page in pages:
            contents = page.get("Contents", [])

            for item in contents:
                item_key = item["Key"]

                # Check if item matches criteria
                matches = (
                    item_key in what if what_is_key else any(pattern.match(item_key) for pattern in compiled_patterns)
                )
                if not matches:
                    continue

                if detail:
                    size_bytes = item.get("Size", 0)
                    item_data = {
                        "key": item_key,
                        "size": size_bytes,
                        "size_human": humanize.naturalsize(size_bytes),
                        "last_modified": item.get("LastModified"),
                        "etag": item.get("ETag", "").strip('"'),
                        "storage_class": item.get("StorageClass", ""),
                    }
                    if include_signed_urls:
                        item_data["signed_download_url"] = self.create_signed_download_url(item_key)
                    result.append(item_data)
                elif include_signed_urls:
                    result.append({
                        "key": item_key,
                        "signed_download_url": self.create_signed_download_url(item_key),
                    })
                else:
                    result.append(item_key)

        return result

    def create_signed_download_url(self, object_key: str, bucket_name: str | None = None) -> str:
        """Generates a signed URL to download a Google Cloud Storage object.

        Args:
            object_key (str): The key of the object to generate a signed URL for.
            bucket_name (str | None): The name of the bucket to generate a signed URL for.
                If None, use the default bucket.

        Returns:
            str: A signed URL that can be used to download from the bucket and key.
        """
        url = self._get_s3_client().generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self._settings.name if bucket_name is None else bucket_name, "Key": object_key},
            ExpiresIn=self._settings.download_signed_url_expiration_seconds,
        )
        return cast("str", url)

    @staticmethod
    def _download_object_from_signed_url(
        object_key: str,
        signed_url: str,
        destination: Path,
        etag: str | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> Path | None:
        """Download a single file from the bucket with content-based caching.

        Args:
            object_key (str): The key of the object to download.
            signed_url (str): The signed URL for downloading the object.
            destination (Path): The directory where the file should be saved.
            etag (str | None): The ETag of the object for cache validation.
            progress_callback (Callable[[int], None] | None): Optional callback for download progress.

        Returns:
            Path | None: The path to the downloaded file if successful, None otherwise.
        """
        filename = object_key.rsplit("/", 1)[-1]
        output_path = destination / filename

        # Check if we should download based on ETag comparison
        if etag:
            should_download = True
            if output_path.exists():
                try:
                    # Calculate hash of existing file and compare with ETag
                    hash_md5 = hashlib.md5()  # noqa: S324
                    with open(output_path, "rb") as f:
                        for chunk in iter(lambda: f.read(ETAG_CHUNK_SIZE), b""):
                            hash_md5.update(chunk)
                    file_hash = hash_md5.hexdigest()
                    should_download = file_hash != etag
                except OSError:
                    # If we can't read the file, download it
                    should_download = True

            if not should_download:
                logger.debug("File %s is up to date (ETag: %s), skipping download", output_path, etag)
                return output_path

        try:
            response = requests.get(signed_url, stream=True, timeout=60)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        if progress_callback:
                            progress_callback(len(chunk))

            logger.info("Successfully downloaded object with key '%s' to '%s'", object_key, output_path)
            return output_path

        except requests.RequestException:
            logger.exception("Failed to download %s", object_key)
            return None

    @staticmethod
    def download_static(
        what: list[str] | None = None,
        destination: Path = get_user_data_directory("bucket_downloads"),  # noqa: B008
        what_is_key: bool = False,
        progress_callback: Callable[[DownloadProgress], None] | None = None,
    ) -> DownloadResult:
        """Download files matching a pattern from the bucket, static method version.

        Args:
            what (list[str] | None): Patterns or keys to match object keys against - all if not specified.
            what_is_key (bool): If True, treat the pattern as a key, else as a regex.
            destination (Path): Destination directory for downloaded files.
            progress_callback (Callable[[DownloadProgress], None] | None): Optional callback for download progress.

        Returns:
            DownloadResult: Result containing lists of successfully downloaded and failed objects.

        Raises:
            ValueError: If any provided regex pattern is invalid.
        """
        return Service().download(what, destination, what_is_key, progress_callback)

    def download(
        self,
        what: list[str] | None = None,
        destination: Path = get_user_data_directory("bucket_downloads"),  # noqa: B008
        what_is_key: bool = False,
        progress_callback: Callable[[DownloadProgress], None] | None = None,
    ) -> DownloadResult:
        """Download files matching a pattern from the bucket.

        Args:
            what (list[str] | None): Patterns or keys to match object keys against - all if not specified.
            what_is_key (bool): If True, treat the pattern as a key, else as a regex.
            destination (Path): Destination directory for downloaded files.
            progress_callback (Callable[[DownloadProgress], None] | None): Optional callback for download progress.

        Returns:
            DownloadResult: Result containing lists of successfully downloaded and failed objects.

        Raises:
            ValueError: If any provided regex pattern is invalid.
        """
        destination.mkdir(parents=True, exist_ok=True)

        matched_objects = self.find(what, what_is_key, detail=True, include_signed_urls=True)

        if not matched_objects:
            return DownloadResult(downloaded=[], failed=[])

        logger.debug(
            "Found %d objects matching '%s' in bucket, downloading to '%s'...",
            len(matched_objects),
            what,
            destination,
        )

        progress = DownloadProgress(
            overall_total=len(matched_objects),
            overall_downloaded=0,
            overall_failed=0,
            current_file_key="",
            current_file_downloaded=0,
            current_file_size=0,
        )

        successful_downloads: list[Path] = []
        failed_downloads: list[str] = []

        for obj in matched_objects:
            obj_dict = cast("dict[str, str]", obj)
            object_key = obj_dict["key"]
            signed_url = obj_dict["signed_download_url"]

            progress = progress.model_copy(
                update={
                    "current_file_key": object_key,
                    "current_file_downloaded": 0,
                }
            )

            try:
                head_response = requests.head(signed_url, timeout=30)
                head_response.raise_for_status()
                file_size = int(head_response.headers.get("content-length", 0))
            except requests.RequestException:
                file_size = 0

            progress = progress.model_copy(update={"current_file_size": file_size})

            if progress_callback:
                progress_callback(progress)

            def file_progress_callback(bytes_downloaded: int) -> None:
                nonlocal progress
                progress = progress.model_copy(
                    update={"current_file_downloaded": progress.current_file_downloaded + bytes_downloaded}
                )
                if progress_callback:
                    progress_callback(progress)

            result_path = self._download_object_from_signed_url(
                object_key, signed_url, destination, obj_dict.get("etag"), file_progress_callback
            )

            if result_path:
                successful_downloads.append(result_path)
                progress = progress.model_copy(update={"overall_downloaded": progress.overall_downloaded + 1})
            else:
                failed_downloads.append(object_key)
                progress = progress.model_copy(update={"overall_failed": progress.overall_failed + 1})

            progress = progress.model_copy(
                update={
                    "current_file_key": "",
                    "current_file_downloaded": 0,
                    "current_file_size": 0,
                }
            )

            if progress_callback:
                progress_callback(progress)

        return DownloadResult(
            downloaded=successful_downloads,
            failed=failed_downloads,
        )

    @staticmethod
    def delete_static(what: list[str] | None, what_is_key: bool = False, dry_run: bool = True) -> int:
        """Delete objects, static variant.

        Args:
            what (list[str] | None): Patterns or keys to match object keys against - all if not specified.
            what_is_key (bool): If True, treat the entries as exact keys, else as regex patterns.
            dry_run (bool): If True, perform a dry run without actual deletion.

        Returns:
            int: Number of objects deleted.

        Raises:
            ValueError: If any provided regex pattern is invalid.
        """
        return Service().delete(what, what_is_key, dry_run)

    def delete(self, what: list[str] | None, what_is_key: bool = False, dry_run: bool = True) -> int:
        """Delete objects.

        Args:
            what (list[str] | None): Patterns or keys to match object keys against - all if not specified.
            what_is_key (bool): If True, treat the entries as exact keys, else as regex patterns.
            dry_run (bool): If True, perform a dry run without actual deletion.

        Returns:
            int: Number of objects deleted.

        Raises:
            ValueError: If any provided regex pattern is invalid.
        """
        from botocore.exceptions import ClientError  # noqa: PLC0415

        matched_objects = self.find(what, what_is_key=what_is_key, detail=False)
        object_keys_to_delete = [obj for obj in matched_objects if isinstance(obj, str)]

        if not object_keys_to_delete:
            logger.warning("No objects found to delete")
            return 0

        if dry_run:
            logger.info("Would delete %d objects", len(object_keys_to_delete))
            return len(object_keys_to_delete)

        s3c = self._get_s3_client()
        deleted_count = 0
        for object_key in object_keys_to_delete:
            logger.debug("Deleting object with key: %s", object_key)
            try:
                s3c.delete_object(Bucket=self._settings.name, Key=object_key)
                deleted_count += 1
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    logger.warning("Object with key '%s' not found", object_key)
                else:
                    logger.exception("Error deleting object with key '%s'", object_key)

        logger.info("Deleted %d objects", deleted_count)
        return deleted_count
