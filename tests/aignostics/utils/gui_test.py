"""Tests for GUI module."""

import os
import platform
from unittest import mock

import pytest

from aignostics.utils._constants import __project_name__
from aignostics.utils._gui import (
    BasePageBuilder,
    gui_register_pages,
    gui_run,
)


@pytest.mark.unit
def test_base_page_builder_is_abstract(record_property) -> None:
    """Test that BasePageBuilder is an abstract class.

    Args:
        record_property: pytest record_property fixture
    """
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with pytest.raises(TypeError):
        BasePageBuilder()  # type: ignore # Cannot instantiate abstract class


@pytest.mark.unit
def test_register_pages_is_abstract(record_property) -> None:
    """Test that register_pages is an abstract method.

    Args:
        record_property: pytest record_property fixture
    """
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")

    class IncompletePageBuilder(BasePageBuilder):
        pass

    with pytest.raises(TypeError):
        IncompletePageBuilder()  # type: ignore # Abstract method not implemented


@pytest.mark.unit
@mock.patch("aignostics.utils._gui.locate_subclasses")
def test_register_pages_calls_all_builders(record_property, mock_locate_subclasses: mock.MagicMock) -> None:
    """Test that gui_register_pages calls register_pages on all builders.

    Args:
        mock_locate_subclasses: Mock for locate_subclasses function
        record_property: pytest record_property fixture
    """
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    # Create mock page builders
    mock_builder1 = mock.MagicMock()
    mock_builder2 = mock.MagicMock()
    mock_locate_subclasses.return_value = [mock_builder1, mock_builder2]

    # Call the function
    gui_register_pages()

    # Assert each builder's register_pages was called
    mock_builder1.register_pages.assert_called_once()
    mock_builder2.register_pages.assert_called_once()


@pytest.mark.unit
@pytest.mark.skip(reason="Nicegui 3 complexity.")
@mock.patch("aignostics.utils._gui.__is_running_in_container__", False)
@mock.patch("aignostics.utils._gui.gui_register_pages")
@mock.patch("nicegui.ui")
def test_gui_run_default_params(record_property, mock_ui: mock.MagicMock, mock_register_pages: mock.MagicMock) -> None:
    """Test gui_run with default parameters.

    Args:
        mock_ui: Mock for nicegui UI
        mock_register_pages: Mock for gui_register_pages function
        nicegui_reset_globals: Fixture to reset NiceGUI globals
        record_property: pytest record_property fixture
    """
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with mock.patch("nicegui.native.find_open_port", return_value=8000):
        os.environ["NICEGUI_SCREEN_TEST_PORT"] = "3392"
        gui_run()
        mock_register_pages.assert_called_once()
        mock_ui.run.assert_called_once()
        # Verify default parameters
        call_kwargs = mock_ui.run.call_args[1]
        assert call_kwargs["title"] == __project_name__
        assert call_kwargs["native"] is (platform.system() != "Linux")
        assert call_kwargs["reload"] is False
        assert call_kwargs["port"] == 8000


@pytest.mark.unit
@mock.patch("aignostics.utils._gui.__is_running_in_container__", False)
@mock.patch("aignostics.utils._gui.gui_register_pages")
@mock.patch("nicegui.ui.run")
def test_gui_run_custom_params(
    record_property, mock_ui_run: mock.MagicMock, mock_register_pages: mock.MagicMock
) -> None:
    """Test gui_run with custom parameters.

    Args:
        mock_ui_run: Mock for nicegui UI run
        mock_register_pages: Mock for gui_register_pages function
        nicegui_reset_globals: Fixture to reset NiceGUI globals
        record_property: pytest record_property fixture
    """
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    os.environ["NICEGUI_SCREEN_TEST_PORT"] = "3392"
    gui_run(
        native=False,
        show=True,
        host="0.0.0.0",
        port=5000,
        title="Test GUI",
        watch=True,
    )
    mock_register_pages.assert_called_once()
    mock_ui_run.assert_called_once()
    # Verify custom parameters
    call_kwargs = mock_ui_run.call_args[1]
    assert call_kwargs["title"] == "Test GUI"
    assert call_kwargs["native"] is False
    assert call_kwargs["reload"] is True
    assert call_kwargs["host"] == "0.0.0.0"
    assert call_kwargs["port"] == 5000
    assert call_kwargs["show"] is True


@pytest.mark.unit
@mock.patch("aignostics.utils._gui.__is_running_in_container__", True)
@mock.patch("nicegui.ui.run")
def test_gui_run_in_container_with_native(record_property, mock_ui: mock.MagicMock) -> None:
    """Test that gui_run raises ValueError when running native in container.

    Args:
        mock_ui: Mock for nicegui UI run
        nicegui_reset_globals: Fixture to reset NiceGUI globals
        record_property: pytest record_property fixture
    """
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with pytest.raises(ValueError) as excinfo:
        gui_run(native=True)
    assert "Native GUI cannot be run in a container" in str(excinfo.value)
    mock_ui.assert_not_called()
