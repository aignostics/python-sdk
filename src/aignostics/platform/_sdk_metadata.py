"""SDK metadata generation for application runs.

This module provides functionality to build structured metadata about the SDK execution context,
including user information, CI/CD environment details, and test execution context.
"""

import os
import sys
from datetime import UTC, datetime
from typing import Any, Literal

from loguru import logger
from pydantic import BaseModel, Field, ValidationError

from aignostics.utils import user_agent

SDK_METADATA_SCHEMA_VERSION = "0.0.4"
ITEM_SDK_METADATA_SCHEMA_VERSION = "0.0.3"


class SubmissionMetadata(BaseModel):
    """Metadata about how the SDK was invoked."""

    date: str = Field(..., description="ISO 8601 timestamp of submission")
    interface: Literal["script", "cli", "launchpad"] = Field(
        ..., description="How the SDK was accessed (script, cli, launchpad)"
    )
    initiator: Literal["user", "test", "bridge"] = Field(
        ..., description="Who/what initiated the run (user, test, bridge)"
    )


class UserMetadata(BaseModel):
    """User information metadata."""

    organization_id: str = Field(..., description="User's organization ID")
    organization_name: str = Field(..., description="User's organization name")
    user_email: str = Field(..., description="User's email address")
    user_id: str = Field(..., description="User's unique ID")


class GitHubCIMetadata(BaseModel):
    """GitHub Actions CI metadata."""

    action: str | None = Field(None, description="GitHub Action name")
    job: str | None = Field(None, description="GitHub job name")
    ref: str | None = Field(None, description="Git reference")
    ref_name: str | None = Field(None, description="Git reference name")
    ref_type: str | None = Field(None, description="Git reference type (branch, tag)")
    repository: str = Field(..., description="Repository name (owner/repo)")
    run_attempt: str | None = Field(None, description="Attempt number for this run")
    run_id: str = Field(..., description="Unique ID for this workflow run")
    run_number: str | None = Field(None, description="Run number for this workflow")
    run_url: str = Field(..., description="URL to the workflow run")
    runner_arch: str | None = Field(None, description="Runner architecture (x64, ARM64, etc.)")
    runner_os: str | None = Field(None, description="Runner operating system")
    sha: str | None = Field(None, description="Git commit SHA")
    workflow: str | None = Field(None, description="Workflow name")
    workflow_ref: str | None = Field(None, description="Reference to the workflow file")


class PytestCIMetadata(BaseModel):
    """Pytest test execution metadata."""

    current_test: str = Field(..., description="Current test being executed")
    markers: list[str] | None = Field(None, description="Pytest markers applied to the test")


class CIMetadata(BaseModel):
    """CI/CD environment metadata."""

    github: GitHubCIMetadata | None = Field(None, description="GitHub Actions metadata")
    pytest: PytestCIMetadata | None = Field(None, description="Pytest test metadata")


class WorkflowMetadata(BaseModel):
    """Workflow control metadata."""

    onboard_to_aignostics_portal: bool = Field(
        default=False, description="Whether to onboard results to the Aignostics Portal"
    )
    validate_only: bool = Field(default=False, description="Whether to only validate without running analysis")


class SchedulingMetadata(BaseModel):
    """Scheduling metadata for run execution."""

    due_date: str | None = Field(
        None,
        description="Requested completion time (ISO 8601). Scheduler will try to complete before this time.",
    )
    deadline: str | None = Field(
        None, description="Hard deadline (ISO 8601). Run may be aborted if processing exceeds this time."
    )


class RunSdkMetadata(BaseModel):
    """Complete Run SDK metadata schema.

    This model defines the structure and validation rules for SDK metadata
    that is attached to application runs. It includes information about:
    - SDK version and timestamps
    - User information (when available)
    - CI/CD environment context (GitHub Actions, pytest)
    - Workflow control flags
    - Scheduling information
    - Optional user note
    """

    schema_version: str = Field(
        ..., description="Schema version for this metadata format", pattern=r"^\d+\.\d+\.\d+-?.*$"
    )

    created_at: str = Field(..., description="ISO 8601 timestamp when the metadata was first created")
    updated_at: str = Field(..., description="ISO 8601 timestamp when the metadata was last updated")
    tags: set[str] | None = Field(None, description="Optional list of tags associated with the run")
    submission: SubmissionMetadata = Field(..., description="Submission context metadata")
    user_agent: str = Field(..., description="User agent string for the SDK client")
    user: UserMetadata | None = Field(None, description="User information (when authenticated)")
    ci: CIMetadata | None = Field(None, description="CI/CD environment metadata")
    note: str | None = Field(None, description="Optional user note for the run")
    workflow: WorkflowMetadata | None = Field(None, description="Workflow control flags")
    scheduling: SchedulingMetadata | None = Field(None, description="Scheduling information")

    model_config = {"extra": "forbid"}  # Reject unknown fields


class PlatformBucketMetadata(BaseModel):
    """Platform bucket storage metadata for items."""

    bucket_name: str = Field(..., description="Name of the cloud storage bucket")
    object_key: str = Field(..., description="Object key/path within the bucket")
    signed_download_url: str = Field(..., description="Signed URL for downloading the object")


class ItemSdkMetadata(BaseModel):
    """Complete Item SDK metadata schema.

    This model defines the structure and validation rules for SDK metadata
    that is attached to individual items within application runs. It includes
    information about where the item is stored in the platform's cloud storage.
    """

    schema_version: str = Field(
        ..., description="Schema version for this metadata format", pattern=r"^\d+\.\d+\.\d+-?.*$"
    )

    created_at: str = Field(..., description="ISO 8601 timestamp when the metadata was first created")
    updated_at: str = Field(..., description="ISO 8601 timestamp when the metadata was last updated")
    tags: set[str] | None = Field(None, description="Optional list of tags associated with the item")
    platform_bucket: PlatformBucketMetadata | None = Field(None, description="Platform bucket storage information")

    model_config = {"extra": "forbid"}  # Reject unknown fields


def build_run_sdk_metadata(existing_metadata: dict[str, Any] | None = None) -> dict[str, Any]:  # noqa: PLR0914
    """Build SDK metadata to attach to runs.

    Includes user agent, user information, GitHub CI/CD context when running in GitHub Actions,
    and test context when running in pytest.

    Args:
        existing_metadata (dict[str, Any] | None): Existing SDK metadata to preserve created_at and submission.date.

    Returns:
        dict[str, Any]: Dictionary containing SDK metadata including user agent,
            user information, and optionally CI information (GitHub workflow and pytest test context).
    """
    from aignostics.platform._client import Client  # noqa: PLC0415

    submission_initiator = "user"  # who/what initiated the run (user, test, bridge)
    submission_interface = "script"  # how the SDK was accessed (script, cli, launchpad)

    if os.environ.get("AIGNOSTICS_BRIDGE_VERSION"):
        submission_initiator = "bridge"
    elif os.environ.get("PYTEST_CURRENT_TEST"):
        submission_initiator = "test"

    if "typer" in sys.argv[0] or "aignostics" in sys.argv[0]:
        submission_interface = "cli"
    elif os.getenv("NICEGUI_HOST"):
        submission_interface = "launchpad"

    now = datetime.now(UTC).isoformat(timespec="seconds")
    existing_sdk = existing_metadata or {}

    # Preserve created_at if it exists, otherwise use current time
    created_at = existing_sdk.get("created_at", now)

    # Preserve submission.date if it exists, otherwise use current time
    existing_submission = existing_sdk.get("submission", {})
    submission_date = existing_submission.get("date", now)

    metadata: dict[str, Any] = {
        "schema_version": SDK_METADATA_SCHEMA_VERSION,
        "created_at": created_at,
        "updated_at": now,
        "submission": {
            "date": submission_date,
            "interface": submission_interface,
            "initiator": submission_initiator,
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
    except Exception:
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


def validate_run_sdk_metadata(metadata: dict[str, Any]) -> bool:
    """Validate the Run SDK metadata structure against the schema.

    Args:
        metadata (dict[str, Any]): The Run SDK metadata to validate.

    Returns:
        bool: True if the metadata is valid, False otherwise.

    Raises:
        ValidationError: If the metadata does not conform to the schema.
    """
    try:
        RunSdkMetadata.model_validate(metadata)
        return True
    except ValidationError:
        logger.exception("SDK metadata validation failed")
        raise


def get_run_sdk_metadata_json_schema() -> dict[str, Any]:
    """Get the JSON Schema for Run SDK metadata.

    Returns:
        dict[str, Any]: JSON Schema definition for Run SDK metadata with $schema and $id fields.
    """
    schema = RunSdkMetadata.model_json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = (
        f"https://raw.githubusercontent.com/aignostics/python-sdk/main/docs/source/_static/sdk_metadata_schema_v{SDK_METADATA_SCHEMA_VERSION}.json"
    )
    return schema


def validate_run_sdk_metadata_silent(metadata: dict[str, Any]) -> bool:
    """Validate Run SDK metadata without raising exceptions.

    Args:
        metadata (dict[str, Any]): The Run SDK metadata to validate.

    Returns:
        bool: True if valid, False if invalid.
    """
    try:
        RunSdkMetadata.model_validate(metadata)
        return True
    except ValidationError:
        return False


def build_item_sdk_metadata(existing_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build SDK metadata to attach to individual items.

    Args:
        existing_metadata (dict[str, Any] | None): Existing SDK metadata to preserve created_at.

    Returns:
        dict[str, Any]: Dictionary containing item SDK metadata including platform bucket information.
    """
    now = datetime.now(UTC).isoformat(timespec="seconds")
    existing_sdk = existing_metadata or {}

    # Preserve created_at if it exists, otherwise use current time
    created_at = existing_sdk.get("created_at", now)

    metadata: dict[str, Any] = {
        "schema_version": ITEM_SDK_METADATA_SCHEMA_VERSION,
        "created_at": created_at,
        "updated_at": now,
    }

    return metadata


def validate_item_sdk_metadata(metadata: dict[str, Any]) -> bool:
    """Validate the Item SDK metadata structure against the schema.

    Args:
        metadata (dict[str, Any]): The Item SDK metadata to validate.

    Returns:
        bool: True if the metadata is valid, False otherwise.

    Raises:
        ValidationError: If the metadata does not conform to the schema.
    """
    try:
        ItemSdkMetadata.model_validate(metadata)
        return True
    except ValidationError:
        logger.exception("Item SDK metadata validation failed")
        raise


def get_item_sdk_metadata_json_schema() -> dict[str, Any]:
    """Get the JSON Schema for Item SDK metadata.

    Returns:
        dict[str, Any]: JSON Schema definition for Item SDK metadata with $schema and $id fields.
    """
    schema = ItemSdkMetadata.model_json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = (
        f"https://raw.githubusercontent.com/aignostics/python-sdk/main/docs/source/_static/item_sdk_metadata_schema_v{ITEM_SDK_METADATA_SCHEMA_VERSION}.json"
    )
    return schema


def validate_item_sdk_metadata_silent(metadata: dict[str, Any]) -> bool:
    """Validate Item SDK metadata without raising exceptions.

    Args:
        metadata (dict[str, Any]): The Item SDK metadata to validate.

    Returns:
        bool: True if valid, False if invalid.
    """
    try:
        ItemSdkMetadata.model_validate(metadata)
        return True
    except ValidationError:
        return False
