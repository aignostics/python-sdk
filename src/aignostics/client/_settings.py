import os
from pathlib import Path

import appdirs
from pydantic import SecretStr, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from aignostics import __project_name__

from ._messages import NOT_YET_IMPLEMENTED, UNKNOWN_ENDPOINT_URL


class AuthenticationSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix=f"{__project_name__.upper()}_",
        env_file=(
            os.getenv(f"{__project_name__.upper()}_ENV_FILE", Path.home() / f".{__project_name__}/env"),
            os.getenv(f"{__project_name__.upper()}_ENV_FILE", Path.home() / f".{__project_name__}/.env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    client_id_device: SecretStr
    client_id_interactive: SecretStr
    api_root: str = "https://platform.aignostics.com"

    scope: str = "offline_access"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def scope_elements(self) -> list[str]:
        if not self.scope:
            return []
        return [element.strip() for element in self.scope.split(",")]

    audience: str
    authorization_base_url: str
    token_url: str
    redirect_uri: str
    device_url: str
    jws_json_url: str

    refresh_token: SecretStr | None = None

    cache_dir: str = appdirs.user_cache_dir(__project_name__)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def token_file(self) -> Path:
        return Path(self.cache_dir) / ".token"

    request_timeout_seconds: int = 30
    authorization_backoff_seconds: int = 3

    @model_validator(mode="before")
    def pre_init(cls, values):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202, N805
        # See https://github.com/pydantic/pydantic/issues/9789
        api_root = values.get("api_root", "https://platform.aignostics.com")
        print(api_root)
        match api_root:
            case "https://platform.aignostics.com":
                # TODO (Andreas): hhva: please fill in
                raise RuntimeError(NOT_YET_IMPLEMENTED)
            case "http://platform-staging.aignostics.com":
                # TODO (Andreas): hhva: please fill in
                raise RuntimeError(NOT_YET_IMPLEMENTED)
            case "https://platform-dev.aignostics.com":
                values["audience"] = "https://dev-8ouohmmrbuh2h4vu-samia"
                values["authorization_base_url"] = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/authorize"
                values["token_url"] = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/oauth/token"  # noqa: S105
                values["redirect_uri"] = "http://localhost:8080/"
                values["device_url"] = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/oauth/device/code"
                values["jws_json_url"] = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/.well-known/jwks.json"
            case _:
                raise ValueError(UNKNOWN_ENDPOINT_URL)

        return values


__cached_authentication_settings: AuthenticationSettings | None = None


def authentication_settings() -> AuthenticationSettings:
    """Lazy load authentication settings from the environment or a file.

    * Given we use Pydantic Settings, validation is done automatically.
    * We only load and validate if we actually need the settings,
        thereby not killing the client on other actions.
    * If the settings have already been loaded, return the cached instance.

    Returns:
        AuthenticationSettings: The loaded authentication settings.
    """
    global __cached_authentication_settings  # noqa: PLW0603
    if __cached_authentication_settings is None:
        __cached_authentication_settings = AuthenticationSettings()  # pyright: ignore[reportCallIssue]
    return __cached_authentication_settings
