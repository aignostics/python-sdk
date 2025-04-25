"""Applications resource module for the Aignostics platform.

This module provides classes for interacting with application resources in the Aignostics API.
It includes functionality for listing applications and managing application versions.
"""

import re
import typing as t

from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.models import ApplicationReadResponse, ApplicationVersionReadResponse

from aignostics.platform.resources.utils import paginate


class Versions:
    """Resource class for managing application versions.

    Provides operations to list and retrieve application versions.
    """

    APPLICATION_VERSION_REGEX = re.compile(r"(?P<application_id>[^:]+):v?(?P<version>[^:]+)")

    def __init__(self, api: PublicApi) -> None:
        """Initializes the Versions resource with the API platform.

        Args:
            api: The configured API platform.
        """
        self._api = api

    def list(self, application: ApplicationReadResponse | str) -> t.Iterator[ApplicationVersionReadResponse]:
        """Lists all versions for a specific application.

        Args:
            application: Either an ApplicationReadResponse object or
                an application ID string.

        Returns:
            Iterator[ApplicationVersionReadResponse]: A Iterator over the available application versions.

        Raises:
            Exception: If the API request fails.
        """
        application_id = application.application_id if isinstance(application, ApplicationReadResponse) else application

        return paginate(
            self._api.list_versions_by_application_id_v1_applications_application_id_versions_get,
            application_id=application_id,
        )

    def details(self, application_version: ApplicationVersionReadResponse | str) -> ApplicationVersionReadResponse:
        """Retrieves details for a specific application version.

        Args:
            application_version: The ID of the application version.

        Returns:
            VersionReadResponse: The version details.

        Raises:
            RuntimeError: If the application version ID is invalid or if the API request fails.
            Exception: If the API request fails.
        """
        if isinstance(application_version, ApplicationVersionReadResponse):
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


class Applications:
    """Resource class for managing applications.

    Provides operations to list applications and access version resources.
    """

    def __init__(self, api: PublicApi) -> None:
        """Initializes the Applications resource with the API platform.

        Args:
            api: The configured API platform.
        """
        self._api = api
        self.versions: Versions = Versions(self._api)

    def list(self) -> t.Iterator[ApplicationReadResponse]:
        """Lists all available applications.

        Returns:
            Iterator[ApplicationReadResponse]: A Iterator over the available applications.

        Raises:
            Exception: If the API request fails.
        """
        return paginate(self._api.list_applications_v1_applications_get)
