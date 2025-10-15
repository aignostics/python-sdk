# CLAUDE.md - Bucket Module

This file provides comprehensive guidance to Claude Code and human engineers when working with the `bucket` module in this repository.

## Module Overview

The bucket module provides enterprise-grade cloud storage operations for the Aignostics Platform, abstracting AWS S3 and Google Cloud Storage with unified interfaces for secure file management in medical imaging workflows.

### Core Responsibilities

- **Cloud Storage Abstraction**: Unified interface for S3, GCS, and Azure Blob Storage
- **Secure File Transfer**: Signed URL generation with expiry and access control
- **Large File Handling**: Multipart uploads, chunked downloads, resume capability
- **Data Integrity**: CRC32C/MD5 checksums, automatic retry on corruption
- **Compliance**: HIPAA-compliant storage patterns, audit logging, encryption

### User Interfaces

**CLI Commands (`_cli.py`):**

- `bucket upload` - Upload files or directories to cloud storage
- `bucket download` - Download files from cloud storage
- `bucket list` - List bucket contents
- `bucket delete` - Delete files from bucket
- `bucket sign` - Generate signed URLs

**GUI Component (`_gui.py`):**

- Storage browser interface
- Upload/download manager with progress
- Signed URL generator

**Service Layer (`_service.py`):**

Core storage operations:
- S3/GCS client management
- Signed URL generation with security constraints
- Chunked upload/download (1MB upload, 10MB download chunks)
- ETag calculation and verification
- Progress tracking with callbacks

## Architecture & Design Patterns

### Service Layer Design

```
┌────────────────────────────────────────────┐
│            Bucket Service                  │
│        (High-Level Operations)             │
├────────────────────────────────────────────┤
│         Storage Abstraction                │
│    ┌─────────┬─────────┬─────────┐        │
│    │   S3    │   GCS   │  Azure  │        │
│    └─────────┴─────────┴─────────┘        │
├────────────────────────────────────────────┤
│      Transfer Management Layer             │
│  (Multipart, Chunking, Resumption)         │
├────────────────────────────────────────────┤
│       Security & Compliance                │
│    (Encryption, Signing, Audit)            │
└────────────────────────────────────────────┘
```

### Storage Patterns

**Hierarchical Organization:**

```
bucket/
├── organizations/{org_id}/
│   ├── applications/{app_id}/
│   │   ├── runs/{run_id}/
│   │   │   ├── inputs/
│   │   │   ├── outputs/
│   │   │   └── metadata.json
│   │   └── versions/
│   └── datasets/
└── temp/  # Temporary uploads with TTL
```

## Critical Implementation Details

### Signed URL Generation (`_service.py`)

**Security-First URL Generation:**

```python
def generate_signed_url(
    bucket: str,
    key: str,
    operation: str = "GET",
    expiry_seconds: int = 3600,
    content_type: str = None,
    metadata: dict = None
) -> str:
    """Generate time-limited signed URL with security constraints."""

    # Validate permissions
    if not has_permission(bucket, key, operation):
        raise PermissionError(f"No {operation} access to {key}")

    # Add security headers
    params = {
        "Bucket": bucket,
        "Key": key,
        "ResponseContentDisposition": f"attachment; filename={Path(key).name}",
        "ResponseContentType": content_type or "application/octet-stream"
    }

    # Add server-side encryption
    if operation == "PUT":
        params["ServerSideEncryption"] = "AES256"
        params["ServerSideEncryptionCustomerAlgorithm"] = "AES256"

    # Generate presigned URL
    url = s3_client.generate_presigned_url(
        ClientMethod=operation.lower() + "_object",
        Params=params,
        ExpiresIn=expiry_seconds
    )

    # Audit log
    audit_logger.info(f"Generated signed URL", extra={
        "operation": operation,
        "bucket": bucket,
        "key": key,
        "expiry": expiry_seconds,
        "user": current_user.id
    })

    return url
```

### Upload and Download Management

**Chunk Size Constants (Actual):**

```python
UPLOAD_CHUNK_SIZE = 1024 * 1024         # 1MB upload chunks
DOWNLOAD_CHUNK_SIZE = 1024 * 1024 * 10  # 10MB download chunks
ETAG_CHUNK_SIZE = 1024 * 1024 * 100     # 100MB for ETag calculation

def upload_file(
    file_path: Path,
    bucket: str,
    key: str,
    progress_callback: Callable = None
) -> str:
    """Upload file with chunking (actual implementation pattern)."""

    # Generate signed URL for upload
    url = self._get_s3_client().generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=3600
    )

    # Upload with chunking
    with file_path.open("rb") as f:
        uploaded = 0
        while True:
            chunk = f.read(UPLOAD_CHUNK_SIZE)  # 1MB chunks
            if not chunk:
                break

            # Upload chunk logic here
            uploaded += len(chunk)
            if progress_callback:
                progress_callback(uploaded, file_path.stat().st_size)

    return url
```

### Download with Stream Processing

**Memory-Efficient Download:**

```python
def download_file(
    url: str,
    output_path: Path,
    progress_callback: Callable = None
) -> None:
    """Download file with streaming (actual implementation pattern)."""

    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("Content-Length", 0))
    downloaded = 0

    with output_path.open("wb") as f:
        for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):  # 10MB chunks
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)

                if progress_callback:
                    progress = DownloadProgress(
                        current_file_downloaded=downloaded,
                        current_file_size=total_size
                    )
                    progress_callback(progress)
```

## Cross-Module Integration

### Platform Module Integration

The bucket module integrates tightly with the [platform module](../platform/CLAUDE.md):

- Uses platform authentication for cloud credentials
- Leverages platform's correlation IDs for tracing
- Shares error handling patterns

### Application Module Usage

The [application module](../application/CLAUDE.md) uses bucket for:

- Uploading WSI files for processing
- Downloading analysis results
- Managing temporary storage during runs

### WSI Module Coordination

Works with [WSI module](../wsi/CLAUDE.md) for:

- Validating image formats before upload
- Streaming large WSI files
- Thumbnail generation and caching

## Usage Patterns & Best Practices

### Basic Operations

```python
from aignostics.bucket import Service

service = Service()

# Upload file with progress
def progress(current, total):
    print(f"Upload: {current/total:.1%}")

url = service.upload(
    file_path=Path("slide.svs"),
    bucket="aignostics-data",
    key=f"runs/{run_id}/inputs/slide.svs",
    progress_callback=progress
)

# Generate signed download URL
download_url = service.generate_signed_url(
    bucket="aignostics-data",
    key=f"runs/{run_id}/outputs/results.json",
    operation="GET",
    expiry_seconds=7200  # 2 hours
)
```

### Advanced Patterns

**Batch Operations with Parallelization:**

```python
from concurrent.futures import ThreadPoolExecutor

def upload_batch(files: list[Path]) -> list[str]:
    """Upload multiple files in parallel."""

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for file_path in files:
            future = executor.submit(
                service.upload,
                file_path=file_path,
                bucket="aignostics-data",
                key=f"batch/{file_path.name}"
            )
            futures.append(future)

        # Collect results
        urls = []
        for future in futures:
            try:
                url = future.result(timeout=300)
                urls.append(url)
            except Exception as e:
                logger.error(f"Upload failed: {e}")
                urls.append(None)

    return urls
```

**Resumable Download:**

```python
def download_with_resume(
    bucket: str,
    key: str,
    output_path: Path
) -> None:
    """Download with automatic resume on failure."""

    # Check for partial download
    if output_path.exists():
        resume_offset = output_path.stat().st_size
        logger.info(f"Resuming download from byte {resume_offset}")
    else:
        resume_offset = 0

    # Download with range header
    response = s3_client.get_object(
        Bucket=bucket,
        Key=key,
        Range=f"bytes={resume_offset}-" if resume_offset > 0 else None
    )

    # Append to existing file or create new
    mode = "ab" if resume_offset > 0 else "wb"
    with output_path.open(mode) as f:
        for chunk in response["Body"].iter_chunks():
            f.write(chunk)
```

## Testing Strategies

### Unit Testing

```python
@pytest.fixture
def mock_s3_client():
    """Mock boto3 S3 client."""
    with patch("boto3.client") as mock:
        client = MagicMock()
        client.generate_presigned_url.return_value = "https://signed.url"
        mock.return_value = client
        yield client

def test_signed_url_generation(mock_s3_client):
    """Test secure URL generation."""
    service = Service()
    url = service.generate_signed_url(
        bucket="test",
        key="file.txt",
        expiry_seconds=3600
    )

    assert url.startswith("https://")
    mock_s3_client.generate_presigned_url.assert_called_once()
```

### Integration Testing

```python
@pytest.mark.docker
def test_multipart_upload_recovery():
    """Test multipart upload with simulated failure."""
    # Use localstack for S3 simulation
    # Interrupt upload midway
    # Verify resume capability
```

## Operational Requirements

### Monitoring & Observability

**Key Metrics:**

- Upload/download throughput (MB/s)
- Signed URL generation rate
- Multipart upload success rate
- Storage costs by organization
- Failed transfer recovery rate

**Logging Standards:**

```python
logger.info("File uploaded", extra={
    "bucket": bucket,
    "key": key,
    "size_mb": file_size / (1024*1024),
    "duration_seconds": duration,
    "transfer_rate_mbps": transfer_rate
})
```

### Security & Compliance

**Data Protection:**

- Server-side encryption (SSE-S3 or SSE-KMS)
- Client-side encryption for sensitive data
- Access logging for audit trails
- Versioning for data recovery
- Object lifecycle policies for retention

**HIPAA Compliance:**

```python
# Ensure PHI data is encrypted
if contains_phi(file_path):
    encryption_config = {
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "aws:kms",
                "KMSMasterKeyID": KMS_KEY_ID
            }
        }]
    }
```

## Performance Optimization

### Transfer Optimization

- Adaptive chunk sizing based on bandwidth
- Parallel part uploads for multipart
- Connection pooling and reuse
- Regional endpoint selection
- Transfer acceleration for cross-region

### Caching Strategies

```python
# Local cache for frequently accessed files
CACHE_DIR = Path.home() / ".aignostics" / "cache"
MAX_CACHE_SIZE = 10 * 1024 * 1024 * 1024  # 10GB

def get_with_cache(bucket: str, key: str) -> Path:
    """Get file with local caching."""
    cache_path = CACHE_DIR / bucket / key

    if cache_path.exists():
        # Verify cache validity
        if is_cache_valid(cache_path, bucket, key):
            return cache_path

    # Download to cache
    download_to_cache(bucket, key, cache_path)
    manage_cache_size()

    return cache_path
```

## Common Pitfalls & Solutions

### Large File Timeouts

**Problem:** Uploads timing out for multi-GB files

**Solution:** Use multipart upload with smaller chunks and retry logic

### Signed URL Expiry

**Problem:** URLs expiring during long operations

**Solution:** Generate URLs just-in-time or implement refresh mechanism

### Cross-Region Latency

**Problem:** Slow transfers across regions

**Solution:** Use S3 Transfer Acceleration or regional replication

## Module Dependencies

### Internal Dependencies

- `platform` - Authentication and API client
- `utils` - Logging and utilities

### External Dependencies

- `boto3` - AWS SDK for S3 operations
- `google-cloud-storage` - GCS client
- `azure-storage-blob` - Azure Blob Storage

## Future Enhancements

1. **Intelligent Tiering**: Automatic storage class optimization
2. **Deduplication**: Content-addressable storage
3. **Compression**: Transparent compression for efficiency
4. **Encryption**: Client-side encryption key management
5. **CDN Integration**: CloudFront/Fastly for global distribution

---

*This module provides enterprise-grade cloud storage operations for medical imaging workflows.*
