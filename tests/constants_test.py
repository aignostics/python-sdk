"""Test constants used across multiple test modules.

Constants for application versions to test and timeouts to use for the corresponding runs
that are shared across different test modules to ensure consistency and easy maintenance.
"""

import os

TEST_SUITE = "AIGNOSTICS"

SPOT_0_GS_URL = (
    "gs://aignostics-platform-ext-a4f7e9/python-sdk-tests/he-tme/slides/8fafc17d-a5cc-4e9d-a982-030b1486ca88.tiff"
)
SPOT_0_FILENAME = "8fafc17d-a5cc-4e9d-a982-030b1486ca88.tiff"
SPOT_0_CRC32C = "5onqtA=="
SPOT_0_FILESIZE = 10562338
SPOT_0_RESOLUTION_MPP = 0.26268186053789266
SPOT_0_WIDTH = 7447
SPOT_0_HEIGHT = 7196

SPOT_1_GS_URL = (
    "gs://aignostics-platform-ext-a4f7e9/python-sdk-tests/he-tme/slides/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
)
SPOT_1_FILENAME = "9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
SPOT_1_CRC32C = "9l3NNQ=="
SPOT_1_FILESIZE = 14681750
SPOT_1_RESOLUTION_MPP = 0.46499982
SPOT_1_WIDTH = 3728
SPOT_1_HEIGHT = 3640

SPOT_2_GS_URL = (
    "gs://aignostics-platform-ext-a4f7e9/python-sdk-tests/he-tme/slides/8c7b079e-8b8a-4036-bfde-5818352b503a.tiff"
)
SPOT_2_FILENAME = "8c7b079e-8b8a-4036-bfde-5818352b503a.tiff"
SPOT_2_CRC32C = "w+ud3g=="
SPOT_2_RESOLUTION_MPP = 0.46499982
SPOT_2_WIDTH = 3616
SPOT_2_HEIGHT = 3400

SPOT_3_GS_URL = (
    "gs://aignostics-platform-ext-a4f7e9/python-sdk-tests/he-tme/slides/1f4f366f-a2c5-4407-9f5e-23400b22d50e.tiff"
)
SPOT_3_FILENAME = "1f4f366f-a2c5-4407-9f5e-23400b22d50e.tiff"
SPOT_3_CRC32C = "Zmx0wA=="
SPOT_3_RESOLUTION_MPP = 0.46499982
SPOT_3_WIDTH = 4016
SPOT_3_HEIGHT = 3952

match os.getenv("AIGNOSTICS_PLATFORM_ENVIRONMENT", "production"):
    case "production":
        TEST_APPLICATION_ID = "test-app"
        TEST_APPLICATION_VERSION = "0.0.6"

        HETA_APPLICATION_ID = "he-tme"
        HETA_APPLICATION_VERSION = "1.0.0"
        TEST_APPLICATION_VERSION_USE_LATEST_FALLBACK_SKIP = False

        PIPELINE_GPU_TYPE = "L4"
        PIPELINE_GPU_PROVISIONING_MODE = "SPOT"
        PIPELINE_GPU_FLEX_START_MAX_RUN_DURATION_MINUTES = None
        PIPELINE_MAX_GPUS_PER_SLIDE = 1
        PIPELINE_CPU_PROVISIONING_MODE = "SPOT"
        PIPELINE_NODE_ACQUISITION_TIMEOUT_MINUTES = (
            30  # Respected starting with 1.0.0-sl.4.1+internal, until then set to 60min by application itself.
        )

        SPECIAL_APPLICATION_ID = "test-app"
        SPECIAL_APPLICATION_VERSION = "0.99.0"

        SPOT_0_EXPECTED_RESULT_FILES = [
            ("tissue_qc_segmentation_map_image.tiff", 1540764, 10),
            ("tissue_qc_geojson_polygons.json", 160668, 10),
            ("tissue_segmentation_geojson_polygons.json", 853784, 10),
            ("readout_generation_slide_readouts.csv", 302252, 10),
            ("readout_generation_cell_readouts.csv", 1472661, 10),
            ("cell_classification_geojson_polygons.json", 9939791, 10),
            ("tissue_segmentation_segmentation_map_image.tiff", 2807584, 10),
            ("tissue_segmentation_csv_class_information.csv", 451, 10),
            ("tissue_qc_csv_class_information.csv", 284, 10),
        ]
        SPOT_0_EXPECTED_CELLS_CLASSIFIED = (35160, 10)

        SPOT_1_EXPECTED_RESULT_FILES = [
            ("tissue_qc_segmentation_map_image.tiff", 440122, 10),
            ("tissue_qc_geojson_polygons.json", 139943, 10),
            ("tissue_segmentation_geojson_polygons.json", 175419, 10),
            ("readout_generation_slide_readouts.csv", 300408, 10),
            ("readout_generation_cell_readouts.csv", 2384271, 10),
            ("cell_classification_geojson_polygons.json", 16384866, 10),
            ("tissue_segmentation_segmentation_map_image.tiff", 508552, 10),
            ("tissue_segmentation_csv_class_information.csv", 443, 10),
            ("tissue_qc_csv_class_information.csv", 284, 10),
        ]

    case "staging":
        TEST_APPLICATION_ID = "test-app"
        TEST_APPLICATION_VERSION = "0.0.6"

        HETA_APPLICATION_ID = "he-tme"
        HETA_APPLICATION_VERSION = "1.0.0"
        TEST_APPLICATION_VERSION_USE_LATEST_FALLBACK_SKIP = True

        PIPELINE_GPU_TYPE = "L4"
        PIPELINE_GPU_PROVISIONING_MODE = "SPOT"
        PIPELINE_GPU_FLEX_START_MAX_RUN_DURATION_MINUTES = None
        PIPELINE_NODE_ACQUISITION_TIMEOUT_MINUTES = 30
        PIPELINE_MAX_GPUS_PER_SLIDE = 1
        PIPELINE_CPU_PROVISIONING_MODE = "SPOT"
        PIPELINE_NODE_ACQUISITION_TIMEOUT_MINUTES = 30

        SPECIAL_APPLICATION_ID = "test-app"
        SPECIAL_APPLICATION_VERSION = "0.99.0"

        SPOT_0_EXPECTED_RESULT_FILES = [
            ("tissue_qc_segmentation_map_image.tiff", 1540764, 10),
            ("tissue_qc_geojson_polygons.json", 160668, 10),
            ("tissue_segmentation_geojson_polygons.json", 853784, 10),
            ("readout_generation_slide_readouts.csv", 302252, 10),
            ("readout_generation_cell_readouts.csv", 1472661, 10),
            ("cell_classification_geojson_polygons.json", 9939791, 10),
            ("tissue_segmentation_segmentation_map_image.tiff", 2807584, 10),
            ("tissue_segmentation_csv_class_information.csv", 451, 10),
            ("tissue_qc_csv_class_information.csv", 284, 10),
        ]
        SPOT_0_EXPECTED_CELLS_CLASSIFIED = (35160, 10)

        SPOT_1_EXPECTED_RESULT_FILES = [
            ("tissue_qc_segmentation_map_image.tiff", 440122, 10),
            ("tissue_qc_geojson_polygons.json", 139943, 10),
            ("tissue_segmentation_geojson_polygons.json", 175419, 10),
            ("readout_generation_slide_readouts.csv", 300408, 10),
            ("readout_generation_cell_readouts.csv", 2384271, 10),
            ("cell_classification_geojson_polygons.json", 16384866, 10),
            ("tissue_segmentation_segmentation_map_image.tiff", 508552, 10),
            ("tissue_segmentation_csv_class_information.csv", 443, 10),
            ("tissue_qc_csv_class_information.csv", 284, 10),
        ]

    case _:
        message = f"Unsupported AIGNOSTICS_PLATFORM_ENVIRONMENT value: {os.getenv('AIGNOSTICS_PLATFORM_ENVIRONMENT')}"
        raise ValueError(message)
