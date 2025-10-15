# CLAUDE.md - System Module

This file provides comprehensive guidance to Claude Code and human engineers when working with the `system` module in this repository.

## Module Overview

The system module provides system-level utilities, diagnostics, and health monitoring for the Aignostics Platform, serving as the diagnostic and monitoring foundation for the SDK.

### Core Responsibilities

- **System Information**: Platform detection, version info, environment variables
- **Health Monitoring**: Comprehensive health checks aggregating status from ALL SDK modules
- **Proxy Configuration**: Corporate proxy setup and testing utilities
- **Exception Handling**: Centralized exception definitions for the SDK
- **API Version Management**: Track and report API compatibility

### User Interfaces

**CLI Commands (`_cli.py`):**

- `system health` - Display health status of all SDK components (JSON/YAML output)
- `system info` - Show system information and environment (with optional secrets masking)
- `system serve` - Start web server for GUI (when NiceGUI installed)
- `system proxy-request` - Test proxy configuration (diagnostic utility)

**GUI Component (`_gui.py`):**

- System dashboard with health status
- Environment information display
- Module dependency visualization
- Real-time health monitoring

**Service Layer (`_service.py`):**

Core system operations and diagnostics:
- Health aggregation from **ALL modules** via dynamic service discovery
- System information collection (platform, Python version, packages)
- Environment detection (proxy settings, environment variables)
- Monitors every module implementing `BaseService` (platform, application, wsi, dataset, bucket, gui, notebook, qupath, utils)

## Architecture & Design Patterns

### Health Check Aggregation Pattern

The system module's health check aggregates status from **ALL modules** in the SDK by discovering and querying every service that inherits from `BaseService`:

```python
def health(self) -> Health:
    """Aggregate health from ALL SDK modules dynamically."""

    from aignostics.utils import locate_implementations, BaseService

    components = {}

    # Discover ALL service implementations in the SDK
    all_services = locate_implementations(BaseService)

    # Check health of EVERY discovered module
    for service_class in all_services:
        module_name = service_class.__module__.split('.')[-2]  # Extract module name
        try:
            service_instance = service_class()
            components[module_name] = service_instance.health()
        except Exception as e:
            components[module_name] = Health(
                status=Health.Code.DOWN,
                reason=str(e)
            )

    # Determine overall status based on ALL modules
    overall = Health.Code.UP if all(
        c.status == Health.Code.UP for c in components.values()
    ) else Health.Code.DOWN

    return Health(status=overall, components=components)
```

### Exception Hierarchy (`_exceptions.py`)

```python
class AignosticsException(Exception):
    """Base exception for all SDK errors."""
    pass

class AuthenticationError(AignosticsException):
    """Authentication/authorization failures."""
    pass

class ConfigurationError(AignosticsException):
    """Configuration/settings errors."""
    pass

class NetworkError(AignosticsException):
    """Network/connectivity issues."""
    pass
```

## Critical Implementation Details

### System Information Collection

**Platform Detection:**

```python
def info(self, include_environ: bool = False, mask_secrets: bool = True) -> dict:
    """Collect comprehensive system information."""

    info = {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version,
            "python_implementation": platform.python_implementation()
        },
        "aignostics": {
            "version": __version__,
            "api_versions": API_VERSIONS,
            "modules": self._get_installed_modules(),
            "extras": self._get_installed_extras()
        },
        "runtime": {
            "cwd": os.getcwd(),
            "user": getpass.getuser(),
            "home": str(Path.home()),
            "data_dir": str(get_user_data_directory())
        }
    }

    if include_environ:
        info["environment"] = self._get_environment(mask_secrets)

    return info
```

**Secret Masking Pattern:**

```python
SENSITIVE_PATTERNS = [
    r".*TOKEN.*",
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*API_KEY.*",
    r".*PRIVATE.*"
]

def _mask_value(key: str, value: str, mask_secrets: bool) -> str:
    """Mask sensitive values based on key patterns."""

    if not mask_secrets:
        return value

    for pattern in SENSITIVE_PATTERNS:
        if re.match(pattern, key, re.IGNORECASE):
            return "***MASKED***"

    return value
```

### Proxy Configuration Support

**Proxy Testing Command:**

```python
@cli.command("proxy-request")
def proxy_request(
    url: str,
    proxy_host: str = HTTP_PROXY_DEFAULT_HOST,
    proxy_port: int = HTTP_PROXY_DEFAULT_PORT,
    proxy_scheme: str = HTTP_PROXY_DEFAULT_SCHEME
) -> None:
    """Test HTTP request through proxy."""

    proxies = {
        "http": f"{proxy_scheme}://{proxy_host}:{proxy_port}",
        "https": f"{proxy_scheme}://{proxy_host}:{proxy_port}"
    }

    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        console.print(f"✓ Success: {response.status_code}")
        console.print(f"Headers: {dict(response.headers)}")
    except Exception as e:
        console.print(f"✗ Failed: {e}", style="error")
        sys.exit(1)
```

### Output Format Flexibility

```python
class OutputFormat(StrEnum):
    """Supported output formats."""
    YAML = "yaml"
    JSON = "json"

def format_output(data: Any, format: OutputFormat) -> str:
    """Format data for output."""

    match format:
        case OutputFormat.JSON:
            return json.dumps(data, indent=2)
        case OutputFormat.YAML:
            return yaml.dump(data, default_flow_style=False, width=80)
```

## Usage Patterns

### Basic Health Check

```python
from aignostics.system import Service

service = Service()

# Get health status
health = service.health()
print(f"System status: {health.status}")

# Check specific component
platform_health = health.components.get("platform")
if platform_health.status != Health.Code.UP:
    print(f"Platform issue: {platform_health.reason}")
```

### System Information Gathering

```python
# Get full system info
info = service.info(include_environ=True, mask_secrets=True)

# Check Python version
python_version = info["platform"]["python_version"]

# Check installed modules
modules = info["aignostics"]["modules"]
print(f"Installed modules: {', '.join(modules)}")

# Check API compatibility
api_versions = info["aignostics"]["api_versions"]
```

### CLI Usage Examples

```bash
# Check system health
aignostics system health

# Get system info in YAML format
aignostics system info --output-format yaml

# Include environment variables (with secrets masked)
aignostics system info --include-environ

# Test proxy configuration
aignostics system proxy-request https://api.aignostics.com \
    --proxy-host proxy.company.com \
    --proxy-port 8080

# Start GUI server
aignostics system serve --port 8000 --open-browser
```

## Dependencies & Integration

### Internal Dependencies

- `utils` - Base service, logging, console output
- `constants` - API versions, system constants
- All SDK modules (for health aggregation)

### External Dependencies

- `typer` - CLI framework
- `yaml` - YAML output formatting
- `requests` - HTTP proxy testing
- `nicegui` - GUI interface (optional)

### Integration Points

- **All Modules**: Aggregates health status from every SDK module
- **Platform Module**: Uses authentication status in health checks
- **GUI Module**: Provides system dashboard in main launchpad

## Operational Requirements

### Monitoring & Observability

**Key Metrics:**

- Overall SDK health status
- Per-module health status
- API version compatibility
- Python version compatibility
- Network connectivity status

**Health Check Response Structure:**

```json
{
  "status": "UP",
  "components": {
    "platform": {
      "status": "UP"
    },
    "application": {
      "status": "UP"
    },
    "wsi": {
      "status": "DOWN",
      "reason": "OpenSlide not installed"
    }
  }
}
```

### Environment Detection

```python
# Detects various runtime environments
def detect_environment() -> dict:
    """Detect runtime environment."""

    return {
        "is_docker": Path("/.dockerenv").exists(),
        "is_kubernetes": Path("/var/run/secrets/kubernetes.io").exists(),
        "is_github_actions": os.getenv("GITHUB_ACTIONS") == "true",
        "is_gitlab_ci": os.getenv("GITLAB_CI") == "true",
        "is_jenkins": os.getenv("JENKINS_URL") is not None,
        "is_notebook": any(key.startswith("JUPYTER") for key in os.environ),
        "is_vscode": os.getenv("VSCODE_PID") is not None
    }
```

## Common Pitfalls & Solutions

### Missing Optional Dependencies

**Problem:** GUI commands fail when NiceGUI not installed

**Solution:**
```python
if find_spec("nicegui"):
    # Register GUI commands
    @cli.command("serve")
    def serve():
        # ...
else:
    # CLI-only mode
    logger.debug("NiceGUI not installed, GUI features disabled")
```

### Health Check Timeouts

**Problem:** Health checks timeout with slow modules

**Solution:**
```python
def health_with_timeout(module_name: str, timeout: float = 5.0) -> Health:
    """Health check with timeout."""

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(get_module_health, module_name)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            return Health(
                status=Health.Code.DOWN,
                reason=f"Health check timed out after {timeout}s"
            )
```

### Circular Import Issues

**Problem:** System imports cause circular dependencies

**Solution:**
```python
# Lazy import pattern
def get_module_service(module_name: str):
    """Lazy import to avoid circular dependencies."""
    from importlib import import_module
    module = import_module(f"aignostics.{module_name}")
    return module.Service()
```

## Testing Strategies

### Unit Testing

```python
def test_health_aggregation():
    """Test health aggregates from all modules."""
    service = Service()
    health = service.health()

    assert health.status in [Health.Code.UP, Health.Code.DOWN]
    assert "platform" in health.components
    assert isinstance(health.components, dict)

def test_secret_masking():
    """Test sensitive values are masked."""
    service = Service()
    info = service.info(include_environ=True, mask_secrets=True)

    # Set test secret
    os.environ["TEST_SECRET_KEY"] = "sensitive"

    env_info = info.get("environment", {})
    assert env_info.get("TEST_SECRET_KEY") == "***MASKED***"
```

### CLI Testing

```python
def test_cli_health_command():
    """Test health CLI command."""
    from typer.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(cli, ["health", "--output-format", "json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "status" in data
    assert "components" in data
```

## Development Guidelines

### Adding New Health Checks

1. Implement health method in module service
2. Follow Health model structure
3. Include meaningful reason on failure
4. Add to system aggregation

### Extending System Information

```python
def add_custom_info(info: dict) -> dict:
    """Add custom system information."""

    info["custom"] = {
        "gpu_available": torch.cuda.is_available() if find_spec("torch") else False,
        "memory_gb": psutil.virtual_memory().total / (1024**3),
        "cpu_count": os.cpu_count(),
        "disk_usage": shutil.disk_usage("/").used / shutil.disk_usage("/").total
    }

    return info
```

## Performance Notes

### Optimization Strategies

1. **Parallel Health Checks**: Run module health checks concurrently
2. **Caching**: Cache system info for repeated calls
3. **Lazy Loading**: Import modules only when needed
4. **Timeout Guards**: Prevent hanging on slow health checks

---

*This module serves as the diagnostic and monitoring foundation for the Aignostics SDK, providing comprehensive system information and health monitoring across all components.*
