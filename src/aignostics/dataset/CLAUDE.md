# CLAUDE.md - Dataset Module

This file provides comprehensive guidance to Claude Code and human engineers when working with the `dataset` module in this repository.

## Module Overview

The dataset module handles enterprise-scale medical imaging dataset operations, providing high-performance downloads from the National Cancer Institute's Imaging Data Commons (IDC) and Aignostics Platform with corporate environment support.

### Core Responsibilities

- **IDC Integration**: Access to 40+ TB of public cancer imaging data
- **High-Performance Downloads**: s5cmd-based parallel transfers
- **Corporate Support**: Proxy handling, custom certificates, firewall traversal
- **Process Management**: Subprocess lifecycle with graceful cleanup
- **Progress Tracking**: Real-time download monitoring with callbacks

### User Interfaces

**CLI Commands (`_cli.py`):**

IDC commands:
- `dataset idc browse` - Open browser to explore IDC portal
- `dataset idc indices` - List available indices
- `dataset idc columns` - Show columns for a given index
- `dataset idc collections` - List available collections
- `dataset idc download` - Download dataset from IDC

Aignostics commands:
- `dataset aignostics download` - Download proprietary sample datasets

**GUI Component (`_gui.py`):**

- Dataset browser interface
- Download manager with progress tracking
- Collection explorer

**Service Layer (`_service.py`):**

Core dataset operations:
- IDC client with proxy support
- s5cmd subprocess management
- Download progress tracking
- Path length validation for Windows
- Process cleanup on exit

## Architecture & Design Patterns

### Service Architecture

```
┌────────────────────────────────────────────┐
│           Dataset Service                  │
│        (High-Level Operations)             │
├────────────────────────────────────────────┤
│         IDC Client Layer                   │
│    (Modified for Corporate Proxies)        │
├────────────────────────────────────────────┤
│       Download Engine (s5cmd)              │
│    (Subprocess Management, Progress)       │
├────────────────────────────────────────────┤
│        Path & Metadata Management          │
│      (DICOM Organization, Layout)          │
└────────────────────────────────────────────┘
```

### Process Management Pattern

```python
# Global process registry for cleanup
_active_processes: list[subprocess.Popen] = []

# Automatic cleanup on exit
atexit.register(_cleanup_processes)
```

## Critical Implementation Details

### IDC Client Enhancement (`third_party/idc_index.py`)

**Corporate Environment Modifications:**

```python
class IDCClient:
    """Enhanced IDC client with corporate proxy support."""

    def __init__(self):
        # Original IDC initialization
        super().__init__()

        # Add proxy support
        self.session = requests.Session()
        self.session.proxies = {
            "http": os.environ.get("HTTP_PROXY"),
            "https": os.environ.get("HTTPS_PROXY")
        }

        # Custom certificate bundle
        if ca_bundle := os.environ.get("REQUESTS_CA_BUNDLE"):
            self.session.verify = ca_bundle

        # Retry configuration for flaky networks
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
```

### High-Performance Download Engine (`_service.py`)

**s5cmd Integration with Process Management:**

```python
TARGET_LAYOUT_DEFAULT = "%collection_id/%PatientID/%StudyInstanceUID/%Modality_%SeriesInstanceUID/"

def download_dataset(
    collection_id: str,
    output_dir: Path,
    progress_callback: Callable = None,
    filters: dict = None
) -> None:
    """Download IDC dataset with s5cmd for maximum performance."""

    # Query IDC for download manifest
    idc_client = IDCClient()
    manifest = idc_client.get_download_manifest(
        collection_id=collection_id,
        filters=filters
    )

    # Create s5cmd commands file
    commands_file = Path(tempfile.mktemp(suffix=".txt"))
    with commands_file.open("w") as f:
        for item in manifest:
            source = f"s3://public-datasets/{item['aws_url']}"
            target = output_dir / self._get_target_path(item)
            f.write(f"cp {source} {target}\n")

    # Launch s5cmd subprocess
    process = subprocess.Popen(
        [
            "s5cmd",
            "--endpoint-url", "https://s3.amazonaws.com",
            "--concurrent", "100",  # Parallel transfers
            "--retry-count", "3",
            "run", str(commands_file)
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=SUBPROCESS_CREATION_FLAGS
    )

    # Track process for cleanup
    _active_processes.append(process)

    try:
        # Monitor progress
        self._monitor_download(process, progress_callback)
    finally:
        # Ensure cleanup
        _active_processes.remove(process)
        commands_file.unlink(missing_ok=True)
```

### Process Lifecycle Management

**Graceful Cleanup (from tests):**

```python
def _terminate_process(process: subprocess.Popen) -> None:
    """Terminate subprocess with escalation strategy."""
    try:
        logger.warning(f"Terminating subprocess {process.pid}")
        process.terminate()

        # Give process time to cleanup
        for _ in range(5):
            if process.poll() is not None:
                return
            time.sleep(0.1)

        # Escalate to kill if needed
        if process.poll() is None:
            logger.warning(f"Force killing subprocess {process.pid}")
            process.kill()
            process.wait(timeout=5)

    except Exception as e:
        logger.exception(f"Error terminating process {process.pid}: {e}")

def _cleanup_processes() -> None:
    """Clean up all active processes on exit."""
    for process in _active_processes[:]:
        if process.poll() is None:  # Still running
            _terminate_process(process)
```

### Progress Tracking Implementation

**Multi-Threaded Progress Monitoring:**

```python
def _monitor_download(
    process: subprocess.Popen,
    progress_callback: Callable
) -> None:
    """Monitor s5cmd output for progress updates."""

    total_files = 0
    completed_files = 0
    failed_files = 0
    current_file = None

    # Parse s5cmd output
    for line in process.stdout:
        if "ERROR" in line:
            failed_files += 1
            logger.error(f"Download error: {line}")

        elif "cp s3://" in line:
            # Extract file being processed
            match = re.search(r"cp s3://[^\s]+ ([^\s]+)", line)
            if match:
                current_file = match.group(1)

        elif "OK" in line:
            completed_files += 1

            if progress_callback:
                progress = DownloadProgress(
                    total_files=total_files,
                    completed_files=completed_files,
                    failed_files=failed_files,
                    current_file=current_file,
                    throughput_mbps=self._calculate_throughput()
                )
                progress_callback(progress)

    # Check final status
    return_code = process.wait()
    if return_code != 0:
        raise RuntimeError(f"s5cmd failed with code {return_code}")
```

## Cross-Module Integration

### Platform Module Coordination

The dataset module works with [platform module](../platform/CLAUDE.md):

- Uses platform authentication for private datasets
- Shares correlation IDs for tracing downloads
- Leverages platform's error handling patterns

### Application Module Usage

The [application module](../application/CLAUDE.md) uses datasets for:

- Bulk WSI file acquisition for batch processing
- Training data preparation for ML models
- Reference dataset management

### WSI Module Integration

Coordinates with [WSI module](../wsi/CLAUDE.md) for:

- Validating downloaded DICOM files
- Converting between imaging formats
- Generating dataset previews

## Usage Patterns & Best Practices

### Basic Dataset Download

```python
from aignostics.dataset import Service, IDCClient

service = Service()
idc = IDCClient()

# Browse available collections
collections = idc.get_collections()
for collection in collections:
    print(f"{collection.id}: {collection.subjects} subjects")

# Download specific collection
def progress_callback(progress):
    print(f"Downloaded: {progress.completed_files}/{progress.total_files}")
    print(f"Throughput: {progress.throughput_mbps:.1f} MB/s")

service.download_dataset(
    collection_id="TCGA-LUAD",
    output_dir=Path("./datasets/lung"),
    progress_callback=progress_callback,
    filters={
        "Modality": "SM",  # Slide Microscopy only
        "BodyPartExamined": "LUNG"
    }
)
```

### Advanced Patterns

**Incremental Download with Resume:**

```python
def download_with_resume(collection_id: str, output_dir: Path):
    """Download dataset with resume capability."""

    # Check existing files
    existing_files = set(output_dir.rglob("*.dcm"))

    # Get manifest
    idc = IDCClient()
    manifest = idc.get_download_manifest(collection_id)

    # Filter already downloaded
    to_download = [
        item for item in manifest
        if Path(item['target_path']) not in existing_files
    ]

    logger.info(f"Resuming download: {len(to_download)} files remaining")

    # Download remaining files
    service.download_filtered(to_download, output_dir)
```

**Parallel Collection Downloads:**

```python
from concurrent.futures import ProcessPoolExecutor

def download_multiple_collections(collections: list[str]):
    """Download multiple collections in parallel."""

    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = {}

        for collection_id in collections:
            output_dir = Path(f"./datasets/{collection_id}")
            future = executor.submit(
                service.download_dataset,
                collection_id=collection_id,
                output_dir=output_dir
            )
            futures[future] = collection_id

        # Monitor completion
        for future in concurrent.futures.as_completed(futures):
            collection_id = futures[future]
            try:
                future.result()
                logger.info(f"Completed: {collection_id}")
            except Exception as e:
                logger.error(f"Failed {collection_id}: {e}")
```

## Testing Strategies

### Process Management Testing (from `service_test.py`)

```python
def test_cleanup_processes_terminates_running():
    """Verify subprocess cleanup on exit."""
    mock_process = MagicMock(spec=subprocess.Popen)
    mock_process.poll.return_value = None  # Still running

    _active_processes.append(mock_process)
    _cleanup_processes()

    # Verify termination sequence
    mock_process.terminate.assert_called_once()
    if mock_process.poll.return_value is None:
        mock_process.kill.assert_called_once()

def test_graceful_termination():
    """Test graceful process shutdown."""
    mock_process = MagicMock(spec=subprocess.Popen)
    mock_process.poll.side_effect = [None, 0]  # Terminates gracefully

    _terminate_process(mock_process)

    mock_process.terminate.assert_called_once()
    mock_process.kill.assert_not_called()
```

### Integration Testing

```python
@pytest.mark.docker
def test_idc_download_with_proxy():
    """Test IDC download through corporate proxy."""
    # Use squid proxy container
    # Verify proxy authentication
    # Check certificate handling
```

## Operational Requirements

### Monitoring & Observability

**Key Metrics:**

- Download throughput (MB/s, GB/hour)
- Success/failure rates by collection
- s5cmd subprocess health
- Disk space utilization
- Network bandwidth usage

**Logging Standards:**

```python
logger.info("Dataset download started", extra={
    "collection_id": collection_id,
    "estimated_size_gb": size_gb,
    "output_directory": str(output_dir),
    "filters": filters
})

logger.error("Download failed", extra={
    "collection_id": collection_id,
    "error": str(e),
    "completed_files": completed,
    "failed_files": failed,
    "duration_seconds": duration
})
```

### Performance Optimization

**Network Optimization:**

- Concurrent transfers (default: 100)
- Adaptive concurrency based on bandwidth
- Regional endpoint selection
- Connection pooling and reuse

**Storage Optimization:**

```python
# Path length validation for Windows
PATH_LENGTH_MAX = 260

def validate_path_length(path: Path) -> bool:
    """Ensure path compatibility with Windows."""
    if len(str(path)) > PATH_LENGTH_MAX:
        # Shorten path using hash
        return shorten_path(path)
    return path
```

### Error Recovery

**Automatic Retry with Exponential Backoff:**

```python
def download_with_retry(manifest_item: dict, max_retries: int = 3):
    """Download single file with retry logic."""

    for attempt in range(max_retries):
        try:
            download_file(manifest_item)
            return
        except Exception as e:
            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
            time.sleep(wait_time)

    raise RuntimeError(f"Failed after {max_retries} attempts")
```

## Common Pitfalls & Solutions

### Corporate Proxy Issues

**Problem:** SSL verification failures behind proxy

**Solution:**
```bash
export HTTPS_PROXY=http://proxy:8080
export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt
export AWS_CA_BUNDLE=/path/to/ca-bundle.crt
```

### Large Dataset Storage

**Problem:** Running out of disk space mid-download

**Solution:**
```python
def check_disk_space(required_gb: float, path: Path):
    """Pre-flight disk space check."""
    free_gb = shutil.disk_usage(path).free / (1024**3)
    if free_gb < required_gb * 1.1:  # 10% buffer
        raise IOError(f"Insufficient space: {free_gb:.1f}GB < {required_gb:.1f}GB")
```

### Windows Path Length

**Problem:** Path too long errors on Windows

**Solution:** Use layout with shorter paths or enable long path support

## Module Dependencies

### Internal Dependencies

- `platform` - Authentication and API client
- `utils` - Logging and process utilities
- `wsi` - Image validation

### External Dependencies

- `s5cmd` - High-performance S3 client
- `idc-index-data` - IDC metadata
- `pydicom` - DICOM file handling
- `duckdb` - Local dataset indexing

### Modified Third-Party

- `third_party/idc_index.py` - Enhanced IDC client with proxy support

## Future Enhancements

1. **Streaming Downloads**: Process files during download
2. **Smart Caching**: Local dataset cache management
3. **Bandwidth Throttling**: Rate limiting for shared networks
4. **Compression**: On-the-fly compression for storage efficiency
5. **P2P Transfer**: Distributed dataset sharing within organization

## Performance Considerations

**Optimization Targets:**

- Parallel downloads using s5cmd with configurable concurrency
- Chunked transfers for large files
- Automatic retry on failures
- Efficient memory usage through streaming

---

*This module enables high-throughput downloads of cancer imaging datasets from public repositories.*
