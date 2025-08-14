"""Tests for Sentry settings."""

from importlib.util import find_spec

if find_spec("sentry_sdk"):
    import os
    import re
    from collections.abc import Generator
    from unittest import mock

    import pytest
    from pydantic import SecretStr

    from aignostics.utils import get_logger
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

    log = get_logger(__name__)

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

    def test_validate_url_scheme() -> None:
        """Test URL scheme validation."""
        import urllib.parse

        # Valid case
        parsed_url = urllib.parse.urlparse(VALID_DSN)
        _validate_url_scheme(parsed_url)  # Should not raise

        # Invalid case - missing scheme
        invalid_url = urllib.parse.urlparse("//missing-scheme.com")
        with pytest.raises(ValueError, match=re.escape(_ERR_MSG_MISSING_SCHEME)):
            _validate_url_scheme(invalid_url)

    def test_validate_url_netloc() -> None:
        """Test network location validation."""
        import urllib.parse

        # Valid case
        parsed_url = urllib.parse.urlparse(VALID_DSN)
        _validate_url_netloc(parsed_url)  # Should not raise

        # Invalid case - missing netloc
        invalid_url = urllib.parse.urlparse("https://")
        with pytest.raises(ValueError, match=re.escape(_ERR_MSG_MISSING_NETLOC)):
            _validate_url_netloc(invalid_url)

    def test_validate_https_scheme() -> None:
        """Test HTTPS scheme validation."""
        import urllib.parse

        # Valid case
        parsed_url = urllib.parse.urlparse(VALID_DSN)
        _validate_https_scheme(parsed_url)  # Should not raise

        # Invalid case - HTTP scheme
        invalid_url = urllib.parse.urlparse("http://example.com")
        with pytest.raises(ValueError, match=re.escape(_ERR_MSG_NON_HTTPS)):
            _validate_https_scheme(invalid_url)

    def test_validate_sentry_domain() -> None:
        """Test Sentry domain validation."""
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

    def test_validate_https_dsn_with_valid_dsn() -> None:
        """Test DSN validation with valid DSN."""
        valid_dsn = SecretStr(VALID_DSN)
        result = _validate_https_dsn(valid_dsn)
        assert result is valid_dsn  # Should return the same object

    def test_validate_https_dsn_with_none() -> None:
        """Test DSN validation with None value."""
        result = _validate_https_dsn(None)
        assert result is None  # Should return None unchanged

    def test_validate_https_dsn_invalid_cases() -> None:
        """Test DSN validation with various invalid cases."""
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

    def test_sentry_initialize_with_no_dsn(mock_environment: None) -> None:
        """Test sentry_initialize with no DSN."""
        with mock.patch("aignostics.utils._sentry.load_settings") as mock_load_settings:
            mock_settings = mock.MagicMock()
            mock_settings.dsn = None
            mock_load_settings.return_value = mock_settings

            result = sentry_initialize()
            assert result is False  # Should return False when no DSN is provided

    def test_sentry_initialize_with_valid_dsn(mock_environment: None) -> None:
        """Test sentry_initialize with a valid DSN."""
        with (
            mock.patch("aignostics.utils._sentry.load_settings") as mock_load_settings,
            mock.patch("sentry_sdk.init") as mock_sentry_init,
        ):
            mock_settings = mock.MagicMock()
            mock_settings.dsn = SecretStr(VALID_DSN)
            mock_load_settings.return_value = mock_settings

            result = sentry_initialize()

            assert result is True  # Should return True when initialization is successful
            mock_sentry_init.assert_called_once()  # Should call sentry_sdk.init
