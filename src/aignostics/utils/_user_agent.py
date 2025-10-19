"""Generate user agent string."""

import os
import platform

from ._constants import __project_name__, __repository_url__, __version_full__


def user_agent() -> str:
    """Generate a user agent string for HTTP requests.

    Format: {project_name}/{version} ({platform}; {current_test}; {github_run})

    Returns:
        str: The user agent string.
    """
    current_test = os.getenv("PYTEST_CURRENT_TEST")  # Set if running under pytest
    github_run_id = os.getenv("GITHUB_RUN_ID")  # Set if running in GitHub Actions
    github_repository = os.getenv("GITHUB_REPOSITORY")  # Set if running in GitHub Actions

    optional_parts = []

    if current_test:
        optional_parts.append(current_test)

    if github_run_id and github_repository:
        github_run_url = f"+https://github.com/{github_repository}/actions/runs/{github_run_id}"
        optional_parts.append(github_run_url)

    optional_suffix = "; " + "; ".join(optional_parts) if optional_parts else ""

    # TODO(Helmut): Find a way to not hard code python-sdk here.
    # Format: {project}/{version} ({platform}; {repository}; {optional_parts})
    base_info = f"{__project_name__}-python-sdk/{__version_full__}"
    system_info = f"{platform.platform()}; +{__repository_url__}{optional_suffix}"

    return f"{base_info} ({system_info})"
