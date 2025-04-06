"""
This module provides the main client interface for interacting with Aignostics services.

It offers functionality for authentication, data management, and API operations.
The primary class in this module is the `Client` class, which serves as the entry point
for all interactions with the Aignostics platform.
"""

from aignostics.client._authentication import authentication_settings
from aignostics.client._client import Client
from aignostics.client.messages import AUTHENTICATION_FAILED

__all__ = [
    "AUTHENTICATION_FAILED",
    "Client",
    "authentication_settings",
]
