"""Test constants used across multiple test modules.

Constants for application versions to test and timeouts to use for the corresponding runs
that are shared across different test modules to ensure consistency and easy maintenance.
"""

# Test Application constants
TEST_APPLICATION_ID = "test-app"
TEST_APPLICATION_VERSION = "0.0.1"
TEST_APPLICATION_TIMEOUT_SECONDS = 2 * 60 * 60  # 1 hour

# HETA Application constants
HETA_APPLICATION_ID = "he-tme"
HETA_APPLICATION_VERSION = "1.0.0-beta.8"
HETA_APPLICATION_TIMEOUT_SECONDS = 6 * 60 * 60  # 6 hours
