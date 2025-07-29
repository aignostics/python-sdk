---
itemId: SWR-APPLICATION-6
itemTitle: Prepare Application Run Metadata
itemHasParent: SHR-APPLICATION-2
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: CLI (command-line interface)
---

## Description

System shall generate metadata CSV files for application runs by scanning source directories for whole slide images. When users execute the prepare command with a valid application identifier, metadata CSV path, and source directory, the system shall:

- Scan the specified source directory for compatible whole slide image files
- Extract file metadata including checksum, resolution, dimensions, and file path
- Generate a CSV file with headers: "reference;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;platform_bucket_url"
- Populate the CSV with extracted metadata, leaving user-editable fields (staining_method, tissue, disease) empty for manual completion
- Complete the operation successfully with exit code 0

The system shall validate that the source directory exists and contains compatible image files before generating the metadata CSV.

**Test Evidence**: `test_cli_application_run_prepare_upload_submit_fail_on_mpp` demonstrates metadata CSV generation with extracted file properties.