"""Applications resource module for the Aignostics platform.

This module provides classes for interacting with application resources in the Aignostics API.
It includes functionality for listing applications and managing application versions.
"""

import builtins
import logging
import typing as t
from operator import itemgetter

import semver
from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.exceptions import NotFoundException, ServiceException
from aignx.codegen.models import ApplicationReadResponse as Application
from aignx.codegen.models import ApplicationReadShortResponse as ApplicationSummary
from aignx.codegen.models import ApplicationVersion as VersionTuple
from aignx.codegen.models import VersionReadResponse as ApplicationVersion
from tenacity import (
    Retrying,
    before_sleep_log,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)
from urllib3.exceptions import IncompleteRead, PoolError, ProtocolError, ProxyError
from urllib3.exceptions import TimeoutError as Urllib3TimeoutError

from aignostics.platform._operation_cache import cached_operation
from aignostics.platform._settings import settings
from aignostics.platform.resources.utils import paginate
from aignostics.utils import get_logger, user_agent

logger = get_logger(__name__)

RETRYABLE_EXCEPTIONS = (
    ServiceException,
    Urllib3TimeoutError,
    PoolError,
    IncompleteRead,
    ProtocolError,
    ProxyError,
)


class Versions:
    """Resource class for managing application versions.

    Provides operations to list and retrieve application versions.
    """

    def __init__(self, api: PublicApi) -> None:
        """Initializes the Versions resource with the API platform.

        Args:
            api (PublicApi): The configured API platform.
        """
        self._api = api

    def list(self, application: Application | str) -> list[VersionTuple]:
        """Find all versions for a specific application.

        Retries on network and server errors.

        Args:
            application (Application | str): The application to find versions for, either object or id

        Returns:
            list[VersionTuple]: List of the available application versions.

        Raises:
            aignx.codegen.exceptions.ApiException: If the API request fails.
        """
        application_id = application.application_id if isinstance(application, Application) else application

        @cached_operation(ttl=settings().application_cache_ttl, use_token=True)
        def list_with_retry(app_id: str) -> Application:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().application_retry_attempts),
                wait=wait_exponential_jitter(
                    initial=settings().application_retry_wait_min, max=settings().application_retry_wait_max
                ),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                reraise=True,
            )(
                lambda: self._api.read_application_by_id_v1_applications_application_id_get(
                    application_id=app_id,
                    _request_timeout=settings().application_timeout,
                    _headers={"User-Agent": user_agent()},
                )
            )

        app = list_with_retry(application_id)
        return app.versions if app.versions is not None else []

    def details(self, application_id: str, application_version: VersionTuple | str | None = None) -> ApplicationVersion:
        """Retrieves details for a specific application version.

        Retries on network and server errors.

        Args:
            application_id (str): The ID of the application.
            application_version (VersionTuple | str | None): The version of the application.
                If None, the latest version will be retrieved.

        Returns:
            ApplicationVersion: The version details.

        Raises:
            ValueError: If the version is not valid semver.
            NotFoundException: If the application or version is not found.
            aignx.codegen.exceptions.ApiException: If the API request fails.
        """
        # Handle version resolution and validation first (not retried)
        if application_version is None:
            application_version = self.latest(application=application_id)
            if application_version is None:
                message = f"No versions found for application '{application_id}'."
                raise NotFoundException(message)
            application_version = application_version.number
        elif isinstance(application_version, VersionTuple):
            application_version = application_version.number
        elif application_version and not semver.Version.is_valid(application_version):
            message = f"Invalid version format: '{application_version}' not compliant with semantic versioning."
            raise ValueError(message)

        # Make the API call with retry logic and caching
        @cached_operation(ttl=settings().application_version_cache_ttl, use_token=True)
        def details_with_retry(app_id: str, app_version: str) -> ApplicationVersion:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().application_version_retry_attempts),
                wait=wait_exponential_jitter(
                    initial=settings().application_version_retry_wait_min,
                    max=settings().application_version_retry_wait_max,
                ),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                reraise=True,
            )(
                lambda: self._api.application_version_details_v1_applications_application_id_versions_version_get(
                    application_id=app_id,
                    version=app_version,
                    _request_timeout=settings().application_version_timeout,
                    _headers={"User-Agent": user_agent()},
                )
            )

        return details_with_retry(application_id, application_version)

    # TODO(Helmut): Refactor given new API capabilities
    def list_sorted(self, application: Application | str) -> builtins.list[VersionTuple]:
        """Get application versions sorted by semver, descending.

        Args:
            application (Application | str): The application to find versions for, either object or id

        Returns:
            list[VersionTuple]: List of version objects sorted by semantic versioning (latest first),
                or empty list if no versions are found
        """
        versions = builtins.list(self.list(application=application))

        # If no versions available
        if not versions:
            return []

        # Extract semantic versions using proper semver parsing
        versions_with_semver = []
        for v in versions:
            try:
                parsed_version = semver.Version.parse(v.number)
                versions_with_semver.append((v, parsed_version))
            except (ValueError, AttributeError):
                # If we can't parse the version or version attribute doesn't exist, skip it
                continue

        # Sort by semantic version (semver objects have built-in comparison)
        if versions_with_semver:
            versions_with_semver.sort(key=itemgetter(1), reverse=True)
            # Return just the version objects, not the tuples
            return [item[0] for item in versions_with_semver]

        # If we couldn't parse any versions, return all versions as is
        return versions

    def latest(self, application: Application | str) -> VersionTuple | None:
        """Get latest version.

        Args:
            application (Application | str): The application to find versions for, either object or id

        Returns:
            VersionTuple | None: The latest version, or None if no versions found.
        """
        sorted_versions = self.list_sorted(application=application)
        return sorted_versions[0] if sorted_versions else None


class Applications:
    """Resource class for managing applications.

    Provides operations to list applications and access version resources.
    """

    def __init__(self, api: PublicApi) -> None:
        """Initializes the Applications resource with the API platform.

        Args:
            api (PublicApi): The configured API platform.
        """
        self._api = api
        self.versions: Versions = Versions(self._api)

    def details(self, application_id: str) -> Application:
        """Find application by id.

        Retries on network and server errors.

        Args:
            application_id (str): The ID of the application.

        Returns:
            Application: The application object

        Raises:
            NotFoundException: If the application with the given ID is not found.
            aignx.codegen.exceptions.ApiException: If the API call fails.
        """

        @cached_operation(ttl=settings().application_cache_ttl, use_token=True)
        def details_with_retry(application_id: str) -> Application:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().application_retry_attempts),
                wait=wait_exponential_jitter(
                    initial=settings().application_retry_wait_min, max=settings().application_retry_wait_max
                ),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                reraise=True,
            )(
                lambda: self._api.read_application_by_id_v1_applications_application_id_get(
                    application_id=application_id,
                    _request_timeout=settings().application_timeout,
                    _headers={"User-Agent": user_agent()},
                )
            )

        return details_with_retry(application_id)

    def list(self) -> t.Iterator[ApplicationSummary]:
        """Find all available applications.

        Retries on network and server errors for each page.

        Returns:
            Iterator[ApplicationSummary]: An iterator over the available applications.

        Raises:
            aignx.codegen.exceptions.ApiException: If the API request fails.
        """

        # Create a wrapper function that applies retry logic and caching to each API call
        # Caching at this level ensures having a fresh iterator on cache hits
        @cached_operation(ttl=settings().application_cache_ttl, use_token=True)
        def list_with_retry(**kwargs: object) -> list[ApplicationSummary]:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().application_retry_attempts),
                wait=wait_exponential_jitter(
                    initial=settings().application_retry_wait_min, max=settings().application_retry_wait_max
                ),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                reraise=True,
            )(
                lambda: self._api.list_applications_v1_applications_get(
                    _request_timeout=settings().application_timeout,
                    _headers={"User-Agent": user_agent()},
                    **kwargs,  # pyright: ignore[reportArgumentType]
                )
            )

        return paginate(list_with_retry)
