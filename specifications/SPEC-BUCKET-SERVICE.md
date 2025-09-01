# Software Item Specification: Bucket Module

---

**Item ID:** SPEC-BUCKET-SERVICE  
**Item Type:** Software Item Spec  
**Item Fulfills:** FE-6386  
**Module:** Bucket  
**Layer:** Domain Service  
**Version:** 0.2.105  
**Date:** August 28, 2025

---

## 1. Description

### 1.1 Purpose

The Bucket Module provides comprehensive integration between the Aignostics Python SDK and S3-compatible cloud storage buckets. It enables secure file upload, download, and management operations with support for both Google Cloud Storage and AWS S3. The module serves as the primary interface for cloud storage operations within the SDK, offering both programmatic and interactive access through CLI and GUI interfaces.

### 1.2 Functional Requirements

The Bucket Module shall:

- **[FR-01]** Provide secure upload and download operations for files and directories to S3-compatible storage.
- **[FR-02]** Support pattern-based file operations using regex for bulk operations and content discovery.
- **[FR-03]** Generate time-limited signed URLs for secure file access without exposing credentials.
- **[FR-04]** Implement ETag-based caching to optimize bandwidth usage by skipping unchanged files.
- **[FR-05]** Offer both command-line and web-based user interfaces for interactive storage management.
- **[FR-06]** Support multiple cloud storage providers (Google Cloud Storage, AWS S3) through configurable protocols.

### 1.3 Non-Functional Requirements

- **Performance**: Handle files up to several GB with chunked transfer (1MB upload chunks, 10MB download chunks), progress tracking with byte-level granularity
- **Security**: HMAC-based authentication, secure credential management with automatic masking in logs, configurable signed URL expiration
- **Reliability**: ETag-based integrity checking, proper error handling with cleanup, retry mechanisms for network failures
- **Usability**: Type-safe CLI with automatic help generation, intuitive web interface with real-time progress indicators
- **Scalability**: Support concurrent operations, configurable chunk sizes for different file sizes and network conditions

### 1.4 Constraints and Limitations

- S3-Compatible API Requirement: Storage backends must support S3-compatible APIs with HMAC authentication
- Protocol Limitation: Currently supports gs:// and s3:// protocols only, no support for other cloud storage APIs
- Single Bucket Operations: Operations are scoped to individual buckets, no cross-bucket operations supported
- Memory Usage: Large file operations may require significant memory for chunked processing and ETag calculation
- **S3-Compatible API**: Uses S3-compatible API endpoints through boto3 library for broad cloud storage compatibility
- **HMAC Authentication**: Requires HMAC access keys for authentication rather than service account credentials
- **Configurable Regions**: Supports configurable regions with EUROPE-WEST3 as default for Google Cloud Storage

---

## 2. Architecture and Design

### 2.1 Module Structure

```
bucket/
├── _service.py          # Core business logic and S3-compatible storage operations
├── _cli.py             # Command-line interface with Typer framework
├── _gui.py             # Web-based GUI components using NiceGUI
├── _settings.py        # Configuration management and environment variables
└── __init__.py        # Module exports: Service, cli, and conditional PageBuilder
```

### 2.2 Key Components

| Component     | Type  | Purpose                                  | Public API                                             |
| ------------- | ----- | ---------------------------------------- | ------------------------------------------------------ |
| `Service`     | Class | Core S3-compatible storage operations    | `upload()`, `download()`, `list()`, `delete()`         |
| `cli`         | Typer | Command-line interface for bucket ops    | `upload`, `download`, `list`, `delete` commands        |
| `PageBuilder` | Class | Web interface for interactive management | `register_pages()` with bucket management UI           |
| `Settings`    | Class | Configuration and credential management  | Environment variable handling, default value provision |

### 2.3 Design Patterns

- **Service Layer Pattern**: Business logic encapsulated in Service class with clear separation from presentation layers
- **Dependency Injection**: Settings injected into Service for configurable behavior and testability
- **Adapter Pattern**: S3-compatible API adapter for Google Cloud Storage using boto3 client
- **Strategy Pattern**: Configurable protocols (gs://, s3://) through protocol-specific URL handling

**Upload Chunking (1MB chunks):**

````python
UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB
# Optimized for memory usage during streaming uploads
def read_in_chunks():
    while True:
        chunk = f.read(UPLOAD_CHUNK_SIZE)
        if not chunk:
---

## 3. Inputs and Outputs

### 3.1 Inputs

| Input Type         | Source        | Format/Type     | Validation Rules                                          |
| ------------------ | ------------- | --------------- | --------------------------------------------------------- |
| Bucket Name        | CLI/GUI/API   | String          | Must match GCS bucket naming conventions                  |
| Object Key/Pattern | CLI/GUI/API   | String/Regex    | Valid path characters, regex patterns for bulk operations |
| Local File Path    | CLI/GUI/API   | Path            | Must exist for upload, valid directory for download       |
| Credentials        | Environment   | HMAC Key Pair   | Required AIGNOSTICS_BUCKET_HMAC_* variables              |
| Protocol           | Configuration | String          | Must be "gs" or "s3"                                     |

### 3.2 Outputs

| Output Type      | Destination     | Format/Type      | Success Criteria                              |
| ---------------- | --------------- | ---------------- | --------------------------------------------- |
| Uploaded Files   | Cloud Storage   | Binary/Metadata  | Successful S3 PUT with ETag confirmation      |
| Downloaded Files | Local Filesystem| Binary           | Complete download with ETag validation        |
| Signed URLs      | Client/Platform | HTTPS URL        | Valid URL with correct expiration time        |
| Progress Updates | CLI/GUI         | Progress Models  | Real-time byte-level progress information     |
| Operation Status | Logs/Console    | Structured Logs  | Success/failure with detailed error messages  |

### 3.3 Data Flow

```mermaid
graph LR
    A[User Input] --> B[Service Layer] --> C[S3-Compatible API]
    B --> D[Progress Tracking]
    E[Environment Config] --> B
    C --> F[Cloud Storage]
    D --> G[UI Updates]
    B --> H[Local Filesystem]
````

---

## 4. Interface Definitions

### 4.1 Public API

#### Core Service Interface

```python
class Service(BaseService):
    """Bucket service for S3-compatible cloud storage operations."""

    def upload(self, source: Path, bucket: str, key: str | None = None,
              progress_callback: Callable[[UploadProgress], None] | None = None) -> str:
        """Upload file or directory to cloud storage.
        Args:
            source: Local file or directory path to upload
            bucket: Target bucket name
            key: Optional object key (auto-generated if None)
            progress_callback: Optional callback for progress updates
        Returns:
            Cloud storage URL of uploaded object
        Raises:
            ValueError: Invalid source path or bucket name
            BotoClientError: S3 API operation failure
        """

    def download(self, source_url: str, destination: Path | None = None,
                pattern: str | None = None,
                progress_callback: Callable[[DownloadProgress], None] | None = None) -> list[Path]:
        """Download files from cloud storage with optional pattern matching.
        Args:
            source_url: Cloud storage URL (gs:// or s3://)
            destination: Local destination directory
            pattern: Optional regex pattern for selective download
            progress_callback: Optional callback for progress updates
        Returns:
            List of downloaded file paths
        Raises:
            ValueError: Invalid URL format or destination
            BotoClientError: S3 API operation failure
        """

    def list(self, source_url: str, pattern: str | None = None,
            detailed: bool = False) -> list[dict[str, Any]]:
        """List bucket contents with optional pattern filtering.
        Returns:
            List of object metadata dictionaries
        """

    def generate_signed_url(self, bucket: str, key: str, operation: str = "download",
                           expiration: int | None = None) -> str:
        """Generate time-limited signed URL for secure access."""
```

### 4.2 CLI Interface

**Command Structure:**

```bash
uvx aignostics bucket [subcommand] [options]
```

**Available Commands:**

- `upload <source> <bucket> [key]`: Upload file or directory to bucket
- `download <url> [destination] [--pattern REGEX]`: Download from bucket with optional pattern
- `list <url> [--pattern REGEX] [--detailed]`: List bucket contents
- `delete <url> [--pattern REGEX] [--dry-run]`: Delete objects from bucket

### 4.3 GUI Interface

- **Navigation**: Accessible via main SDK GUI menu under "Cloud Storage"
- **Key UI Components**: File upload drag-and-drop, progress bars, bucket browser, pattern-based filtering
- **User Workflows**: Interactive file management, real-time progress tracking, signed URL generation

---

## 5. Dependencies and Integration

### 5.1 Internal Dependencies

| Dependency Module | Usage Purpose              | Interface Used                  |
| ----------------- | -------------------------- | ------------------------------- |
| Platform Service  | User authentication/config | Environment variable management |
| Utils Module      | Logging and base services  | `BaseService`, `get_logger`     |
| GUI Module        | Web interface framework    | `frame` component for UI layout |

### 5.2 External Dependencies

| Dependency | Version  | Purpose                      | Optional/Required |
| ---------- | -------- | ---------------------------- | ----------------- |
| boto3      | >=1.39.8 | S3-compatible API client     | Required          |
| pydantic   | >=2.0    | Data validation and settings | Required          |
| typer      | Latest   | CLI framework                | Required          |
| nicegui    | Latest   | Web GUI framework            | Optional          |
| rich       | Latest   | Enhanced console output      | Required          |

### 5.3 Integration Points

- **Aignostics Platform API**: Credential management and user authentication
- **Cloud Storage Services**: Google Cloud Storage (primary), AWS S3 (secondary) via S3-compatible APIs
- **Local Filesystem**: File operations, progress tracking, user data directories

---

## 6. Configuration and Settings

### 6.1 Configuration Parameters

| Parameter                    | Type | Default                                      | Description               | Required |
| ---------------------------- | ---- | -------------------------------------------- | ------------------------- | -------- |
| `protocol`                   | str  | "gs"                                         | Storage protocol (gs/s3)  | No       |
| `endpoint_url`               | str  | "https://storage.googleapis.com"             | S3-compatible endpoint    | No       |
| `region`                     | str  | "EUROPE-WEST3"                               | Storage region            | No       |
| `download_default_directory` | Path | `~/.local/share/aignostics/bucket_downloads` | Default download location | No       |

### 6.2 Environment Variables

| Variable                           | Purpose                   | Example Value              |
| ---------------------------------- | ------------------------- | -------------------------- |
| `AIGNOSTICS_BUCKET_HMAC_ACCESS_ID` | S3 access key ID          | `GOOG1A2B3C4D5`            |
| `AIGNOSTICS_BUCKET_HMAC_SECRET`    | S3 secret access key      | `secret123...`             |
| `AIGNOSTICS_BUCKET_PROTOCOL`       | Override default protocol | `s3`                       |
| `AIGNOSTICS_BUCKET_ENDPOINT_URL`   | Override endpoint URL     | `https://s3.amazonaws.com` |

---

## 7. Error Handling and Validation

### 7.1 Error Categories

| Error Type        | Cause                           | Handling Strategy               | User Impact                   |
| ----------------- | ------------------------------- | ------------------------------- | ----------------------------- |
| `CredentialError` | Missing/invalid HMAC keys       | Clear error with setup guide    | Operation blocked until fixed |
| `NetworkError`    | Connection/timeout issues       | Retry with exponential backoff  | Temporary delay, then retry   |
| `ValidationError` | Invalid input parameters        | Input validation with feedback  | Clear error message shown     |
| `PermissionError` | Insufficient bucket permissions | Auth error with troubleshooting | Access denied notification    |

### 7.2 Input Validation

- **Bucket Names**: Must follow GCS/S3 naming conventions (lowercase, no special chars)
- **Object Keys**: Validated for path safety, no leading/trailing slashes
- **File Paths**: Existence checks for uploads, directory validation for downloads
- **URLs**: Protocol validation (gs:// or s3://), proper bucket/key parsing

### 7.3 Graceful Degradation

- **When credentials unavailable**: CLI operations fail with setup instructions, GUI shows configuration needed
- **When cloud storage unreachable**: Operations timeout gracefully with retry options
- **When local filesystem full**: Upload operations pause with disk space warnings

---

## 8. Security Considerations

### 8.1 Data Protection

- **Authentication**: HMAC key-based authentication for S3-compatible APIs
- **Data Encryption**: HTTPS for all transfers, cloud provider encryption at rest
- **Access Control**: Bucket-level permissions managed through cloud provider IAM

### 8.2 Security Measures

- **Input Sanitization**: All file paths and object keys validated against injection attacks
- **Secret Management**: HMAC keys never logged, masked in output with `mask_secrets()`
- **Audit Logging**: All operations logged with timestamps, user context, and outcomes

---

## 9. Testing and Quality Assurance

### 9.1 Testing Strategy

- **Unit Tests**: Mock S3 client for isolated service testing, validate all public methods
- **Integration Tests**: Real cloud storage operations in test environment
- **Performance Tests**: Large file upload/download benchmarks, concurrent operation testing
- **Security Tests**: Credential handling validation, input sanitization verification

### 9.2 Quality Metrics

- **Code Coverage**: Minimum 80% test coverage for service layer
- **Performance Benchmarks**: <30s for 1GB file operations, <5s for signed URL generation
- **Reliability Targets**: 99.9% operation success rate, <1% data corruption tolerance

---

## 10. Implementation Details

### 10.1 Key Algorithms

- **Chunked Transfer**: Adaptive chunk sizing based on operation type (1MB upload, 10MB download, 100MB ETag)
- **ETag Caching**: MD5-based content comparison to avoid redundant downloads
- **Progress Calculation**: Byte-level progress tracking with transfer speed estimation

### 10.2 State Management

- **Configuration State**: Settings cached from environment variables with lazy loading
- **Runtime State**: Progress models maintain operation state with real-time updates
- **Cache Management**: ETag-based file validation cache for efficient re-download detection

### 10.3 Concurrency and Threading

- **Async Operations**: Generator-based progress callbacks for non-blocking UI updates
- **Thread Safety**: Immutable progress models, thread-safe logging configuration
- **Resource Management**: Proper cleanup of S3 client connections and file handles
