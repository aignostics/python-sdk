---
itemId: API-DATASET-DOWNLOAD
itemTitle: Dataset Download API
itemType: Software Item Spec
itemFulfills: SWR-BUCKET-5
itemExtends: ADR-10-CLOUD-STORAGE-SERVICE-ARCHITECTURE
owner: engineering@aignostics.com
approvers: product@aignostics.com, architecture@aignostics.com
informed: stakeholders@aignostics.com
date: 2025-07-31
status: active
product: Platform
platform: Platform
components: 
  - Dataset Download Service
  - Progress Tracking API
  - File Management API
risk: low
sop: SW-SOP-01
---

# Dataset Download API

The Dataset Download API enables users to download datasets with progress tracking, resumable downloads, and format conversion capabilities.

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

### List Available Datasets

Get a list of downloadable datasets for the authenticated user.

```http
GET /datasets
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Maximum datasets to return (default: 20, max: 100) |
| `offset` | integer | No | Number of datasets to skip (default: 0) |
| `status` | string | No | Filter by status: `ready`, `processing`, `failed` |
| `format` | string | No | Filter by format: `csv`, `json`, `parquet`, `hdf5` |

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/datasets?limit=10&status=ready" \
  -H "Authorization: Bearer your-access-token"
```

**Example Response:**

```json
{
  "datasets": [
    {
      "dataset_id": "ds_abc123",
      "name": "Cell Population Analysis Dataset",
      "status": "ready",
      "format": "csv",
      "file_size_bytes": 52428800,
      "record_count": 10000,
      "created_at": "2025-07-31T09:00:00Z",
      "expires_at": "2025-12-31T09:00:00Z"
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 10,
    "offset": 0
  }
}
```

### Get Dataset Details

Get detailed information about a specific dataset.

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
  "name": "Cell Population Analysis Dataset",
  "description": "Comprehensive cell analysis results with morphological features",
  "status": "ready",
  "format": "csv",
  "file_size_bytes": 52428800,
  "record_count": 10000,
  "columns": [
    {"name": "cell_id", "type": "string", "description": "Unique cell identifier"},
    {"name": "area", "type": "float", "description": "Cell area in pixels"},
    {"name": "perimeter", "type": "float", "description": "Cell perimeter in pixels"}
  ],
  "metadata": {
    "analysis_type": "morphological",
    "image_count": 50,
    "software_version": "1.2.3"
  },
  "created_at": "2025-07-31T09:00:00Z",
  "expires_at": "2025-12-31T09:00:00Z"
}
```

### Download Dataset

Download a specific dataset with optional format conversion.

```http
GET /datasets/{dataset_id}/download
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dataset_id` | string | Yes | Unique identifier of the dataset |
| `format` | string | No | Output format: `csv`, `json`, `parquet`, `hdf5` (default: original) |
| `compression` | string | No | Compression: `none`, `gzip`, `bzip2` (default: `none`) |

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/datasets/ds_abc123/download?format=parquet&compression=gzip" \
  -H "Authorization: Bearer your-access-token" \
  -o dataset.parquet.gz
```

**Example Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="dataset.parquet.gz"
Content-Length: 52428800
X-Dataset-Format: parquet
X-Dataset-Compression: gzip

<binary file content>
```

### Create Streaming Download

Initiate a streaming download for large datasets with progress tracking.

```http
POST /datasets/{dataset_id}/stream
```

**Request Body:**

```json
{
  "format": "csv",
  "compression": "gzip",
  "chunk_size": 1000,
  "include_metadata": true
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `format` | string | No | Output format (default: original) |
| `compression` | string | No | Compression type (default: `none`) |
| `chunk_size` | integer | No | Records per chunk (default: 1000) |
| `include_metadata` | boolean | No | Include metadata file (default: `true`) |

**Example Request:**

```bash
curl -X POST "https://api.aignostics.com/v1/datasets/ds_abc123/stream" \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "csv",
    "compression": "gzip",
    "chunk_size": 1000
  }'
```

**Example Response:**

```json
{
  "stream_id": "str_xyz789",
  "status": "preparing",
  "total_chunks": 10,
  "chunk_size": 1000,
  "progress_url": "/datasets/ds_abc123/stream/str_xyz789/progress",
  "download_url": "/datasets/ds_abc123/stream/str_xyz789/download"
}
```

### Monitor Streaming Progress

Check the progress of a streaming download operation.

```http
GET /datasets/{dataset_id}/stream/{stream_id}/progress
```

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/datasets/ds_abc123/stream/str_xyz789/progress" \
  -H "Authorization: Bearer your-access-token"
```

**Example Response:**

```json
{
  "stream_id": "str_xyz789",
  "status": "ready",
  "progress_percentage": 100,
  "chunks_processed": 10,
  "total_chunks": 10,
  "download_url": "/datasets/ds_abc123/stream/str_xyz789/download",
  "expires_at": "2025-08-07T10:00:00Z"
}
```

### Download Stream Chunks

Download the prepared streaming dataset.

```http
GET /datasets/{dataset_id}/stream/{stream_id}/download
```

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/datasets/ds_abc123/stream/str_xyz789/download" \
  -H "Authorization: Bearer your-access-token" \
  -o streamed_dataset.csv.gz
```

## CLI Usage

### List Datasets

```bash
aignostics datasets list [OPTIONS]
```

**Options:**

- `--status` - Filter by status: `ready`, `processing`, `failed`
- `--format` - Filter by format: `csv`, `json`, `parquet`, `hdf5`
- `--limit` - Maximum datasets to return

**Example:**

```bash
# List ready datasets
aignostics datasets list --status ready --limit 20

# List CSV datasets
aignostics datasets list --format csv
```

### Download Dataset

```bash
aignostics datasets download <dataset_id> [OPTIONS]
```

**Options:**

- `--output-dir` - Output directory (default: current directory)
- `--format` - Output format: `csv`, `json`, `parquet`, `hdf5`
- `--compression` - Compression: `none`, `gzip`, `bzip2`
- `--progress` - Show progress bar

**Example:**

```bash
# Download with format conversion
aignostics datasets download ds_abc123 --format parquet --compression gzip --progress

# Download to specific directory
aignostics datasets download ds_abc123 --output-dir ./data --progress
```

### Stream Large Dataset

```bash
aignostics datasets stream <dataset_id> [OPTIONS]
```

**Options:**

- `--output-file` - Output filename
- `--chunk-size` - Records per chunk
- `--wait` - Wait for completion

**Example:**

```bash
# Stream with chunking
aignostics datasets stream ds_abc123 \
  --output-file large_dataset.csv.gz \
  --chunk-size 5000 \
  --wait
```

## Python SDK

```python
from aignostics import AignosticsClient

# Initialize client
client = AignosticsClient(api_key="your-api-key")

# List datasets
datasets = client.datasets.list(status="ready", format="csv")

# Get dataset details
dataset = client.datasets.get("ds_abc123")

# Download dataset
client.datasets.download(
    dataset_id="ds_abc123",
    output_path="./dataset.parquet",
    format="parquet",
    compression="gzip"
)

# Stream large dataset
stream = client.datasets.stream(
    dataset_id="ds_abc123",
    format="csv",
    chunk_size=1000
)

# Monitor progress
progress = stream.get_progress()
print(f"Progress: {progress.percentage}%")
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Download successful |
| 202 | Stream initiated |
| 400 | Invalid request |
| 401 | Authentication required |
| 404 | Dataset not found |
| 429 | Rate limit exceeded |

## Error Responses

```json
{
  "error": {
    "code": "DATASET_NOT_FOUND",
    "message": "Dataset with ID ds_abc123 not found"
  }
}
```

**Common Error Codes:**

- `DATASET_NOT_FOUND` - Requested dataset does not exist
- `FORMAT_NOT_SUPPORTED` - Requested format conversion not available
- `DATASET_EXPIRED` - Dataset has expired and is no longer available

## Rate Limits

- **Dataset queries**: 30 per minute
- **Downloads**: 5 per minute
- **Streams**: 3 per minute
- **Concurrent downloads**: 3 per user