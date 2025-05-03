"""Service of the bucket module."""

from typing import Any

import s3fs
from boto3 import Session
from botocore.client import Config

from aignostics.utils import BaseService, Health, get_logger

from ._settings import Settings

logger = get_logger(__name__)

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

    def _get_s3_client(self, endpoint_url: str = ENDPOINT_URL_DEFAULT):  # noqa: ANN202
        """Get a Boto3 S3 client instance for cloud bucket on Aignostics Platform.

        Returns:
            botocore.client.S3: A Boto3 S3 client instance.
        """
        # https://www.kmp.tw/post/accessgcsusepythonboto3/
        session = Session(
            aws_access_key_id=self._settings.hmac_access_key_id.get_secret_value(),
            aws_secret_access_key=self._settings.hmac_secret_access_key.get_secret_value(),
            region_name=self._settings.region_name,
        )
        return session.client("s3", endpoint_url=endpoint_url, config=Config(signature_version=SIGNATURE_VERSION))

    def s3fs(self, endpoint_url: str = ENDPOINT_URL_DEFAULT) -> s3fs.S3FileSystem:
        """Get a file system instance for cloud bucket on Aignostics Platform.

        Returns:
            s3fs.S3FileSystem: A Boto3 S3 file system instance.
        """
        return s3fs.S3FileSystem(
            key=self._settings.hmac_access_key_id.get_secret_value(),
            secret=self._settings.hmac_secret_access_key.get_secret_value(),
            endpoint_url=endpoint_url,
            client_kwargs={"region_name": self._settings.region_name},
            config_kwargs={"signature_version": SIGNATURE_VERSION},
        )

    def get_bucket_name(self) -> str:
        """Get the bucket name.

        Returns:
            str: The bucket name.
        """
        return self._settings.name

    def ls(self, detail: bool = False) -> list[str | dict[str, Any]]:
        """List objects.

        Returns:
            detail (bool): If True, return detailed information, else return only names.
            list[str]: List of objects in the bucket.
        """
        s3fs = self.s3fs()
        return s3fs.ls(self._settings.name, detail=detail)

    def find(self, detail: bool = False) -> list[str | dict[str, Any]]:
        """List objects.

        Returns:
            detail (bool): If True, return detailed information, else return only names.
            list[str]: List of objects in the bucket.
        """
        s3fs = self.s3fs()
        result = s3fs.find(self._settings.name, withdirs=True, detail=detail)
        if detail:
            # Filter out entries with empty or None key
            return [item for item in result.values() if item.get("Key") not in (None, "")]  # type: ignore
        return result  # type: ignore

    def delete_objects(self, keys: list[str]) -> bool:
        """Delete  objects.

        Args:
            keys (list[str]): List of keys to delete.

        Returns:
            bool: True if successful, False otherwise.
        """
        s3fs = self.s3fs()
        for key in keys:
            s3fs.rm(key)
        #        s3c = self._get_s3_client()
        #        s3c.delete_objects(
        #            Bucket=self._settings.name,
        #            Delete={
        #                "Objects": [{"Key": key} for key in keys],
        #            },
        #        )
        return True
