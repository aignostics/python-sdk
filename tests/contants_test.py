"""Test constants used across multiple test modules.

Constants for application versions to test and timeouts to use for the corresponding runs
that are shared across different test modules to ensure consistency and easy maintenance.
"""

import os

match os.getenv("AIGNOSTICS_PLATFORM_ENVIRONMENT", "production"):
    case "staging":
        TEST_APPLICATION_ID = "test-app"
        TEST_APPLICATION_VERSION = "0.0.5"
        TEST_APPLICATION_TIMEOUT_SECONDS = 60 * 45  # 45 minutes

        HETA_APPLICATION_ID = "he-tme"
        HETA_APPLICATION_VERSION = "1.0.0-beta.8"
        HETA_APPLICATION_TIMEOUT_SECONDS = 5 * 60 * 60  # 5 hours
    case _:
        TEST_APPLICATION_ID = "test-app"
        TEST_APPLICATION_VERSION = "0.0.5"
        TEST_APPLICATION_TIMEOUT_SECONDS = 60 * 45  # 45 minutes

        HETA_APPLICATION_ID = "he-tme"
        HETA_APPLICATION_VERSION = "1.0.0-beta.8"
        HETA_APPLICATION_TIMEOUT_SECONDS = 5 * 60 * 60  # 5 hours
