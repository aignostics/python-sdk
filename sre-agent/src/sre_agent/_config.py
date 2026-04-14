"""Configuration for the SRE incident response agent."""

from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SREAgentSettings(BaseSettings):
    """Settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="SRE_")

    # Anthropic Managed Agent resources (created by _setup.py)
    agent_id: str
    environment_id: str
    vault_id: str

    # BetterStack API (for fetching incident details)
    betterstack_api_token: SecretStr

    # GitHub repo to mount in the agent session
    github_repo: str = "aignostics/python-sdk"
