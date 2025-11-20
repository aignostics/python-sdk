"""Unit tests for SDK metadata generation."""

import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from aignostics.platform._sdk_metadata import (
    ITEM_SDK_METADATA_SCHEMA_VERSION,
    SDK_METADATA_SCHEMA_VERSION,
    build_item_sdk_metadata,
    build_run_sdk_metadata,
    get_item_sdk_metadata_json_schema,
    get_run_sdk_metadata_json_schema,
    validate_item_sdk_metadata,
    validate_item_sdk_metadata_silent,
    validate_run_sdk_metadata,
    validate_run_sdk_metadata_silent,
)


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clean environment variables."""
    env_vars_to_clear = [
        "AIGNOSTICS_SUBMISSION_INITIATOR_BRIDGE",
        "GITHUB_ACTIONS",
        "GITHUB_SERVER_URL",
        "GITHUB_REPOSITORY",
        "GITHUB_SHA",
        "GITHUB_WORKFLOW",
        "GITHUB_WORKFLOW_REF",
        "PYTEST_CURRENT_TEST",
        "PYTEST_MARKERS",
    ]
    for var in env_vars_to_clear:
        monkeypatch.delenv(var, raising=False)


class TestBuildRunSdkMetadata:
    """Test cases for build_run_sdk_metadata function."""

    @pytest.mark.unit
    @staticmethod
    def test_basic_metadata_structure(clean_env: None) -> None:
        """Test that basic metadata structure is created correctly."""
        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()

            assert "schema_version" in metadata
            assert metadata["schema_version"] == SDK_METADATA_SCHEMA_VERSION
            assert "submission" in metadata
            assert "user_agent" in metadata

    @pytest.mark.unit
    @staticmethod
    def test_submission_metadata_default(clean_env: None) -> None:
        """Test default submission metadata when no special environment is detected."""
        with (
            patch("aignostics.platform._client.Client") as mock_client,
            patch("os.environ.get", return_value=None),
        ):
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()

            assert metadata["submission"]["initiator"] == "user"
            assert metadata["submission"]["interface"] == "script"
            assert "date" in metadata["submission"]
            # Verify date is in ISO format
            datetime.fromisoformat(metadata["submission"]["date"])

    @pytest.mark.unit
    @staticmethod
    def test_submission_initiator_bridge(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that bridge initiator is detected when AIGNOSTICS_BRIDGE_VERSION is set."""
        monkeypatch.setenv("AIGNOSTICS_BRIDGE_VERSION", "1.0.0")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()

            assert metadata["submission"]["initiator"] == "bridge"

    @pytest.mark.unit
    @staticmethod
    def test_submission_initiator_test(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that test initiator is detected when PYTEST_CURRENT_TEST is set."""
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/test_example.py::test_func")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()

            assert metadata["submission"]["initiator"] == "test"

    @pytest.mark.unit
    @staticmethod
    def test_submission_initiator_bridge_takes_precedence(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that bridge initiator takes precedence over test initiator."""
        monkeypatch.setenv("AIGNOSTICS_BRIDGE_VERSION", "1.0.0")
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/test_example.py::test_func")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()

            assert metadata["submission"]["initiator"] == "bridge"

    @pytest.mark.unit
    @staticmethod
    def test_submission_interface_cli_typer(clean_env: None) -> None:
        """Test that CLI interface is detected when running via typer."""
        original_argv = sys.argv
        try:
            sys.argv = ["/path/to/typer", "command"]

            with patch("aignostics.platform._client.Client") as mock_client:
                mock_client.return_value.me.side_effect = Exception("No client available")

                metadata = build_run_sdk_metadata()

                assert metadata["submission"]["interface"] == "cli"
        finally:
            sys.argv = original_argv

    @pytest.mark.unit
    @staticmethod
    def test_submission_interface_cli_aignostics(clean_env: None) -> None:
        """Test that CLI interface is detected when running via aignostics command."""
        original_argv = sys.argv
        try:
            sys.argv = ["/path/to/aignostics", "command"]

            with patch("aignostics.platform._client.Client") as mock_client:
                mock_client.return_value.me.side_effect = Exception("No client available")

                metadata = build_run_sdk_metadata()

                assert metadata["submission"]["interface"] == "cli"
        finally:
            sys.argv = original_argv

    @pytest.mark.unit
    @staticmethod
    def test_submission_interface_launchpad(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that launchpad interface is detected when NICEGUI_HOST is set."""
        monkeypatch.setenv("NICEGUI_HOST", "localhost")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()

            assert metadata["submission"]["interface"] == "launchpad"

    @pytest.mark.unit
    @staticmethod
    def test_user_metadata_success(clean_env: None) -> None:
        """Test that user metadata is included when Client().me() succeeds."""
        mock_me = MagicMock()
        mock_me.organization.id = "org-123"
        mock_me.organization.name = "Test Org"
        mock_me.user.email = "test@example.com"
        mock_me.user.id = "user-456"

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.return_value = mock_me

            metadata = build_run_sdk_metadata()

            assert "user" in metadata
            assert metadata["user"]["organization_id"] == "org-123"
            assert metadata["user"]["organization_name"] == "Test Org"
            assert metadata["user"]["user_email"] == "test@example.com"
            assert metadata["user"]["user_id"] == "user-456"

    @pytest.mark.unit
    @staticmethod
    def test_user_metadata_failure(clean_env: None) -> None:
        """Test that user metadata is omitted when Client().me() fails."""
        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("Auth failed")

            metadata = build_run_sdk_metadata()

            assert "user" not in metadata

    @pytest.mark.unit
    @staticmethod
    def test_github_ci_metadata(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that GitHub CI metadata is collected correctly."""
        monkeypatch.setenv("GITHUB_RUN_ID", "12345")
        monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
        monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
        monkeypatch.setenv("GITHUB_ACTION", "test-action")
        monkeypatch.setenv("GITHUB_JOB", "test-job")
        monkeypatch.setenv("GITHUB_REF", "refs/heads/main")
        monkeypatch.setenv("GITHUB_REF_NAME", "main")
        monkeypatch.setenv("GITHUB_REF_TYPE", "branch")
        monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "1")
        monkeypatch.setenv("GITHUB_RUN_NUMBER", "42")
        monkeypatch.setenv("RUNNER_ARCH", "X64")
        monkeypatch.setenv("RUNNER_OS", "Linux")
        monkeypatch.setenv("GITHUB_SHA", "abc123")
        monkeypatch.setenv("GITHUB_WORKFLOW", "CI")
        monkeypatch.setenv("GITHUB_WORKFLOW_REF", "owner/repo/.github/workflows/ci.yml@main")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()

            assert "ci" in metadata
            assert "github" in metadata["ci"]

            github = metadata["ci"]["github"]
            assert github["action"] == "test-action"
            assert github["job"] == "test-job"
            assert github["ref"] == "refs/heads/main"
            assert github["ref_name"] == "main"
            assert github["ref_type"] == "branch"
            assert github["repository"] == "owner/repo"
            assert github["run_attempt"] == "1"
            assert github["run_id"] == "12345"
            assert github["run_number"] == "42"
            assert github["run_url"] == "https://github.com/owner/repo/actions/runs/12345"
            assert github["runner_arch"] == "X64"
            assert github["runner_os"] == "Linux"
            assert github["sha"] == "abc123"
            assert github["workflow"] == "CI"
            assert github["workflow_ref"] == "owner/repo/.github/workflows/ci.yml@main"

    @pytest.mark.unit
    @staticmethod
    def test_github_ci_metadata_custom_server(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test GitHub CI metadata with custom server URL."""
        monkeypatch.setenv("GITHUB_RUN_ID", "12345")
        monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.enterprise.com")
        monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()

            assert metadata["ci"]["github"]["run_url"] == (
                "https://github.enterprise.com/owner/repo/actions/runs/12345"
            )

    @pytest.mark.unit
    @staticmethod
    def test_pytest_metadata_basic(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that pytest metadata is collected correctly."""
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/test_example.py::test_func (call)")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()

            assert "ci" in metadata
            assert "pytest" in metadata["ci"]
            assert metadata["ci"]["pytest"]["current_test"] == "tests/test_example.py::test_func (call)"

    @pytest.mark.unit
    @staticmethod
    def test_pytest_metadata_with_markers(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that pytest markers are parsed correctly."""
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/test_example.py::test_func (call)")
        monkeypatch.setenv("PYTEST_MARKERS", "slow,integration,unit")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()

            assert "markers" in metadata["ci"]["pytest"]
            assert metadata["ci"]["pytest"]["markers"] == ["slow", "integration", "unit"]

    @pytest.mark.unit
    @staticmethod
    def test_combined_github_and_pytest_metadata(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that both GitHub and pytest metadata can coexist."""
        monkeypatch.setenv("GITHUB_RUN_ID", "12345")
        monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/test_example.py::test_func (call)")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()

            assert "ci" in metadata
            assert "github" in metadata["ci"]
            assert "pytest" in metadata["ci"]

    @pytest.mark.unit
    @staticmethod
    def test_no_ci_metadata_when_not_in_ci(clean_env: None) -> None:
        """Test that ci field is omitted when not in CI environment."""
        with (
            patch("aignostics.platform._client.Client") as mock_client,
            patch("os.environ.get", return_value=None),
        ):
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()

            assert "ci" not in metadata

    @pytest.mark.unit
    @staticmethod
    def test_user_agent_included(clean_env: None) -> None:
        """Test that user_agent is included in metadata."""
        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")
            with patch("aignostics.platform._sdk_metadata.user_agent", return_value="test-agent/1.0"):
                metadata = build_run_sdk_metadata()

                assert metadata["user_agent"] == "test-agent/1.0"

    @pytest.mark.unit
    @staticmethod
    def test_metadata_date_format(clean_env: None) -> None:
        """Test that submission date is in correct ISO format with seconds precision."""
        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()

            date_str = metadata["submission"]["date"]
            # Should be able to parse as datetime
            parsed_date = datetime.fromisoformat(date_str)
            # Should have timezone info
            assert parsed_date.tzinfo is not None
            # Should be in ISO format with seconds precision (no microseconds)
            assert "." not in date_str or date_str.count(".") == 0 or len(date_str.split(".")[-1]) <= 3


class TestRunSdkMetadataValidation:
    """Test cases for Run SDK metadata validation."""

    @pytest.mark.unit
    @staticmethod
    def test_validate_basic_metadata(clean_env: None) -> None:
        """Test validation of basic metadata structure."""
        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()
            assert validate_run_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_metadata_with_user(clean_env: None) -> None:
        """Test validation of metadata with user information."""
        with patch("aignostics.platform._client.Client") as mock_client:
            mock_user = MagicMock()
            mock_user.organization.id = "org-123"
            mock_user.organization.name = "Test Org"
            mock_user.user.email = "test@example.com"
            mock_user.user.id = "user-456"
            mock_client.return_value.me.return_value = mock_user

            metadata = build_run_sdk_metadata()
            assert validate_run_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_metadata_with_github_ci(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test validation of metadata with GitHub CI information."""
        monkeypatch.setenv("GITHUB_RUN_ID", "123456")
        monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()
            assert validate_run_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_metadata_with_pytest_ci(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test validation of metadata with pytest information."""
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/test_example.py::test_func")
        monkeypatch.setenv("PYTEST_MARKERS", "unit,integration")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()
            assert validate_run_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_metadata_with_workflow(clean_env: None) -> None:
        """Test validation of metadata with workflow fields."""
        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()
            metadata["note"] = "Test run note"
            metadata["workflow"] = {
                "onboard_to_aignostics_portal": True,
                "validate_only": False,
            }
            metadata["scheduling"] = {
                "due_date": "2025-12-31T23:59:59+00:00",
                "deadline": "2026-01-01T00:00:00+00:00",
            }

            assert validate_run_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_invalid_schema_version() -> None:
        """Test that invalid schema version fails validation."""
        metadata = {
            "schema_version": "invalid-version",
            "submission": {
                "date": "2025-10-19T12:00:00+00:00",
                "interface": "script",
                "initiator": "user",
            },
            "user_agent": "test-agent/1.0",
        }

        with pytest.raises(ValidationError):
            validate_run_sdk_metadata(metadata)

    @pytest.mark.unit
    @staticmethod
    def test_validate_invalid_submission_interface() -> None:
        """Test that invalid submission interface fails validation."""
        metadata = {
            "schema_version": SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "submission": {
                "date": "2025-10-19T12:00:00+00:00",
                "interface": "invalid",
                "initiator": "user",
            },
            "user_agent": "test-agent/1.0",
        }

        with pytest.raises(ValidationError):
            validate_run_sdk_metadata(metadata)

    @pytest.mark.unit
    @staticmethod
    def test_validate_invalid_submission_initiator() -> None:
        """Test that invalid submission initiator fails validation."""
        metadata = {
            "schema_version": SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "submission": {
                "date": "2025-10-19T12:00:00+00:00",
                "interface": "script",
                "initiator": "invalid",
            },
            "user_agent": "test-agent/1.0",
        }

        with pytest.raises(ValidationError):
            validate_run_sdk_metadata(metadata)

    @pytest.mark.unit
    @staticmethod
    def test_validate_missing_required_fields() -> None:
        """Test that missing required fields fail validation."""
        metadata = {
            "schema_version": SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "submission": {
                "date": "2025-10-19T12:00:00+00:00",
                "interface": "script",
            },
            # Missing initiator
            "user_agent": "test-agent/1.0",
        }

        with pytest.raises(ValidationError):
            validate_run_sdk_metadata(metadata)

    @pytest.mark.unit
    @staticmethod
    def test_validate_extra_fields_rejected() -> None:
        """Test that extra unknown fields are rejected."""
        metadata = {
            "schema_version": SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "submission": {
                "date": "2025-10-19T12:00:00+00:00",
                "interface": "script",
                "initiator": "user",
            },
            "user_agent": "test-agent/1.0",
            "unknown_field": "should fail",
        }

        with pytest.raises(ValidationError):
            validate_run_sdk_metadata(metadata)

    @pytest.mark.unit
    @staticmethod
    def test_validate_with_tags_set() -> None:
        """Test validation with tags as a set of strings."""
        metadata = {
            "schema_version": SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "submission": {
                "date": "2025-10-19T12:00:00+00:00",
                "interface": "script",
                "initiator": "user",
            },
            "user_agent": "test-agent/1.0",
            "tags": {"experiment", "production", "v2"},
        }

        assert validate_run_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_with_empty_tags_set() -> None:
        """Test validation with empty tags set."""
        metadata = {
            "schema_version": SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "submission": {
                "date": "2025-10-19T12:00:00+00:00",
                "interface": "script",
                "initiator": "user",
            },
            "user_agent": "test-agent/1.0",
            "tags": set(),
        }

        assert validate_run_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_with_tags_none() -> None:
        """Test validation with tags as None."""
        metadata = {
            "schema_version": SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "submission": {
                "date": "2025-10-19T12:00:00+00:00",
                "interface": "script",
                "initiator": "user",
            },
            "user_agent": "test-agent/1.0",
            "tags": None,
        }

        assert validate_run_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_without_tags_field() -> None:
        """Test validation when tags field is omitted entirely."""
        metadata = {
            "schema_version": SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "submission": {
                "date": "2025-10-19T12:00:00+00:00",
                "interface": "script",
                "initiator": "user",
            },
            "user_agent": "test-agent/1.0",
        }

        assert validate_run_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_with_tags_list_converted_to_set() -> None:
        """Test that list is automatically converted to set by Pydantic."""
        metadata = {
            "schema_version": SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "submission": {
                "date": "2025-10-19T12:00:00+00:00",
                "interface": "script",
                "initiator": "user",
            },
            "user_agent": "test-agent/1.0",
            "tags": ["tag1", "tag2"],  # List gets converted to set
        }

        # Validation should succeed as Pydantic converts list to set
        assert validate_run_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_with_tags_invalid_type_dict() -> None:
        """Test validation fails when tags is a dict instead of set."""
        metadata = {
            "schema_version": SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "submission": {
                "date": "2025-10-19T12:00:00+00:00",
                "interface": "script",
                "initiator": "user",
            },
            "user_agent": "test-agent/1.0",
            "tags": {"key": "value"},  # Dict instead of set
        }

        with pytest.raises(ValidationError):
            validate_run_sdk_metadata(metadata)

    @pytest.mark.unit
    @staticmethod
    def test_validate_with_tags_non_string_values() -> None:
        """Test validation fails when tags contains non-string values."""
        metadata = {
            "schema_version": SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "submission": {
                "date": "2025-10-19T12:00:00+00:00",
                "interface": "script",
                "initiator": "user",
            },
            "user_agent": "test-agent/1.0",
            "tags": {"valid", 123, None},  # Mixed types
        }

        with pytest.raises(ValidationError):
            validate_run_sdk_metadata(metadata)

    @pytest.mark.unit
    @staticmethod
    def test_validate_sdk_metadata_silent_valid(clean_env: None) -> None:
        """Test silent validation with valid metadata."""
        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_run_sdk_metadata()
            assert validate_run_sdk_metadata_silent(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_sdk_metadata_silent_invalid() -> None:
        """Test silent validation with invalid metadata."""
        metadata = {
            "schema_version": "invalid",
            "submission": {
                "date": "2025-10-19T12:00:00+00:00",
                "interface": "invalid",
                "initiator": "user",
            },
            "user_agent": "test-agent/1.0",
        }

        assert validate_run_sdk_metadata_silent(metadata) is False

    @pytest.mark.unit
    @staticmethod
    def test_get_json_schema() -> None:
        """Test that JSON schema can be exported."""
        schema = get_run_sdk_metadata_json_schema()

        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert "$id" in schema
        assert (
            schema["$id"]
            == f"https://raw.githubusercontent.com/aignostics/python-sdk/main/docs/source/_static/sdk_metadata_schema_v{SDK_METADATA_SCHEMA_VERSION}.json"
        )
        assert "properties" in schema
        assert "schema_version" in schema["properties"]
        assert "submission" in schema["properties"]
        assert "user_agent" in schema["properties"]
        assert "required" in schema
        assert "schema_version" in schema["required"]
        assert "submission" in schema["required"]
        assert "user_agent" in schema["required"]


class TestItemSdkMetadata:
    """Test cases for Item SDK metadata."""

    @pytest.mark.unit
    @staticmethod
    def test_build_item_metadata_basic() -> None:
        """Test that basic item metadata structure is created correctly."""
        metadata = build_item_sdk_metadata()

        assert metadata["schema_version"] == ITEM_SDK_METADATA_SCHEMA_VERSION
        assert "platform_bucket" not in metadata

    @pytest.mark.unit
    @staticmethod
    def test_validate_item_metadata_basic() -> None:
        """Test validation of the default item metadata."""
        metadata = build_item_sdk_metadata()

        assert validate_item_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_item_metadata_with_platform_bucket() -> None:
        """Test validation succeeds with platform bucket metadata present."""
        metadata = {
            "schema_version": ITEM_SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "platform_bucket": {
                "bucket_name": "sdk-bucket",
                "object_key": "runs/123/items/456",
                "signed_download_url": "https://example.com/run-item",
            },
        }

        assert validate_item_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_item_metadata_missing_platform_bucket_fields() -> None:
        """Test validation fails when required platform bucket fields are missing."""
        metadata = {
            "schema_version": ITEM_SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "platform_bucket": {
                "bucket_name": "sdk-bucket",
                "object_key": "runs/123/items/456",
            },
        }

        with pytest.raises(ValidationError):
            validate_item_sdk_metadata(metadata)

    @pytest.mark.unit
    @staticmethod
    def test_validate_item_metadata_invalid_schema_version() -> None:
        """Test that an invalid schema version fails validation."""
        metadata = {
            "schema_version": "invalid",
        }

        with pytest.raises(ValidationError):
            validate_item_sdk_metadata(metadata)

    @pytest.mark.unit
    @staticmethod
    def test_validate_item_metadata_extra_fields() -> None:
        """Test that extra fields are rejected for item metadata."""
        metadata = {
            "schema_version": ITEM_SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "unexpected": "value",
        }

        with pytest.raises(ValidationError):
            validate_item_sdk_metadata(metadata)

    @pytest.mark.unit
    @staticmethod
    def test_validate_item_metadata_silent_valid() -> None:
        """Test silent validation passes for valid item metadata."""
        metadata = build_item_sdk_metadata()

        assert validate_item_sdk_metadata_silent(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_item_metadata_silent_invalid() -> None:
        """Test silent validation fails for invalid item metadata."""
        metadata = {
            "schema_version": "invalid",
        }

        assert validate_item_sdk_metadata_silent(metadata) is False

    @pytest.mark.unit
    @staticmethod
    def test_get_item_json_schema() -> None:
        """Test that the item metadata JSON schema can be exported."""
        schema = get_item_sdk_metadata_json_schema()

        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert "$id" in schema
        assert schema["$id"] == (
            f"https://raw.githubusercontent.com/aignostics/python-sdk/main/docs/source/_static/"
            f"item_sdk_metadata_schema_v{ITEM_SDK_METADATA_SCHEMA_VERSION}.json"
        )
        assert "properties" in schema
        assert "schema_version" in schema["properties"]
        assert "required" in schema
        assert "schema_version" in schema["required"]

    @pytest.mark.unit
    @staticmethod
    def test_validate_item_metadata_with_tags() -> None:
        """Test validation of item metadata with tags as a set of strings."""
        metadata = {
            "schema_version": ITEM_SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "tags": {"slide", "tumor", "he-stained"},
        }

        assert validate_item_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_item_metadata_with_empty_tags() -> None:
        """Test validation of item metadata with empty tags set."""
        metadata = {
            "schema_version": ITEM_SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "tags": set(),
        }

        assert validate_item_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_item_metadata_with_tags_none() -> None:
        """Test validation of item metadata with tags as None."""
        metadata = {
            "schema_version": ITEM_SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "tags": None,
        }

        assert validate_item_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_item_metadata_without_tags() -> None:
        """Test validation of item metadata when tags field is omitted."""
        metadata = {
            "schema_version": ITEM_SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
        }

        assert validate_item_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_item_metadata_tags_list_converted() -> None:
        """Test that list is automatically converted to set by Pydantic."""
        metadata = {
            "schema_version": ITEM_SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "tags": ["tag1", "tag2"],  # List gets converted to set
        }

        # Validation should succeed as Pydantic converts list to set
        assert validate_item_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_validate_item_metadata_tags_non_string() -> None:
        """Test validation fails when tags contains non-string values."""
        metadata = {
            "schema_version": ITEM_SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "tags": {"valid", 123},  # Mixed types
        }

        with pytest.raises(ValidationError):
            validate_item_sdk_metadata(metadata)


class TestPipelineConfiguration:
    """Test cases for pipeline configuration models."""

    @pytest.mark.unit
    @staticmethod
    def test_pipeline_config_defaults() -> None:
        """Test that pipeline configuration uses correct defaults."""
        from aignostics.platform import (
            DEFAULT_CPU_PROVISIONING_MODE,
            DEFAULT_GPU_PROVISIONING_MODE,
            DEFAULT_GPU_TYPE,
            DEFAULT_MAX_GPUS_PER_SLIDE,
            PipelineConfig,
        )

        config = PipelineConfig()

        assert config.gpu.gpu_type.value == DEFAULT_GPU_TYPE
        assert config.gpu.provisioning_mode.value == DEFAULT_GPU_PROVISIONING_MODE
        assert config.gpu.max_gpus_per_slide == DEFAULT_MAX_GPUS_PER_SLIDE
        assert config.cpu.provisioning_mode.value == DEFAULT_CPU_PROVISIONING_MODE

    @pytest.mark.unit
    @staticmethod
    def test_pipeline_config_custom_values() -> None:
        """Test pipeline configuration with custom values."""
        from aignostics.platform._sdk_metadata import GPUType, PipelineConfig, ProvisioningMode

        config = PipelineConfig(
            gpu={
                "gpu_type": GPUType.L4,
                "provisioning_mode": ProvisioningMode.SPOT,
                "max_gpus_per_slide": 4,
            },
            cpu={"provisioning_mode": ProvisioningMode.SPOT},
        )

        assert config.gpu.gpu_type == GPUType.L4
        assert config.gpu.provisioning_mode == ProvisioningMode.SPOT
        assert config.gpu.max_gpus_per_slide == 4
        assert config.cpu.provisioning_mode == ProvisioningMode.SPOT

    @pytest.mark.unit
    @staticmethod
    def test_gpu_type_enum() -> None:
        """Test GPUType enum values."""
        from aignostics.platform._sdk_metadata import GPUType

        assert GPUType.L4.value == "L4"
        assert GPUType.A100.value == "A100"
        assert len(GPUType) == 2

    @pytest.mark.unit
    @staticmethod
    def test_provisioning_mode_enum() -> None:
        """Test ProvisioningMode enum values."""
        from aignostics.platform._sdk_metadata import ProvisioningMode

        assert ProvisioningMode.SPOT.value == "SPOT"
        assert ProvisioningMode.ON_DEMAND.value == "ON_DEMAND"
        assert len(ProvisioningMode) == 2

    @pytest.mark.unit
    @staticmethod
    def test_metadata_with_pipeline_config() -> None:
        """Test that metadata validates with pipeline configuration."""
        from aignostics.platform._sdk_metadata import GPUType, ProvisioningMode

        metadata = {
            "schema_version": SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "submission": {
                "date": "2025-10-19T12:00:00+00:00",
                "interface": "script",
                "initiator": "user",
            },
            "user_agent": "aignostics-sdk/1.0.0",
            "pipeline": {
                "gpu": {
                    "gpu_type": GPUType.L4.value,
                    "provisioning_mode": ProvisioningMode.SPOT.value,
                    "max_gpus_per_slide": 2,
                },
                "cpu": {"provisioning_mode": ProvisioningMode.ON_DEMAND.value},
            },
        }

        assert validate_run_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_metadata_without_pipeline_config() -> None:
        """Test that metadata validates without pipeline configuration (optional field)."""
        metadata = {
            "schema_version": SDK_METADATA_SCHEMA_VERSION,
            "created_at": "2025-10-19T12:00:00+00:00",
            "updated_at": "2025-10-19T12:00:00+00:00",
            "submission": {
                "date": "2025-10-19T12:00:00+00:00",
                "interface": "script",
                "initiator": "user",
            },
            "user_agent": "aignostics-sdk/1.0.0",
        }

        assert validate_run_sdk_metadata(metadata) is True

    @pytest.mark.unit
    @staticmethod
    def test_gpu_config_invalid_max_gpus() -> None:
        """Test that invalid max_gpus_per_slide value is rejected."""
        from aignostics.platform._sdk_metadata import GPUConfig

        with pytest.raises(ValidationError):
            GPUConfig(max_gpus_per_slide=0)  # Must be positive

        with pytest.raises(ValidationError):
            GPUConfig(max_gpus_per_slide=-1)  # Must be positive
