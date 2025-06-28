"""Service of the platform module."""

import time
from datetime import datetime
from http import HTTPStatus
from typing import Any

import urllib3
from pydantic import BaseModel, computed_field

from aignostics.utils import UNHIDE_SENSITIVE_INFO, BaseService, Health, __version__, get_logger

from ._authentication import CLAIM_ROLE, get_token, remove_cached_token, userinfo, verify_and_decode_token
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
        return cls(
            issuer=claims["iss"],
            issued_at=claims["iat"],
            expires_at=claims["exp"],
            scope=claims["scope"].split(),
            audience=claims["aud"] if isinstance(claims["aud"], list) else [claims["aud"]],
            authorized_party=claims["azp"],
        )


class UserProfile(BaseModel):
    """Class to store info about the user."""

    name: str | None = None  # userinfo.name
    given_name: str | None = None  # userinfo.given_name
    family_name: str | None = None  # userinfo.family_name
    nickname: str | None = None  # userinfo.nickname
    email: str | None = None  # userinfo.email
    email_verified: bool | None = None  # userinfo.email_verified
    picture: str | None = None  # userinfo.picture
    updated_at: datetime | None = None  # userinfo.updated_at

    @classmethod
    def from_userinfo(cls, userinfo: dict[str, Any]) -> "UserProfile":
        """Create UserProfile from auth0 userinfo.

        Args:
            userinfo (dict[str, Any] | None): User information dictionary from auth0.

        Returns:
            UserProfile: User information extracted from auth0 userinfo.
        """
        return cls(
            name=userinfo.get("name"),
            given_name=userinfo.get("given_name"),
            family_name=userinfo.get("family_name"),
            nickname=userinfo.get("nickname"),
            email=userinfo.get("email"),
            email_verified=userinfo.get("email_verified"),
            picture=userinfo.get("picture"),
            updated_at=userinfo.get("updated_at"),
        )


class UserInfo(BaseModel):
    """Class to store info about the user."""

    id: str  # token.sub
    org_id: str  # token.org_id
    org_name: str | None  # token.org_name
    role: str  # token.CLAIM_ROLE
    token: TokenInfo
    profile: UserProfile | None = None

    @classmethod
    def from_claims_and_userinfo(cls, claims: dict[str, Any], userinfo: dict[str, Any] | None = None) -> "UserInfo":
        """Create UserInfo from JWT claims and optional auth0 userinfo.

        Args:
            claims (dict[str, Any]): JWT token claims dictionary.
            userinfo (dict[str, Any] | None): Optional user information dictionary from auth0.

        Returns:
            UserInfo: User information extracted from claims.
        """
        return cls(
            id=claims["sub"],
            org_id=claims["org_id"],
            org_name=claims.get("org_name"),
            role=claims[CLAIM_ROLE],
            token=TokenInfo.from_claims(claims),
            profile=UserProfile.from_userinfo(userinfo) if userinfo else None,
        )


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
            "userinfo": user_info.model_dump(mode="json") if user_info else None,
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
                headers={"User-Agent": f"aignostics-python-sdk/{__version__}"},
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
        logger.debug("Logging out...")
        rtn = remove_cached_token()
        logger.debug("Logout successful: %s", rtn)
        return rtn

    @staticmethod
    def get_user_info(relogin: bool = False) -> UserInfo | None:
        """Get user information from authentication token.

        Args:
            relogin (bool): If True, forces a re-login even if a token is cached.

        Returns:
            UserInfo | None: User information if successfully authenticated, None if login failed.
        """
        if relogin:
            Service.logout()
        try:
            token = get_token(use_cache=True)
            claims = verify_and_decode_token(token)
            info = None
            try:
                info = userinfo(token)
            except RuntimeError as e:
                message = f"Error retrieving user info: {e!s}"
                logger.exception(message)
            return UserInfo.from_claims_and_userinfo(claims, info)
        except RuntimeError as e:
            message = f"Error during login: {e!s}"
            logger.exception(message)
            return None
