"""Unit tests for SDK metadata generation."""

import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from aignostics.platform._sdk_metadata import SDK_METADATA_SCHEMA_VERSION, build_sdk_metadata


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clean environment variables."""
    env_vars_to_clear = [
        "AIGNOSTICS_SUBMISSION_SOURCE_BRIDGE",
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


class TestBuildSdkMetadata:
    """Test cases for build_sdk_metadata function."""

    @staticmethod
    def test_basic_metadata_structure(clean_env: None) -> None:
        """Test that basic metadata structure is created correctly."""
        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_sdk_metadata()

            assert "schema_version" in metadata
            assert metadata["schema_version"] == SDK_METADATA_SCHEMA_VERSION
            assert "submission" in metadata
            assert "user_agent" in metadata

    @staticmethod
    def test_submission_metadata_default(clean_env: None) -> None:
        """Test default submission metadata when no special environment is detected."""
        with (
            patch("aignostics.platform._client.Client") as mock_client,
            patch("os.environ.get", return_value=None),
        ):
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_sdk_metadata()

            assert metadata["submission"]["source"] == "user"
            assert metadata["submission"]["interface"] == "script"
            assert "date" in metadata["submission"]
            # Verify date is in ISO format
            datetime.fromisoformat(metadata["submission"]["date"])

    @staticmethod
    def test_submission_source_bridge(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that bridge source is detected when AIGNOSTICS_BRIDGE_VERSION is set."""
        monkeypatch.setenv("AIGNOSTICS_BRIDGE_VERSION", "1.0.0")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_sdk_metadata()

            assert metadata["submission"]["source"] == "bridge"

    @staticmethod
    def test_submission_source_test(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that test source is detected when PYTEST_CURRENT_TEST is set."""
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/test_example.py::test_func")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_sdk_metadata()

            assert metadata["submission"]["source"] == "test"

    @staticmethod
    def test_submission_source_bridge_takes_precedence(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that bridge source takes precedence over test source."""
        monkeypatch.setenv("AIGNOSTICS_BRIDGE_VERSION", "1.0.0")
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/test_example.py::test_func")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_sdk_metadata()

            assert metadata["submission"]["source"] == "bridge"

    @staticmethod
    def test_submission_interface_cli_typer(clean_env: None) -> None:
        """Test that CLI interface is detected when running via typer."""
        original_argv = sys.argv
        try:
            sys.argv = ["/path/to/typer", "command"]

            with patch("aignostics.platform._client.Client") as mock_client:
                mock_client.return_value.me.side_effect = Exception("No client available")

                metadata = build_sdk_metadata()

                assert metadata["submission"]["interface"] == "cli"
        finally:
            sys.argv = original_argv

    @staticmethod
    def test_submission_interface_cli_aignostics(clean_env: None) -> None:
        """Test that CLI interface is detected when running via aignostics command."""
        original_argv = sys.argv
        try:
            sys.argv = ["/path/to/aignostics", "command"]

            with patch("aignostics.platform._client.Client") as mock_client:
                mock_client.return_value.me.side_effect = Exception("No client available")

                metadata = build_sdk_metadata()

                assert metadata["submission"]["interface"] == "cli"
        finally:
            sys.argv = original_argv

    @staticmethod
    def test_submission_interface_launchpad(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that launchpad interface is detected when NICEGUI_HOST is set."""
        monkeypatch.setenv("NICEGUI_HOST", "localhost")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_sdk_metadata()

            assert metadata["submission"]["interface"] == "launchpad"

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

            metadata = build_sdk_metadata()

            assert "user" in metadata
            assert metadata["user"]["organization_id"] == "org-123"
            assert metadata["user"]["organization_name"] == "Test Org"
            assert metadata["user"]["user_email"] == "test@example.com"
            assert metadata["user"]["user_id"] == "user-456"

    @staticmethod
    def test_user_metadata_failure(clean_env: None) -> None:
        """Test that user metadata is omitted when Client().me() fails."""
        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("Auth failed")

            metadata = build_sdk_metadata()

            assert "user" not in metadata

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

            metadata = build_sdk_metadata()

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

    @staticmethod
    def test_github_ci_metadata_custom_server(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test GitHub CI metadata with custom server URL."""
        monkeypatch.setenv("GITHUB_RUN_ID", "12345")
        monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.enterprise.com")
        monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_sdk_metadata()

            assert metadata["ci"]["github"]["run_url"] == (
                "https://github.enterprise.com/owner/repo/actions/runs/12345"
            )

    @staticmethod
    def test_pytest_metadata_basic(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that pytest metadata is collected correctly."""
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/test_example.py::test_func (call)")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_sdk_metadata()

            assert "ci" in metadata
            assert "pytest" in metadata["ci"]
            assert metadata["ci"]["pytest"]["current_test"] == "tests/test_example.py::test_func (call)"

    @staticmethod
    def test_pytest_metadata_with_markers(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that pytest markers are parsed correctly."""
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/test_example.py::test_func (call)")
        monkeypatch.setenv("PYTEST_MARKERS", "slow,integration,unit")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_sdk_metadata()

            assert "markers" in metadata["ci"]["pytest"]
            assert metadata["ci"]["pytest"]["markers"] == ["slow", "integration", "unit"]

    @staticmethod
    def test_combined_github_and_pytest_metadata(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that both GitHub and pytest metadata can coexist."""
        monkeypatch.setenv("GITHUB_RUN_ID", "12345")
        monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/test_example.py::test_func (call)")

        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_sdk_metadata()

            assert "ci" in metadata
            assert "github" in metadata["ci"]
            assert "pytest" in metadata["ci"]

    @staticmethod
    def test_no_ci_metadata_when_not_in_ci(clean_env: None) -> None:
        """Test that ci field is omitted when not in CI environment."""
        with (
            patch("aignostics.platform._client.Client") as mock_client,
            patch("os.environ.get", return_value=None),
        ):
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_sdk_metadata()

            assert "ci" not in metadata

    @staticmethod
    def test_user_agent_included(clean_env: None) -> None:
        """Test that user_agent is included in metadata."""
        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")
            with patch("aignostics.platform._sdk_metadata.user_agent", return_value="test-agent/1.0"):
                metadata = build_sdk_metadata()

                assert metadata["user_agent"] == "test-agent/1.0"

    @staticmethod
    def test_metadata_date_format(clean_env: None) -> None:
        """Test that submission date is in correct ISO format with seconds precision."""
        with patch("aignostics.platform._client.Client") as mock_client:
            mock_client.return_value.me.side_effect = Exception("No client available")

            metadata = build_sdk_metadata()

            date_str = metadata["submission"]["date"]
            # Should be able to parse as datetime
            parsed_date = datetime.fromisoformat(date_str)
            # Should have timezone info
            assert parsed_date.tzinfo is not None
            # Should be in ISO format with seconds precision (no microseconds)
            assert "." not in date_str or date_str.count(".") == 0 or len(date_str.split(".")[-1]) <= 3
