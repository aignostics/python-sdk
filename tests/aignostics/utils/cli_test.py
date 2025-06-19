"""Tests for CLI utilities."""

from typing import Optional
from unittest.mock import MagicMock, Mock, patch

import pytest
from typer.models import CommandInfo, TyperInfo

from aignostics.utils._cli import prepare_cli

# Constants to avoid duplication
LOCATE_IMPLEMENTATIONS_PATH = "aignostics.utils._cli.locate_implementations"
TEST_EPILOG = "Test Epilog"


class MockTyper:
    """Mock Typer class for stattesting."""

    def __init__(self) -> None:
        """Initialize the mock Typer with necessary attributes."""
        self.registered_commands: list[CommandInfo] = []
        self.registered_groups: list[TyperInfo] = []
        self.info = Mock()
        self.info.epilog = ""
        self.info.no_args_is_help = False
        self.typer_instance = None

    def add_typer(self, cli: "MockTyper") -> None:
        """Mock method to add a typer instance."""

    def callback(self, *, invoke_without_command: bool = False) -> "callable":  # noqa: PLR6301
        """Mock callback method that returns a decorator function."""

        def decorator(func: "callable") -> "callable":
            """Decorator function that just returns the original function."""
            return func

        return decorator


class MockCommand:
    """Mock Command class for testing."""

    def __init__(self) -> None:
        """Initialize the mock Command."""
        self.epilog = ""


class MockGroup:
    """Mock Group class for testing."""

    def __init__(self, instance: Optional["MockTyper"] = None) -> None:
        """Initialize the mock Group."""
        self.typer_instance = instance
        self.no_args_is_help = False


@pytest.fixture
def mock_typer() -> MockTyper:
    """Create a mock typer instance for testing."""
    return MockTyper()


@pytest.fixture
def mock_command() -> MockCommand:
    """Create a mock command for testing."""
    return MockCommand()


@pytest.fixture
def mock_group(mock_typer: MockTyper) -> MockGroup:
    """Create a mock group for testing."""
    return MockGroup(mock_typer)


def test_prepare_cli_adds_typers(mock_typer: MockTyper) -> None:
    """Test that prepare_cli correctly adds discovered typers."""
    with patch(LOCATE_IMPLEMENTATIONS_PATH) as mock_locate:
        # Create a different typer instance to be discovered
        other_typer = MockTyper()
        mock_locate.return_value = [other_typer]

        # Mock the add_typer method
        mock_typer.add_typer = MagicMock()

        prepare_cli(mock_typer, TEST_EPILOG)

        # Verify add_typer was called with the discovered typer
        mock_typer.add_typer.assert_called_once_with(other_typer)


def test_prepare_cli_sets_epilog(mock_typer: MockTyper) -> None:
    """Test that prepare_cli correctly sets the epilog."""
    with patch(LOCATE_IMPLEMENTATIONS_PATH, return_value=[]):
        prepare_cli(mock_typer, TEST_EPILOG)
        assert mock_typer.info.epilog == TEST_EPILOG


@pytest.mark.skip(reason="https://github.com/fastapi/typer/pull/1240")
def test_prepare_cli_sets_no_args_is_help(mock_typer: MockTyper) -> None:
    """Test that prepare_cli correctly sets no_args_is_help."""
    with patch(LOCATE_IMPLEMENTATIONS_PATH, return_value=[]):
        prepare_cli(mock_typer, TEST_EPILOG)
        assert mock_typer.info.no_args_is_help is True


@pytest.mark.parametrize(
    ("argv_parts", "expected_calls"),
    [
        (["script", "with", "typer"], 0),  # Contains "typer", don't add epilog recursively
        (["script", "without", "keywords"], 1),  # Doesn't contain "typer", add epilog recursively
    ],
)
def test_prepare_cli_conditional_epilog_recursion(
    argv_parts: list[str],
    expected_calls: int,
    mock_typer: MockTyper,
) -> None:
    """Test that prepare_cli conditionally calls _add_epilog_recursively based on sys.argv."""
    with (
        patch(LOCATE_IMPLEMENTATIONS_PATH, return_value=[]),
        patch("aignostics.utils._cli.Path") as mock_path,
        patch("aignostics.utils._cli._add_epilog_recursively") as mock_add_epilog,
    ):
        mock_path.return_value.parts = argv_parts
        prepare_cli(mock_typer, TEST_EPILOG)
        assert mock_add_epilog.call_count == expected_calls


def test_add_epilog_recursively_with_cycle(mock_typer: MockTyper) -> None:
    """Test that _add_epilog_recursively handles cycles in the typer structure."""
    # Create a cycle by having the typer reference itself
    mock_typer.registered_groups = []
    group = Mock(spec=TyperInfo)
    group.typer_instance = mock_typer
    mock_typer.registered_groups.append(group)
