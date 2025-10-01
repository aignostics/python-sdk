"""Service of the platform module."""

import json
import time
from http import HTTPStatus
from typing import Any

import urllib3
from aignx.codegen.models import MeReadResponse as Me
from aignx.codegen.models import OrganizationReadResponse as Organization
from aignx.codegen.models import UserReadResponse as User
from pydantic import BaseModel, computed_field

from aignostics.utils import UNHIDE_SENSITIVE_INFO, BaseService, Health, get_logger, user_agent

from ._authentication import get_token, remove_cached_token, verify_and_decode_token
from ._client import Client
from ._settings import Settings

logger = get_logger(__name__)


class TokenInfo(BaseModel):
    """Class to store token information."""

    issuer: str  # iss
    issued_at: int  # iat
    expires_at: int  # exp
    scope: list[str]  # scope
    audience: list[str]  # aud
    authorized_party: str  # azp

    org_id: str  # org_id
    role: str  # https://audience/role

    @computed_field  # type: ignore[prop-decorator]
    @property
    def expires_in(self) -> int:
        """Calculate seconds until token expires.

        Returns:
            int: Number of seconds until the token expires. Negative if already expired.
        """
        return self.expires_at - int(time.time())

    @classmethod
    def from_claims(cls, claims: dict[str, Any]) -> "TokenInfo":
        """Create TokenInfo from JWT claims.

        Args:
            claims: JWT token claims dictionary.

        Returns:
            TokenInfo: Token information extracted from claims.
        """
        audience = claims["aud"] if isinstance(claims["aud"], list) else [claims["aud"]]

        return cls(
            issuer=claims["iss"],
            issued_at=claims["iat"],
            expires_at=claims["exp"],
            scope=claims["scope"].split(),
            audience=audience,
            authorized_party=claims["azp"],
            org_id=claims["org_id"],
            role=claims.get(audience[0] + "/role", "member"),
        )


class UserInfo(BaseModel):
    """Class to store info about the user."""

    role: str  # token.CLAIM_ROLE
    token: TokenInfo
    user: User
    organization: Organization

    @classmethod
    def from_claims_and_me(cls, claims: dict[str, Any], me: Me) -> "UserInfo":
        """Create UserInfo from JWT claims and optional auth0 userinfo.

        Args:
            claims (dict[str, Any]): JWT token claims dictionary.
            me (Me): Info about calling user and their oganisation.

        Returns:
            UserInfo: User information extracted from claims.
        """
        token = TokenInfo.from_claims(claims)
        return cls(
            role=token.role,
            token=token,
            user=me.user,
            organization=me.organization,
        )

    def model_dump_secrets_masked(self) -> dict[str, Any]:
        """Dump model to dict with sensitive organization and user secrets masked.

        Returns:
            dict[str, Any]: Dictionary representation with sensitive organization and user fields masked.
        """
        data = self.model_dump(mode="json")

        # Define mapping of data keys to their sensitive fields
        sensitive_fields_mapping = {
            "organization": [
                "aignostics_bucket_hmac_secret_access_key",
                "aignostics_logfire_token",
                "aignostics_sentry_dsn",
            ],
            "user": ["email"],
        }

        # Mask sensitive fields for each data section
        for data_key, secret_fields in sensitive_fields_mapping.items():
            if data.get(data_key):
                section_data = data[data_key]
                for field_name in secret_fields:
                    if section_data.get(field_name):
                        original_value = section_data[field_name]
                        section_data[field_name] = f"***MASKED({len(original_value)})***"

        return data

    def model_dump_json_secrets_masked(self) -> str:
        """Dump model to JSON with sensitive organization secrets masked.

        Returns:
            str: JSON representation with aignostics_bucket_hmac_access_key_id and
                 aignostics_bucket_hmac_secret_access_key masked.
        """
        return json.dumps(self.model_dump_secrets_masked())


# Services derived from BaseService and exported by modules via their __init__.py are automatically registered
# with the system module, enabling for dynamic discovery of health, info and further functionality.
class Service(BaseService):
    """Service of the application module."""

    _settings: Settings

    def __init__(self) -> None:
        """Initialize service."""
        super().__init__(Settings)  # automatically loads and validates the settings

    def info(self, mask_secrets: bool = True) -> dict[str, Any]:
        """Determine info of this service.

        Args:
            mask_secrets (bool): Whether to mask sensitive information in the output.

        Returns:
            dict[str,Any]: The info of this service.
        """
        user_info = self.get_user_info(relogin=mask_secrets)
        return {
            "settings": self._settings.model_dump(context={UNHIDE_SENSITIVE_INFO: not mask_secrets}),
            "userinfo": (user_info.model_dump_secrets_masked() if mask_secrets else user_info.model_dump(mode="json"))
            if user_info
            else None,
        }

    def _determine_api_public_health(self) -> Health:
        """Determine healthiness and reachability of Aignostics Platform API.

        - Checks if health endpoint is reachable and returns 200 OK
        - Uses urllib3 for a direct connection check without authentication

        Returns:
            Health: The healthiness of the Aignostics Platform API via basic unauthenticated request.
        """
        try:
            http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=5.0, read=10.0))
            response = http.request(
                method="GET",
                url=f"{self._settings.api_root}/api/v1/health",
                headers={"User-Agent": user_agent()},
            )

            if response.status != HTTPStatus.OK:
                logger.error("Aignostics Platform API (public) returned '%s'", response.status)
                return Health(
                    status=Health.Code.DOWN, reason=f"Aignostics Platform API returned status '{response.status}'"
                )
        except Exception as e:
            logger.exception("Issue with Aignostics Platform API")
            return Health(status=Health.Code.DOWN, reason=f"Issue with Aignostics Platform API: '{e}'")

        return Health(status=Health.Code.UP)

    def _determine_api_authenticated_health(self) -> Health:
        """Determine healthiness and reachability of Aignostics Platform API via authenticated API client.

        - Checks if health endpoint is reachable and returns 200 OK

        Returns:
            Health: The healthiness of the Aignostics Platform API when trying to reach via authenticated API client.
        """
        try:
            client = Client()
            api_client = client.get_api_client(cache_token=True).api_client
            response = api_client.call_api(
                url=self._settings.api_root + "/api/v1/health",
                method="GET",
            )
            if response.status != HTTPStatus.OK:
                logger.error("Aignostics Platform API (authenticated) returned '%s'", response.status)
                return Health(status=Health.Code.DOWN, reason=f"Aignostics Platform API returned '{response.status}'")
        except Exception as e:
            logger.exception("Issue with Aignostics Platform API")
            return Health(status=Health.Code.DOWN, reason=f"Issue with Aignostics Platform API: '{e}'")
        return Health(status=Health.Code.UP)

    def health(self) -> Health:
        """Determine health of this service.

        Returns:
            Health: The health of the service.
        """
        return Health(
            status=Health.Code.UP,
            components={
                "api_public": self._determine_api_public_health(),
                "api_authenticated": self._determine_api_authenticated_health(),
            },
        )

    @staticmethod
    def login(relogin: bool = False) -> bool:
        """Login.

        Args:
            relogin (bool): If True, forces a re-login even if a token is cached.

        Returns:
            bool: True if successfully logged in, False if login failed
        """
        if relogin:
            Service.logout()
        try:
            _ = get_token(use_cache=True)
            return True
        except RuntimeError as e:
            message = f"Error during login: {e!s}"
            logger.exception(message)
            return False

    @staticmethod
    def logout() -> bool:
        """Logout if authenticated.

        Deletes the cached authentication token if existing.

        Returns:
            bool: True if successfully logged out, False if not logged in.
        """
        return remove_cached_token()

    @staticmethod
    def get_user_info(relogin: bool = False) -> UserInfo:
        """Get user information from authentication token.

        Args:
            relogin (bool): If True, forces a re-login even if a token is cached.

        Returns:
            UserInfo | None: User information if successfully authenticated, None if login failed.

        Raises:
            RuntimeError: If the token cannot be verified or decoded.
        """
        if relogin:
            Service.logout()
        try:
            return UserInfo.from_claims_and_me(verify_and_decode_token(get_token()), Client().me())
        except RuntimeError as e:
            message = f"Error during login: {e!s}"
            logger.exception(message)
            raise
