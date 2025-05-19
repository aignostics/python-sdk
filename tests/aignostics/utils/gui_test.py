"""Tests for GUI module."""

import platform
from unittest import mock

import pytest

from aignostics.utils._constants import __project_name__
from aignostics.utils._gui import (
    BasePageBuilder,
    gui_register_pages,
    gui_run,
)


def test_base_page_builder_is_abstract() -> None:
    """Test that BasePageBuilder is an abstract class.

    Args:
        None
    """
    with pytest.raises(TypeError):
        BasePageBuilder()  # type: ignore # Cannot instantiate abstract class


def test_register_pages_is_abstract() -> None:
    """Test that register_pages is an abstract method.

    Args:
        None
    """

    class IncompletePageBuilder(BasePageBuilder):
        pass

    with pytest.raises(TypeError):
        IncompletePageBuilder()  # type: ignore # Abstract method not implemented


@mock.patch("aignostics.utils._gui.locate_subclasses")
def test_register_pages_calls_all_builders(mock_locate_subclasses: mock.MagicMock) -> None:
    """Test that gui_register_pages calls register_pages on all builders.

    Args:
        mock_locate_subclasses: Mock for locate_subclasses function
    """
    # Create mock page builders
    mock_builder1 = mock.MagicMock()
    mock_builder2 = mock.MagicMock()
    mock_locate_subclasses.return_value = [mock_builder1, mock_builder2]

    # Call the function
    gui_register_pages()

    # Assert each builder's register_pages was called
    mock_builder1.register_pages.assert_called_once()
    mock_builder2.register_pages.assert_called_once()


@mock.patch("aignostics.utils._gui.__is_running_in_container__", False)
@mock.patch("aignostics.utils._gui.gui_register_pages")
@mock.patch("nicegui.ui")
def test_gui_run_default_params(mock_ui: mock.MagicMock, mock_register_pages: mock.MagicMock) -> None:
    """Test gui_run with default parameters.

    Args:
        mock_ui: Mock for nicegui UI
        mock_register_pages: Mock for gui_register_pages function
    """
    with mock.patch("nicegui.native.find_open_port", return_value=8000):
        gui_run()
        mock_register_pages.assert_called_once()
        mock_ui.run.assert_called_once()
        # Verify default parameters
        call_kwargs = mock_ui.run.call_args[1]
        assert call_kwargs["title"] == __project_name__
        assert call_kwargs["native"] is (platform.system() != "Linux")
        assert call_kwargs["reload"] is False
        assert call_kwargs["port"] == 8000


@mock.patch("aignostics.utils._gui.__is_running_in_container__", False)
@mock.patch("aignostics.utils._gui.gui_register_pages")
@mock.patch("nicegui.ui")
def test_gui_run_custom_params(mock_ui: mock.MagicMock, mock_register_pages: mock.MagicMock) -> None:
    """Test gui_run with custom parameters.

    Args:
        mock_ui: Mock for nicegui UI
        mock_register_pages: Mock for gui_register_pages function
    """
    gui_run(
        native=False,
        show=True,
        host="0.0.0.0",
        port=5000,
        title="Test GUI",
        watch=True,
    )
    mock_register_pages.assert_called_once()
    mock_ui.run.assert_called_once()
    # Verify custom parameters
    call_kwargs = mock_ui.run.call_args[1]
    assert call_kwargs["title"] == "Test GUI"
    assert call_kwargs["native"] is False
    assert call_kwargs["reload"] is True
    assert call_kwargs["host"] == "0.0.0.0"
    assert call_kwargs["port"] == 5000
    assert call_kwargs["show"] is True


@mock.patch("aignostics.utils._gui.__is_running_in_container__", True)
@mock.patch("nicegui.ui")
def test_gui_run_in_container_with_native(mock_ui: mock.MagicMock) -> None:
    """Test that gui_run raises ValueError when running native in container.

    Args:
        mock_ui: Mock for nicegui UI
    """
    with pytest.raises(ValueError) as excinfo:
        gui_run(native=True)
    assert "Native GUI cannot be run in a container" in str(excinfo.value)
    mock_ui.run.assert_not_called()
