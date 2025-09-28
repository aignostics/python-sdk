# CLAUDE.md - Notebook Module

This file provides comprehensive guidance to Claude Code and human engineers when working with the `notebook` module in this repository.

## Module Overview

The notebook module provides interactive Marimo notebook functionality for the Aignostics Platform, enabling data exploration and analysis in a reactive notebook environment.

### Core Responsibilities

- **Marimo Integration**: Embedded Marimo notebook server management
- **Process Management**: Lifecycle control of notebook server subprocess
- **Health Monitoring**: Server health checks and status reporting
- **Interactive Analysis**: Reactive notebook environment for data exploration

### User Interfaces

**Service Layer (`_service.py`):**

The service manages the Marimo notebook server:
- Server lifecycle (start/stop/restart)
- Health monitoring
- Process management with graceful shutdown

**GUI Component (`_gui.py`):**

- Embedded notebook interface within the main GUI
- Server status display
- Launch controls

**No CLI**: This module is GUI-only for interactive use

## Architecture & Design Patterns

### Process Management Pattern

```python
class _Runner:
    """Manages Marimo server subprocess."""

    _marimo_server: Popen[str] | None = None
    _monitor_thread: Thread | None = None
    _server_ready: Event = Event()

    def __init__(self):
        atexit.register(self.stop)  # Cleanup on exit
```

### Server Lifecycle

```
Start → Monitor Output → Extract URL → Ready
                ↓
            Health Check
                ↓
        Stop → Cleanup
```

## Critical Implementation Details

### Marimo Server Management

**Server Startup:**

```python
MARIMO_SERVER_STARTUP_TIMEOUT = 60  # seconds

def start(self, notebook_path: Path, host: str, port: int):
    """Start Marimo server subprocess."""

    cmd = [
        sys.executable, "-m", "marimo",
        "run", str(notebook_path),
        "--host", host,
        "--port", str(port),
        "--headless"
    ]

    self._marimo_server = Popen(
        cmd,
        stdout=PIPE,
        stderr=STDOUT,
        text=True,
        creationflags=SUBPROCESS_CREATION_FLAGS
    )

    # Monitor thread watches for server URL
    self._monitor_thread = Thread(
        target=self._monitor_output,
        daemon=True
    )
```

**URL Extraction Pattern:**

```python
def _monitor_output(self):
    """Monitor Marimo output for server URL."""

    url_pattern = r"http://\S+:\d+"

    for line in self._marimo_server.stdout:
        self._output += line

        if match := re.search(url_pattern, line):
            self._server_url = match.group()
            self._server_ready.set()
```

### Health Monitoring

```python
def health(self) -> Health:
    """Check server and monitor thread health."""

    components = {
        "marimo_server": Health(
            status=Health.Code.UP if self.is_marimo_server_running() else Health.Code.DOWN
        ),
        "monitor_thread": Health(
            status=Health.Code.UP if self.is_monitor_thread_alive() else Health.Code.DOWN
        )
    }

    return Health(status=Health.Code.UP, components=components)
```

## Usage Patterns

### Starting a Notebook Session

```python
from aignostics.notebook import Service
from pathlib import Path

service = Service()

# Start Marimo server
notebook = Path("analysis.marimo.py")
server_url = service.start_notebook(
    notebook_path=notebook,
    host="127.0.0.1",
    port=8080
)

# Server URL available after startup
print(f"Notebook running at: {server_url}")

# Check health
health = service.health()
print(f"Server status: {health.status}")

# Stop when done
service.stop_notebook()
```

### Integration with GUI

The notebook module integrates with the main GUI launchpad:

```python
# In GUI context
from aignostics.notebook._gui import create_notebook_interface

def setup_notebook_tab(ui):
    """Add notebook tab to GUI."""

    with ui.tab("Notebook"):
        create_notebook_interface()
```

## Dependencies & Integration

### Internal Dependencies

- `utils` - Base service, logging, subprocess flags
- `constants` - Default notebook configuration

### External Dependencies

- `marimo` - Reactive notebook framework (required)

### Integration Points

- **GUI Module**: Embedded in main launchpad interface
- **Application Module**: Can launch notebooks for result analysis
- **Dataset Module**: Interactive data exploration after downloads

## Operational Requirements

### Process Management

- **Startup timeout**: 60 seconds
- **Graceful shutdown**: Registered with `atexit`
- **Output monitoring**: Separate daemon thread
- **Resource cleanup**: Automatic on exit

### Monitoring & Observability

**Key Metrics:**

- Server startup time
- Active notebook sessions
- Memory usage per session
- CPU utilization

**Logging Patterns:**

```python
logger.info("Starting Marimo server", extra={
    "notebook": str(notebook_path),
    "host": host,
    "port": port
})

logger.warning("Server startup timeout", extra={
    "timeout": MARIMO_SERVER_STARTUP_TIMEOUT,
    "output": self._output
})
```

## Common Pitfalls & Solutions

### Port Conflicts

**Problem:** Port already in use

**Solution:**
```python
def find_free_port(start=8080, end=9000):
    """Find available port."""
    import socket
    for port in range(start, end):
        with socket.socket() as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    raise RuntimeError("No free ports")
```

### Server Startup Failures

**Problem:** Marimo server fails to start

**Solution:**
```python
# Check Marimo installation
if not find_spec("marimo"):
    raise ImportError("Marimo not installed: pip install marimo")

# Verify notebook file exists
if not notebook_path.exists():
    raise FileNotFoundError(f"Notebook not found: {notebook_path}")
```

### Zombie Processes

**Problem:** Server process not cleaned up

**Solution:**
```python
def cleanup_zombie_processes():
    """Kill any lingering Marimo processes."""
    import psutil
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'marimo' in proc.info['cmdline']:
            proc.terminate()
```

## Development Guidelines

### Adding New Notebook Templates

1. Create template in `notebooks/` directory
2. Use `.marimo.py` extension
3. Include metadata header:
   ```python
   # /// script
   # requires-python = ">=3.10"
   # dependencies = ["aignostics", "marimo", "pandas"]
   # ///
   ```

### Extending Server Management

```python
class ExtendedRunner(_Runner):
    """Extended runner with additional features."""

    def restart(self):
        """Restart server."""
        self.stop()
        self.start(self._last_notebook, self._last_host, self._last_port)

    def get_notebooks(self) -> list[Path]:
        """List available notebooks."""
        notebook_dir = get_user_data_directory() / "notebooks"
        return list(notebook_dir.glob("*.marimo.py"))
```

## Testing Strategies

### Unit Testing

```python
@pytest.fixture
def mock_marimo_server():
    """Mock Marimo subprocess."""
    with patch("subprocess.Popen") as mock:
        process = MagicMock()
        process.stdout = iter(["Starting server...", "http://localhost:8080"])
        process.poll.return_value = None
        mock.return_value = process
        yield mock

def test_server_startup(mock_marimo_server):
    """Test server starts and extracts URL."""
    service = Service()
    url = service.start_notebook(Path("test.marimo.py"))
    assert url == "http://localhost:8080"
```

### Integration Testing

```python
@pytest.mark.integration
def test_real_marimo_server():
    """Test with actual Marimo server."""
    service = Service()

    # Create test notebook
    notebook = Path("test.marimo.py")
    notebook.write_text("import marimo as mo\nmo.md('Test')")

    try:
        url = service.start_notebook(notebook)
        assert requests.get(url).status_code == 200
    finally:
        service.stop_notebook()
        notebook.unlink()
```

## Performance Notes

### Resource Usage

- **Memory**: ~100-500MB per notebook session
- **CPU**: Minimal when idle, spikes during cell execution
- **Network**: Local server only (default 127.0.0.1)

### Optimization Opportunities

1. Connection pooling for multiple notebooks
2. Shared kernel for resource efficiency
3. Notebook preloading for faster startup
4. Output caching for repeated computations

---

*This module enables interactive data analysis through reactive Marimo notebooks integrated with the Aignostics Platform.*
