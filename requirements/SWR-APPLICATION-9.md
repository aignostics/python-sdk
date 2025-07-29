---
itemId: SWR-APPLICATION-9
itemTitle: Manage Application Run Lifecycle
itemHasParent: SHR-APPLICATION-2
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: CLI (command-line interface)
---

## Description

System shall provide comprehensive management of application run lifecycles including listing, describing, and canceling runs. The system shall:

**List Runs**:
- Display run identifiers with pagination support using --limit parameter
- Show "Application Run IDs:" for standard format and "Application Runs:" for verbose format
- Include "Item Status Counts:" in verbose output
- Display completion message "Listed '[count]' run(s)." with actual count
- Complete with exit code 0

**Describe Runs**:
- Display detailed run information in format "Run Details for [run-id]"
- Show current run status (e.g., "Status: RUNNING", "Status: CANCELED_USER")
- Return exit code 1 with "Error: Failed to retrieve run details for ID '[id]'" for invalid UUIDs
- Return exit code 2 with "Warning: Run with ID '[id]' not found." for non-existent runs

**Cancel Runs**:
- Cancel running application runs when provided with valid run identifiers
- Display confirmation message "Run with ID '[run-id]' has been canceled."
- Return exit code 1 with "Failed to cancel run with ID '[id]'" for invalid UUIDs
- Return exit code 2 with "Warning: Run with ID '[id]' not found." for non-existent runs

**Test Evidence**: `test_cli_run_submit_and_describe_and_cancel_and_download`, `test_cli_run_list_limit_10`, `test_cli_run_list_verbose_limit_1`, `test_cli_run_describe_invalid_uuid`, `test_cli_run_describe_not_found`, `test_cli_run_cancel_invalid_run_id`, `test_cli_run_cancel_not_found`