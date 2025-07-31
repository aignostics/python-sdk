---
itemId: API-DATASET-STORAGE
itemTitle: Dataset Storage Integration API
itemType: Software Item Spec
itemFulfills: SWR-DATASET-5, SWR-DATASET-6
itemExtends: ADR-12-DATASET-DOWNLOAD-SERVICE-ARCHITECTURE
owner: engineering@aignostics.com
approvers: product@aignostics.com, architecture@aignostics.com
informed: stakeholders@aignostics.com
date: 2025-07-31
status: active
product: Platform
platform: Platform
components: 
  - Dataset Storage Service
  - File Upload API
  - Storage Integration API
risk: low
sop: SW-SOP-01
---

# Dataset Storage Integration API

The Dataset Storage Integration API provides upload, storage management, and integration capabilities for datasets across multiple storage backends.

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

### Get Upload URL

Generate a secure upload URL for dataset files.

```http
POST /datasets/{dataset_id}/upload-url
```

**Request Body:**

```json
{
  "filename": "analysis_results.csv",
  "file_size_bytes": 52428800,
  "content_type": "text/csv",
  "chunk_upload": true
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `filename` | string | Yes | Name of the file to upload |
| `file_size_bytes` | integer | Yes | Size of the file in bytes |
| `content_type` | string | No | MIME type of the file |
| `chunk_upload` | boolean | No | Enable chunked upload (default: false) |

**Example Request:**

```bash
curl -X POST "https://api.aignostics.com/v1/datasets/ds_abc123/upload-url" \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "analysis_results.csv",
    "file_size_bytes": 52428800,
    "content_type": "text/csv"
  }'
```

**Example Response:**

```json
{
  "upload_id": "upl_xyz789",
  "upload_url": "https://upload.aignostics.com/datasets/ds_abc123/upl_xyz789",
  "method": "PUT",
  "headers": {
    "Content-Type": "text/csv",
    "Content-Length": "52428800"
  },
  "expires_at": "2025-07-31T11:00:00Z"
}
```

### Upload Dataset File

Upload dataset file content to the storage system.

```http
PUT {upload_url}
```

**Headers:**

```http
Content-Type: text/csv
Content-Length: 52428800
```

**Example Request:**

```bash
curl -X PUT "https://upload.aignostics.com/datasets/ds_abc123/upl_xyz789" \
  -H "Content-Type: text/csv" \
  -H "Content-Length: 52428800" \
  --data-binary @analysis_results.csv
```

**Example Response:**

```http
HTTP/1.1 200 OK
ETag: "abc123def456"
X-Upload-Id: upl_xyz789
```

### Confirm Upload

Confirm successful upload and trigger dataset processing.

```http
POST /datasets/{dataset_id}/confirm-upload
```

**Request Body:**

```json
{
  "upload_id": "upl_xyz789",
  "etag": "abc123def456",
  "file_size_bytes": 52428800
}
```

**Example Request:**

```bash
curl -X POST "https://api.aignostics.com/v1/datasets/ds_abc123/confirm-upload" \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "upload_id": "upl_xyz789",
    "etag": "abc123def456"
  }'
```

**Example Response:**

```json
{
  "dataset_id": "ds_abc123",
  "status": "processing",
  "processing_id": "proc_def456",
  "estimated_completion": "2025-07-31T11:30:00Z"
}
```

### Get Upload Progress

Monitor the progress of file upload and processing.

```http
GET /datasets/{dataset_id}/upload/{upload_id}/progress
```

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/datasets/ds_abc123/upload/upl_xyz789/progress" \
  -H "Authorization: Bearer your-access-token"
```

**Example Response:**

```json
{
  "upload_id": "upl_xyz789",
  "dataset_id": "ds_abc123",
  "status": "completed",
  "upload_progress": 100,
  "processing_progress": 75,
  "bytes_uploaded": 52428800,
  "total_bytes": 52428800,
  "records_processed": 7500,
  "total_records": 10000,
  "estimated_completion": "2025-07-31T11:15:00Z"
}
```

### Initiate Chunked Upload

Start a chunked upload session for large files.

```http
POST /datasets/{dataset_id}/chunked-upload
```

**Request Body:**

```json
{
  "filename": "large_dataset.csv",
  "total_size_bytes": 1073741824,
  "chunk_size_bytes": 10485760,
  "content_type": "text/csv"
}
```

**Example Request:**

```bash
curl -X POST "https://api.aignostics.com/v1/datasets/ds_abc123/chunked-upload" \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "large_dataset.csv",
    "total_size_bytes": 1073741824,
    "chunk_size_bytes": 10485760
  }'
```

**Example Response:**

```json
{
  "upload_id": "upl_large123",
  "total_chunks": 102,
  "chunk_size_bytes": 10485760,
  "upload_urls": [
    {
      "chunk_number": 1,
      "upload_url": "https://upload.aignostics.com/chunks/upl_large123/1",
      "expires_at": "2025-07-31T12:00:00Z"
    }
  ]
}
```

### Upload Chunk

Upload a single chunk of a large file.

```http
PUT {chunk_upload_url}
```

**Headers:**

```http
Content-Type: application/octet-stream
Content-Length: 10485760
X-Chunk-Number: 1
```

**Example Request:**

```bash
curl -X PUT "https://upload.aignostics.com/chunks/upl_large123/1" \
  -H "Content-Type: application/octet-stream" \
  -H "Content-Length: 10485760" \
  -H "X-Chunk-Number: 1" \
  --data-binary @chunk_001.bin
```

### Complete Chunked Upload

Finalize a chunked upload and assemble the complete file.

```http
POST /datasets/{dataset_id}/chunked-upload/{upload_id}/complete
```

**Request Body:**

```json
{
  "chunks": [
    {"chunk_number": 1, "etag": "abc123"},
    {"chunk_number": 2, "etag": "def456"}
  ]
}
```

**Example Request:**

```bash
curl -X POST "https://api.aignostics.com/v1/datasets/ds_abc123/chunked-upload/upl_large123/complete" \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "chunks": [
      {"chunk_number": 1, "etag": "abc123"},
      {"chunk_number": 2, "etag": "def456"}
    ]
  }'
```

### Get Storage Info

Get storage information and statistics for a dataset.

```http
GET /datasets/{dataset_id}/storage
```

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/datasets/ds_abc123/storage" \
  -H "Authorization: Bearer your-access-token"
```

**Example Response:**

```json
{
  "dataset_id": "ds_abc123",
  "storage_backend": "s3",
  "storage_location": "s3://aignostics-datasets/ds_abc123/",
  "file_size_bytes": 52428800,
  "compressed_size_bytes": 15728640,
  "compression_ratio": 0.3,
  "storage_class": "standard",
  "replicated": true,
  "backup_status": "completed",
  "last_accessed": "2025-07-31T10:30:00Z"
}
```

## CLI Usage

### Upload Dataset

```bash
aignostics datasets upload <dataset_id> <file_path> [OPTIONS]
```

**Options:**

- `--chunk-size` - Chunk size for large files (bytes)
- `--parallel` - Number of parallel uploads
- `--progress` - Show progress bar
- `--verify` - Verify upload integrity

**Example:**

```bash
# Upload with progress
aignostics datasets upload ds_abc123 analysis_results.csv --progress

# Chunked upload for large files
aignostics datasets upload ds_abc123 large_dataset.csv \
  --chunk-size 10485760 \
  --parallel 4 \
  --progress
```

### Check Upload Status

```bash
aignostics datasets upload-status <dataset_id> <upload_id>
```

**Example:**

```bash
# Check upload progress
aignostics datasets upload-status ds_abc123 upl_xyz789
```

### Get Storage Info

```bash
aignostics datasets storage-info <dataset_id>
```

**Example:**

```bash
# Get storage details
aignostics datasets storage-info ds_abc123
```

## Python SDK

```python
from aignostics import AignosticsClient

# Initialize client
client = AignosticsClient(api_key="your-api-key")

# Simple upload
upload_result = client.datasets.upload(
    dataset_id="ds_abc123",
    file_path="analysis_results.csv",
    show_progress=True
)

# Chunked upload for large files
upload_result = client.datasets.upload_chunked(
    dataset_id="ds_abc123",
    file_path="large_dataset.csv",
    chunk_size=10485760,
    parallel_uploads=4
)

# Monitor upload progress
progress = client.datasets.get_upload_progress(
    dataset_id="ds_abc123",
    upload_id="upl_xyz789"
)

# Get storage information
storage_info = client.datasets.get_storage_info("ds_abc123")
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Request successful |
| 201 | Upload initiated |
| 202 | Upload accepted |
| 400 | Invalid request |
| 401 | Authentication required |
| 404 | Dataset not found |
| 413 | File too large |
| 507 | Insufficient storage |

## Error Responses

```json
{
  "error": {
    "code": "UPLOAD_FAILED",
    "message": "File upload failed",
    "details": {
      "upload_id": "upl_xyz789",
      "reason": "Network timeout during upload"
    }
  }
}
```

**Common Error Codes:**

- `UPLOAD_FAILED` - File upload failed
- `FILE_TOO_LARGE` - File exceeds size limits
- `INVALID_FILE_TYPE` - File type not supported
- `STORAGE_QUOTA_EXCEEDED` - Storage quota exceeded

## Rate Limits

- **Upload URL generation**: 30 per minute
- **Concurrent uploads**: 5 per user
- **Chunked uploads**: 100 chunks per minute
- **Storage queries**: 60 per minute