"""Tests of the system service."""

import os
from unittest import mock

import pytest

from aignostics.system._service import Service


@pytest.mark.timeout(15)
def test_is_token_valid() -> None:
    """Test that is_token_valid works correctly with environment variable."""
    # Set the environment variable for the test
    the_value = "the_value"
    with mock.patch.dict(os.environ, {"AIGNOSTICS_SYSTEM_TOKEN": the_value}):
        # Create a new service instance to pick up the environment variable
        service = Service()

        # Test with matching token
        assert service.is_token_valid(the_value) is True

        # Test with non-matching token
        assert service.is_token_valid("wrong-value") is False

        # Test with empty token
        assert service.is_token_valid("") is False


def test_is_token_valid_when_not_set() -> None:
    """Test that is_token_valid handles the case when no token is set."""
    # Ensure the environment variable is not set
    with mock.patch.dict(os.environ, {"AIGNOSTICS_SYSTEM_TOKEN": ""}, clear=True):
        # Create a new service instance with no token set
        service = Service()

        # Should return False for any token when no token is set
        assert service.is_token_valid("any-token") is False
        assert service.is_token_valid("") is False
