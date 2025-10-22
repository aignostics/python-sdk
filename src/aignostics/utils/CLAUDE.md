# CLAUDE.md - Utils Module

This file provides guidance to Claude Code when working with the `utils` module in this repository.

## Module Overview

The utils module provides core infrastructure and shared utilities used across all other modules:

- **Dependency Injection**: Custom DI container for service management
- **Logging**: Structured logging with multiple backends (Logfire, Sentry)
- **Configuration**: Pydantic-based settings management
- **Health Checking**: Service health monitoring
- **File System**: Path utilities and data directory management
- **Process Management**: Cross-platform subprocess utilities

## Key Components

**Core Infrastructure:**

- `_di.py` - Dependency injection container with service discovery
- `_settings.py` - Settings management with Pydantic validation
- `_log.py` - Structured logging configuration
- `_health.py` - Health check framework
- `_user_agent.py` - **Enhanced user agent generation with CI/CD context** (NEW)
- `boot.py` - Application bootstrap and initialization

**System Utilities:**

- `_fs.py` - File system operations and path sanitization
- `_process.py` - Process information and subprocess utilities
- `_constants.py` - Project metadata and environment detection
- `_console.py` - Rich console interface

**Integration Services:**

- `_logfire.py` - Logfire observability integration
- `_sentry.py` - Sentry error monitoring
- `_notebook.py` - Jupyter notebook utilities
- `_gui.py` - GUI utilities and NiceGUI helpers

## Usage Patterns

**Service Discovery:**

```python
from aignostics.utils import locate_implementations, locate_subclasses
from aignostics.utils import BaseService

# Find all service implementations
services = locate_implementations(BaseService)

# Find all subclasses of a type
subclasses = locate_subclasses(BaseService)

# Services inherit from BaseService
class MyService(BaseService):
    def health(self) -> Health:
        return Health(status=Health.Code.UP)

    def info(self, mask_secrets=True) -> dict:
        return {"version": "1.0.0"}
```

**User Agent Generation:**

```python
from aignostics.utils import user_agent

# Generate enhanced user agent with CI/CD context
ua = user_agent()
# Format: {project_name}/{version} ({platform}; {pytest_test}; {github_run_url})

# Examples:
# "aignostics/1.0.0-beta.7 (darwin)"
# "aignostics/1.0.0-beta.7 (linux; tests/platform/test_auth.py::test_login)"
# "aignostics/1.0.0-beta.7 (linux; +https://github.com/org/repo/actions/runs/123)"
# "aignostics/1.0.0-beta.7 (linux; tests/.../test_e2e.py; +https://github.com/org/repo/actions/runs/456)"

# Used automatically by:
# - SDK metadata system (platform._sdk_metadata)
# - API client HTTP headers
# - Logging context
```

**Logging:**

```python
from aignostics.utils import get_logger

logger = get_logger(__name__)
logger.info("Application started", extra={"correlation_id": "123"})
```

**Settings Management:**

```python
from aignostics.utils import load_settings
from pydantic import BaseModel

class MySettings(BaseModel):
    api_url: str = "https://api.example.com"

settings = load_settings(MySettings)
```

**Health Checks:**

```python
from aignostics.utils import Health, BaseService

class MyService(BaseService):
    def health(self) -> Health:
        return Health(
            status=Health.Code.UP,
            details={"database": "connected"}
        )
```

## Technical Implementation

**User Agent System (`_user_agent.py`):**

**NEW FEATURE**: Enhanced user agent generation with automatic CI/CD context detection.

```python
def user_agent() -> str:
    """Generate user agent string for HTTP requests.

    Format: {project_name}/{version} ({platform}; {current_test}; {github_run})

    Detection:
    - Platform: sys.platform (darwin, linux, win32)
    - Pytest: PYTEST_CURRENT_TEST environment variable
    - GitHub Actions: GITHUB_RUN_ID, GITHUB_REPOSITORY environment variables

    Returns:
        str: User agent string with contextual information
    """
    current_test = os.getenv("PYTEST_CURRENT_TEST")  # e.g., "tests/test_foo.py::test_bar"
    github_run_id = os.getenv("GITHUB_RUN_ID")  # GitHub Actions workflow run ID
    github_repository = os.getenv("GITHUB_REPOSITORY")  # e.g., "owner/repo"

    optional_parts = []

    # Add test context if running under pytest
    if current_test:
        optional_parts.append(current_test)

    # Add GitHub Actions context if available
    if github_run_id and github_repository:
        github_run_url = f"+https://github.com/{github_repository}/actions/runs/{github_run_id}"
        optional_parts.append(github_run_url)

    # Build user agent
    base = f"{PROJECT_NAME}/{VERSION} ({sys.platform})"
    if optional_parts:
        return f"{base}; {'; '.join(optional_parts)}"
    return base
```

**Usage in SDK:**

1. **SDK Metadata**: Included in every run's metadata (`platform._sdk_metadata.build_sdk_metadata()`)
2. **HTTP Headers**: Set in API client configuration for all HTTP requests
3. **Logging Context**: Available for structured logging and observability
4. **Debugging**: Provides traceability from API requests back to specific tests or workflow runs

**Key Features:**

- **Automatic Context Detection**: No manual configuration required
- **CI/CD Integration**: Captures GitHub Actions workflow context with direct links to runs
- **Test Traceability**: Links API requests to specific pytest tests
- **Platform Identification**: Operating system detection for debugging platform-specific issues
- **Lightweight**: Minimal performance overhead, simple environment variable reads

**Service Discovery System:**

- Dynamic discovery of implementations and subclasses
- Automatic module loading across the package
- Caching of discovered implementations
- No decorator needed - uses class inheritance

**Structured Logging:**

- Multiple backend support (Logfire, Sentry, Console)
- Correlation ID tracking
- Structured JSON output
- Performance monitoring integration
- Error tracking and alerting

**Settings Architecture:**

- Pydantic models for type safety
- Environment variable binding
- Validation and transformation
- Sensitive data masking
- Multi-environment support

**Health Monitoring:**

- Service-level health checks
- Dependency health aggregation
- Standardized health reporting format
- Integration with monitoring systems

## File Organization

**Core Files:**

- `__init__.py` - Public API exports and module coordination
- `boot.py` - Application initialization and setup
- `_di.py` - Dependency injection implementation
- `_settings.py` - Configuration management
- `_log.py` - Logging infrastructure

**System Utilities:**

- `_fs.py` - File system operations
- `_process.py` - Process utilities
- `_constants.py` - Environment and metadata
- `_console.py` - Console interface
- `_health.py` - Health check framework

**Integration Modules:**

- `_logfire.py` - Observability platform
- `_sentry.py` - Error monitoring
- `_notebook.py` - Jupyter integration
- `_gui.py` - GUI framework utilities

## Development Notes

**Service Management:**

- Dynamic service discovery via inheritance
- Module-wide implementation scanning
- Cached discovery results for performance
- BaseService abstract class pattern

**Configuration Patterns:**

- Environment-based configuration
- Pydantic validation and transformation
- Sensitive data handling
- Development vs production settings

**Observability:**

- Structured logging with correlation IDs
- Error tracking and performance monitoring
- Health check aggregation
- Telemetry and metrics collection

**Testing Considerations:**

- Mock dependency injection for unit tests
- Isolated service testing
- Configuration override for test environments
- Health check validation
- Log output verification

**Performance Considerations:**

- Lazy service initialization
- Efficient module discovery
- Minimal overhead logging
- Optimized path operations
- Memory-efficient configuration loading

**Cross-Platform Support:**

- Windows, macOS, and Linux compatibility
- Path separator handling
- Process creation flags
- File system permissions
- Environment variable handling
