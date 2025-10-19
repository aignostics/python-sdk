"""SDK metadata generation for application runs.

This module provides functionality to build structured metadata about the SDK execution context,
including user information, CI/CD environment details, and test execution context.
"""

import os
import sys
from datetime import UTC, datetime
from typing import Any

from aignostics.utils import get_logger, user_agent

logger = get_logger(__name__)

SDK_METADATA_SCHEMA_VERSION = "0.0.1-alpha"


def build_sdk_metadata() -> dict[str, Any]:
    """Build SDK metadata to attach to runs.

    Includes user agent, user information, GitHub CI/CD context when running in GitHub Actions,
    and test context when running in pytest.

    Returns:
        dict[str, Any]: Dictionary containing SDK metadata including user agent,
            user information, and optionally CI information (GitHub workflow and pytest test context).
    """
    from aignostics.platform._client import Client  # noqa: PLC0415

    submission_source = "user"  # who/what initiated the run (user, test, bridge)
    submission_interface = "script"  # how the SDK was accessed (script, cli, launchpad)

    if os.environ.get("AIGNOSTICS_BRIDGE_VERSION"):
        submission_source = "bridge"
    elif os.environ.get("PYTEST_CURRENT_TEST"):
        submission_source = "test"

    if "typer" in sys.argv[0] or "aignostics" in sys.argv[0]:
        submission_interface = "cli"
    elif os.getenv("NICEGUI_HOST"):
        submission_interface = "launchpad"

    metadata: dict[str, Any] = {
        "schema_version": SDK_METADATA_SCHEMA_VERSION,
        "submission": {
            "date": datetime.now(UTC).isoformat(timespec="seconds"),
            "interface": submission_interface,
            "source": submission_source,
        },
        "user_agent": user_agent(),
    }

    try:
        me = Client().me()
        metadata["user"] = {
            "organization_id": me.organization.id,
            "organization_name": me.organization.name,
            "user_email": me.user.email,
            "user_id": me.user.id,
        }
    except Exception:  # noqa: BLE001
        logger.warning("Failed to fetch user information for SDK metadata")

    ci_metadata: dict[str, Any] = {}

    github_run_id = os.environ.get("GITHUB_RUN_ID")
    if github_run_id:
        github_server_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
        github_repository = os.environ.get("GITHUB_REPOSITORY", "")

        ci_metadata["github"] = {
            "action": os.environ.get("GITHUB_ACTION"),
            "job": os.environ.get("GITHUB_JOB"),
            "ref": os.environ.get("GITHUB_REF"),
            "ref_name": os.environ.get("GITHUB_REF_NAME"),
            "ref_type": os.environ.get("GITHUB_REF_TYPE"),
            "repository": github_repository,
            "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "run_id": github_run_id,
            "run_number": os.environ.get("GITHUB_RUN_NUMBER"),
            "run_url": f"{github_server_url}/{github_repository}/actions/runs/{github_run_id}",
            "runner_arch": os.environ.get("RUNNER_ARCH"),
            "runner_os": os.environ.get("RUNNER_OS"),
            "sha": os.environ.get("GITHUB_SHA"),
            "workflow": os.environ.get("GITHUB_WORKFLOW"),
            "workflow_ref": os.environ.get("GITHUB_WORKFLOW_REF"),
        }

    pytest_current_test = os.environ.get("PYTEST_CURRENT_TEST")
    if pytest_current_test:
        pytest_metadata: dict[str, Any] = {
            "current_test": pytest_current_test,
        }

        pytest_markers = os.environ.get("PYTEST_MARKERS")
        if pytest_markers:
            pytest_metadata["markers"] = pytest_markers.split(",")

        ci_metadata["pytest"] = pytest_metadata

    if ci_metadata:
        metadata["ci"] = ci_metadata

    return metadata
