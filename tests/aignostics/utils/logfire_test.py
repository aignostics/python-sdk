"""Tests for Logfire integration."""

from importlib.util import find_spec

if find_spec("logfire"):
    import os
    from collections.abc import Generator
    from unittest import mock

    import pytest
    from pydantic import SecretStr

    from aignostics.utils import get_logger
    from aignostics.utils._logfire import logfire_initialize

    log = get_logger(__name__)

    VALID_TOKEN = "test_token_12345"  # noqa: S105

    @pytest.fixture
    def mock_environment() -> Generator[None, None, None]:
        """Fixture to set up the environment for testing."""
        with mock.patch.dict(
            os.environ,
            {
                "PATH": os.environ.get("PATH", ""),  # Needed for Win32
            },
            clear=True,
        ):
            yield

    @pytest.mark.unit
    def test_logfire_initialize_with_no_token(record_property, mock_environment: None) -> None:
        """Test logfire_initialize with no token."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        with mock.patch("aignostics.utils._logfire.load_settings") as mock_load_settings:
            mock_settings = mock.MagicMock()
            mock_settings.token = None
            mock_settings.enabled = True
            mock_load_settings.return_value = mock_settings

            result = logfire_initialize(modules_to_instrument=None)
            assert result is False  # Should return False when no token is provided
            # Verify LOGFIRE_PYDANTIC_RECORD is turned off
            assert os.environ.get("LOGFIRE_PYDANTIC_RECORD") == "off"

    @pytest.mark.unit
    def test_logfire_initialize_with_disabled_setting(record_property, mock_environment: None) -> None:
        """Test logfire_initialize with enabled=False."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        with mock.patch("aignostics.utils._logfire.load_settings") as mock_load_settings:
            mock_settings = mock.MagicMock()
            mock_settings.token = SecretStr(VALID_TOKEN)
            mock_settings.enabled = False
            mock_load_settings.return_value = mock_settings

            result = logfire_initialize(modules_to_instrument=None)
            assert result is False  # Should return False when disabled
            # Verify LOGFIRE_PYDANTIC_RECORD is turned off
            assert os.environ.get("LOGFIRE_PYDANTIC_RECORD") == "off"

    @pytest.mark.unit
    def test_logfire_initialize_with_valid_token(record_property, mock_environment: None) -> None:
        """Test logfire_initialize with a valid token."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        with (
            mock.patch("aignostics.utils._logfire.load_settings") as mock_load_settings,
            mock.patch("logfire.configure") as mock_logfire_configure,
            mock.patch("logfire.instrument_pydantic") as mock_instrument_pydantic,
        ):
            mock_settings = mock.MagicMock()
            mock_settings.token = SecretStr(VALID_TOKEN)
            mock_settings.enabled = True
            mock_settings.instrument_system_metrics = False
            mock_load_settings.return_value = mock_settings

            result = logfire_initialize(modules_to_instrument=None)

            assert result is True  # Should return True when initialization is successful
            mock_logfire_configure.assert_called_once()  # Should call logfire.configure
            mock_instrument_pydantic.assert_called_once()  # Should instrument pydantic

            # Verify configure was called with correct parameters
            call_kwargs = mock_logfire_configure.call_args[1]
            assert call_kwargs["send_to_logfire"] == "if-token-present"
            assert call_kwargs["token"] == VALID_TOKEN
            assert call_kwargs["console"] is False

    @pytest.mark.unit
    def test_logfire_initialize_with_system_metrics(record_property, mock_environment: None) -> None:
        """Test logfire_initialize with system metrics enabled."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        with (
            mock.patch("aignostics.utils._logfire.load_settings") as mock_load_settings,
            mock.patch("logfire.configure") as mock_logfire_configure,
            mock.patch("logfire.instrument_pydantic") as mock_instrument_pydantic,
            mock.patch("logfire.instrument_system_metrics") as mock_instrument_system_metrics,
        ):
            mock_settings = mock.MagicMock()
            mock_settings.token = SecretStr(VALID_TOKEN)
            mock_settings.enabled = True
            mock_settings.instrument_system_metrics = True
            mock_load_settings.return_value = mock_settings

            result = logfire_initialize(modules_to_instrument=None)

            assert result is True
            mock_logfire_configure.assert_called_once()
            mock_instrument_pydantic.assert_called_once()
            mock_instrument_system_metrics.assert_called_once_with(base="full")

    @pytest.mark.unit
    def test_logfire_initialize_with_modules_to_instrument(record_property, mock_environment: None) -> None:
        """Test logfire_initialize with modules to instrument."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        with (
            mock.patch("aignostics.utils._logfire.load_settings") as mock_load_settings,
            mock.patch("logfire.configure") as mock_logfire_configure,
            mock.patch("logfire.instrument_pydantic") as mock_instrument_pydantic,
            mock.patch("logfire.install_auto_tracing") as mock_install_auto_tracing,
        ):
            mock_settings = mock.MagicMock()
            mock_settings.token = SecretStr(VALID_TOKEN)
            mock_settings.enabled = True
            mock_settings.instrument_system_metrics = False
            mock_load_settings.return_value = mock_settings

            modules = ["module1", "module2"]
            result = logfire_initialize(modules_to_instrument=modules)

            assert result is True
            mock_logfire_configure.assert_called_once()
            mock_instrument_pydantic.assert_called_once()
            mock_install_auto_tracing.assert_called_once_with(modules=modules, min_duration=0.0)

    @pytest.mark.unit
    def test_logfire_initialize_with_empty_modules_list(record_property, mock_environment: None) -> None:
        """Test logfire_initialize with empty modules list."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        with (
            mock.patch("aignostics.utils._logfire.load_settings") as mock_load_settings,
            mock.patch("logfire.configure") as mock_logfire_configure,
            mock.patch("logfire.instrument_pydantic") as mock_instrument_pydantic,
            mock.patch("logfire.install_auto_tracing") as mock_install_auto_tracing,
        ):
            mock_settings = mock.MagicMock()
            mock_settings.token = SecretStr(VALID_TOKEN)
            mock_settings.enabled = True
            mock_settings.instrument_system_metrics = False
            mock_load_settings.return_value = mock_settings

            result = logfire_initialize(modules_to_instrument=[])

            assert result is True
            mock_logfire_configure.assert_called_once()
            mock_instrument_pydantic.assert_called_once()
            # Should NOT call install_auto_tracing with empty list
            mock_install_auto_tracing.assert_not_called()

    @pytest.mark.unit
    def test_logfire_initialize_with_none_modules(record_property, mock_environment: None) -> None:
        """Test logfire_initialize with None modules."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        with (
            mock.patch("aignostics.utils._logfire.load_settings") as mock_load_settings,
            mock.patch("logfire.configure") as mock_logfire_configure,
            mock.patch("logfire.instrument_pydantic") as mock_instrument_pydantic,
            mock.patch("logfire.install_auto_tracing") as mock_install_auto_tracing,
        ):
            mock_settings = mock.MagicMock()
            mock_settings.token = SecretStr(VALID_TOKEN)
            mock_settings.enabled = True
            mock_settings.instrument_system_metrics = False
            mock_load_settings.return_value = mock_settings

            result = logfire_initialize(modules_to_instrument=None)

            assert result is True
            mock_logfire_configure.assert_called_once()
            mock_instrument_pydantic.assert_called_once()
            # Should NOT call install_auto_tracing with None
            mock_install_auto_tracing.assert_not_called()
