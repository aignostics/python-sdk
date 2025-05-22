"""Applications resource module for the Aignostics platform.

This module provides classes for interacting with application resources in the Aignostics API.
It includes functionality for listing applications and managing application versions.
"""

import builtins
import re
import typing as t
from operator import itemgetter

from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.models import ApplicationReadResponse as Application
from aignx.codegen.models import ApplicationVersionReadResponse as ApplicationVersion

from aignostics.platform.resources.utils import paginate


class Versions:
    """Resource class for managing application versions.

    Provides operations to list and retrieve application versions.
    """

    APPLICATION_VERSION_REGEX = re.compile(r"(?P<application_id>[^:]+):v?(?P<version>[^:]+)")

    def __init__(self, api: PublicApi) -> None:
        """Initializes the Versions resource with the API platform.

        Args:
            api (PublicApi): The configured API platform.
        """
        self._api = api

    def list(self, application: Application | str) -> t.Iterator[ApplicationVersion]:
        """Find all versions for a specific application.

        Args:
            application (Application | str): The application to find versions for, either object or id

        Returns:
            Iterator[ApplicationVersion]: A Iterator over the available application versions.

        Raises:
            Exception: If the API request fails.
        """
        application_id = application.application_id if isinstance(application, Application) else application

        return paginate(
            self._api.list_versions_by_application_id_v1_applications_application_id_versions_get,
            application_id=application_id,
        )

    # TODO(Andreas,Helmut): Discuss. This is getting an application version and returning it.
    # Can we make this a find_by_id, just getting an application_version_id as a string,
    # and returning the application version object?
    def details(self, application_version: ApplicationVersion | str) -> ApplicationVersion:
        """Retrieves details for a specific application version.

        Args:
            application_version (ApplicationVersion | str): The ID of the application version.

        Returns:
            ApplicationVersion: The version details.

        Raises:
            RuntimeError: If the application version ID is invalid or if the API request fails.
            Exception: If the API request fails.
        """
        if isinstance(application_version, ApplicationVersion):
            application_id = application_version.application_id
            version = application_version.version
        else:
            # split by colon
            m = Versions.APPLICATION_VERSION_REGEX.match(application_version)
            if not m:
                msg = f"Invalid application_version_id: {application_version}"
                raise RuntimeError(msg)
            application_id = m.group("application_id")
            version = m.group("version")

        application_versions = self._api.list_versions_by_application_id_v1_applications_application_id_versions_get(
            application_id=application_id,
            version=version,
        )
        if len(application_versions) != 1:
            # this invariance is enforced by the system. If that error occurs, we have an internal error
            msg = "Internal server error. Please contact Aignostics support."
            raise RuntimeError(msg)
        return application_versions[0]

    # TODO(Andreas): Remove when supported in backend
    def list_sorted(self, application: Application | str) -> builtins.list[ApplicationVersion]:
        """Get application versions sorted by semver, descending.

        Args:
            application (Application | str): The application to find versions for, either object or id

        Returns:
            list[ApplicationVersion]: List of version objects sorted by semantic versioning (latest first),
                or empty list if no versions are found
        """
        versions = builtins.list(self.list(application=application))

        # If no versions available
        if not versions:
            return []

        # Extract semantic versions from the version property
        versions_with_semver = []
        for v in versions:
            try:
                # Split into major, minor, patch components for proper comparison
                version_parts = [int(x) for x in v.version.split(".")]
                versions_with_semver.append((v, version_parts))
            except (ValueError, AttributeError):
                # If we can't parse the version or version attribute doesn't exist, skip it
                continue

        # Sort by semantic version (major, minor, patch)
        if versions_with_semver:
            versions_with_semver.sort(key=itemgetter(1), reverse=True)
            # Return just the version objects, not the tuples
            return [item[0] for item in versions_with_semver]

        # If we couldn't parse any versions, return all versions as is
        return versions

    def latest(self, application: Application | str) -> ApplicationVersion | None:
        """Get latest version.

        Args:
            application (Application | str): The application to find versions for, either object or id

        Returns:
            ApplicationVersion | None: The latest version id, or None if no versions found.
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

    def list(self) -> t.Iterator[Application]:
        """Find all available applications.

        Returns:
            Iterator[Application]: A Iterator over the available applications.

        Raises:
            Exception: If the API request fails.
        """
        return paginate(self._api.list_applications_v1_applications_get)
