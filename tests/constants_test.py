"""Test constants used across multiple test modules.

Constants for application versions to test and timeouts to use for the corresponding runs
that are shared across different test modules to ensure consistency and easy maintenance.
"""

import os

HETA_SINGLE_SPOT_GS_URL = (
    "gs://platform-api-application-test-data/heta/slides/8fafc17d-a5cc-4e9d-a982-030b1486ca88.tiff"
)
HETA_SINGLE_SPOT_FILENAME = "8fafc17d-a5cc-4e9d-a982-030b1486ca88.tiff"
HETA_SINGLE_SPOT_FILESIZE = 10562338  # in bytes
HETA_SINGLE_SPOT_EXPECTED_RESULT_FILES = [
    ("tissue_segmentation_csv_class_information.csv", 342, 10),
    ("cell_classification_geojson_polygons.json", 16054058, 10),
    ("readout_generation_cell_readouts.csv", 2228907, 10),
    ("tissue_qc_csv_class_information.csv", 232, 10),
    ("tissue_segmentation_geojson_polygons.json", 270931, 10),
    ("tissue_qc_geojson_polygons.json", 180522, 10),
    ("tissue_qc_segmentation_map_image.tiff", 464908, 10),
    ("readout_generation_slide_readouts.csv", 295268, 10),
    ("tissue_segmentation_segmentation_map_image.tiff", 581258, 10),
]

HETA_ANOTHER_SPOT_GS_URL = (
    "gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
)
HETA_ANOTHER_SPOT_FILENAME = "9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
HETA_ANOTHER_SPOT_FILESIZE = 14681750  # in bytes
HETA_ANOTHER_SPOT_EXPECTED_RESULT_FILES = [
    ("tissue_segmentation_csv_class_information.csv", 361, 10),
    ("cell_classification_geojson_polygons.json", 9915953, 10),
    ("readout_generation_cell_readouts.csv", 1470036, 10),
    ("tissue_qc_csv_class_information.csv", 236, 10),
    ("tissue_segmentation_geojson_polygons.json", 927599, 10),
    ("tissue_qc_geojson_polygons.json", 315019, 10),
    ("tissue_segmentation_segmentation_map_image.tiff", 2989980, 10),
    ("readout_generation_slide_readouts.csv", 299865, 10),
    ("tissue_segmentation_segmentation_map_image.tiff", 581258, 10),
]

TEST_THREE_SPOTS_GS_URLS = [
    "gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff",
    "gs://aignx-storage-service-dev/sample_data_formatted/8c7b079e-8b8a-4036-bfde-5818352b503a.tiff",
    "gs://aignx-storage-service-dev/sample_data_formatted/1f4f366f-a2c5-4407-9f5e-23400b22d50e.tiff",
]

match os.getenv("AIGNOSTICS_PLATFORM_ENVIRONMENT", "production"):
    case "production":
        TEST_APPLICATION_ID = "test-app"
        TEST_APPLICATION_VERSION = "0.0.4"

        HETA_APPLICATION_ID = "he-tme"
        HETA_APPLICATION_VERSION = "1.0.0-beta.8"
    case "staging":
        TEST_APPLICATION_ID = "test-app"
        TEST_APPLICATION_VERSION = "0.0.5"

        HETA_APPLICATION_ID = "he-tme"
        HETA_APPLICATION_VERSION = "1.0.0-beta.8"
    case _:
        message = f"Unsupported AIGNOSTICS_PLATFORM_ENVIRONMENT value: {os.getenv('AIGNOSTICS_PLATFORM_ENVIRONMENT')}"
        raise ValueError(message)
