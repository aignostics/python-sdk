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
* Use `make lint_fix` to automatically fix code style issues.
* Use `make test_unit` to run the unit test suite.
* Use `make test_integration` to run the integration test suite.
* Use `make test_e2e` to run the end-to-end (e2e) test suite.
* Use `make audit` to run security audits of 3rd party dependencies and check compliance with our license policy.

If you write code yourself, it is a strict requirement to validate your work on completion before you call it done:

* Linting must pass.
* The unit, integration and e2e test suites must pass.
* Auditing must pass.

If you you are creating a pull request yourself:

* Add a label skip:test:long_running, to skip running long running tests. This is important because some tests in this repository are marked as long_running and can take a significant amount of time to complete. By adding this label, you help ensure that the CI pipeline runs efficiently and avoids unnecessary delays.

## Module Documentation Index

Every module has detailed CLAUDE.md documentation. For module-specific guidance, see:

* [.github/CLAUDE.md](.github/CLAUDE.md) - **CI/CD workflows and GitHub Actions complete guide**
* [src/aignostics/CLAUDE.md](src/aignostics/CLAUDE.md) - **Module index and architecture overview**
* [src/aignostics/platform/CLAUDE.md](src/aignostics/platform/CLAUDE.md) - Authentication and API client
* [src/aignostics/application/CLAUDE.md](src/aignostics/application/CLAUDE.md) - Application run orchestration
* [src/aignostics/wsi/CLAUDE.md](src/aignostics/wsi/CLAUDE.md) - Whole slide image processing
* [src/aignostics/dataset/CLAUDE.md](src/aignostics/dataset/CLAUDE.md) - Dataset operations
* [src/aignostics/bucket/CLAUDE.md](src/aignostics/bucket/CLAUDE.md) - Cloud storage management
* [src/aignostics/utils/CLAUDE.md](src/aignostics/utils/CLAUDE.md) - Core infrastructure and MCP server
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
make test 3.14       # Run tests on specific Python version
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
* Default timeout: 10 seconds (override with `@pytest.mark.timeout(timeout=N)`)
* Use `uv run pytest tests/path/to/test.py::test_function` for single tests
* See **Testing Workflow** section below for complete marker documentation
* Special test commands: `make test_unit`, `make test_integration`, `make test_e2e`, `make test_long_running`, `make test_very_long_running`, `make test_sequential`, `make test_scheduled`

**Type Checking (NEW in v1.0.0-beta.7 - Dual Type Checkers):**

* **MyPy**: Strict mode enforced (`make lint` runs MyPy)
* **PyRight**: Basic mode with selective exclusions (`pyrightconfig.json`)
  * Excludes: tests, codegen, third_party modules, notebook, dataset, wsi
  * Mode: `basic` (less strict than MyPy for compatibility)
  * Both type checkers must pass in CI/CD
* All public APIs require type hints
* Use `from __future__ import annotations` for forward references

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
* Structured logging (via `loguru.logger`)
* Settings management (Pydantic-based)
* Health check framework (`BaseService`, `Health`)
* MCP server with auto-discovery of plugin tools (`mcp_create_server`, `mcp_run`, `mcp_list_tools`)
* GUI navigation infrastructure (`BaseNavBuilder`, `NavItem`, `NavGroup`)
* Enhanced user agent generation with CI/CD context (`user_agent`)

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
| **utils** | ✅ | ✅ | ❌ | Core Infrastructure |
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
run = client.runs.create(application_id="heta", files=["slide.svs"])
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

# MCP server (AI agent integration)
aignostics mcp run
aignostics mcp list-tools
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
* `noxfile.py` - **Enhanced with SDK metadata schema generation task** (NEW)
* `ruff.toml` - Linting and formatting rules
* `.pre-commit-config.yaml` - Git hooks
* `cliff.toml` - Changelog generation

**Noxfile Enhancements:**

The `noxfile.py` now includes automated SDK metadata schema generation:

```python
def _generate_sdk_metadata_schema(session: nox.Session) -> None:
    """Generate versioned JSON Schema for SDK metadata.

    - Calls `aignostics sdk metadata-schema` CLI command
    - Extracts schema version from $id field
    - Outputs both versioned (v0.0.1) and latest files
    - Published to docs/source/_static/
    """
```

This ensures the JSON Schema is automatically regenerated during documentation builds.

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

### SDK Metadata System (ENHANCED - Run v0.0.6, Item v0.0.3)

**Automatic Run & Item Tracking**: Every application run and item submitted through the SDK automatically includes comprehensive metadata about the execution context, with support for tags and timestamps.

**Key Features:**

* **Automatic Attachment**: SDK metadata added to every run and item without user action
* **Environment Detection**: Automatically detects script/CLI/GUI and user/test/bridge contexts
* **CI/CD Integration**: Captures GitHub Actions workflow information and pytest test context
* **User Information**: Includes authenticated user and organization details
* **Schema Validation**: Pydantic-based validation with JSON Schema (Run: v0.0.6, Item: v0.0.3)
* **Versioned Schema**: Published JSON Schema at `docs/source/_static/sdk_{run|item}_custom_metadata_schema_*.json`
* **Tags Support** (NEW): Associate runs and items with searchable tags
* **Timestamps** (NEW): Track creation and update times (`created_at`, `updated_at`)
* **Metadata Updates** (NEW): Update custom metadata via CLI and GUI
* **Item Metadata** (NEW): Separate schema for item-level metadata including platform bucket information

**What's Tracked (Run Level):**

* Submission metadata (date, interface, initiator)
* Enhanced user agent with platform and CI/CD context
* User and organization information (when authenticated)
* GitHub Actions workflow details (repository, run URL, runner info)
* Pytest test context (current test, markers)
* Workflow control flag (onboard_to_portal)
* Scheduling information (due dates, deadlines)
* Optional user notes
* **Tags** (NEW): Set of tags for filtering (`set[str]`)
* **Timestamps** (NEW): `created_at`, `updated_at`

**What's Tracked (Item Level - NEW):**

* **Platform Bucket Metadata**: Cloud storage location (bucket name, object key, signed URL)
* **Tags**: Item-level tags (`set[str]`)
* **Timestamps**: `created_at`, `updated_at`

**CLI Commands:**

```bash
# Export SDK run metadata JSON Schema
aignostics sdk metadata-schema --pretty > run_schema.json

# Update run custom metadata (including tags)
aignostics application run custom-metadata update RUN_ID \
  --custom-metadata '{"sdk": {"tags": ["experiment-1", "batch-A"]}}'

# Dump run custom metadata as JSON
aignostics application run custom-metadata dump RUN_ID --pretty

# Find runs by tags
aignostics application run list --tags experiment-1,batch-A
```

**Implementation:**

* Module: `platform._sdk_metadata`
* **Run Functions**: `build_run_sdk_metadata()`, `validate_run_sdk_metadata()`, `get_run_sdk_metadata_json_schema()`
* **Item Functions** (NEW): `build_item_sdk_metadata()`, `validate_item_sdk_metadata()`, `get_item_sdk_metadata_json_schema()`
* Integration: Automatic in `platform.resources.runs.submit()`
* User Agent: Enhanced `utils.user_agent()` with CI/CD context
* Tests: Comprehensive test suite in `tests/aignostics/platform/sdk_metadata_test.py`
* **Schema Files**: `sdk_run_custom_metadata_schema_v0.0.6.json` and `sdk_item_custom_metadata_schema_v0.0.3.json`

See `platform/CLAUDE.md` for detailed documentation.

### Operation Caching & Retry System (NEW in v1.0.0-beta.7)

**Enterprise-Grade Performance**: The SDK now implements intelligent operation caching and retry logic to ensure reliability and performance in production environments.

**Operation Caching (`platform/_operation_cache.py`):**

**Key Features:**

* **Token-Aware Caching**: Per-user cache isolation prevents data leakage
* **Configurable TTLs**: 5 minutes for stable data (apps/versions), 15 seconds for dynamic data (runs)
* **Automatic Invalidation**: All caches cleared on mutations (submit/cancel/delete)
* **Memory Efficient**: Dictionary-based storage with automatic expiration

**Cached Operations:**

* `Client.me()` - User information (5 min TTL)
* `Client.application()` / `application_version()` - Application metadata (5 min TTL)
* `Applications.list()` / `details()` - Application lists (5 min TTL)
* `Runs.details()` / `results()` / `list()` - Run data (15 sec TTL)

**Performance Impact:**

* Cache Hit: ~0.1ms (1000x faster than API call)
* Cache Miss: Standard API latency (50-500ms)
* Typical Speedup: 100-1000x for repeated reads within TTL

**Retry Logic with Exponential Backoff:**

**Key Features:**

* **Tenacity-Based**: Industry-standard retry library with exponential backoff
* **Configurable**: Per-operation retry attempts (default: 4), wait times (0.1s-60s), timeouts (30s)
* **Smart Exceptions**: Only retries transient errors (5xx, timeouts, connection issues)
* **Jitter**: Randomized wait times prevent thundering herd problem

**Retryable Exceptions:**

* ServiceException (5xx server errors)
* Urllib3TimeoutError
* PoolError (connection pool exhausted)
* IncompleteRead / ProtocolError / ProxyError

**Retry Pattern:**

```
Attempt 1: Immediate
Attempt 2: ~100ms wait
Attempt 3: ~200-400ms wait (exponential + jitter)
Attempt 4: ~400-800ms wait (capped at 60s max)
```

**Configuration:**

```bash
# Example .env configuration
AIGNOSTICS_ME_RETRY_ATTEMPTS=4
AIGNOSTICS_ME_RETRY_WAIT_MIN=0.1
AIGNOSTICS_ME_RETRY_WAIT_MAX=60.0
AIGNOSTICS_ME_TIMEOUT=30.0
AIGNOSTICS_ME_CACHE_TTL=300

AIGNOSTICS_RUN_RETRY_ATTEMPTS=4
AIGNOSTICS_RUN_TIMEOUT=30.0
AIGNOSTICS_RUN_CACHE_TTL=15
```

**Cache Control:**

```python
# Bypass cache for specific operations (useful in tests or when fresh data is required)
run = client.runs.details(run_id, nocache=True)  # Force API call
applications = client.applications.list(nocache=True)  # Bypass cache
```

**Design Decisions:**

* ✅ **Read-Only Retries**: Only safe, idempotent read operations retry
* ✅ **Global Cache Clearing**: Simple consistency model - clear everything on writes
* ✅ **Cache Bypass** (NEW): `nocache=True` parameter forces fresh API calls
* ✅ **Logging**: Warnings logged before retry sleeps for observability
* ✅ **Re-raise**: Original exception re-raised after exhausting retries

See `platform/CLAUDE.md` for implementation details and usage patterns.

### API v1.0.0-beta.7 State Models (MAJOR CHANGE)

**Breaking Change**: Complete refactoring of run, item, and artifact state management with enum-based models and termination reasons.

**New State Enums:**

* `RunState`: PENDING → PROCESSING → TERMINATED
* `ItemState`: PENDING → PROCESSING → TERMINATED
* `ArtifactState`: PENDING → PROCESSING → TERMINATED

**New Termination Reason Enums:**

* `RunTerminationReason`: ALL_ITEMS_PROCESSED, CANCELED_BY_USER, CANCELED_BY_SYSTEM
* `ItemTerminationReason`: SUCCEEDED, USER_ERROR, SYSTEM_ERROR, SKIPPED
* `ArtifactTerminationReason`: SUCCEEDED, USER_ERROR, SYSTEM_ERROR

**New Models:**

* `RunItemStatistics` - Aggregate counts (total, succeeded, user_error, system_error, skipped, pending, processing)
* `RunOutput`, `ItemOutput`, `ArtifactOutput` - Structured output models with state + termination_reason

**Deleted Models (Breaking Changes):**

* ❌ `UserPayload` → Replaced with `Auth0User` and `Auth0Organization`
* ❌ `PayloadItem` → Replaced with `ItemOutput`
* ❌ `ApplicationVersionReadResponse` → Renamed to `ApplicationVersion`

**Benefits:**

1. **Type Safety**: Enum-based states prevent typos
2. **Clear Semantics**: Separate "what happened" (state) from "why" (termination_reason)
3. **Granular Errors**: Distinguish user errors from system errors for better debugging
4. **Progress Tracking**: RunItemStatistics provides real-time aggregate view

**Usage Example:**

```python
run = client.run("run-123")
details = run.details()

if details.output.state == RunState.TERMINATED:
    if details.output.termination_reason == RunTerminationReason.ALL_ITEMS_PROCESSED:
        print(f"✅ Run complete: {details.output.statistics.succeeded} items succeeded")
        print(
            f"❌ Failures: {details.output.statistics.user_error} user errors, "
            f"{details.output.statistics.system_error} system errors"
        )
```

See `platform/CLAUDE.md` for complete state machine diagrams and migration guide.

## Testing Workflow

### Test Suite Organization

The SDK has a comprehensive test suite organized by test type and execution strategy.

**Pytest Configuration**:

* Default timeout: **10 seconds** per test
* Coverage requirement: **85% minimum**
* Async mode: `auto` (detects async tests automatically)
* Parallel execution: Via pytest-xdist with work stealing

**Test Markers** (authoritative definitions from `pyproject.toml`):

**IMPORTANT**: Every test **MUST** have at least one of: `unit`, `integration`, or `e2e` marker, otherwise it will **NOT run in CI**. The CI pipeline explicitly runs tests with these markers only.

**Test Categories** (Martin Fowler's Solitary vs Sociable distinction):

* **`unit`** - Solitary unit tests
  * Test a layer of a module in isolation with all dependencies mocked (except shared utils and systems module)
  * Must pass **offline** (no external service calls)
  * Timeout: ≤ 10s (default), must be < 5 min
  * ~3 minutes total execution time

* **`integration`** - Sociable integration tests
  * Test interactions across architectural layers (CLI/GUI→Service, Service→Utils) or between modules (Application→Platform)
  * Uses real SDK collaborators, real file I/O, real subprocesses, real Docker containers
  * Must pass **offline** (mock external services: Aignostics Platform API, Auth0, S3/GCS, IDC)
  * Timeout: ≤ 10s (default), must be < 5 min
  * ~5 minutes total execution time

* **`e2e`** - End-to-end tests
  * Test complete workflows with **real external network services** (Aignostics Platform API, cloud storage, IDC, etc)
  * If timeout ≥ 5 min and < 60 min, additionally mark as `long_running`
  * If timeout ≥ 60 min, additionally mark as `very_long_running`
  * ~7 minutes total execution time (regular tests only)

**Test Execution Control Markers**:

* **`long_running`** - Tests with timeout **≥ 5 min and < 60 min**
  * CI/CD runs with **one Python version only** (3.14)
  * Excluded by default in `make test` - use `make test_long_running`
  * Can be skipped in PRs with `skip:test:long_running` label

* **`very_long_running`** - Tests with timeout **≥ 60 min**
  * CI/CD runs with **one Python version only** (3.14)
  * Excluded by default in `make test` - use `make test_very_long_running`
  * Only runs when explicitly enabled with `enable:test:very_long_running` label

**Scheduling Markers**:

* **`scheduled`** - Tests to run on a schedule
  * Still part of non-scheduled test executions
  * Run every 6h (staging) and 24h (production)

* **`scheduled_only`** - Tests to run **on schedule only**
  * Never run in regular CI/CD
  * Only in scheduled test workflows

**Infrastructure Markers**:

* **`sequential`** - Exclude from parallel test execution
  * Tests that must run in specific order or have interdependencies

* **`docker`** - Tests that require Docker
  * Docker daemon must be running

* **`skip_with_act`** - Don't run with [Act](https://github.com/nektos/act)
  * For local GitHub Actions testing

* **`no_extras`** - Tests that require no extras installed
  * Test behavior without optional dependencies

**Test Structure:**

```text
tests/
├── conftest.py           # Global fixtures and configuration
├── aignostics/
│   ├── platform/        # Platform module tests
│   │   ├── sdk_metadata_test.py  (519 lines)
│   │   ├── authentication_test.py
│   │   ├── client_test.py
│   │   └── resources/
│   ├── application/     # Application module tests
│   ├── wsi/             # WSI module tests
│   ├── utils/           # Utils module tests
│   │   └── user_agent_test.py    (258 lines)
│   └── ...
└── CLAUDE.md            # Test suite documentation
```

### Running Tests

**Quick commands:**

```bash
# Run all default tests (unit + integration + e2e, no long_running)
make test

# Run specific test types
make test_unit              # Unit tests only
make test_integration       # Integration tests only
make test_e2e               # E2E tests (requires .env with credentials)

# Run tests with specific markers
make test_sequential        # Sequential tests only
make test_long_running      # Long-running tests
make test_scheduled         # Scheduled tests

# Run on specific Python version
make test 3.12              # Python 3.12
make test 3.13              # Python 3.13
make test 3.14              # Python 3.14
```

**Direct pytest commands:**

```bash
# Run single test file
uv run pytest tests/aignostics/platform/sdk_metadata_test.py -v

# Run specific test function
uv run pytest tests/aignostics/platform/sdk_metadata_test.py::test_build_sdk_metadata_minimal -v

# Run with markers
uv run pytest -m "unit and not long_running" -v

# Run with coverage
uv run pytest --cov=src/aignostics --cov-report=term-missing

# Debug mode (with pdb)
uv run pytest tests/test_file.py --pdb

# Show print statements
uv run pytest tests/test_file.py -s

# Verbose output
uv run pytest tests/test_file.py -vv
```

### Test Parallelization

The test suite uses pytest-xdist for parallel execution with intelligent distribution:

**Configuration (noxfile.py):**

```python
# Worker factors control parallelism
XDIST_WORKER_FACTOR = {
    "unit": 0.0,  # No parallelization (fast, no overhead needed)
    "integration": 0.2,  # 20% of logical CPUs
    "e2e": 1.0,  # 100% of logical CPUs (I/O bound)
    "default": 1.0,  # 100% for mixed test runs
}

# Calculate workers: max(1, int(cpu_count * factor))
# Example: 8 CPU machine
#   unit: 1 worker (sequential)
#   integration: max(1, int(8 * 0.2)) = 1 worker
#   e2e: max(1, int(8 * 1.0)) = 8 workers
```

**Parallel vs Sequential:**

```bash
# Parallel tests (most tests)
uv run pytest -n logical --dist worksteal tests/

# Sequential tests (marked with @pytest.mark.sequential)
uv run pytest -m sequential tests/
```

**Why different factors?**

* **Unit tests (0.0)**: Fast enough that parallelization overhead hurts performance
* **Integration tests (0.2)**: Some I/O but mostly CPU-bound, limited parallelism
* **E2E tests (1.0)**: Network I/O bound, full parallelization maximizes throughput

### Coverage Requirements

**Minimum Coverage: 85%**

```bash
# Check coverage
uv run coverage report

# Generate HTML report
uv run coverage html
open htmlcov/index.html

# Coverage enforced in CI
uv run coverage report --fail-under=85
```

**Coverage Configuration (.coveragerc):**

* Source: `src/aignostics`
* Omits: `*/tests/*`, `*/__init__.py`, `*/codegen/*`
* Reports: Terminal, XML (Codecov), HTML, Markdown

### E2E Test Setup

E2E tests require credentials to run against staging environment:

**Required .env file:**

```bash
# Create .env in repository root
AIGNOSTICS_API_ROOT=https://platform-staging.aignostics.com
AIGNOSTICS_CLIENT_ID_DEVICE=your-staging-client-id
AIGNOSTICS_REFRESH_TOKEN=your-staging-refresh-token
```

**In CI/CD:**

* GitHub Actions secrets automatically populate .env
* Uses `AIGNOSTICS_CLIENT_ID_DEVICE_STAGING` and `AIGNOSTICS_REFRESH_TOKEN_STAGING`
* GCP credentials for bucket access also configured

**Running E2E locally:**

```bash
# Ensure .env exists with staging credentials
make test_e2e

# Or with pytest directly
uv run pytest -m "e2e and not long_running" -v
```

### Pytest Configuration Details

**From `pyproject.toml` `[tool.pytest.ini_options]`**:

**Test Discovery**:

* Test paths: `tests/`
* Python files: `*_test.py`, `test_*.py`
* Main file: `tests/main.py`

**CLI Options** (always applied):

```bash
-p nicegui.testing.plugin  # NiceGUI testing support
-v                          # Verbose output
--strict-markers            # Error on unknown markers
--log-disable=aignostics    # Disable SDK logging during tests
--cov=aignostics            # Coverage for src/aignostics
--cov-report=term-missing   # Terminal report with missing lines
--cov-report=xml:reports/coverage.xml     # XML for Codecov
--cov-report=html:reports/coverage_html   # HTML report
```

**Timeouts**:

* Default: **10 seconds** per test
* Override in test: `@pytest.mark.timeout(timeout=60)`
* Method: `signal` (can be configured)

**Async Support**:

* Mode: `auto` (automatically detects async tests)
* Default fixture loop scope: `function`

**Coverage**:

* Environment: `COVERAGE_FILE=.coverage`, `COVERAGE_PROCESS_START=pyproject.toml`
* Minimum: 85% (enforced in CI)
* Branch coverage: Enabled
* Parallel mode: Enabled (thread + multiprocessing concurrency)

**Markdown Reports**:

* Enabled: `md_report = true`
* Output: `reports/pytest.md`
* Flavor: GitHub-flavored markdown
* Exclude outcomes: `passed`, `skipped` (only show failures/errors)

### Test Fixtures and Patterns

**Key fixtures (conftest.py):**

* Environment isolation (HOME, config dirs)
* Mocked responses for API calls
* Temporary file creation
* Authentication mocking

**Example test pattern:**

```python
import pytest
from unittest.mock import patch


@pytest.mark.unit
def test_sdk_metadata_minimal(monkeypatch):
    """Test SDK metadata with clean environment."""
    # Isolate environment
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    # Run test
    result = build_sdk_metadata()

    # Assertions
    assert result.submission.date is not None
    assert result.user_agent is not None
```

**See tests/CLAUDE.md for comprehensive testing patterns and examples.**

### Finding Unmarked Tests

**Critical**: To find tests missing category markers (which will NOT run in CI):

```bash
# Find all tests without unit/integration/e2e markers
uv run pytest -m "not unit and not integration and not e2e" --collect-only

# This should return 0 tests if all are properly marked
# If tests are found, they are missing required markers
```

**Why this works**: The marker expression matches tests that don't have any of the required category markers.

**Add to pre-commit checks**:

```bash
# Verify no unmarked tests exist
if uv run pytest -m "not unit and not integration and not e2e" --collect-only 2>&1 | grep -q "collected 0 items"; then
    echo "✅ All tests have category markers"
else
    echo "❌ Found tests without category markers - they will NOT run in CI!"
    exit 1
fi
```

## Development Workflow

### Initial Setup

```bash
# Clone repository
git clone https://github.com/aignostics/python-sdk.git
cd python-sdk

# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies including dev tools
make install
# This runs: uv sync --all-extras + installs pre-commit hooks

# Verify installation
uv run aignostics --version
```

### Development Cycle

**1. Create Feature Branch**

```bash
# From main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feat/my-feature

# Or bugfix branch
git checkout -b fix/bug-description
```

**2. Make Changes and Validate**

```bash
# Run linting (this is fast, run frequently)
make lint
# Runs: ruff format, ruff check, pyright, mypy

# Run tests
make test
# Or specific test types
make test_unit           # Fast unit tests only
make test_integration    # Integration tests

# Full validation (what CI runs)
make all
# Runs: lint + test + docs + audit (~20 minutes)
```

**3. Pre-commit Hooks (Automatic)**

The repository uses pre-commit hooks installed by `make install`:

```yaml
# .pre-commit-config.yaml
hooks:
  - ruff formatting check
  - ruff linting check
  - mypy type checking
  - trailing whitespace removal
  - end-of-file fixer
  - yaml validation
```

**Skip hooks only if necessary:**

```bash
git commit --no-verify -m "WIP: debugging"
```

**4. Commit Convention**

Use conventional commits for automatic changelog generation:

```bash
# Feature
git commit -m "feat(platform): add operation caching system"

# Bug fix
git commit -m "fix(application): handle missing artifact states"

# Documentation
git commit -m "docs: update testing workflow in CLAUDE.md"

# Refactor
git commit -m "refactor(wsi): simplify thumbnail generation"

# Test
git commit -m "test(platform): add SDK metadata validation tests"

# Chore
git commit -m "chore: bump dependencies"
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `perf`, `build`

**5. Push and Create PR**

```bash
# Push to remote
git push origin feat/my-feature

# Create PR (via gh cli or GitHub UI)
gh pr create --title "feat: add operation caching" --body "Description..."

# IMPORTANT: Add label to skip long-running tests
gh pr edit --add-label "skip:test:long_running"
```

**PR triggers:**

* Lint checks (~5 min)
* Security audit (~3 min)
* Test matrix on Python 3.11, 3.12, 3.13, 3.14 (~15 min)
* CodeQL security scanning (~10 min)
* Claude Code automated review (~10 min)
* Ketryx compliance reporting

**6. Address Review Feedback**

```bash
# Make changes
git add .
git commit -m "fix: address review comments"
git push origin feat/my-feature

# CI re-runs automatically
```

**7. Merge PR**

* Ensure all CI checks pass (green checkmarks)
* Get approval from maintainer
* Squash and merge (default) or merge commit
* Delete feature branch after merge

### Build System (Nox)

The SDK uses Nox for build automation with uv integration:

**Key Nox sessions:**

```bash
# Lint session (ruff format + check + pyright + mypy)
uv run nox -s lint

# Audit session (pip-audit + pip-licenses + SBOMs)
uv run nox -s audit

# Test session (pytest with coverage)
uv run nox -s test           # Default markers
uv run nox -s test -- -m unit  # Specific markers

# Test matrix (all Python versions)
uv run nox -s test-3.11
uv run nox -s test-3.12
uv run nox -s test-3.13
uv run nox -s test-3.14

# Documentation
uv run nox -s docs           # Build Sphinx docs

# Setup session (install all dev tools)
uv run nox -s setup

# Version bumping
uv run nox -s bump -- patch  # 1.0.0 -> 1.0.1
uv run nox -s bump -- minor  # 1.0.0 -> 1.1.0
uv run nox -s bump -- major  # 1.0.0 -> 2.0.0
```

**Makefile wraps Nox for convenience:**

```bash
make lint      → uv run nox -s lint
make test      → uv run nox -s test
make docs      → uv run nox -s docs
make audit     → uv run nox -s audit
make all       → all of the above
```

### Adding Dependencies

**Runtime dependency:**

```bash
# Add to main dependencies
uv add requests

# Add with version constraint
uv add "httpx>=0.25.0"

# Update pyproject.toml automatically
```

**Development dependency:**

```bash
# Add to dev dependencies
uv add --dev pytest-mock

# Or specific group
uv add --group docs sphinx-rtd-theme
```

**Optional dependency group:**

```bash
# Edit pyproject.toml
[project.optional-dependencies]
gui = ["nicegui>=1.0.0"]
qupath = ["ijson>=3.0.0"]

# Install with extras
uv sync --extra gui
uv sync --all-extras  # Install all optional groups
```

### Version Bumping and Releases

Releases follow a **four-phase GitHub workflow–based strategy** that allows Ketryx compliance approvals to be collected *before* publishing:

```
Prerequisite (anytime): Create the Ketryx release in the Ketryx portal
Phase 1:                make prepare-release x.y.z
Phase 2:                Point Ketryx release to release/vX.Y.Z; collect approvals
Phase 3:                make publish-release
Phase 4:                make merge-release
```

**Phase 1 — Prepare the release branch:**

```bash
# Creates release/vX.Y.Z branch from main, bumps version files, and pushes.
# No tag is created yet.
make prepare-release 1.2.3   # explicit version
```

This triggers `prepare-release.yml` on GitHub Actions, which:

1. Creates `release/vX.Y.Z` branch from `main`
2. Runs `bump-my-version` (commits version files + `uv.lock`)
3. Pushes the branch — CI runs lint/test/audit on it

**Phase 2 — Collect Ketryx approvals:**

Point the Ketryx release to the `release/vX.Y.Z` branch and collect required approvals. CI must be green on the branch before proceeding.

**Phase 3 — Publish (tag + PyPI):**

```bash
# Generates CHANGELOG.md, creates vX.Y.Z tag, pushes → triggers CI/CD publish.
make publish-release

# Optionally specify a branch explicitly:
make publish-release release/v1.2.3
```

This triggers `publish-release.yml`, which:

1. Generates `CHANGELOG.md` for the release range
2. Commits the changelog
3. Creates and pushes the annotated `vX.Y.Z` tag
4. CI/CD fires on the tag; Ketryx check must pass before PyPI publish

**Phase 4 — Merge back to main:**

```bash
# Merges the release branch into main (--no-ff) and deletes the branch.
make merge-release

# Optionally specify a branch explicitly:
make merge-release release/v1.2.3
```

This triggers `merge-release.yml`, which:

1. Merges `release/vX.Y.Z` into `main` with `--no-ff`
2. Pushes `main`
3. Deletes the remote release branch

**What triggers CI/CD:**

```
make prepare-release  → push to release/vX.Y.Z  → lint + test + audit + Ketryx
make publish-release  → push vX.Y.Z tag          → full CI + PyPI + Docker + GitHub release
make merge-release    → push to main              → full CI pipeline
```

### CI/CD Integration

See [.github/CLAUDE.md](.github/CLAUDE.md) for comprehensive CI/CD documentation including:

* Complete workflow architecture
* Claude Code automation (PR reviews, interactive sessions)
* Environment configuration (staging/production)
* Scheduled testing (6h staging, 24h production)
* Debugging failed CI runs
* Secrets management

**Quick CI reference:**

```bash
# Skip CI for commit
git commit -m "docs: update README [skip ci]"

# Or with skip:ci in commit message
git commit -m "skip:ci: work in progress"

# Add PR label to skip long-running tests
gh pr edit --add-label "skip:test:long_running"
```

### IDE Setup Recommendations

**VS Code (.vscode/settings.json):**

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["-v"],
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "ruff",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

**PyCharm:**

* Configure Python interpreter: `.venv/bin/python`
* Enable pytest as test runner
* Set up ruff as external tool
* Configure mypy plugin for type checking

## Tips and Tricks for Claude Code Efficiency

### Quick Discovery Commands

**Find files by pattern**:

```bash
# Find all test files
find tests -name "*_test.py" -o -name "test_*.py"

# Find Python files excluding tests
find src -name "*.py" | grep -v __pycache__

# Find configuration files
find . -maxdepth 2 -name "*.toml" -o -name "*.yml" -o -name "*.yaml" | grep -v node_modules
```

**Search code effectively**:

```bash
# Find all imports of a module
grep -r "from aignostics.platform import" --include="*.py"

# Find all test markers
grep -r "@pytest.mark." tests/ --include="*.py" | cut -d: -f2 | sort | uniq -c

# Find all CLI commands
grep -r "@cli.*\.command" src/ --include="*.py"

# Find TODOs and FIXMEs
grep -rn "TODO\|FIXME" src/ --include="*.py"
```

**Git exploration**:

```bash
# View commit history for a specific file
git log --oneline --follow -- path/to/file.py

# See what changed in recent commits
git log --oneline --stat -10

# Find who last modified a line
git blame -L 100,110 path/to/file.py

# Check current branch and recent commits
git log --oneline --graph --decorate -20
```

### Testing Shortcuts

**Run specific test categories**:

```bash
# Run only fast tests (unit + integration, no e2e)
uv run pytest -m "unit or integration" -v

# Run tests for a specific module
uv run pytest tests/aignostics/platform/ -v

# Run tests matching a pattern
uv run pytest -k "metadata" -v

# Run last failed tests
uv run pytest --lf

# Run tests that failed in last session, then continue with others
uv run pytest --ff
```

**Test discovery and validation**:

```bash
# Collect tests without running (verify test discovery)
uv run pytest --collect-only

# Find tests without category markers (CRITICAL - they won't run in CI!)
uv run pytest -m "not unit and not integration and not e2e" --collect-only

# List all available markers
uv run pytest --markers

# Dry run with verbose output
uv run pytest --collect-only -v | grep "<Function"
```

**Coverage shortcuts**:

```bash
# Quick coverage check without HTML
uv run pytest --cov=aignostics --cov-report=term-missing --no-cov-on-fail

# Coverage for specific module
uv run pytest tests/aignostics/platform/ --cov=aignostics.platform --cov-report=term

# View coverage report from last run
uv run coverage report

# Open HTML coverage report
open reports/coverage_html/index.html
```

### Code Quality Checks

**Incremental linting** (faster than full `make lint`):

```bash
# Format only changed files
git diff --name-only --diff-filter=AM | grep "\.py$" | xargs ruff format

# Lint only changed files
git diff --name-only --diff-filter=AM | grep "\.py$" | xargs ruff check

# Type check specific file
uv run mypy src/aignostics/platform/_client.py

# Check specific file with pyright
uv run pyright src/aignostics/platform/_client.py
```

**Quick fixes**:

```bash
# Auto-fix ruff issues
ruff check . --fix

# Auto-fix unsafe issues too (use with caution)
ruff check . --fix --unsafe-fixes

# Format all Python files
ruff format .
```

### Debugging Techniques

**Pytest debugging**:

```bash
# Drop into pdb on first failure
uv run pytest --pdb

# Drop into pdb on any exception
uv run pytest --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb

# Show local variables on failure
uv run pytest --showlocals

# Ultra-verbose output
uv run pytest -vvv --tb=long

# Capture output for debugging
uv run pytest -s --log-cli-level=DEBUG
```

**Module import testing**:

```bash
# Test if module imports successfully
python -c "from aignostics.platform import Client; print('OK')"

# Check module version
python -c "import aignostics; print(aignostics.__version__)"

# List module contents
python -c "from aignostics import platform; print(dir(platform))"
```

### Efficient File Exploration

**Understanding module structure**:

```bash
# List all Python modules
find src/aignostics -type d -name "[!_]*" | grep -v __pycache__

# Count lines of code by module
for dir in src/aignostics/*/; do
  echo "$(find "$dir" -name '*.py' | xargs wc -l | tail -1 | awk '{print $1}') lines in $(basename $dir)"
done | sort -rn

# Find largest Python files
find src -name "*.py" -exec wc -l {} \; | sort -rn | head -10

# Count test files vs source files
echo "Source: $(find src -name '*.py' | wc -l) files"
echo "Tests: $(find tests -name '*test.py' | wc -l) files"
```

**Checking dependencies**:

```bash
# List all direct dependencies
grep "dependencies = \[" pyproject.toml -A 50 | grep -E "^\s+\"" | head -20

# Check installed packages
uv pip list

# Find unused imports (requires autoflake)
uv run python -m autoflake --check --remove-all-unused-imports src/

# Check for outdated dependencies
uv pip list --outdated
```

### Working with Reports

**Generated reports location**: `reports/`

```bash
# View pytest summary
cat reports/pytest.md

# Check coverage summary
cat reports/coverage.md

# View JUnit XML for specific marker
ls reports/junit_*.xml

# Quick coverage percentage
grep "TOTAL" reports/coverage.md
```

### Nox Session Shortcuts

```bash
# List all available nox sessions
uv run nox --list

# Run specific session
uv run nox -s lint

# Run session with specific Python version
uv run nox -s test-3.14.3

# Run multiple sessions
uv run nox -s lint audit

# Pass arguments to pytest through nox
uv run nox -s test -- -v -k "metadata"

# Reuse existing virtualenvs (faster)
uv run nox --reuse-existing-virtualenvs -s test
```

### Branch and Commit Hygiene

**Before starting work**:

```bash
# Ensure clean state
git status
make lint
make test_unit

# Update from main
git fetch origin
git rebase origin/main
```

**During development**:

```bash
# Incremental validation (fast feedback)
make lint                    # ~5 min
make test_unit              # ~3 min

# Full validation before commit
make all                    # ~20 min (lint + test + docs + audit)
```

**Before creating PR**:

```bash
# Verify all tests pass
make test

# Check for unmarked tests
uv run pytest -m "not unit and not integration and not e2e" --collect-only

# Verify no lint issues
make lint

# Check coverage hasn't dropped
uv run coverage report --fail-under=85

# Review changes
git diff origin/main..HEAD --stat
```

### Performance Profiling

**Test execution time**:

```bash
# Show slowest tests
uv run pytest --durations=10

# Show slowest tests with setup/teardown
uv run pytest --durations=10 --durations-min=1.0

# Profile test execution
uv run pytest --profile

# Time a specific test
time uv run pytest tests/aignostics/platform/sdk_metadata_test.py -v
```

**Memory profiling**:

```bash
# Run with memory profiler
python -m memory_profiler script.py

# Check memory usage during tests
uv run pytest --memray tests/
```

### Documentation Generation

```bash
# Build docs locally
make docs

# Open generated docs
open docs/build/html/index.html

# Check for broken links in docs
uv run sphinx-build -b linkcheck docs/source docs/build/linkcheck

# Generate API documentation
uv run sphinx-apidoc -o docs/source/api src/aignostics
```

### CLI Testing and Exploration

```bash
# Test CLI works
uv run aignostics --help

# Test specific command
uv run aignostics user whoami --mask-secrets

# Test with verbose output
uv run aignostics system info --verbose

# Check CLI completion
uv run aignostics --install-completion

# Test SDK metadata schema export
uv run aignostics sdk metadata-schema --pretty | jq .
```

### Quick Fixes for Common Issues

**"No module named" errors**:

```bash
uv sync --all-extras
```

**Test failures after merge**:

```bash
# Clean caches
make clean
rm -rf .pytest_cache .mypy_cache .ruff_cache

# Reinstall
uv sync --all-extras
```

**Coverage file issues**:

```bash
# Reset coverage
make test_coverage_reset

# Rerun tests
make test
```

**Git conflicts in lockfiles**:

```bash
# Regenerate uv.lock
uv lock --upgrade
```

**Type checking errors**:

```bash
# Check which type checker is failing
uv run mypy src/aignostics/platform/
uv run pyright src/aignostics/platform/

# See pyrightconfig.json for exclusions
cat pyrightconfig.json
```

### Efficient Code Review

**Review checklist**:

```bash
# 1. Check what changed
git diff --stat origin/main...HEAD

# 2. Review code changes
git diff origin/main...HEAD

# 3. Check test coverage for changed files
git diff --name-only origin/main...HEAD | grep "\.py$" | xargs uv run pytest --cov-report=term-missing --cov=

# 4. Verify tests pass
make test_unit

# 5. Check for new TODOs
git diff origin/main...HEAD | grep "+.*TODO"

# 6. Verify lint passes
make lint
```

**Finding related tests**:

```bash
# Given a source file, find its tests
src_file="src/aignostics/platform/_client.py"
test_file="tests/aignostics/platform/$(basename ${src_file%%.py}_test.py)"
ls $test_file
```

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

## Publishing

**Internal registry (use for pre-release / integration builds on this branch):**

```
https://europe-python.pkg.dev/aignx-development/aignx-development-python-registry/aignostics-sdk
```

To publish to the internal registry instead of PyPI:

```bash
uv publish --index-url https://europe-python.pkg.dev/aignx-development/aignx-development-python-registry/ dist/aignostics_sdk-*
```

## SDLC Configuration

- **JIRA Project Key:** PYSDK
- **Atlassian Cloud ID:** fff788d2-8a2a-4c36-a884-dde2bb4a2b49
- **Ketryx Project:** Python SDK (KXPRJ2Q4PA8AADY975SFMKF276TYV75)

**Item type locations:**
- Change Requests: Ketryx Change Request (JIRA)
- Stakeholder Requirements: requirements/SHR-*.md (Git)
- Software Requirements: Requirement (JIRA) | requirements/SWR-*.md (Git, preferred)
- Risks: Risk (JIRA)
- Software Item Specs: Software Item Spec (JIRA) | specifications/SPEC-*.md (Git, preferred)
- Test Cases: tests/**/TC-*.feature (Git)

**Approval structure:**
- Ketryx Change Request: Product Manager → Engineering Tech Lead → Quality Managers → Risk Managers
- Software Requirement: Area Lead (BD) → Security Engineer → Regulatory Affairs Specialist → Engineer → Engineering Tech Lead → Product Manager
- Software Item Spec: Engineer → Engineering Tech Lead
- Risk: Quality Managers → Security Engineer → Product Managers → Tech Lead → Engineer → Engineering Tech Lead → Product Manager → Engineer
- Test Case: Engineer → Engineering Tech Lead
- Anomaly: Engineer → Engineering Tech Lead
