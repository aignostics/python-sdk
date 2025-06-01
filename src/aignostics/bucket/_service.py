"""Service of the bucket module."""

from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any, cast

import requests
from botocore.client import BaseClient, Config
from botocore.exceptions import ClientError

from aignostics.utils import BaseService, Health, get_logger

from ._settings import Settings

logger = get_logger(__name__)

BUCKET_PROTOCOL = "gs"
ENDPOINT_URL_DEFAULT = "https://storage.googleapis.com"
SIGNATURE_VERSION = "s3v4"


class Service(BaseService):
    """Service of the bucket module."""

    _settings: Settings

    def __init__(self) -> None:
        """Initialize service."""
        super().__init__(Settings)

    def info(self) -> dict[str, Any]:  # noqa: PLR6301
        """Determine info of this service.

        Returns:
            dict[str,Any]: The info of this service.
        """
        return {}

    def health(self) -> Health:  # noqa: PLR6301
        """Determine health of this service.

        Returns:
            Health: The health of the service.
        """
        return Health(
            status=Health.Code.UP,
            components={},
        )

    def _get_s3_client(self, endpoint_url: str = ENDPOINT_URL_DEFAULT) -> BaseClient:
        """Get a Boto3 S3 client instance for cloud bucket on Aignostics Platform.

        Args:
            endpoint_url (str): The endpoint URL for the S3 service.

        Returns:
            BaseClient: A Boto3 S3 client instance.
        """
        from boto3 import Session  # noqa: PLC0415

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
            ExpiresIn=3600,
        )
        return cast("str", url)

    def upload_file(
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
                        chunk = f.read(1048576)  # ~1MB chunks
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
            ExpiresIn=3600,
        )
        return cast("str", url)

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
            if self.upload_file(source_path, object_key, callback):
                results["success"].append(object_key)
            else:
                results["failed"].append(object_key)

        elif source_path.is_dir():
            for file_path in source_path.glob("**/*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(source_path)
                    object_key = f"{destination_prefix}/{rel_path}"

                    if self.upload_file(file_path, object_key, callback):
                        results["success"].append(object_key)
                    else:
                        results["failed"].append(object_key)
        else:
            logger.error("Source path '%s' is neither a file nor directory", source_path)

        return results

    def ls(self, detail: bool = False) -> list[str | dict[str, Any]]:
        """List objects directly in the bucket (non-recursive).

        Args:
            detail (bool): If True, return detailed information including object type, else return only paths.

        Returns:
            list[Union[str, dict[str, Any]]]: List of objects directly in the bucket with optional detail.
        """
        s3c = self._get_s3_client()
        response = s3c.list_objects_v2(Bucket=self._settings.name, Prefix="", Delimiter="/")

        result: list[str | dict[str, Any]] = []
        contents = response.get("Contents", [])
        common_prefixes = response.get("CommonPrefixes", [])

        if detail:
            # Process directories (common prefixes)
            for prefix in common_prefixes:
                if prefix.get("Prefix") not in {None, ""}:
                    prefix_path = f"{self._settings.name}/{prefix['Prefix']}"
                    result.append({
                        "key": prefix_path,
                        "size": 0,
                        "last_modified": None,
                        "etag": "",
                        "storage_class": "",
                        "type": "directory",
                    })

            # Process files
            for item in contents:
                if item.get("Key") not in {None, ""}:
                    # Determine if this item is a "directory" (ends with /)
                    item_key = item["Key"]
                    item_type = "directory" if item_key.endswith("/") else "file"
                    item_path = f"{self._settings.name}/{item_key}"

                    result.append({
                        "key": item_path,
                        "size": item.get("Size", 0),
                        "last_modified": item.get("LastModified"),
                        "etag": item.get("ETag", "").strip('"'),
                        "storage_class": item.get("StorageClass", ""),
                        "type": item_type,
                    })
        else:
            # Process directories (common prefixes) for non-detailed view
            for prefix in common_prefixes:
                if prefix.get("Prefix") not in {None, ""}:
                    prefix_path = f"{self._settings.name}/{prefix['Prefix']}"
                    result.append(prefix_path)

            # Process files for non-detailed view
            for item in contents:
                if item.get("Key") not in {None, ""}:
                    item_path = f"{self._settings.name}/{item['Key']}"
                    result.append(item_path)

        return result

    def find(self, detail: bool = False) -> list[str | dict[str, Any]]:  # noqa: C901
        """List objects recursively in the bucket.

        Args:
            detail (bool): If True, return detailed information including object type, else return only paths.

        Returns:
            list[Union[str, dict[str, Any]]]: List of objects in the bucket with optional detail.
        """
        s3c = self._get_s3_client()
        paginator = s3c.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=self._settings.name)

        result: list[str | dict[str, Any]] = []
        for page in pages:
            contents = page.get("Contents", [])
            common_prefixes = page.get("CommonPrefixes", [])

            if detail:
                # Process directories (common prefixes)
                for prefix in common_prefixes:
                    if prefix.get("Prefix") not in {None, ""}:
                        prefix_path = f"{prefix['Prefix']}"
                        result.append({
                            "key": prefix_path,
                            "size": 0,
                            "last_modified": None,
                            "etag": "",
                            "storage_class": "",
                            "type": "directory",
                        })

                # Process files
                for item in contents:
                    if item.get("Key") not in {None, ""}:
                        # Determine if this item is a "directory" (ends with /)
                        item_key = item["Key"]
                        item_type = "directory" if item_key.endswith("/") else "file"
                        item_path = f"{item_key}"

                        result.append({
                            "key": item_path,
                            "size": item.get("Size", 0),
                            "last_modified": item.get("LastModified"),
                            "etag": item.get("ETag", "").strip('"'),
                            "storage_class": item.get("StorageClass", ""),
                            "type": item_type,
                        })
            else:
                # Process directories (common prefixes) for non-detailed view
                for prefix in common_prefixes:
                    if prefix.get("Prefix") not in {None, ""}:
                        prefix_path = f"{prefix['Prefix']}"
                        result.append(prefix_path)

                # Process files for non-detailed view
                for item in contents:
                    if item.get("Key") not in {None, ""}:
                        item_path = f"{item['Key']}"
                        result.append(item_path)

        return result

    def delete_objects(self, keys: list[str]) -> bool:
        """Delete  objects.

        Args:
            keys (list[str]): List of keys to delete.

        Returns:
            bool: True if successful, False otherwise.
        """
        s3c = self._get_s3_client()
        for key in keys:
            logger.debug("Deleting key: %s", key)
            # Strip bucket prefix if present in key
            pruned_key = key.removeprefix(f"{self._settings.name}/")
            try:
                s3c.delete_object(Bucket=self._settings.name, Key=pruned_key)
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    logger.warning("Object with key '%s' not found", key)
                    return False
                logger.exception("Error deleting object with key '%s'", key)
                return False
        logger.info("Deleted %d objects", len(keys))
        return True
