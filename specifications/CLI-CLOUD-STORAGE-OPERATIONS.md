---
itemId: CLI-CLOUD-STORAGE-OPERATIONS
itemTitle: Cloud Storage CLI Operations  
itemType: Software Item Spec
itemFulfills: SWR-BUCKET-4, SWR-BUCKET-6
itemExtends: ADR-10-CLOUD-STORAGE-SERVICE-ARCHITECTURE
---

# Cloud Storage CLI Operations API

CLI operations for cloud storage object management including delete operations and bulk management capabilities.

## Delete Operations

### Delete Objects by Pattern
```bash
aignostics storage delete <pattern> [OPTIONS]
```

**Options:**
- `--confirm` - Skip confirmation prompt
- `--dry-run` - Show what would be deleted without actually deleting

**Example:**
```bash
# Delete with confirmation
aignostics storage delete "logs/*.txt" --confirm

# Output: "Deleted 5 object(s) matching ['logs/*.txt']"
```

## Bulk Operations

### Purge Bucket with Dry-Run
```bash
aignostics storage purge <bucket> [OPTIONS]
```

**Options:**
- `--dry-run` - Analyze without deleting
- `--force` - Skip all confirmations

**Example:**
```bash
# Dry-run analysis
aignostics storage purge my-bucket --dry-run

# Output: "Would purge bucket by deleting 150 object(s)"
```