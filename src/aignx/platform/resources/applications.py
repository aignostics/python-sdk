from aignx.codegen.api.externals_api import ExternalsApi
from aignx.codegen.models import ApplicationVersionReadResponse, VersionReadResponse
from aignx.codegen.models.application_read_response import ApplicationReadResponse


class Versions:
    def __init__(self, api: ExternalsApi):
        self._api = api

    def list(self, for_application: ApplicationReadResponse | str) -> list[ApplicationVersionReadResponse]:
        if isinstance(for_application, ApplicationReadResponse):
            application_id = for_application.application_id
        else:
            application_id = for_application
        res = self._api.list_versions_by_application_id_v1_applications_application_id_versions_get(
            application_id=application_id
        )
        return res

    def __call__(self, for_application_version_id: str) -> VersionReadResponse:
        return self._api.get_version_v1_versions_application_version_id_get(
            application_version_id=for_application_version_id
        )


class Applications:
    def __init__(self, api: ExternalsApi):
        self._api = api
        self.versions = Versions(self._api)

    def list(self) -> list[ApplicationReadResponse]:
        res = self._api.list_applications_v1_applications_get()
        return res
