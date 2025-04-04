from aignx.codegen.api.externals_api import ExternalsApi
from aignx.codegen.models import ApplicationReadResponse, ApplicationVersionReadResponse, VersionReadResponse


class Versions:
    """Resource class for managing application versions.

    Provides operations to list and retrieve application versions.
    """

    def __init__(self, api: ExternalsApi):
        """Initializes the Versions resource with the API client.

        Args:
            api: The configured API client.
        """
        self._api = api

    def list(self, for_application: ApplicationReadResponse | str) -> list[ApplicationVersionReadResponse]:
        """Lists all versions for a specific application.

        Args:
            for_application: Either an ApplicationReadResponse object or
                an application ID string.

        Returns:
            list[ApplicationVersionReadResponse]: A list of application versions.

        Raises:
            Exception: If the API request fails.
        """
        if isinstance(for_application, ApplicationReadResponse):
            application_id = for_application.application_id
        else:
            application_id = for_application
        res = self._api.list_versions_by_application_id_v1_applications_application_id_versions_get(
            application_id=application_id
        )
        return res

    def details(self, for_application_version_id: str) -> VersionReadResponse:
        """Retrieves details for a specific application version.

        Args:
            for_application_version_id: The ID of the application version.

        Returns:
            VersionReadResponse: The version details.

        Raises:
            Exception: If the API request fails.
        """
        return self._api.get_version_v1_versions_application_version_id_get(
            application_version_id=for_application_version_id
        )


class Applications:
    """Resource class for managing applications.

    Provides operations to list applications and access version resources.
    """

    def __init__(self, api: ExternalsApi):
        """Initializes the Applications resource with the API client.

        Args:
            api: The configured API client.
        """
        self._api = api
        self.versions: Versions = Versions(self._api)

    def list(self) -> list[ApplicationReadResponse]:
        """Lists all available applications.

        Returns:
            list[ApplicationReadResponse]: A list of applications.

        Raises:
            Exception: If the API request fails.
        """
        res = self._api.list_applications_v1_applications_get()
        return res
