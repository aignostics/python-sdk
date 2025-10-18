# CLAUDE.md

This file provides comprehensive guidance to Claude Code (claude.ai/code) when working with the Aignostics Python SDK repository.

## You do raise the bar, always

It is your goal to enable the contributor while insisting on highest standards at all times:

* Fully read, understand and follow this CLAUDE.md and **ALL** recursively referenced documents herein for guidance on style and conventions.
* In case of doubt apply best practices of enterprise grade software engineering.
* On every review you make or code you contribute raise the bar on engineering and operational excellence in this repository
* Do web research on any libraries, frameworks, principles or tools you are not familiar with.

If you want to execute and verify code yourself:

* uv, python and further development dependencies are already installed.
* Use `uv sync --all-extras` to install any missing dependencies for your branch.
* Use `uv run pytest ...` to run tests.
* Use `uv run aignostics ...` to run the CLI and commands.
* Use `make lint` to check code style and types.
* Use `make test_unit` to run the unit test suite.
* Use `make test_integration` to run the integration test suite.
* Use `make test_e2e` to run the end-to-end (e2e) test suite.
* Use `make audit` to run security audits of 3rd party dependencies and check compliance with our license policy.

If you write code yourself, it is a strict requirement to validate your work on completion before you call it done:

* Linting must pass.
* The unit, integration and e2e test suites must pass.
* Auditing must pass.

If you you are creating a pull request yourself:

* Add a label skip:test_long_running, to skip running long running tests. This is important because some tests in this repository are marked as long_running and can take a significant amount of time to complete. By adding this label, you help ensure that the CI pipeline runs efficiently and avoids unnecessary delays.

## Module Documentation Index

Every module has detailed CLAUDE.md documentation. For module-specific guidance, see:

* [src/aignostics/CLAUDE.md](src/aignostics/CLAUDE.md) - **Module index and architecture overview**
* [src/aignostics/platform/CLAUDE.md](src/aignostics/platform/CLAUDE.md) - Authentication and API client
* [src/aignostics/application/CLAUDE.md](src/aignostics/application/CLAUDE.md) - Application run orchestration
* [src/aignostics/wsi/CLAUDE.md](src/aignostics/wsi/CLAUDE.md) - Whole slide image processing
* [src/aignostics/dataset/CLAUDE.md](src/aignostics/dataset/CLAUDE.md) - Dataset operations
* [src/aignostics/bucket/CLAUDE.md](src/aignostics/bucket/CLAUDE.md) - Cloud storage management
* [src/aignostics/utils/CLAUDE.md](src/aignostics/utils/CLAUDE.md) - Core infrastructure
* [src/aignostics/gui/CLAUDE.md](src/aignostics/gui/CLAUDE.md) - Desktop interface
* [src/aignostics/notebook/CLAUDE.md](src/aignostics/notebook/CLAUDE.md) - Marimo notebook integration
* [src/aignostics/qupath/CLAUDE.md](src/aignostics/qupath/CLAUDE.md) - QuPath bioimage analysis
* [src/aignostics/system/CLAUDE.md](src/aignostics/system/CLAUDE.md) - System diagnostics
* [tests/CLAUDE.md](tests/CLAUDE.md) - Test suite documentation

## Development Commands

**Primary workflow commands (use these):**

```bash
make install          # Install dev dependencies + pre-commit hooks
make all             # Run lint, test, docs, audit (full CI pipeline)
make test            # Run tests with coverage
make test 3.12       # Run tests on specific Python version
make lint            # Ruff formatting + linting + MyPy type checking
make docs            # Build Sphinx documentation
make audit           # Security and license compliance checks
```

**Package management:**

* Uses `uv` as package manager (not pip/poetry)
* Run `uv sync` to install dependencies
* Run `uv add <package>` to add new dependencies

**Testing:**

* Pytest with 85% minimum coverage requirement
* Use `pytest tests/path/to/test.py::test_function` for single tests
* Docker integration tests available with `make test-docker`
* Test markers available: `sequential`, `long_running`, `scheduled`, `docker`, `skip_with_act`
* Special test commands: `make test_sequential`, `make test_long_running`, `make test_scheduled`

## Software Architecture Principles

This SDK follows a **Modulith Architecture** with these core principles:

### 1. Modulith Design

* **Single deployable unit** with well-defined module boundaries
* **High cohesion** within modules, **loose coupling** between modules
* **Each module is self-contained** with its own service, configuration, and optional UI
* **Clear dependency hierarchy** preventing circular dependencies

### 2. Dependency Injection & Service Discovery

* **No decorators or annotations** - uses runtime service discovery
* **Dynamic module loading** via `locate_implementations(BaseService)`
* **All services inherit from `BaseService`** providing standard `health()` and `info()` interfaces
* **Singleton pattern** for service instances within the DI container

### 3. Presentation Layer Pattern

Each module can have **zero, one, or both** presentation layers:

* **CLI (_cli.py)**: Text-based interface using Typer framework
* **GUI (_gui.py)**: Graphical interface using NiceGUI framework
* **Both layers depend on the Service layer**, never on each other

### Module Architecture Pattern

Each module follows a consistent three-layer architecture:

```text
Module/
├── _service.py     # Business logic layer (core operations)
├── _cli.py         # CLI presentation layer (Typer commands)
├── _gui.py         # GUI presentation layer (NiceGUI interface)
├── _settings.py    # Configuration (Pydantic models)
└── CLAUDE.md       # Comprehensive documentation
```

**Presentation layers (CLI/GUI) depend on Service layer:**

```text
┌─────────────┐     ┌─────────────┐
│  CLI Layer  │     │  GUI Layer  │
│  (_cli.py)  │     │  (_gui.py)  │
└──────┬──────┘     └──────┬──────┘
       └──────────┬─────────┘
                  ↓
         ┌────────────────┐
         │  Service Layer │
         │ (_service.py)  │
         └────────────────┘
```

## Core Modules & Dependencies

### Foundation Layer

**utils** - Infrastructure module providing:

* Dependency injection container (`locate_implementations`, `locate_subclasses`)
* Structured logging (`get_logger`)
* Settings management (Pydantic-based)
* Health check framework (`BaseService`, `Health`)

### API Layer

**platform** - Authentication and API gateway:

* OAuth 2.0 device flow authentication
* Token lifecycle management
* Resource clients (applications, runs)
* *Dependencies*: `utils`

### Domain Modules

**application** - ML application orchestration:

* Run lifecycle management
* Version control (semver)
* File upload/download with progress
* *Dependencies*: `platform`, `bucket`, `wsi`, `utils`, `qupath` (optional)

**wsi** - Whole slide image processing:

* Multi-format support (OpenSlide, PyDICOM)
* Thumbnail generation
* Tile extraction
* *Dependencies*: `utils`

**dataset** - Large-scale data operations:

* IDC (Imaging Data Commons) integration
* High-performance downloads (s5cmd)
* *Dependencies*: `platform`, `utils`

**bucket** - Cloud storage abstraction:

* S3/GCS unified interface
* Signed URL generation
* Chunked transfers
* *Dependencies*: `platform`, `utils`

### Integration Modules

**qupath** - Bioimage analysis platform:

* QuPath installation and lifecycle
* Project management
* Script execution
* *Dependencies*: `utils`, requires `ijson`

**notebook** - Interactive analysis:

* Marimo notebook server
* Process management
* *Dependencies*: `utils`, requires `marimo`

### System Modules

**system** - Diagnostics and monitoring:

* **Health aggregation from ALL modules** via `BaseService.health()`
* Comprehensive system information
* Environment detection and diagnostics
* *Dependencies*: All modules (queries health status from every service)

**gui** - Desktop launchpad:

* Aggregates all module GUIs
* Unified desktop interface
* *Dependencies*: All modules with GUI components

### Dependency Graph

```text
                    ┌──────────────┐
                    │     gui      │ (GUI Aggregator)
                    └──────┬───────┘
                           │ uses all GUI modules
        ┌──────────────────┴──────────────────┐
        │                                      │
   ┌────┴─────┐                         ┌─────┴────┐
   │  system  │                         │ notebook │
   └────┬─────┘                         └─────┬────┘
        │ monitors health of ALL modules       │
   ┌────┴─────────────────────────────────────┴────┐
   │                                                │
   │            ┌──────────────┐                   │
   │            │ application  │                   │
   │            └──────┬───────┘                   │
   │                   │ uses                      │
   │    ┌──────┬───────┼────────┬──────────┐      │
   │    ↓      ↓       ↓        ↓          ↓      │
   │ ┌─────┐┌──────┐┌──────┐┌──────┐┌─────────┐  │
   │ │ wsi ││dataset││bucket││qupath││platform │  │
   │ └──┬──┘└───┬──┘└───┬──┘└───┬──┘└────┬────┘  │
   │    │       │       │       │         │       │
   │    └───────┴───────┴───────┴─────────┘       │
   │                        │                      │
   │                    ┌───┴────┐                 │
   └────────────────────│  utils │─────────────────┘
                        └────────┘
                      (Foundation Layer)

Note: The system module collects health status from ALL modules
in the SDK by calling their health() methods, providing a
comprehensive view of the entire SDK's operational status.
```

### Module Capabilities Matrix

| Module | Service | CLI | GUI | Purpose |
|--------|---------|-----|-----|---------|
| **platform** | ✅ | ✅ | ❌ | Authentication & API client |
| **application** | ✅ | ✅ | ✅ | ML application orchestration |
| **wsi** | ✅ | ✅ | ✅ | Medical image processing |
| **dataset** | ✅ | ✅ | ✅ | Dataset downloads |
| **bucket** | ✅ | ✅ | ✅ | Cloud storage |
| **utils** | ✅ | ❌ | ❌ | Infrastructure |
| **gui** | ✅ | ❌ | ✅ | Desktop launchpad |
| **notebook** | ✅ | ❌ | ✅ | Marimo notebooks |
| **qupath** | ✅ | ✅ | ✅ | QuPath integration |
| **system** | ✅ | ✅ | ✅ | Diagnostics |

## SDK Usage Patterns

### Client Library Usage

```python
from aignostics import platform

# Main SDK entry point
client = platform.Client()

# List applications
for app in client.applications.list():
    print(app.application_id)

# Submit run
run = client.runs.create(
    application_id="heta",
    files=["slide.svs"]
)
```

### Service Discovery Pattern

```python
from aignostics.utils import locate_implementations, BaseService

# Find all service implementations dynamically
services = locate_implementations(BaseService)

# Each service provides health and info
for service_class in services:
    service = service_class()
    health = service.health()
    info = service.info(mask_secrets=True)
```

### CLI Usage

```bash
# Authentication
aignostics user login

# Application operations
aignostics application list
aignostics application run submit --application-id heta --files "*.svs"

# Dataset downloads
aignostics dataset idc download --collection-id TCGA-LUAD

# WSI processing
aignostics wsi inspect slide.svs

# QuPath integration
aignostics qupath install
aignostics qupath launch --project my_project.qpproj

# System diagnostics
aignostics system health
```

### GUI Launch

```bash
# Install with GUI support
pip install "aignostics[gui]"

# Launch desktop interface
aignostics gui

# Or with uvx
uvx --with "aignostics[gui]" aignostics gui
```

## Code Standards

**Type Checking:**

* MyPy strict mode enforced
* All public APIs must have type hints
* Use `from __future__ import annotations` for forward references

**Code Style:**

* Ruff handles all formatting/linting (Black-compatible)
* 120 character line limit
* Google-style docstrings required for public APIs

**Import Organization:**

* Standard library imports first
* Third-party imports second
* Local imports last
* Use relative imports within modules (`from ._service import Service`)

**Error Handling:**

* Custom exceptions in `system/_exceptions.py`
* Use structured logging with correlation IDs
* HTTP errors wrapped in domain-specific exceptions

**Security:**

* OAuth-based authentication via `platform/_authentication.py`
* No secrets/tokens in code or commits
* Signed URLs for data transfer
* Sensitive data masking in logs and info outputs

## Medical Domain Context

This is a computational pathology SDK working with:

* **DICOM medical imaging standards** - Medical image format
* **Whole slide images (WSI)** - Gigapixel-scale pathology images
* **IDC (Imaging Data Commons)** - National Cancer Institute data repository
* **QuPath** - Leading bioimage analysis platform
* **Machine learning inference** - AI/ML model execution on medical data
* **HIPAA compliance** - Medical data privacy requirements

**WSI Processing:**

* OpenSlide for standard formats (.svs, .tiff, .ndpi)
* PyDICOM for DICOM files
* Support for multi-resolution pyramidal images
* Tile-based processing for memory efficiency

## Build System

**Project structure:**

```text
aignostics-python-sdk/
├── src/aignostics/      # Source code
├── tests/               # Test suite
├── docs/                # Sphinx documentation
├── pyproject.toml       # Project configuration
├── Makefile            # Build commands
└── CLAUDE.md           # This file
```

**Build configuration:**

* `pyproject.toml` - Package metadata and dependencies
* `ruff.toml` - Linting and formatting rules
* `.pre-commit-config.yaml` - Git hooks
* `cliff.toml` - Changelog generation

## Development Guidelines

### Adding New Modules

1. Create module directory in `src/aignostics/`
2. Implement service layer (`_service.py`) inheriting from `BaseService`
3. Add CLI commands (`_cli.py`) using Typer
4. Add GUI interface (`_gui.py`) using NiceGUI (optional)
5. Create settings (`_settings.py`) with Pydantic
6. Write comprehensive `CLAUDE.md` documentation
7. Add tests in `tests/aignostics/<module>/`
8. Update module index in `src/aignostics/CLAUDE.md`

### Service Implementation Pattern

```python
from aignostics.utils import BaseService, Health

class Service(BaseService):
    """Module service implementation."""

    def health(self) -> Health:
        """Health check implementation."""
        return Health(status=Health.Code.UP)

    def info(self, mask_secrets: bool = True) -> dict:
        """Service information."""
        return {"version": "1.0.0"}
```

### CLI Pattern

```python
import typer
from ._service import Service

cli = typer.Typer(name="module", help="Module description")

@cli.command("action")
def action_command(param: str):
    """Action description."""
    service = Service()
    result = service.perform_action(param)
    console.print(result)
```

### Testing Requirements

* Minimum 85% code coverage
* Unit tests for all public methods
* Integration tests for CLI commands
* Mock external dependencies
* Use fixtures from `conftest.py`

## Important Notes

### Module Loading

Some modules have conditional loading based on dependencies:

* **qupath** requires `ijson` package
* **gui** requires `nicegui` package
* **notebook** requires `marimo` package

### Platform Authentication

* Token cached in `~/.aignostics/token.json`
* Format: `token:expiry_timestamp`
* 5-minute refresh buffer before expiry
* OAuth 2.0 device flow

### Performance Considerations

* Chunked uploads/downloads (1MB/10MB chunks)
* Streaming for large files
* Process management for subprocesses
* Memory-efficient WSI tile processing

### Common Pitfalls

1. **Import errors**: Check optional dependencies
2. **Token expiry**: Force refresh with `remove_cached_token()`
3. **Large files**: Use streaming and chunking
4. **WSI memory**: Process in tiles, not full image
5. **Platform differences**: Check Windows path lengths

---

*This documentation provides comprehensive guidance for working with the Aignostics Python SDK. Each module has detailed CLAUDE.md files with implementation specifics, usage examples, and best practices.*
