---
itemId: API-DATASET-MANAGEMENT
itemTitle: Dataset Management API
itemType: Software Item Spec
itemFulfills: SWR-DATASET-2
itemExtends: ADR-12-DATASET-DOWNLOAD-SERVICE-ARCHITECTURE
owner: engineering@aignostics.com
approvers: product@aignostics.com, architecture@aignostics.com
informed: stakeholders@aignostics.com
date: 2025-07-31
status: active
product: Platform
platform: Platform
components: 
  - Dataset Management Service
  - Metadata Management API
  - Validation Service
risk: low
sop: SW-SOP-01
---

# Dataset Management API

The Dataset Management API enables users to create, manage, and organize datasets with comprehensive metadata handling and validation capabilities.

## Base URL

```
https://api.aignostics.com/v1/datasets
```

## Authentication

All requests require a Bearer token:

```http
Authorization: Bearer <your-access-token>
```

## Endpoints

### Create Dataset

Create a new dataset with metadata and validation.

```http
POST /datasets
```

**Request Body:**

```json
{
  "name": "Cell Analysis Results",
  "description": "Morphological analysis results from tissue samples",
  "format": "csv",
  "tags": ["analysis", "morphology", "cells"],
  "metadata": {
    "analysis_type": "morphological",
    "software_version": "1.2.3",
    "parameters": {
      "threshold": 0.5,
      "min_area": 100
    }
  },
  "schema": {
    "columns": [
      {"name": "cell_id", "type": "string", "required": true},
      {"name": "area", "type": "float", "required": true},
      {"name": "perimeter", "type": "float", "required": false}
    ]
  }
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Dataset display name |
| `description` | string | No | Dataset description |
| `format` | string | Yes | Data format: `csv`, `json`, `parquet`, `hdf5` |
| `tags` | array | No | Tags for categorization |
| `metadata` | object | No | Custom metadata |
| `schema` | object | No | Data schema definition |

**Example Request:**

```bash
curl -X POST "https://api.aignostics.com/v1/datasets" \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cell Analysis Results",
    "format": "csv",
    "tags": ["analysis", "morphology"]
  }'
```

**Example Response:**

```json
{
  "dataset_id": "ds_abc123",
  "name": "Cell Analysis Results",
  "description": "Morphological analysis results from tissue samples",
  "status": "created",
  "format": "csv",
  "upload_url": "https://upload.aignostics.com/datasets/ds_abc123",
  "created_at": "2025-07-31T10:00:00Z"
}
```

### Update Dataset

Update dataset metadata and properties.

```http
PUT /datasets/{dataset_id}
```

**Request Body:**

```json
{
  "name": "Updated Cell Analysis Results",
  "description": "Updated description with additional context",
  "tags": ["analysis", "morphology", "updated"],
  "metadata": {
    "analysis_type": "morphological",
    "updated_parameters": {
      "threshold": 0.6
    }
  }
}
```

**Example Request:**

```bash
curl -X PUT "https://api.aignostics.com/v1/datasets/ds_abc123" \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Cell Analysis Results",
    "tags": ["analysis", "morphology", "updated"]
  }'
```

**Example Response:**

```json
{
  "dataset_id": "ds_abc123",
  "name": "Updated Cell Analysis Results",
  "description": "Updated description with additional context",
  "status": "ready",
  "format": "csv",
  "updated_at": "2025-07-31T11:00:00Z"
}
```

### Get Dataset

Retrieve detailed information about a specific dataset.

```http
GET /datasets/{dataset_id}
```

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/datasets/ds_abc123" \
  -H "Authorization: Bearer your-access-token"
```

**Example Response:**

```json
{
  "dataset_id": "ds_abc123",
  "name": "Cell Analysis Results",
  "description": "Morphological analysis results from tissue samples",
  "status": "ready",
  "format": "csv",
  "file_size_bytes": 52428800,
  "record_count": 10000,
  "tags": ["analysis", "morphology"],
  "metadata": {
    "analysis_type": "morphological",
    "software_version": "1.2.3"
  },
  "schema": {
    "columns": [
      {"name": "cell_id", "type": "string", "required": true},
      {"name": "area", "type": "float", "required": true}
    ]
  },
  "created_at": "2025-07-31T10:00:00Z",
  "updated_at": "2025-07-31T11:00:00Z"
}
```

### List Datasets

Get a paginated list of datasets with filtering options.

```http
GET /datasets
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Maximum datasets to return (default: 20, max: 100) |
| `offset` | integer | No | Number of datasets to skip (default: 0) |
| `status` | string | No | Filter by status |
| `format` | string | No | Filter by format |
| `tags` | string | No | Filter by tags (comma-separated) |
| `search` | string | No | Search in name and description |

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/datasets?tags=analysis,morphology&limit=10" \
  -H "Authorization: Bearer your-access-token"
```

### Delete Dataset

Delete a dataset and all associated data.

```http
DELETE /datasets/{dataset_id}
```

**Example Request:**

```bash
curl -X DELETE "https://api.aignostics.com/v1/datasets/ds_abc123" \
  -H "Authorization: Bearer your-access-token"
```

**Example Response:**

```json
{
  "message": "Dataset ds_abc123 has been scheduled for deletion",
  "deletion_id": "del_xyz789",
  "estimated_completion": "2025-07-31T12:00:00Z"
}
```

### Validate Dataset

Validate dataset content against schema and data quality rules.

```http
POST /datasets/{dataset_id}/validate
```

**Request Body:**

```json
{
  "validation_rules": [
    "schema_compliance",
    "data_quality",
    "completeness"
  ],
  "sample_size": 1000
}
```

**Example Request:**

```bash
curl -X POST "https://api.aignostics.com/v1/datasets/ds_abc123/validate" \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "validation_rules": ["schema_compliance", "data_quality"]
  }'
```

**Example Response:**

```json
{
  "validation_id": "val_def456",
  "status": "completed",
  "results": {
    "schema_compliance": {
      "passed": true,
      "issues": []
    },
    "data_quality": {
      "passed": false,
      "issues": [
        {
          "type": "missing_values",
          "column": "area",
          "count": 5,
          "percentage": 0.05
        }
      ]
    }
  },
  "overall_score": 0.85
}
```

## CLI Usage

### Create Dataset

```bash
aignostics datasets create <name> [OPTIONS]
```

**Options:**

- `--format` - Data format: `csv`, `json`, `parquet`, `hdf5`
- `--description` - Dataset description
- `--tags` - Comma-separated tags
- `--metadata` - JSON metadata file path

**Example:**

```bash
# Create dataset with metadata
aignostics datasets create "Cell Analysis Results" \
  --format csv \
  --description "Morphological analysis results" \
  --tags "analysis,morphology" \
  --metadata metadata.json
```

### Update Dataset

```bash
aignostics datasets update <dataset_id> [OPTIONS]
```

**Options:**

- `--name` - New dataset name
- `--description` - New description
- `--tags` - New tags (replaces existing)
- `--add-tags` - Add tags to existing

**Example:**

```bash
# Update dataset metadata
aignostics datasets update ds_abc123 \
  --name "Updated Analysis Results" \
  --add-tags "validated"
```

### List Datasets

```bash
aignostics datasets list [OPTIONS]
```

**Options:**

- `--status` - Filter by status
- `--format` - Filter by format
- `--tags` - Filter by tags
- `--search` - Search query

**Example:**

```bash
# List datasets with filters
aignostics datasets list \
  --tags analysis \
  --format csv \
  --limit 20
```

### Validate Dataset

```bash
aignostics datasets validate <dataset_id> [OPTIONS]
```

**Options:**

- `--rules` - Validation rules to apply
- `--sample-size` - Sample size for validation

**Example:**

```bash
# Validate dataset
aignostics datasets validate ds_abc123 \
  --rules schema_compliance,data_quality \
  --sample-size 1000
```

## Python SDK

```python
from aignostics import AignosticsClient

# Initialize client
client = AignosticsClient(api_key="your-api-key")

# Create dataset
dataset = client.datasets.create(
    name="Cell Analysis Results",
    format="csv",
    tags=["analysis", "morphology"],
    metadata={"analysis_type": "morphological"}
)

# Update dataset
client.datasets.update(
    dataset_id="ds_abc123",
    name="Updated Analysis Results",
    tags=["analysis", "morphology", "validated"]
)

# Get dataset
dataset = client.datasets.get("ds_abc123")

# List datasets
datasets = client.datasets.list(
    tags=["analysis"],
    format="csv",
    limit=20
)

# Validate dataset
validation = client.datasets.validate(
    dataset_id="ds_abc123",
    rules=["schema_compliance", "data_quality"]
)

# Delete dataset
client.datasets.delete("ds_abc123")
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Request successful |
| 201 | Dataset created |
| 400 | Invalid request |
| 401 | Authentication required |
| 404 | Dataset not found |
| 409 | Dataset already exists |
| 422 | Validation failed |

## Error Responses

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Dataset validation failed",
    "details": {
      "field": "format",
      "issue": "Unsupported format 'xml'"
    }
  }
}
```

**Common Error Codes:**

- `DATASET_NOT_FOUND` - Dataset does not exist
- `VALIDATION_FAILED` - Request validation failed
- `SCHEMA_MISMATCH` - Data doesn't match schema
- `DUPLICATE_NAME` - Dataset name already exists

## Rate Limits

- **Dataset operations**: 60 per minute
- **Validation requests**: 10 per minute
- **Bulk operations**: 5 per minute