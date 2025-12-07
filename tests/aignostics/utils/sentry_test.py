"""Tests for Sentry settings."""

from importlib.util import find_spec

if find_spec("sentry_sdk"):
    import os
    import re
    from collections.abc import Generator
    from unittest import mock

    import pytest
    from pydantic import SecretStr

    from aignostics.utils._sentry import (
        _ERR_MSG_INVALID_DOMAIN,
        _ERR_MSG_MISSING_NETLOC,
        _ERR_MSG_MISSING_SCHEME,
        _ERR_MSG_NON_HTTPS,
        _validate_https_dsn,
        _validate_https_scheme,
        _validate_sentry_domain,
        _validate_url_netloc,
        _validate_url_scheme,
        sentry_initialize,
    )

    VALID_DSN = "https://abcdef1234567890@o12345.ingest.us.sentry.io/1234567890"

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
    def test_validate_url_scheme(record_property) -> None:
        """Test URL scheme validation."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        import urllib.parse

        # Valid case
        parsed_url = urllib.parse.urlparse(VALID_DSN)
        _validate_url_scheme(parsed_url)  # Should not raise

        # Invalid case - missing scheme
        invalid_url = urllib.parse.urlparse("//missing-scheme.com")
        with pytest.raises(ValueError, match=re.escape(_ERR_MSG_MISSING_SCHEME)):
            _validate_url_scheme(invalid_url)

    @pytest.mark.unit
    def test_validate_url_netloc(record_property) -> None:
        """Test network location validation."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        import urllib.parse

        # Valid case
        parsed_url = urllib.parse.urlparse(VALID_DSN)
        _validate_url_netloc(parsed_url)  # Should not raise

        # Invalid case - missing netloc
        invalid_url = urllib.parse.urlparse("https://")
        with pytest.raises(ValueError, match=re.escape(_ERR_MSG_MISSING_NETLOC)):
            _validate_url_netloc(invalid_url)

    @pytest.mark.unit
    def test_validate_https_scheme(record_property) -> None:
        """Test HTTPS scheme validation."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        import urllib.parse

        # Valid case
        parsed_url = urllib.parse.urlparse(VALID_DSN)
        _validate_https_scheme(parsed_url)  # Should not raise

        # Invalid case - HTTP scheme
        invalid_url = urllib.parse.urlparse("http://example.com")
        with pytest.raises(ValueError, match=re.escape(_ERR_MSG_NON_HTTPS)):
            _validate_https_scheme(invalid_url)

    @pytest.mark.unit
    def test_validate_sentry_domain(record_property) -> None:
        """Test Sentry domain validation."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        import urllib.parse

        # Valid cases
        parsed_url = urllib.parse.urlparse(VALID_DSN)
        _validate_sentry_domain(parsed_url.netloc)  # Should not raise

        parsed_url = urllib.parse.urlparse("https://abcdef1234567890@o12345.ingest.de.sentry.io/1234567890")
        _validate_sentry_domain(parsed_url.netloc)  # Should not raise

        # Invalid case - missing @
        invalid_netloc = "example.com"
        with pytest.raises(ValueError, match=re.escape(_ERR_MSG_INVALID_DOMAIN)):
            _validate_sentry_domain(invalid_netloc)

        # Invalid case - wrong domain format
        invalid_netloc = "user@example.com"
        with pytest.raises(ValueError, match=re.escape(_ERR_MSG_INVALID_DOMAIN)):
            _validate_sentry_domain(invalid_netloc)

    @pytest.mark.unit
    def test_validate_https_dsn_with_valid_dsn(record_property) -> None:
        """Test DSN validation with valid DSN."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        valid_dsn = SecretStr(VALID_DSN)
        result = _validate_https_dsn(valid_dsn)
        assert result is valid_dsn  # Should return the same object

    @pytest.mark.unit
    def test_validate_https_dsn_with_none(record_property) -> None:
        """Test DSN validation with None value."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        result = _validate_https_dsn(None)
        assert result is None  # Should return None unchanged

    @pytest.mark.unit
    def test_validate_https_dsn_invalid_cases(record_property) -> None:
        """Test DSN validation with various invalid cases."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        # Missing scheme
        with pytest.raises(ValueError, match=re.escape(_ERR_MSG_MISSING_SCHEME)):
            _validate_https_dsn(SecretStr("//invalid.com"))

        # Missing netloc
        with pytest.raises(ValueError, match=re.escape(_ERR_MSG_MISSING_NETLOC)):
            _validate_https_dsn(SecretStr("https://"))

        # HTTP scheme instead of HTTPS
        with pytest.raises(ValueError, match=re.escape(_ERR_MSG_NON_HTTPS)):
            _validate_https_dsn(SecretStr("http://abcdef1234567890@o12345.ingest.us.sentry.io/1234567890"))

        # Invalid Sentry domain
        with pytest.raises(ValueError, match=re.escape(_ERR_MSG_INVALID_DOMAIN)):
            _validate_https_dsn(SecretStr("https://user@example.com"))

    @pytest.mark.unit
    def test_sentry_initialize_with_no_dsn(record_property, mock_environment: None) -> None:
        """Test sentry_initialize with no DSN."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        with mock.patch("aignostics.utils._sentry.load_settings") as mock_load_settings:
            mock_settings = mock.MagicMock()
            mock_settings.dsn = None
            mock_load_settings.return_value = mock_settings

            result = sentry_initialize(integrations=None)
            assert result is False  # Should return False when no DSN is provided

    @pytest.mark.unit
    def test_sentry_initialize_with_valid_dsn(record_property, mock_environment: None) -> None:
        """Test sentry_initialize with a valid DSN."""
        record_property("tested-item-id", "SPEC-UTILS-SERVICE")
        with (
            mock.patch("aignostics.utils._sentry.load_settings") as mock_load_settings,
            mock.patch("sentry_sdk.init") as mock_sentry_init,
        ):
            mock_settings = mock.MagicMock()
            mock_settings.dsn = SecretStr(VALID_DSN)
            mock_settings.enabled = True
            mock_load_settings.return_value = mock_settings

            result = sentry_initialize(integrations=None)

            assert result is True  # Should return True when initialization is successful
            mock_sentry_init.assert_called_once()  # Should call sentry_sdk.init
