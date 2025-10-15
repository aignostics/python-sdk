# CLAUDE.md - Application Module

This file provides comprehensive guidance to Claude Code and human engineers when working with the `application` module in this repository.

## Module Overview

The application module provides high-level orchestration for AI/ML applications on the Aignostics Platform, managing complex workflows for computational pathology analysis with enterprise-grade reliability and observability.

### Core Responsibilities

- **Workflow Orchestration**: End-to-end management of application runs from file upload to result retrieval
- **Version Management**: Semantic versioning validation using `semver` library
- **Progress Tracking**: Multi-stage progress monitoring with real-time updates and QuPath integration
- **File Processing**: WSI validation, chunked uploads, CRC32C integrity verification
- **State Management**: Complex state machines for run lifecycle with error recovery
- **Integration Hub**: Bridges platform, WSI, bucket, and QuPath services seamlessly

### User Interfaces

**CLI Commands (`_cli.py`):**

- `application list` - List available applications and versions
- `application dump-schemata` - Export input/output schemas
- `application run list` - List application runs
- `application run submit` - Submit new application run
- `application run describe` - Show run details and status
- `application run result download` - Download run results
- `application run result delete` - Delete run results

**GUI Components (`_gui/`):**

- `_page_index.py` - Main application listing and run submission
- `_page_application_describe.py` - Application details and version information
- `_page_application_run_describe.py` - Run monitoring with real-time progress
- QuPath integration for WSI visualization (when ijson installed)

**Service Layer (`_service.py`):**

Core application operations:
- Application listing and version management (semver validation)
- Run lifecycle management (submit, monitor, complete)
- File upload with chunking (1MB chunks) and CRC32C verification
- Result download with progress tracking
- State machine for run status transitions
- QuPath project creation (when ijson available)

## Architecture & Design Patterns

### Service Layer Architecture

```
┌────────────────────────────────────────────┐
│          Application Service               │
│         (High-Level Orchestration)         │
├────────────────────────────────────────────┤
│    Progress Tracking & State Management    │
├────────────────────────────────────────────┤
│         Integration Layer                  │
│  ┌──────────┬───────────┬──────────┐      │
│  │ Platform │    WSI    │  QuPath  │      │
│  │ Service  │  Service  │ Service  │      │
│  └──────────┴───────────┴──────────┘      │
├────────────────────────────────────────────┤
│         File Processing Layer              │
│    (Upload, Download, Verification)        │
└────────────────────────────────────────────┘
```

### State Machine Design

```python
ApplicationRunStatus:
    QUEUED → RUNNING → COMPLETED
                ↓
            FAILED / CANCELLED

ItemStatus:
    PENDING → PROCESSING → COMPLETED
                  ↓
              FAILED
```

### Progress Tracking Architecture

```python
DownloadProgress:
    ├── Status (State Machine)
    ├── Run Metadata
    ├── Item Progress (0..1)
    ├── Artifact Progress (0..1)
    └── QuPath Integration Progress
        ├── Add Input Progress
        ├── Add Results Progress
        └── Annotate Progress
```

## Critical Implementation Details

### Version Management (`_service.py`)

**Actual Semantic Version Validation:**

```python
def application_version(self, application_version_id: str,
                       use_latest_if_no_version_given: bool = True):
    """Validate and retrieve application version."""

    # Pattern: application_id:vX.Y.Z
    match = re.match(r"^([^:]+):v(.+)$", application_version_id)

    # Uses semver library for validation
    if not match or not semver.Version.is_valid(match.group(2)):
        if use_latest_if_no_version_given:
            # Try to find latest version
            application_id = match.group(1) if match else application_version_id
            latest_version = self.application_version_latest(self.application(application_id))
            if latest_version:
                return latest_version
            raise ValueError(f"No valid version found, no latest version available")

        raise ValueError(f"Invalid application version id format: {application_version_id}. "
                        "Expected format: application_id:vX.Y.Z")

    # Lookup version in application
    application_id = match.group(1)
    application = self.application(application_id)
    for version in self.application_versions(application):
        if version.application_version_id == application_version_id:
            return version
    raise NotFoundException(f"Version {application_version_id} not found")
```

**Key Points:**

- Uses `semver.Version.is_valid()` for validation (NOT custom regex)
- Version MUST have 'v' prefix: `app-id:v1.2.3`
- Falls back to latest version if configured
- Iterates through versions to find match

### File Processing Constants (Actual Values)

```python
# From _service.py
APPLICATION_RUN_FILE_READ_CHUNK_SIZE = 1024 * 1024 * 1024  # 1GB
APPLICATION_RUN_DOWNLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB
APPLICATION_RUN_UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB
APPLICATION_RUN_DOWNLOAD_SLEEP_SECONDS = 5  # Wait between status checks
```

### Progress State Management

**Actual DownloadProgress Model:**

```python
class DownloadProgress(BaseModel):
    # Core state
    status: DownloadProgressState = DownloadProgressState.INITIALIZING

    # Run and item tracking
    run: ApplicationRunData | None = None
    item: ItemResult | None = None
    item_count: int | None = None
    item_index: int | None = None
    item_reference: str | None = None

    # Artifact tracking
    artifact: OutputArtifactElement | None = None
    artifact_count: int | None = None
    artifact_index: int | None = None
    artifact_path: Path | None = None
    artifact_download_url: str | None = None
    artifact_size: int | None = None
    artifact_downloaded_chunk_size: int = 0  # Last chunk size
    artifact_downloaded_size: int = 0  # Total downloaded

    # QuPath integration (conditional)
    if has_qupath_extra:
        qupath_add_input_progress: QuPathAddProgress | None = None
        qupath_add_results_progress: QuPathAddProgress | None = None
        qupath_annotate_input_with_results_progress: QuPathAnnotateProgress | None = None

    @computed_field
    @property
    def total_artifact_count(self) -> int | None:
        if self.item_count and self.artifact_count:
            return self.item_count * self.artifact_count
        return None

    @computed_field
    @property
    def item_progress_normalized(self) -> float:
        """Normalized progress 0..1 across all items."""
        # Implementation details...
```

### QuPath Integration (Conditional Loading)

**Actual Implementation:**

```python
# At module level
has_qupath_extra = find_spec("ijson")
if has_qupath_extra:
    from aignostics.qupath import (
        AddProgress as QuPathAddProgress,
        AnnotateProgress as QuPathAnnotateProgress,
        Service as QuPathService
    )

# In methods
def process_with_qupath(self, ...):
    if not has_qupath_extra:
        logger.warning("QuPath integration not available (ijson not installed)")
        return
    # QuPath processing...
```

**Download Progress States:**

```python
class DownloadProgressState(StrEnum):
    INITIALIZING = "Initializing ..."
    QUPATH_ADD_INPUT = "Adding input slides to QuPath project ..."
    CHECKING = "Checking run status ..."
    WAITING = "Waiting for item completing ..."
    DOWNLOADING = "Downloading artifact ..."
    QUPATH_ADD_RESULTS = "Adding result images to QuPath project ..."
    QUPATH_ANNOTATE_INPUT_WITH_RESULTS = "Annotating input slides in QuPath project with results ..."
    COMPLETED = "Completed."
```

## Usage Patterns & Best Practices

### Basic Application Execution

```python
from aignostics.application import Service

service = Service()

# List applications
apps = service.list_applications()

# Get specific version (actual pattern)
try:
    # Requires 'v' prefix
    app_version = service.application_version(
        "heta:v2.1.0",  # Must be app-id:vX.Y.Z format
        use_latest_if_no_version_given=True
    )
except ValueError as e:
    # Handle invalid format or missing version
    logger.error(f"Version error: {e}")
except NotFoundException as e:
    # Handle missing application
    logger.error(f"Application not found: {e}")

# Run application (simplified - actual has more parameters)
run = service.run_application(
    application_id="heta",
    files=["slide1.svs", "slide2.tiff"]
)
```

### File Upload Pattern (Actual Implementation)

```python
def upload_file(self, file_path: Path, signed_url: str):
    """Upload file with chunking and CRC32C."""

    with file_path.open("rb") as f:
        # Calculate CRC32C
        crc = google_crc32c.Checksum()

        # Upload in chunks
        while True:
            chunk = f.read(APPLICATION_RUN_UPLOAD_CHUNK_SIZE)  # 1MB chunks
            if not chunk:
                break

            crc.update(chunk)
            # Upload chunk to signed URL
            # (Implementation details vary)

    # Return CRC32C for verification
    return base64.b64encode(crc.digest()).decode("utf-8")
```

### Download with Progress (Actual Pattern)

```python
def download_artifact(self, url: str, output_path: Path, progress_callback):
    """Download with progress tracking."""

    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("Content-Length", 0))

    downloaded = 0
    with output_path.open("wb") as f:
        for chunk in response.iter_content(chunk_size=APPLICATION_RUN_DOWNLOAD_CHUNK_SIZE):
            f.write(chunk)
            downloaded += len(chunk)

            # Update progress
            progress = DownloadProgress(
                status=DownloadProgressState.DOWNLOADING,
                artifact_downloaded_chunk_size=len(chunk),
                artifact_downloaded_size=downloaded,
                artifact_size=total_size
            )

            if progress_callback:
                progress_callback(progress)
```

## Testing Strategies (Actual Test Patterns)

### Semver Validation Testing (`service_test.py`)

```python
def test_application_version_valid_semver_formats():
    """Test valid semver formats."""
    valid_formats = [
        "test-app:v1.0.0",
        "test-app:v1.2.3",
        "test-app:v10.20.30",
        "test-app:v1.1.2-prerelease+meta",
        "test-app:v1.0.0-alpha",
        "test-app:v1.0.0-beta",
        "test-app:v1.0.0-alpha.beta",
        "test-app:v1.0.0-rc.1+meta",
    ]

    for version_id in valid_formats:
        try:
            service.application_version(version_id)
        except ValueError as e:
            pytest.fail(f"Valid format '{version_id}' rejected: {e}")
        except NotFoundException:
            # Application doesn't exist, but format is valid
            pytest.skip(f"Application not found for {version_id}")

def test_application_version_invalid_semver_formats():
    """Test invalid formats are rejected."""
    invalid_formats = [
        "test-app:1.0.0",     # Missing 'v' prefix
        "test-app:v1.0",      # Incomplete version
        "test-app:v1.0.0-",   # Trailing dash
        ":v1.0.0",            # Missing application ID
        "no-colon-v1.0.0",    # Missing colon separator
    ]

    for version_id in invalid_formats:
        with pytest.raises(ValueError, match="Invalid application version id format"):
            service.application_version(version_id)
```

### Use Latest Fallback Test

```python
def test_application_version_use_latest_fallback():
    """Test fallback to latest version."""
    service = ApplicationService()

    try:
        # Try with just application ID (no version)
        result = service.application_version(
            HETA_APPLICATION_ID,
            use_latest_if_no_version_given=True
        )
        assert result is not None
        assert result.application_version_id.startswith(f"{HETA_APPLICATION_ID}:v")
    except ValueError as e:
        if "no latest version available" in str(e):
            # Expected if no versions exist
            pass
        else:
            pytest.fail(f"Unexpected error: {e}")
```

## Operational Requirements

### File Processing Limits

- **Upload chunk size**: 1 MB
- **Download chunk size**: 1 MB
- **File read chunk size**: 1 GB (for large file processing)
- **Status check interval**: 5 seconds

### Monitoring & Observability

**Key Metrics:**

- Run completion rate by application
- Average processing time per WSI file
- Upload/download throughput (MB/s)
- Progress callback frequency
- QuPath integration availability

**Logging Patterns (Actual):**

```python
logger = get_logger(__name__)

logger.info("Starting application run", extra={
    "application_id": app_id,
    "file_count": len(files)
})

logger.warning("QuPath integration not available (ijson not installed)")

logger.error("Application version validation failed", extra={
    "version_id": version_id,
    "error": str(e)
})
```

## Common Pitfalls & Solutions

### Semver Format Issues

**Problem:** Missing 'v' prefix in version

**Solution:**
```python
# Always include 'v' prefix
version_id = "app-id:v1.2.3"  # Correct
# NOT: "app-id:1.2.3"  # Wrong
```

### QuPath Availability

**Problem:** QuPath features not working

**Solution:**
```python
# Check if ijson is installed
if not has_qupath_extra:
    print("QuPath features require: pip install ijson")
```

### Large File Processing

**Problem:** Memory issues with large files

**Solution:**
```python
# Use streaming with appropriate chunk size
chunk_size = APPLICATION_RUN_FILE_READ_CHUNK_SIZE  # 1GB
with open(file_path, 'rb') as f:
    while chunk := f.read(chunk_size):
        process_chunk(chunk)
```

## Module Dependencies

### Internal Dependencies

- `platform` - Client and API operations
- `wsi` - WSI file validation
- `bucket` - Cloud storage operations
- `qupath` - Analysis integration (optional, requires ijson)
- `utils` - Logging and utilities

### External Dependencies

- `semver` - Semantic version validation (using `Version.is_valid()`)
- `google-crc32c` - File integrity checking
- `requests` - HTTP operations
- `pydantic` - Data models with validation
- `ijson` - Required for QuPath features (optional)

## Performance Notes

### Current Implementation Details

1. **Chunk sizes are fixed** (not adaptive)
2. **Single-threaded uploads/downloads** (no parallelization)
3. **Synchronous progress callbacks** (may impact performance)
4. **No connection pooling** configured explicitly

### Optimization Opportunities

1. Implement adaptive chunk sizing based on bandwidth
2. Add parallel upload/download for multiple files
3. Use async progress callbacks to avoid blocking
4. Configure connection pooling for better throughput

---

*This documentation reflects the actual implementation verified against the codebase.*
