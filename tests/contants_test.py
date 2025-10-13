"""Test constants used across multiple test modules.

Constants for application versions to test and timeouts to use for the corresponding runs
that are shared across different test modules to ensure consistency and easy maintenance.
"""

# Test Application constants
TEST_APPLICATION_ID = "test-app"
TEST_APPLICATION_VERSION_ID = "test-app:v0.0.1"
TEST_APPLICATION_TIMEOUT_SECONDS = 60 * 45  # 45 minutes

# HETA Application constants
HETA_APPLICATION_ID = "he-tme"
HETA_APPLICATION_VERSION_ID = "he-tme:v1.0.0-beta.8"
HETA_APPLICATION_TIMEOUT_SECONDS = 60 * 60 * 5  # 5 hours
