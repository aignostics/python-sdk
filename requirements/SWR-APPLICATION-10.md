---
itemId: SWR-APPLICATION-10
itemTitle: Execute Complete Application Workflows
itemHasParent: SHR-APPLICATION-2
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: CLI (command-line interface)
---

## Description

System shall execute complete end-to-end application workflows that integrate preparation, upload, submission, and result retrieval. When users execute the complete workflow, the system shall:

- Accept pattern-based metadata specification in format: ".*\\.tiff:staining_method=H&E,tissue=LUNG,disease=LUNG_CANCER"
- Generate metadata CSV files automatically based on file patterns and user-specified metadata
- Upload whole slide images to the platform storage
- Submit runs for processing and wait for completion
- Download results to specified output directories
- Create organized output directory structure with run-specific subdirectories
- Generate expected output files including:
  - tissue_segmentation_csv_class_information.csv
  - cell_classification_geojson_polygons.json
  - readout_generation_cell_readouts.csv
  - tissue_qc_csv_class_information.csv
  - tissue_segmentation_geojson_polygons.json
  - tissue_qc_geojson_polygons.json
  - tissue_qc_segmentation_map_image.tiff
  - readout_generation_slide_readouts.csv
  - tissue_segmentation_segmentation_map_image.tiff
- Complete the entire workflow with exit code 0

The system shall validate file sizes and content to ensure processing was successful, with output files meeting expected size tolerances (±10% of expected values).

**Test Evidence**: `test_cli_run_execute` demonstrates complete workflow execution with file pattern matching, automatic processing, and result validation.