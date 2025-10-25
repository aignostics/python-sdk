"""Test constants used across multiple test modules.

Constants for application versions to test and timeouts to use for the corresponding runs
that are shared across different test modules to ensure consistency and easy maintenance.
"""

import os

HETA_SINGLE_SPOT_GS_URL = (
    "gs://platform-api-application-test-data/heta/slides/8fafc17d-a5cc-4e9d-a982-030b1486ca88.tiff"
)

TEST_THREE_SPOTS_GS_URLS = [
    "gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff",
    "gs://aignx-storage-service-dev/sample_data_formatted/8c7b079e-8b8a-4036-bfde-5818352b503a.tiff",
    "gs://aignx-storage-service-dev/sample_data_formatted/1f4f366f-a2c5-4407-9f5e-23400b22d50e.tiff",
]

match os.getenv("AIGNOSTICS_PLATFORM_ENVIRONMENT", "production"):
    case "production":
        TEST_APPLICATION_ID = "test-app"
        TEST_APPLICATION_VERSION = "0.0.4"
        TEST_APPLICATION_TIMEOUT_SECONDS = 60 * 45  # 45 minutes

        HETA_APPLICATION_ID = "he-tme"
        HETA_APPLICATION_VERSION = "1.0.0-beta.8"
        HETA_APPLICATION_TIMEOUT_SECONDS = 5 * 60 * 60  # 5 hours
    case "staging":
        TEST_APPLICATION_ID = "test-app"
        TEST_APPLICATION_VERSION = "0.0.5"
        TEST_APPLICATION_TIMEOUT_SECONDS = 60 * 45  # 45 minutes

        HETA_APPLICATION_ID = "he-tme"
        HETA_APPLICATION_VERSION = "1.0.0-beta.8"
        HETA_APPLICATION_TIMEOUT_SECONDS = 5 * 60 * 60  # 5 hours
    case _:
        message = f"Unsupported AIGNOSTICS_PLATFORM_ENVIRONMENT value: {os.getenv('AIGNOSTICS_PLATFORM_ENVIRONMENT')}"
        raise ValueError(message)
