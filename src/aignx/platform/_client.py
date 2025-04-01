import httpx

from aignx.codegen.api.externals_api import ExternalsApi
from aignx.codegen.api_client import ApiClient
from aignx.codegen.configuration import Configuration
from aignx.platform._authentication import get_token
from aignx.platform.resources.applications import Applications, Versions
from aignx.platform.resources.runs import Runs

API_ROOT = "https://platform-dev.aignostics.com"


class Client:
    def __init__(self):
        self._api = Client._get_api_client()
        self.applications: Applications = Applications(self._api)
        self.versions: Versions = Versions(self._api)
        self.runs: Runs = Runs(self._api)

    def _check_health(self):
        httpx.get(str(API_ROOT) + "/health")

    @staticmethod
    def _get_api_client() -> ExternalsApi:
        token = get_token()
        client = ApiClient(
            Configuration(
                host=API_ROOT,
                # debug=True,
                # the following can be used if the auth is set in the schema
                # api_key={"Authorization": T},
                # api_key_prefix={"Authorization": "Bearer"},
            ),
            header_name="Authorization",
            header_value=f"Bearer {token}"
        )
        return ExternalsApi(client)
