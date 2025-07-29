---
itemId: SPEC-APPLICATION-4
itemTitle: CLI Application List Command Interface
itemType: Software Item Spec
itemFulfills: SWR-APPLICATION-1, SWR-APPLICATION-2
Layer: CLI (command-line interface)
---

## Description

This specification defines the technical interface contract for the CLI application list command syntax and output formats.

### Command Syntax

```
application list [--verbose]
```

**Parameters:**
- `--verbose` (optional): Enables detailed output with artifact counts

### Response Contract

**Exit Code:** `0` (success)

**Standard Output Format:**
- Plain text containing application identifiers
- Must include: "he-tme", "test-app" (example identifiers from test evidence)

**Verbose Output Format:**
- All standard output content plus:
- Artifact count line with exact format: `"Artifacts: X input(s), Y output(s)"`
- Where X and Y are integers (e.g., "Artifacts: 1 input(s), 6 output(s)")

### Data Format Contract

**Application Identifier Requirements:**
- Format: String identifiers for available applications
- Examples from test evidence: "he-tme", "test-app"
- Output: One or more identifiers present in response text

**Artifact Count Format:**
- Exact template: `"Artifacts: {input_count} input(s), {output_count} output(s)"`
- Values: Non-negative integers
- Placement: Additional line in verbose mode only

**Test Evidence:** Command syntax and output formats extracted from `test_cli_application_list` (basic execution with application IDs) and `test_cli_application_list_verbose` (verbose flag and artifact count format).