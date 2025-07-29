---
itemId: SPEC-APPLICATION-5
itemTitle: CLI Application Describe Command Interface
itemType: Software Item Spec
itemFulfills: SWR-APPLICATION-3, SWR-APPLICATION-4
Layer: CLI (command-line interface)
---

## Description

This specification defines the technical interface contract for the CLI application describe command syntax, parameter validation, and response formats.

### Command Syntax

```
application describe [APPLICATION_ID]
```

**Parameters:**
- `APPLICATION_ID` (required): String identifier for target application

### Response Contract

**Success Response:**
- Exit code: `0`
- Output: Application details including artifact identifiers
- Content requirement: Must include artifact identifiers in format `"artifact_name:artifact_type"`
- Example from test evidence: `"tissue_qc:geojson_polygons"`

**Error Response:**
- Exit code: `2`
- Output format: `"Application with ID '[APPLICATION_ID]' not found."`
- Format rules: Single quotes around ID, period at end
- Example: `"Application with ID 'unknown' not found."`

### Data Format Contract

**Application Detail Content:**
- Must include artifact specifications
- Artifact identifier format: `"{name}:{type}"`
- Example artifact identifiers: `"tissue_qc:geojson_polygons"`

**Error Message Template:**
- Template: `"Application with ID '[{provided_id}]' not found."`
- Substitution: Replace `{provided_id}` with actual user input
- Formatting: Maintain single quotes and trailing period

### Validation Contract

**Valid Application IDs:** "he-tme", "test-app" (examples from test evidence)
**Invalid Application IDs:** Any string not matching available applications
**Parameter Requirements:** Exactly one APPLICATION_ID parameter required

**Test Evidence:** Command syntax and response formats extracted from `test_cli_application_describe` (successful execution with artifact identifier content) and `test_cli_application_describe_not_found` (error handling with exact exit code and message format).