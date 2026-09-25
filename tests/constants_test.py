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
    "gs://aignostics-platform-ext-a4f7e9/python-sdk-tests/he-tme/slides/1603ba4c-398a-49db-926b-c14d8f17dc83.tiff"
)
SPOT_1_FILENAME = "1603ba4c-398a-49db-926b-c14d8f17dc83.tiff"
SPOT_1_CRC32C = "MKWV1g=="
SPOT_1_FILESIZE = 8942460
SPOT_1_RESOLUTION_MPP = 0.25
SPOT_1_WIDTH = 6649
SPOT_1_HEIGHT = 6578
SPOT_1_TISSUE = "BREAST"
SPOT_1_DISEASE = "BREAST_CANCER"

# SPOT_2, SPOT_3 (and the former SPOT_1 / 9375e3ed): these slides have a known 10x resolution
# ambiguity — certain VIPS versions read their MPP as ~0.0465 instead of ~0.465 due to differing
# interpretations of the TIFF ResolutionUnit tag. The values below reflect the correct 0.465 MPP.
# If a test fails with an off-by-10x resolution error, check the VIPS version in use.
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

SPOT_4_GS_URL = (
    "gs://aignostics-platform-ext-a4f7e9/python-sdk-tests/he-tme/slides/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
)
SPOT_4_FILENAME = "9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
SPOT_4_CRC32C = "9l3NNQ=="
SPOT_4_FILESIZE = 14681750
SPOT_4_RESOLUTION_MPP = 0.46499982
SPOT_4_WIDTH = 3728
SPOT_4_HEIGHT = 3640

# To update file sizes: the tests print every file's actual size before asserting. Run with
# -s to see them, then paste the printed byte values as the second element of each tuple.
# Both are e2e tests and skip silently without their marker:
# SPOT_0: uv run pytest tests/aignostics/application/gui_test.py::test_gui_run_download \
#           -m "e2e and long_running" -s --no-cov
# SPOT_1: uv run pytest tests/aignostics/application/cli_test.py::test_cli_run_execute \
#           -m "e2e and very_long_running" -s --no-cov
#
# These defaults reflect the production he-tme run. If staging produces different output (e.g.
# after deploying a new application version to staging before production), add an override inside
# the "staging" case below — only the constants that actually differ need to be reassigned.
# Note: defined here rather than inside each match arm to avoid SonarCloud flagging the
# nearly-identical blocks as duplicated code (the 3% duplication threshold).
SPOT_0_EXPECTED_RESULT_FILES = [
    ("tissue_qc_geojson_polygons.json", 112068, 10),
    ("tissue_qc_parquet_polygons.parquet", 32364, 10),
    ("tissue_qc_segmentation_map_image.tiff", 1670903, 10),
    ("tissue_segmentation_geojson_polygons.json", 556273, 10),
    ("tissue_segmentation_parquet_polygons.parquet", 102220, 10),
    ("tissue_segmentation_segmentation_map_image.tiff", 3031723, 10),
    ("cell_classification_geojson_polygons.json", 9841861, 10),
    ("cell_classification_parquet_polygons.parquet", 2902904, 10),
    ("whole_tumor_region_geojson_polygons.json", 69845, 10),
    ("whole_tumor_region_parquet_polygons.parquet", 22684, 10),
    ("tumor_cellularity_geojson_polygons.json", 476, 10),
    ("tumor_cellularity_parquet_polygons.parquet", 4106, 10),
    ("readout_generation_readouts_bundle.zip", 632626, 10),
]

SPOT_1_EXPECTED_RESULT_FILES = [
    ("tissue_qc_geojson_polygons.json", 25621, 10),
    ("tissue_qc_parquet_polygons.parquet", 10556, 10),
    ("tissue_qc_segmentation_map_image.tiff", 1281477, 10),
    ("tissue_segmentation_geojson_polygons.json", 73826, 10),
    ("tissue_segmentation_parquet_polygons.parquet", 23318, 10),
    ("tissue_segmentation_segmentation_map_image.tiff", 1783129, 10),
    ("cell_classification_geojson_polygons.json", 2847846, 10),
    ("cell_classification_parquet_polygons.parquet", 880714, 10),
    ("whole_tumor_region_geojson_polygons.json", 16970, 10),
    ("whole_tumor_region_parquet_polygons.parquet", 8187, 10),
    ("tumor_cellularity_geojson_polygons.json", 1518, 10),
    ("tumor_cellularity_parquet_polygons.parquet", 4377, 10),
    ("readout_generation_readouts_bundle.zip", 278167, 10),
]

match os.getenv("AIGNOSTICS_PLATFORM_ENVIRONMENT", "production"):
    case "production":
        TEST_APPLICATION_ID = "test-app"
        TEST_APPLICATION_VERSION = "1.3.0"

        HETA_APPLICATION_ID = "he-tme"
        HETA_APPLICATION_VERSION = "2.0.0"
        TEST_APPLICATION_VERSION_USE_LATEST_FALLBACK_SKIP = True

        PIPELINE_GPU_TYPE = "A100"
        PIPELINE_GPU_PROVISIONING_MODE = "SPOT"
        PIPELINE_GPU_FLEX_START_MAX_RUN_DURATION_MINUTES = None
        PIPELINE_MAX_GPUS_PER_SLIDE = 1
        PIPELINE_CPU_PROVISIONING_MODE = "SPOT"
        PIPELINE_NODE_ACQUISITION_TIMEOUT_MINUTES = 25

    case "staging":
        TEST_APPLICATION_ID = "test-app"
        TEST_APPLICATION_VERSION = "1.3.0"

        HETA_APPLICATION_ID = "he-tme"
        HETA_APPLICATION_VERSION = "2.0.0"
        TEST_APPLICATION_VERSION_USE_LATEST_FALLBACK_SKIP = True

        PIPELINE_GPU_TYPE = "A100"
        PIPELINE_GPU_PROVISIONING_MODE = "SPOT"
        PIPELINE_GPU_FLEX_START_MAX_RUN_DURATION_MINUTES = None
        PIPELINE_MAX_GPUS_PER_SLIDE = 1
        PIPELINE_CPU_PROVISIONING_MODE = "SPOT"
        PIPELINE_NODE_ACQUISITION_TIMEOUT_MINUTES = 25

        # If staging outputs differ from the defaults above, override them here, e.g.:
        # SPOT_0_EXPECTED_RESULT_FILES = [("tissue_qc_segmentation_map_image.tiff", <bytes>, 10), ...]
        # SPOT_1_EXPECTED_RESULT_FILES = [("tissue_qc_segmentation_map_image.tiff", <bytes>, 10), ...]

    case _:
        message = f"Unsupported AIGNOSTICS_PLATFORM_ENVIRONMENT value: {os.getenv('AIGNOSTICS_PLATFORM_ENVIRONMENT')}"
        raise ValueError(message)
