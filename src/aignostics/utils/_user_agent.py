"""Generate user agent string."""

import os
import platform

from ._constants import __project_name__, __version_full__


def user_agent() -> str:
    """Generate a user agent string for HTTP requests.

    Format: {project_name}/{version} ({platform}; {current_test})

    Returns:
        str: The user agent string.
    """
    current_test = os.getenv("PYTEST_CURRENT_TEST")
    return (
        f"{__project_name__}-python-sdk/{__version_full__} "
        f"({platform.platform()}"
        f"{'; ' + current_test if current_test else ''})"
    )
