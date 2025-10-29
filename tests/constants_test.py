"""Test constants used across multiple test modules.

Constants for application versions to test and timeouts to use for the corresponding runs
that are shared across different test modules to ensure consistency and easy maintenance.
"""

import os

SPOT_0_GS_URL = "gs://platform-api-application-test-data/heta/slides/8fafc17d-a5cc-4e9d-a982-030b1486ca88.tiff"
SPOT_0_FILENAME = "8fafc17d-a5cc-4e9d-a982-030b1486ca88.tiff"
SPOT_0_FILESIZE = 10562338
SPOT_0_EXPECTED_RESULT_FILES = [
    ("tissue_qc_segmentation_map_image.tiff", 1698570, 10),
    ("tissue_qc_geojson_polygons.json", 315019, 10),
    ("tissue_segmentation_geojson_polygons.json", 927599, 10),
    ("readout_generation_slide_readouts.csv", 299865, 10),
    ("readout_generation_cell_readouts.csv", 1470036, 10),
    ("cell_classification_geojson_polygons.json", 9915953, 10),
    ("tissue_segmentation_segmentation_map_image.tiff", 2989980, 10),
    ("tissue_segmentation_csv_class_information.csv", 361, 10),
    ("tissue_qc_csv_class_information.csv", 236, 10),
]
SPOT_0_EXPECTED_CELLS_CLASSIFIED = (35160, 10)
SPOT_0_CRC32C = "5onqtA=="
SPOT_0_RESOLUTION_MPP = 0.26268186053789266
SPOT_0_WIDTH = 7447
SPOT_0_HEIGHT = 7196

SPOT_1_GS_URL = "gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
SPOT_1_FILENAME = "9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
SPOT_1_FILESIZE = 14681750
SPOT_1_EXPECTED_RESULT_FILES = [
    ("tissue_qc_segmentation_map_image.tiff", 464908, 10),
    ("tissue_qc_geojson_polygons.json", 180522, 10),
    ("tissue_segmentation_geojson_polygons.json", 270931, 10),
    ("readout_generation_slide_readouts.csv", 295268, 10),
    ("readout_generation_cell_readouts.csv", 2228907, 10),
    ("cell_classification_geojson_polygons.json", 16054058, 10),
    ("tissue_segmentation_segmentation_map_image.tiff", 581258, 10),
    ("tissue_segmentation_csv_class_information.csv", 342, 10),
    ("tissue_qc_csv_class_information.csv", 232, 10),
]
SPOT_1_CRC32C = "9l3NNQ=="
SPOT_1_WIDTH = 3728
SPOT_1_HEIGHT = 3640
SPOT_1_RESOLUTION_MPP = 0.46499982

SPOT_2_GS_URL = "gs://aignx-storage-service-dev/sample_data_formatted/8c7b079e-8b8a-4036-bfde-5818352b503a.tiff"
SPOT_2_FILENAME = "8c7b079e-8b8a-4036-bfde-5818352b503a.tiff"
SPOT_2_FILESIZE = 20153772
SPOT_2_CRC32C = "w+ud3g=="
SPOT_2_WIDTH = 3616
SPOT_2_HEIGHT = 3400
SPOT_2_RESOLUTION_MPP = 0.46499982

SPOT_3_GS_URL = "gs://aignx-storage-service-dev/sample_data_formatted/1f4f366f-a2c5-4407-9f5e-23400b22d50e.tiff"
SPOT_3_FILENAME = "1f4f366f-a2c5-4407-9f5e-23400b22d50e.tiff"
SPOT_3_CRC32C = "Zmx0wA=="
SPOT_3_WIDTH = 4016
SPOT_3_HEIGHT = 3952
SPOT_3_RESOLUTION_MPP = 0.46499982

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
        HETA_APPLICATION_VERSION = "1.0.0-sl+3"
    case _:
        message = f"Unsupported AIGNOSTICS_PLATFORM_ENVIRONMENT value: {os.getenv('AIGNOSTICS_PLATFORM_ENVIRONMENT')}"
        raise ValueError(message)
