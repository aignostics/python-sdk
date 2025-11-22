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
- **SDK Metadata Integration**: Automatic attachment of SDK context metadata to all submitted runs
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

### Module Structure (NEW in v1.0.0-beta.7)

The application module is organized into focused submodules:

```
application/
├── _service.py      # High-level orchestration and API integration
├── _models.py       # Data models (DownloadProgress, DownloadProgressState) [NEW]
├── _download.py     # Download helpers with progress tracking [NEW]
├── _utils.py        # Shared utilities
├── _cli.py          # CLI commands
└── _gui/            # GUI components
```

**Key Separation:**

- **_models.py**: Pydantic models for progress tracking with computed fields
- **_download.py**: Pure download logic (URLs, artifacts, progress callbacks)
- **_service.py**: High-level business logic and module integration

### Service Layer Architecture

```
┌────────────────────────────────────────────┐
│          Application Service               │
│         (High-Level Orchestration)         │
├────────────────────────────────────────────┤
│    Progress Tracking & State Management    │
│         (_models.py - NEW)                 │
├────────────────────────────────────────────┤
│         Integration Layer                  │
│  ┌──────────┬───────────┬──────────┐      │
│  │ Platform │    WSI    │  QuPath  │      │
│  │ Service  │  Service  │ Service  │      │
│  └──────────┴───────────┴──────────┘      │
├────────────────────────────────────────────┤
│         File Processing Layer              │
│    (Upload, Download, Verification)        │
│         (_download.py - NEW)               │
└────────────────────────────────────────────┘
```

### State Machine Design

```python
RunState:
    QUEUED → RUNNING → COMPLETED
                ↓
            FAILED / CANCELLED

ItemState:
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
def application_version(self, application_id: str,
                       version_number: str | None = None) -> ApplicationVersion:
    """Validate and retrieve application version.
    
    Args:
        application_id: The ID of the application (e.g., 'heta')
        version_number: The semantic version number (e.g., '1.0.0')
                       If None, returns the latest version
    
    Returns:
        ApplicationVersion with application_id and version_number attributes
    """
    # Delegates to platform client which validates semver format
    # Platform client uses Versions resource internally
    return self.platform_client.application_version(
        application_id=application_id,
        version_number=version_number
    )
```

**Key Points:**

- Application ID and version number are now **separate parameters**
- Version format: semantic version string without 'v' prefix (e.g., `"1.0.0"`, not `"v1.0.0"`)
- Uses `semver.Version.is_valid()` for validation in the platform layer
- Falls back to latest version if `version_number` is `None`
- Returns `ApplicationVersion` object with `application_id` and `version_number` attributes

### File Processing Constants (Actual Values)

```python
# From _service.py
APPLICATION_RUN_FILE_READ_CHUNK_SIZE = 1024 * 1024 * 1024  # 1GB
APPLICATION_RUN_DOWNLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB
APPLICATION_RUN_UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB
APPLICATION_RUN_DOWNLOAD_SLEEP_SECONDS = 5  # Wait between status checks
```

### Progress State Management

**Actual DownloadProgress Model (`_models.py`):**

```python
class DownloadProgress(BaseModel):
    """Model for tracking download progress with computed progress metrics."""

    # Core state
    status: DownloadProgressState = DownloadProgressState.INITIALIZING

    # Run and item tracking
    run: RunData | None = None
    item: ItemResult | None = None
    item_count: int | None = None
    item_index: int | None = None
    item_external_id: str | None = None

    # Artifact tracking
    artifact: OutputArtifactElement | None = None
    artifact_count: int | None = None
    artifact_index: int | None = None
    artifact_path: Path | None = None
    artifact_download_url: str | None = None
    artifact_size: int | None = None
    artifact_downloaded_chunk_size: int = 0  # Last chunk size
    artifact_downloaded_size: int = 0  # Total downloaded

    # Input slide tracking (NEW in v1.0.0-beta.7)
    input_slide_path: Path | None = None
    input_slide_url: str | None = None
    input_slide_size: int | None = None
    input_slide_downloaded_chunk_size: int = 0
    input_slide_downloaded_size: int = 0

    # QuPath integration (conditional)
    if has_qupath_extra:
        qupath_add_input_progress: QuPathAddProgress | None = None
        qupath_add_results_progress: QuPathAddProgress | None = None
        qupath_annotate_input_with_results_progress: QuPathAnnotateProgress | None = None

    @computed_field
    @property
    def total_artifact_count(self) -> int | None:
        """Calculate total number of artifacts across all items."""
        if self.item_count and self.artifact_count:
            return self.item_count * self.artifact_count
        return None

    @computed_field
    @property
    def total_artifact_index(self) -> int | None:
        """Calculate the current artifact index across all items."""
        if self.item_count and self.artifact_count and self.item_index is not None and self.artifact_index is not None:
            return self.item_index * self.artifact_count + self.artifact_index
        return None

    @computed_field
    @property
    def item_progress_normalized(self) -> float:
        """Normalized progress 0..1 across all items.

        Handles different progress states:
        - DOWNLOADING_INPUT: Progress through items being downloaded
        - DOWNLOADING: Progress through artifacts being downloaded
        - QUPATH_*: QuPath-specific progress tracking
        """
        # Implementation varies by state...

    @computed_field
    @property
    def artifact_progress_normalized(self) -> float:
        """Normalized progress 0..1 for current artifact/input download.

        Handles different download types:
        - DOWNLOADING_INPUT: Input slide download progress
        - DOWNLOADING: Artifact download progress
        - QUPATH_ANNOTATE: QuPath annotation progress
        """
        # Implementation varies by state...
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

**Download Progress States (`_models.py`):**

```python
class DownloadProgressState(StrEnum):
    """Enum for download progress states."""
    INITIALIZING = "Initializing ..."
    DOWNLOADING_INPUT = "Downloading input slide ..."  # NEW in v1.0.0-beta.7
    QUPATH_ADD_INPUT = "Adding input slides to QuPath project ..."
    CHECKING = "Checking run status ..."
    WAITING = "Waiting for item completing ..."
    DOWNLOADING = "Downloading artifact ..."
    QUPATH_ADD_RESULTS = "Adding result images to QuPath project ..."
    QUPATH_ANNOTATE_INPUT_WITH_RESULTS = "Annotating input slides in QuPath project with results ..."
    COMPLETED = "Completed."
```

### Download Module (`_download.py` - NEW in v1.0.0-beta.7)

The download module provides reusable download helper functions with comprehensive progress tracking.

**Key Functions:**

```python
def extract_filename_from_url(url: str) -> str:
    """Extract a filename from a URL robustly.

    Supports:
    - gs:// (Google Cloud Storage)
    - http:// and https:// URLs
    - Handles query parameters and trailing slashes
    - Sanitizes filenames for filesystem use

    Examples:
        >>> extract_filename_from_url("gs://bucket/path/to/file.tiff")
        'file.tiff'
        >>> extract_filename_from_url("https://example.com/slides/sample.svs?token=abc")
        'sample.svs'
    """

def download_url_to_file_with_progress(
    progress: DownloadProgress,
    url: str,
    destination_path: Path,
    download_progress_queue: Any | None = None,
    download_progress_callable: Callable | None = None,
) -> Path:
    """Download a file from a URL (gs://, http://, or https://) with progress tracking.

    Features:
    - Converts gs:// URLs to signed URLs automatically
    - Streams downloads with 1MB chunks (APPLICATION_RUN_DOWNLOAD_CHUNK_SIZE)
    - Updates progress on every chunk
    - Supports both queue and callback progress updates
    - Creates parent directories automatically

    Args:
        progress: Progress tracking object (updated in place)
        url: URL to download (gs://, http://, https://)
        destination_path: Local file path to save to
        download_progress_queue: Optional queue for GUI progress updates
        download_progress_callable: Optional callback for CLI progress updates

    Returns:
        Path: The path to the downloaded file

    Raises:
        ValueError: If URL scheme is unsupported
        RuntimeError: If download fails
    """

def download_available_items(
    progress: DownloadProgress,
    application_run: Run,
    destination_directory: Path,
    downloaded_items: set[str],
    create_subdirectory_per_item: bool = False,
    download_progress_queue: Any | None = None,
    download_progress_callable: Callable | None = None,
) -> None:
    """Download items that are available and not yet downloaded.

    Features:
    - Only downloads TERMINATED items with FULL output
    - Skips already downloaded items (tracked via external_id)
    - Optional subdirectory per item
    - Progress tracking for each item and artifact

    Args:
        progress: Progress tracking object
        application_run: Run object with results
        destination_directory: Directory to save files
        downloaded_items: Set of already downloaded external_ids
        create_subdirectory_per_item: Create item subdirectories
        download_progress_queue: Optional queue for GUI updates
        download_progress_callable: Optional callback for CLI updates
    """

def download_item_artifact(
    progress: DownloadProgress,
    artifact: Any,
    destination_directory: Path,
    prefix: str = "",
    download_progress_queue: Any | None = None,
    download_progress_callable: Callable | None = None,
) -> None:
    """Download an artifact of a result item with progress tracking.

    Features:
    - CRC32C checksum verification
    - Skips download if file exists with correct checksum
    - Automatic file extension detection
    - Chunked downloads with progress updates

    Raises:
        ValueError: If no checksum metadata found or checksum mismatch
        requests.HTTPError: If download fails
    """
```

**Constants:**

```python
# From _download.py
APPLICATION_RUN_FILE_READ_CHUNK_SIZE = 1024 * 1024 * 1024  # 1GB (for checksum calculation)
APPLICATION_RUN_DOWNLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB (for streaming downloads)
```

**URL Support:**

The download module supports three URL schemes:

1. **gs://** - Google Cloud Storage (converted to signed URLs via `platform.generate_signed_url()`)
2. **http://** - HTTP URLs (used directly)
3. **https://** - HTTPS URLs (used directly)

**Progress Update Pattern:**

```python
def update_progress(
    progress: DownloadProgress,
    download_progress_callable: Callable | None = None,
    download_progress_queue: Any | None = None,
) -> None:
    """Update download progress via callback or queue.

    Dual update mechanism:
    - Callback: Synchronous update (CLI, blocking)
    - Queue: Asynchronous update (GUI, non-blocking)

    Both can be used simultaneously.
    """
    if download_progress_callable:
        download_progress_callable(progress)
    if download_progress_queue:
        download_progress_queue.put_nowait(progress)
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
    # Application ID and version are separate parameters
    app_version = service.application_version(
        application_id="heta",
        version_number="2.1.0"  # Semantic version without 'v' prefix
    )
    # Access attributes
    print(f"Application: {app_version.application_id}")
    print(f"Version: {app_version.version_number}")
    
    # Get latest version
    latest = service.application_version(
        application_id="heta",
        version_number=None  # Returns latest version
    )
except ValueError as e:
    # Handle invalid version format
    logger.error(f"Version error: {e}")
except NotFoundException as e:
    # Handle missing application or version
    logger.error(f"Application not found: {e}")

# Run application (simplified - actual has more parameters)
run = service.run_application(
    application_id="heta",
    application_version="2.1.0",  # Optional, uses latest if omitted
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

**Basic download with progress callback:**

```python
from aignostics.application._download import download_url_to_file_with_progress
from aignostics.application._models import DownloadProgress
from pathlib import Path

# Create progress object
progress = DownloadProgress()

# Define progress callback
def on_progress(p: DownloadProgress):
    if p.input_slide_size:
        percent = (p.input_slide_downloaded_size / p.input_slide_size) * 100
        print(f"Downloaded: {percent:.1f}%")

# Download from gs://, http://, or https://
downloaded_file = download_url_to_file_with_progress(
    progress=progress,
    url="gs://my-bucket/slides/sample.svs",
    destination_path=Path("./downloads/sample.svs"),
    download_progress_callable=on_progress
)

print(f"Downloaded to: {downloaded_file}")
```

**Download with GUI queue (non-blocking):**

```python
from queue import Queue
from aignostics.application._download import download_url_to_file_with_progress

# Create queue for GUI updates
progress_queue = Queue()

# Download in background thread
download_url_to_file_with_progress(
    progress=DownloadProgress(),
    url="https://example.com/slide.tiff",
    destination_path=Path("./slide.tiff"),
    download_progress_queue=progress_queue  # Non-blocking updates
)

# In GUI thread, poll queue
while not progress_queue.empty():
    progress = progress_queue.get()
    ui.update(progress.artifact_progress_normalized)
```

**Download application run results:**

```python
from aignostics.application._download import download_available_items

# Track downloaded items to avoid re-downloading
downloaded_items = set()

# Download all available items
download_available_items(
    progress=DownloadProgress(),
    application_run=run,
    destination_directory=Path("./results"),
    downloaded_items=downloaded_items,
    create_subdirectory_per_item=True,  # Create dirs per item
    download_progress_callable=lambda p: print(f"Item {p.item_index}/{p.item_count}")
)
```

## Testing Strategies (Actual Test Patterns)

### Semver Validation Testing (`service_test.py`)

```python
def test_application_version_valid_semver_formats():
    """Test valid semver formats."""
    valid_versions = [
        "1.0.0",
        "1.2.3",
        "10.20.30",
        "1.1.2-prerelease+meta",
        "1.0.0-alpha",
        "1.0.0-beta",
        "1.0.0-alpha.beta",
        "1.0.0-rc.1+meta",
    ]

    for version in valid_versions:
        try:
            result = service.application_version(
                application_id="test-app",
                version_number=version
            )
            assert result.application_id == "test-app"
            assert result.version_number == version
        except ValueError as e:
            pytest.fail(f"Valid format '{version}' rejected: {e}")
        except NotFoundException:
            # Application doesn't exist, but format is valid
            pytest.skip(f"Application not found for test-app")

def test_application_version_invalid_semver_formats():
    """Test invalid formats are rejected."""
    invalid_versions = [
        "v1.0.0",      # 'v' prefix not allowed
        "1.0",         # Incomplete version
        "1.0.0-",      # Trailing dash
        "",            # Empty string
        "not-semver",  # Not a valid semver
    ]

    for version in invalid_versions:
        with pytest.raises(ValueError, match="Invalid version format"):
            service.application_version(
                application_id="test-app",
                version_number=version
            )
```

### Use Latest Fallback Test

```python
def test_application_version_use_latest_fallback():
    """Test fallback to latest version."""
    service = ApplicationService()

    try:
        # Get latest version by passing None
        result = service.application_version(
            application_id=HETA_APPLICATION_ID,
            version_number=None  # Falls back to latest
        )
        assert result is not None
        assert result.application_id == HETA_APPLICATION_ID
        assert result.version_number is not None
        # version_number should be valid semver
        assert semver.Version.is_valid(result.version_number)
    except NotFoundException as e:
        if "No versions found" in str(e):
            # Expected if no versions exist
            pytest.skip(f"No versions available for {HETA_APPLICATION_ID}")
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


logger.debug("Starting application run", extra={
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

**Problem:** Using incorrect version format or combining application ID with version

**Solution:**

```python
# Correct: Separate application_id and version_number
app_version = service.application_version(
    application_id="heta",
    version_number="1.2.3"  # No 'v' prefix
)

# Wrong: Old combined format
# app_version = service.application_version("heta:v1.2.3")  # No longer supported

# Wrong: Version with 'v' prefix
# version_number="v1.2.3"  # Will fail validation
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

### Internal Module Organization (NEW in v1.0.0-beta.7)

The application module is organized into focused submodules:

- **`_service.py`** - High-level orchestration, API integration, run lifecycle management
- **`_models.py`** - Data models (DownloadProgress, DownloadProgressState)
- **`_download.py`** - Download helpers with progress tracking and checksum verification
- **`_utils.py`** - Shared utilities
- **`_cli.py`** - CLI commands
- **`_gui/`** - GUI components (page builders, reactive components)

### Internal SDK Dependencies

- `platform` - Client, API operations, **SDK metadata system** (automatic attachment to all runs), signed URLs
- `wsi` - WSI file validation
- `bucket` - Cloud storage operations
- `qupath` - Analysis integration (optional, requires ijson)
- `utils` - Logging, sanitization, and base utilities

**SDK Metadata Integration:**

Every run submitted through the application module automatically includes SDK metadata:

- **Run metadata** (v0.0.4): Execution context, user info, CI/CD details, tags, timestamps
- **Item metadata** (v0.0.3): Platform bucket location, tags, timestamps
- Automatic attachment via `platform._sdk_metadata.build_run_sdk_metadata()`

See `platform/CLAUDE.md` for detailed SDK metadata documentation and schema.

**Signed URL Generation:**

The `_download.py` module uses `platform.generate_signed_url()` to convert `gs://` URLs to time-limited signed URLs for downloads.

### External Dependencies

- `semver` - Semantic version validation (using `Version.is_valid()`)
- `google-crc32c` - File integrity checking (CRC32C checksums)
- `requests` - HTTP operations (streaming downloads)
- `pydantic` - Data models with validation and computed fields
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
