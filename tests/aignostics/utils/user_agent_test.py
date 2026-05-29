"""Tests for user agent string generation."""

import platform
from unittest.mock import patch

import pytest

from aignostics_sdk.utils._user_agent import user_agent


@pytest.mark.unit
def test_user_agent_basic_format(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test basic user agent format without optional environment variables."""
    # Clear environment variables
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)

    with (
        patch("aignostics_sdk.utils._user_agent.__project_name__", "aignostics"),
        patch("aignostics_sdk.utils._user_agent.__version_full__", "1.0.0"),
        patch("aignostics_sdk.utils._user_agent.__repository_url__", "https://github.com/aignostics/python-sdk"),
    ):
        result = user_agent()

        # Check basic structure
        assert result.startswith("aignostics-python-sdk/1.0.0 (")
        assert platform.platform() in result
        assert "https://github.com/aignostics/python-sdk" in result
        assert result.endswith(")")


@pytest.mark.unit
def test_user_agent_with_pytest_current_test(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test user agent includes PYTEST_CURRENT_TEST when set."""
    test_name = "tests/test_module.py::test_function"
    monkeypatch.setenv("PYTEST_CURRENT_TEST", test_name)
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)

    with (
        patch("aignostics_sdk.utils._user_agent.__project_name__", "aignostics"),
        patch("aignostics_sdk.utils._user_agent.__version_full__", "1.0.0"),
        patch("aignostics_sdk.utils._user_agent.__repository_url__", "https://github.com/aignostics/python-sdk"),
    ):
        result = user_agent()

        assert test_name in result
        assert f"; {test_name})" in result


@pytest.mark.unit
def test_user_agent_with_github_run_info(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test user agent includes GitHub run information when both variables are set."""
    run_id = "12345678"
    repository = "aignostics/python-sdk"
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setenv("GITHUB_RUN_ID", run_id)
    monkeypatch.setenv("GITHUB_REPOSITORY", repository)

    with (
        patch("aignostics_sdk.utils._user_agent.__project_name__", "aignostics"),
        patch("aignostics_sdk.utils._user_agent.__version_full__", "1.0.0"),
        patch("aignostics_sdk.utils._user_agent.__repository_url__", "https://github.com/aignostics/python-sdk"),
    ):
        result = user_agent()

        expected_github_url = f"+https://github.com/{repository}/actions/runs/{run_id}"
        assert expected_github_url in result
        assert result.endswith(f"{expected_github_url})")


@pytest.mark.unit
def test_user_agent_with_github_run_id_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test user agent does not include GitHub Actions run URL when only GITHUB_RUN_ID is set."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setenv("GITHUB_RUN_ID", "12345678")
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)

    with (
        patch("aignostics_sdk.utils._user_agent.__project_name__", "aignostics"),
        patch("aignostics_sdk.utils._user_agent.__version_full__", "1.0.0"),
        patch("aignostics_sdk.utils._user_agent.__repository_url__", "https://github.com/aignostics/python-sdk"),
    ):
        result = user_agent()

        # The GitHub Actions run URL (with +https prefix) should not be included
        # when GITHUB_REPOSITORY is not set
        assert "+https://github.com/aignostics/python-sdk/actions/runs/" not in result


@pytest.mark.unit
def test_user_agent_with_github_repository_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test user agent does not include GitHub Actions run URL when only GITHUB_REPOSITORY is set."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    monkeypatch.setenv("GITHUB_REPOSITORY", "aignostics/python-sdk")

    with (
        patch("aignostics_sdk.utils._user_agent.__project_name__", "aignostics"),
        patch("aignostics_sdk.utils._user_agent.__version_full__", "1.0.0"),
        patch("aignostics_sdk.utils._user_agent.__repository_url__", "https://github.com/aignostics/python-sdk"),
    ):
        result = user_agent()

        # The GitHub Actions run URL (with +https prefix) should not be included
        # when GITHUB_RUN_ID is not set
        assert "+https://github.com/aignostics/python-sdk/actions/runs/" not in result


@pytest.mark.unit
def test_user_agent_with_all_optional_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test user agent includes all optional information when all variables are set."""
    test_name = "tests/test_module.py::test_function"
    run_id = "12345678"
    repository = "aignostics/python-sdk"

    monkeypatch.setenv("PYTEST_CURRENT_TEST", test_name)
    monkeypatch.setenv("GITHUB_RUN_ID", run_id)
    monkeypatch.setenv("GITHUB_REPOSITORY", repository)

    with (
        patch("aignostics_sdk.utils._user_agent.__project_name__", "aignostics"),
        patch("aignostics_sdk.utils._user_agent.__version_full__", "1.0.0"),
        patch("aignostics_sdk.utils._user_agent.__repository_url__", "https://github.com/aignostics/python-sdk"),
    ):
        result = user_agent()

        # Check all components are present
        assert "aignostics-python-sdk/1.0.0" in result
        assert platform.platform() in result
        assert "https://github.com/aignostics/python-sdk" in result
        assert test_name in result
        expected_github_url = f"+https://github.com/{repository}/actions/runs/{run_id}"
        assert expected_github_url in result

        # Check ordering - test name should come before GitHub URL
        test_index = result.index(test_name)
        github_index = result.index(expected_github_url)
        assert test_index < github_index


@pytest.mark.unit
def test_user_agent_version_with_build_number(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test user agent properly handles version with build number."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)

    with (
        patch("aignostics_sdk.utils._user_agent.__project_name__", "aignostics"),
        patch("aignostics_sdk.utils._user_agent.__version_full__", "1.0.0+42"),
        patch("aignostics_sdk.utils._user_agent.__repository_url__", "https://github.com/aignostics/python-sdk"),
    ):
        result = user_agent()

        assert "aignostics-python-sdk/1.0.0+42" in result


@pytest.mark.unit
def test_user_agent_special_characters_in_test_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test user agent handles special characters in test names."""
    test_name = "tests/test_module.py::TestClass::test_method[param-with-dashes]"
    monkeypatch.setenv("PYTEST_CURRENT_TEST", test_name)
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)

    with (
        patch("aignostics_sdk.utils._user_agent.__project_name__", "aignostics"),
        patch("aignostics_sdk.utils._user_agent.__version_full__", "1.0.0"),
        patch("aignostics_sdk.utils._user_agent.__repository_url__", "https://github.com/aignostics/python-sdk"),
    ):
        result = user_agent()

        assert test_name in result


@pytest.mark.unit
def test_user_agent_format_consistency(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that user agent format is consistent across different scenarios."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)

    with (
        patch("aignostics_sdk.utils._user_agent.__project_name__", "aignostics"),
        patch("aignostics_sdk.utils._user_agent.__version_full__", "1.0.0"),
        patch("aignostics_sdk.utils._user_agent.__repository_url__", "https://github.com/aignostics/python-sdk"),
    ):
        result = user_agent()

        # Verify format: {base_info} ({system_info})
        assert result.count("(") == 1
        assert result.count(")") == 1
        assert result.index("(") < result.index(")")
        assert result.endswith(")")


@pytest.mark.unit
def test_user_agent_empty_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test user agent handles empty string environment variables correctly."""
    # Empty strings should be treated as not set
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "")
    monkeypatch.setenv("GITHUB_RUN_ID", "")
    monkeypatch.setenv("GITHUB_REPOSITORY", "")

    with (
        patch("aignostics_sdk.utils._user_agent.__project_name__", "aignostics"),
        patch("aignostics_sdk.utils._user_agent.__version_full__", "1.0.0"),
        patch("aignostics_sdk.utils._user_agent.__repository_url__", "https://github.com/aignostics/python-sdk"),
    ):
        result = user_agent()

        # Empty strings are falsy in Python, so they should not be included
        # Only base info and system info should be present
        # Should have: base_info, platform, repository_url (no optional parts)
        # Format: base_info (platform; repository_url)
        assert result.startswith("aignostics-python-sdk/1.0.0")
        # The GitHub Actions run URL should not be included with empty env vars
        assert "+https://github.com/aignostics/python-sdk/actions/runs/" not in result


@pytest.mark.unit
def test_user_agent_different_repository_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test user agent works with different repository URL formats."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)

    custom_repo_url = "https://gitlab.com/custom-org/custom-project"

    with (
        patch("aignostics_sdk.utils._user_agent.__project_name__", "aignostics"),
        patch("aignostics_sdk.utils._user_agent.__version_full__", "1.0.0"),
        patch("aignostics_sdk.utils._user_agent.__repository_url__", custom_repo_url),
    ):
        result = user_agent()

        assert custom_repo_url in result


@pytest.mark.unit
def test_user_agent_platform_info_included(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that platform information is always included."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)

    with (
        patch("aignostics_sdk.utils._user_agent.__project_name__", "aignostics"),
        patch("aignostics_sdk.utils._user_agent.__version_full__", "1.0.0"),
        patch("aignostics_sdk.utils._user_agent.__repository_url__", "https://github.com/aignostics/python-sdk"),
    ):
        result = user_agent()

        # Platform info should always be present
        platform_info = platform.platform()
        assert platform_info in result
