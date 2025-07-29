---
itemId: SWR-APPLICATION-7
itemTitle: Upload Whole Slide Images to Platform
itemHasParent: SHR-APPLICATION-2
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: CLI (command-line interface)
---

## Description

System shall upload whole slide images to the platform for processing by AI applications. When users execute the upload command with a valid application identifier and metadata CSV file, the system shall:

- Read the metadata CSV file and validate its format and content
- Verify that all referenced source files exist at their specified paths
- Upload each whole slide image file to the platform storage
- Display "Upload completed." message upon successful completion
- Complete the operation with exit code 0

The system shall validate file existence before attempting upload and return exit code 2 with a warning message in the format "Warning: Source file '[filename]' (row [index]) does not exist" when referenced files are missing.

**Test Evidence**: `test_cli_application_run_prepare_upload_submit_fail_on_mpp` demonstrates successful upload completion message, and `test_cli_application_run_upload_fails_on_missing_source` demonstrates missing file validation.