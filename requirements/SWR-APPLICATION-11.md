---
itemId: SWR-APPLICATION-11
itemTitle: Provide Run Management Interface
itemHasParent: SHR-APPLICATION-2
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: GUI (web interface)
---

## Description

System shall provide a web interface for managing application runs including viewing, canceling, and monitoring run status. The interface shall:

**Run Display and Navigation**:
- Display submitted runs in the sidebar with application version information
- Allow navigation to specific run detail pages using run identifiers
- Show run information including application version and current status
- Update run status dynamically (e.g., from "RUNNING" to "CANCELED_USER")

**Run Cancellation**:
- Provide "Cancel" button functionality for running application runs
- Display confirmation notifications: "Canceling application run with id '[run-id]' ..." 
- Show success notification: "Application run cancelled!"
- Update the interface to reflect the new run status after cancellation

**Application Workflow Integration**:
- Support complete workflows from data selection through run submission
- Integrate with dataset download functionality for seamless data preparation
- Provide upload and submission capabilities through the web interface
- Display progress notifications throughout the workflow process

The interface shall maintain responsive behavior and provide clear user feedback for all run management operations.

**Test Evidence**: `test_gui_cli_to_run_cancel`, `test_gui_download_dataset_via_application_to_run_cancel` demonstrate complete web interface workflows for run management and cancellation.