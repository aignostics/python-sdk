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
