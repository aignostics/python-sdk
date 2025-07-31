---
itemId: SWR-APPLICATION-18
itemTitle: Validate Download Request Parameters
itemHasParent: SHR-APPLICATION-3
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: CLI (command-line interface)
---

System shall validate run identifiers for download requests and return appropriate error responses. When users provide invalid run ID formats, the system shall respond with exit code 2 and display an error message indicating the run ID is invalid. When users request downloads for non-existent runs, the system shall respond with exit code 2 and display a message indicating the run was not found.