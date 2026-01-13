---
name: troubleshoot-run
description: Troubleshoot failed or problematic Aignostics Platform runs. Use when user asks about run errors, failures, or why items didn't process successfully.
---

# Troubleshooting Aignostics Runs

This skill guides you through diagnosing and understanding run failures.

## Quick Diagnosis

### 1. Get Run Overview

```
→ run_summary(run_id)
```

This shows:
- Run state (PENDING, PROCESSING, TERMINATED)
- Termination reason (ALL_ITEMS_PROCESSED, CANCELED_BY_USER, CANCELED_BY_SYSTEM)
- Statistics (succeeded/failed/skipped counts)
- Per-item status with error previews

### 2. Check Item Details

```
→ get_run_items(run_id)
```

Shows each item with:
- State and output status
- Error messages (truncated)

## Common Issues

### User Errors (USER_ERROR)

These are problems with the input data that the user can fix:

| Error Pattern | Likely Cause | Solution |
|---------------|--------------|----------|
| "cannot be processed" | Invalid file format | Check file is valid DICOM/SVS |
| "unsupported format" | Wrong image type | Verify supported formats |
| "resolution too low" | Image quality | Use higher resolution scan |
| "corrupt file" | File damaged | Re-upload the file |

### System Errors (SYSTEM_ERROR)

These are platform-side issues:

| Error Pattern | Likely Cause | Action |
|---------------|--------------|--------|
| "timeout" | Processing took too long | Contact support |
| "internal error" | Platform issue | Retry or contact support |
| "resource exhausted" | Memory/compute limits | May need smaller batch |

### Skipped Items (SKIPPED)

Items marked as skipped were intentionally not processed:
- Duplicate detection
- Previous successful processing
- User-configured skip rules

## Workflow for Failed Runs

1. **Check overall statistics**
   ```
   → get_run_status(run_id)
   ```
   Look at the item counts - are ALL items failing or just some?

2. **Identify the pattern**
   ```
   → get_run_items(run_id)
   ```
   - All items same error? → Likely configuration or application issue
   - Some items succeed, some fail? → Likely input data quality varies
   - Random failures? → Possible transient system issue

3. **For USER_ERROR items**
   - Review the input files
   - Check file formats and quality
   - Verify files meet application requirements

4. **For SYSTEM_ERROR items**
   - Note the error message
   - Check if it's a known issue
   - Consider retrying the run
   - Contact support if persistent

## Retrying Failed Items

Currently, you need to:
1. Create a new run with only the failed items
2. Or contact support for a partial retry

## Getting Help

If you can't resolve the issue:
1. Note the run_id and error messages
2. Check the item external_ids to identify problematic files
3. Contact Aignostics support with this information
