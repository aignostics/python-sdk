---
itemId: API-RESULT-DOWNLOAD
itemTitle: Result Download API
itemType: Software Item Spec
itemFulfills: SWR-APPLICATION-13, SWR-APPLICATION-14, SWR-APPLICATION-16
itemExtends: ADR-6-CLOUD-STORAGE-INFRASTRUCTURE
owner: engineering@aignostics.com
approvers: product@aignostics.com, architecture@aignostics.com
informed: stakeholders@aignostics.com
date: 2025-07-31
status: active
product: Platform
platform: Platform
components: 
  - Result Download Service
  - Progress Tracking API
  - File Management API
risk: low
sop: SW-SOP-01
---

# Result Download API

The Result Download API enables users to download analysis results with progress tracking and resumable downloads.

## Base URL

```
https://api.aignostics.com/v1/results
```

## Authentication

All requests require a Bearer token:

```http
Authorization: Bearer <your-access-token>
```

## Endpoints

### List Available Results

Get a list of downloadable results for the authenticated user.

```http
GET /results
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Maximum results to return (default: 20, max: 100) |
| `offset` | integer | No | Number of results to skip (default: 0) |
| `status` | string | No | Filter by status: `ready`, `processing`, `failed` |

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/results?limit=10&status=ready" \
  -H "Authorization: Bearer your-access-token"
```

**Example Response:**

```json
{
  "results": [
    {
      "result_id": "res_abc123",
      "name": "Cell Analysis - Sample 001",
      "status": "ready",
      "format": "pdf",
      "file_size_bytes": 2048576,
      "created_at": "2025-07-31T09:00:00Z",
      "expires_at": "2025-08-31T09:00:00Z"
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 10,
    "offset": 0
  }
}
```

### Download Result

Download a specific analysis result.

```http
GET /results/{result_id}/download
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `result_id` | string | Yes | Unique identifier of the result |
| `format` | string | No | File format: `original`, `pdf`, `csv` (default: `original`) |

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/results/res_abc123/download?format=pdf" \
  -H "Authorization: Bearer your-access-token" \
  -o analysis_result.pdf
```

**Example Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="analysis_result.pdf"
Content-Length: 2048576

<binary file content>
```

### Create Bulk Download

Initiate a bulk download for multiple results.

```http
POST /results/bulk-download
```

**Request Body:**

```json
{
  "result_ids": ["res_abc123", "res_def456"],
  "format": "zip",
  "include_metadata": true
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `result_ids` | array | Yes | List of result IDs to download |
| `format` | string | No | Archive format: `zip`, `tar.gz` (default: `zip`) |
| `include_metadata` | boolean | No | Include metadata files (default: `true`) |

**Example Request:**

```bash
curl -X POST "https://api.aignostics.com/v1/results/bulk-download" \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "result_ids": ["res_abc123", "res_def456"],
    "format": "zip",
    "include_metadata": true
  }'
```

**Example Response:**

```json
{
  "download_id": "dl_xyz789",
  "status": "preparing",
  "estimated_size_bytes": 5242880,
  "progress_url": "/results/bulk-download/dl_xyz789/progress"
}
```

### Check Bulk Download Progress

Monitor the progress of a bulk download operation.

```http
GET /results/bulk-download/{download_id}/progress
```

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/results/bulk-download/dl_xyz789/progress" \
  -H "Authorization: Bearer your-access-token"
```

**Example Response:**

```json
{
  "download_id": "dl_xyz789",
  "status": "completed",
  "progress_percentage": 100,
  "download_url": "/results/bulk-download/dl_xyz789/download",
  "expires_at": "2025-08-07T10:00:00Z"
}
```

### Download Bulk Archive

Download the prepared bulk archive.

```http
GET /results/bulk-download/{download_id}/download
```

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/results/bulk-download/dl_xyz789/download" \
  -H "Authorization: Bearer your-access-token" \
  -o bulk_results.zip
```

## CLI Usage

### Download Single Result

```bash
aignostics results download <result_id> [OPTIONS]
```

**Options:**

- `--output-dir` - Output directory (default: current directory)
- `--format` - File format: `original`, `pdf`, `csv`
- `--progress` - Show progress bar

**Example:**

```bash
# Download with progress
aignostics results download res_abc123 --format pdf --progress

# Download to specific directory
aignostics results download res_abc123 --output-dir ./downloads
```

### Bulk Download Results

```bash
aignostics results bulk-download [RESULT_IDS...] [OPTIONS]
```

**Options:**

- `--output-file` - Output filename for archive
- `--format` - Archive format: `zip`, `tar.gz`
- `--wait` - Wait for completion

**Example:**

```bash
# Bulk download with wait
aignostics results bulk-download res_abc123 res_def456 \
  --output-file my_results.zip \
  --wait

# Async bulk download
aignostics results bulk-download res_abc123 res_def456 \
  --format tar.gz
```

### Monitor Download Progress

```bash
aignostics results download-status <download_id>
```

**Example:**

```bash
# Check status once
aignostics results download-status dl_xyz789

# Monitor continuously
watch -n 2 "aignostics results download-status dl_xyz789"
```

## Python SDK

```python
from aignostics import AignosticsClient

# Initialize client
client = AignosticsClient(api_key="your-api-key")

# List available results
results = client.results.list(status="ready", limit=10)

# Download single result
client.results.download(
    result_id="res_abc123",
    output_path="./analysis_result.pdf",
    format="pdf"
)

# Bulk download
download = client.results.bulk_download(
    result_ids=["res_abc123", "res_def456"],
    output_path="./bulk_results.zip"
)

# Monitor progress
progress = download.get_progress()
print(f"Progress: {progress.percentage}%")
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Download successful |
| 202 | Bulk download initiated |
| 400 | Invalid request |
| 401 | Authentication required |
| 404 | Result not found |
| 429 | Rate limit exceeded |

## Error Responses

```json
{
  "error": {
    "code": "RESULT_NOT_FOUND",
    "message": "Result with ID res_abc123 not found"
  }
}
```

**Common Error Codes:**

- `RESULT_NOT_FOUND` - Requested result does not exist
- `DOWNLOAD_EXPIRED` - Download link has expired
- `RATE_LIMIT_EXCEEDED` - Too many requests

## Rate Limits

- **Download requests**: 10 per minute
- **Progress checks**: 60 per minute
- **Concurrent downloads**: 5 per user