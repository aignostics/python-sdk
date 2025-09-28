# CLAUDE.md - QuPath Module

This file provides comprehensive guidance to Claude Code and human engineers when working with the `qupath` module in this repository.

## Module Overview

The qupath module provides deep integration with QuPath, the leading open-source bioimage analysis platform for digital pathology, enabling automated WSI analysis workflows and annotation management.

### Core Responsibilities

- **QuPath Installation**: Automated download and installation management
- **Application Control**: Launch, monitor, and terminate QuPath processes
- **Script Automation**: Execute Groovy scripts programmatically
- **Project Management**: Create and manage QuPath projects
- **Annotation Integration**: Add images, results, and annotations to projects
- **Progress Tracking**: Real-time monitoring of long-running operations

### User Interfaces

**CLI Commands (`_cli.py`):**

- `qupath install` - Download and install QuPath application
- `qupath launch` - Start QuPath with optional project
- `qupath processes` - List running QuPath processes
- `qupath terminate` - Stop all QuPath processes
- `qupath uninstall` - Remove QuPath installation
- `qupath add` - Add images to QuPath project
- `qupath annotate` - Annotate images with results
- `qupath inspect` - Show project information
- `qupath run-script` - Execute Groovy script

**GUI Component (`_gui.py`):**

- Installation manager with progress
- Process monitor dashboard
- Project browser interface
- Script execution panel

**Service Layer (`_service.py`):**

Core QuPath operations:

- Installation lifecycle management
- Process management with PID tracking
- Project file manipulation
- Script execution engine

## Architecture & Design Patterns

### Conditional Module Loading

```python
# Module only loads if ijson is available
from importlib.util import find_spec

has_ijson = find_spec("ijson")

if has_ijson:
    from ._service import Service, AddProgress, AnnotateProgress
else:
    # Module not available without ijson
    raise ImportError("QuPath module requires: pip install aignostics[qupath]")
```

### Process Management Pattern

```python
class Service(BaseService):
    """QuPath application lifecycle management."""

    _processes: dict[int, subprocess.Popen] = {}

    def launch_qupath(
        self,
        project: Path | None = None,
        headless: bool = False
    ) -> int:
        """Launch QuPath with process tracking."""

        cmd = [str(self.get_qupath_executable())]
        if project:
            cmd.extend(["--project", str(project)])
        if headless:
            cmd.append("--headless")

        process = subprocess.Popen(
            cmd,
            creationflags=SUBPROCESS_CREATION_FLAGS
        )

        self._processes[process.pid] = process
        return process.pid
```

### Progress Tracking Architecture

```python
class AddProgress(BaseModel):
    """Progress tracking for adding images."""

    state: AddProgressState
    total_images: int
    processed_images: int
    current_image: str | None

    @property
    def progress_normalized(self) -> float:
        if self.total_images == 0:
            return 0.0
        return self.processed_images / self.total_images

class AnnotateProgress(BaseModel):
    """Progress tracking for annotations."""

    state: AnnotateProgressState
    total_annotations: int
    processed_annotations: int
    current_annotation: str | None
```

## Critical Implementation Details

### QuPath Installation Management

**Platform-Specific Installation:**

```python
QUPATH_VERSION = "0.5.1"

def get_download_url(version: str, system: str, machine: str) -> str:
    """Get platform-specific QuPath download URL."""

    # Platform mapping
    platform_map = {
        ("Windows", "AMD64"): "win-x64",
        ("Darwin", "x86_64"): "mac-x64",
        ("Darwin", "arm64"): "mac-arm64",
        ("Linux", "x86_64"): "linux-x64"
    }

    platform_str = platform_map.get((system, machine))
    if not platform_str:
        raise UnsupportedPlatformError(f"{system} {machine} not supported")

    return f"https://github.com/qupath/qupath/releases/download/v{version}/QuPath-v{version}-{platform_str}.zip"
```

**Installation Progress Tracking:**

```python
class InstallProgressState(StrEnum):
    DOWNLOADING = "Downloading QuPath..."
    EXTRACTING = "Extracting archive..."
    CONFIGURING = "Configuring installation..."
    COMPLETED = "Installation complete"
    FAILED = "Installation failed"

def install_with_progress(
    version: str,
    path: Path,
    progress_callback: Callable[[InstallProgress], None]
) -> None:
    """Install QuPath with progress updates."""

    progress = InstallProgress(
        state=InstallProgressState.DOWNLOADING,
        total_size=get_download_size(version),
        downloaded_size=0
    )

    # Download with progress
    with requests.get(url, stream=True) as response:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
            progress.downloaded_size += len(chunk)
            progress_callback(progress)
```

### Project File Manipulation

**QuPath Project Structure:**

```python
def create_project(project_path: Path, images: list[Path]) -> None:
    """Create QuPath project with images."""

    # QuPath project structure
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "project.qpproj").write_text(
        json.dumps({
            "version": "0.5.0",
            "createTimestamp": time.time() * 1000,
            "modifyTimestamp": time.time() * 1000,
            "uri": project_path.as_uri(),
            "images": []
        })
    )

    # Add images to project
    data_dir = project_path / "data"
    for image in images:
        image_id = hashlib.md5(str(image).encode()).hexdigest()
        image_data_dir = data_dir / image_id
        image_data_dir.mkdir(parents=True, exist_ok=True)

        # Create image data.qpdata file
        (image_data_dir / "data.qpdata").write_text(
            json.dumps({
                "path": str(image),
                "id": image_id,
                "metadata": {}
            })
        )
```

### Script Execution

**Groovy Script Execution:**

```python
def run_script(
    script_path: Path,
    project: Path | None = None,
    image: Path | None = None,
    args: dict[str, Any] | None = None
) -> str:
    """Execute QuPath Groovy script."""

    cmd = [
        str(self.get_qupath_executable()),
        "script",
        str(script_path)
    ]

    if project:
        cmd.extend(["--project", str(project)])
    if image:
        cmd.extend(["--image", str(image)])
    if args:
        cmd.extend(["--args", json.dumps(args)])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout
```

## Usage Patterns

### Basic QuPath Installation and Launch

```python
from aignostics.qupath import Service

service = Service()

# Install QuPath if not already installed
if not service.is_qupath_installed():
    service.install_qupath(
        version="0.5.1",
        progress_callback=lambda p: print(f"Progress: {p.progress_normalized:.1%}")
    )

# Launch QuPath
pid = service.launch_qupath()
print(f"QuPath launched with PID: {pid}")

# List running processes
processes = service.list_processes()
for proc in processes:
    print(f"PID {proc['pid']}: {proc['status']}")

# Terminate when done
service.terminate_all()
```

### Project Creation and Image Addition

```python
from pathlib import Path

# Create project
project_path = Path("my_project.qpproj")
images = [Path("slide1.svs"), Path("slide2.svs")]

service.create_project(project_path, images)

# Add more images with progress
def on_progress(progress: AddProgress):
    print(f"Adding images: {progress.processed_images}/{progress.total_images}")

service.add_images_to_project(
    project_path,
    additional_images,
    progress_callback=on_progress
)
```

### Script Automation

```python
# Run analysis script
script = Path("cell_detection.groovy")
results = service.run_script(
    script_path=script,
    project=project_path,
    args={"threshold": 0.5, "min_area": 10}
)

print(f"Script output: {results}")
```

### CLI Usage Examples

```bash
# Install QuPath
aignostics qupath install --version 0.5.1

# Launch QuPath with project
aignostics qupath launch --project /path/to/project.qpproj

# Add images to project
aignostics qupath add --project project.qpproj --images "*.svs"

# Run analysis script
aignostics qupath run-script \
    --script cell_detection.groovy \
    --project project.qpproj \
    --args '{"threshold": 0.5}'

# List running processes
aignostics qupath processes

# Terminate all QuPath processes
aignostics qupath terminate

# Uninstall QuPath
aignostics qupath uninstall
```

## Dependencies & Integration

### Internal Dependencies

- `utils` - Base service, logging, process management
- `application` - Integration point for WSI analysis workflows
- `wsi` - Image format validation and processing

### External Dependencies

- `ijson` - Streaming JSON parser (required)
- `requests` - HTTP downloads for installation
- `nicegui` - GUI interface (optional)

### QuPath Requirements

- Java Runtime Environment (JRE) 17+
- Platform-specific QuPath binary
- Sufficient disk space (~500MB)

### Integration Points

- **Application Module**: Launches QuPath for result visualization
- **WSI Module**: Validates images before QuPath processing
- **GUI Module**: Embedded QuPath manager in launchpad

## Operational Requirements

### Installation Management

- **Default location**: `~/.aignostics/qupath/`
- **Download size**: ~200-300MB depending on platform
- **Extraction size**: ~500MB
- **Supported platforms**: Windows, macOS (Intel/ARM), Linux (x64)

### Process Management

- **Process tracking**: PID-based lifecycle management
- **Graceful shutdown**: SIGTERM with timeout, then SIGKILL
- **Orphan cleanup**: Automatic on module exit
- **Memory usage**: ~500MB-2GB depending on project size

### Monitoring & Observability

**Key Metrics:**

- Installation success/failure rate
- Process launch success rate
- Script execution time
- Project size (number of images)
- Memory usage per process

**Logging Patterns:**

```python
logger.info("Installing QuPath", extra={
    "version": version,
    "path": str(path),
    "platform": f"{system}-{machine}"
})

logger.warning("QuPath process terminated unexpectedly", extra={
    "pid": pid,
    "exit_code": process.returncode
})
```

## Common Pitfalls & Solutions

### Java Runtime Missing

**Problem:** QuPath fails to launch due to missing JRE

**Solution:**

```python
def check_java_version() -> bool:
    """Verify Java 17+ is available."""
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True
        )
        # Parse version from stderr
        return "17" in result.stderr or "18" in result.stderr
    except FileNotFoundError:
        raise RuntimeError("Java not found. Install JRE 17+")
```

### Platform Not Supported

**Problem:** ARM Linux not supported by QuPath

**Solution:**

```python
if platform.system() == "Linux" and platform.machine() in ["aarch64", "arm64"]:
    raise UnsupportedPlatformError(
        "QuPath is not available for ARM64 Linux. "
        "Consider using x86_64 emulation or container."
    )
```

### Project Lock Issues

**Problem:** Project locked by running QuPath instance

**Solution:**

```python
def unlock_project(project_path: Path) -> None:
    """Remove project lock file."""
    lock_file = project_path / ".lock"
    if lock_file.exists():
        logger.warning(f"Removing lock file: {lock_file}")
        lock_file.unlink()
```

## Testing Strategies

### Unit Testing

```python
@pytest.fixture
def mock_qupath_executable():
    """Mock QuPath executable."""
    with patch("aignostics.qupath._service.Service.get_qupath_executable") as mock:
        mock.return_value = Path("/mock/QuPath")
        yield mock

def test_launch_qupath(mock_qupath_executable):
    """Test QuPath launch."""
    service = Service()

    with patch("subprocess.Popen") as mock_popen:
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        pid = service.launch_qupath()
        assert pid == 12345
```

### Integration Testing

```python
@pytest.mark.integration
def test_full_workflow():
    """Test complete QuPath workflow."""
    service = Service()

    # Install if needed
    if not service.is_qupath_installed():
        service.install_qupath()

    # Create project
    project = Path("test_project.qpproj")
    try:
        service.create_project(project, [Path("test.svs")])

        # Launch and verify
        pid = service.launch_qupath(project)
        assert pid in [p["pid"] for p in service.list_processes()]

    finally:
        service.terminate_all()
        if project.exists():
            shutil.rmtree(project)
```

## Development Guidelines

### Adding New Script Templates

```python
SCRIPT_TEMPLATES = {
    "cell_detection": """
        import qupath.lib.images.servers.ImageServer
        def detectCells(server, params) {
            // Cell detection logic
        }
    """,
    "tissue_segmentation": """
        import qupath.lib.roi.ROIs
        def segmentTissue(server, params) {
            // Tissue segmentation logic
        }
    """
}

def get_script_template(name: str) -> str:
    """Get predefined script template."""
    return SCRIPT_TEMPLATES.get(name, "")
```

### Extending Progress Tracking

```python
class CustomProgress(BaseModel):
    """Custom progress tracker."""

    operation: str
    current_step: int
    total_steps: int
    details: dict[str, Any]

    @property
    def progress_percent(self) -> float:
        return (self.current_step / self.total_steps) * 100 if self.total_steps else 0
```

## Performance Notes

### Optimization Strategies

1. **Batch Operations**: Process multiple images in single script run
2. **Headless Mode**: Run without GUI for automation
3. **Memory Management**: Limit concurrent QuPath instances
4. **Script Caching**: Reuse compiled Groovy scripts

### Resource Limits

```python
MAX_CONCURRENT_PROCESSES = 3
MAX_PROJECT_SIZE_GB = 50
MAX_IMAGES_PER_BATCH = 100
SCRIPT_TIMEOUT_SECONDS = 3600
```

---

*This module provides comprehensive QuPath integration for automated digital pathology workflows within the Aignostics Platform.*
