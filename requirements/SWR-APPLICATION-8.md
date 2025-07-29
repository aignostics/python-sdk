---
itemId: SWR-APPLICATION-8
itemTitle: Submit Application Runs for Processing
itemHasParent: SHR-APPLICATION-2
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: CLI (command-line interface)
---

## Description

System shall submit application runs for processing using uploaded whole slide images and metadata. When users execute the submit command with a valid application identifier and metadata CSV file, the system shall:

- Validate the application version identifier format and existence
- Validate metadata CSV content against application requirements
- Validate platform bucket URLs format (must use 'gs://' protocol)
- Ensure all required URL parameters are provided (not empty)
- Submit the run to the platform for processing
- Return a run identifier in the format "Submitted run with id '[run-id]' for '[application-version]'"
- Complete the operation with exit code 0

The system shall return appropriate error codes and messages for validation failures:
- Exit code 1 with "Error: Failed to create run for application version" for invalid application versions
- Exit code 2 with "Invalid platform bucket URL: '[url]'" for unsupported cloud providers or missing URLs
- Exit code 2 with "Invalid metadata for artifact" when metadata validation fails

**Test Evidence**: `test_cli_run_submit_and_describe_and_cancel_and_download`, `test_cli_run_submit_fails_on_application_not_found`, `test_cli_run_submit_fails_on_unsupported_cloud`, `test_cli_run_submit_fails_on_missing_url`, `test_cli_application_run_prepare_upload_submit_fail_on_mpp`