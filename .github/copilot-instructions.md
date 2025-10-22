# Copilot Instructions - Aignostics Python SDK

## Tooling specific to use in VSCode

When interacting with you NiceGUI is typically running in watch mode via `make gui_watch` in the terminal. In that case you can point the browser to http://localhost:8000
to go to the homepage of the app, and from there via the left sidebar or top-right burger menu navigate to the page, e.g. top-left in the sidebar
to the application_describe page. Check the output of the terminal to find the port, can be 8000 or 8001 etc.

You are running embedded in VSCode. Bias to use the MCP tools made available for you. E.g. when asked to make changes in the GUI layer prefer opening
the openSimpleBrowser, go to the page, make the code change, check output in inbuilt browser. When asked to go to the HETA application (describe) page
you can typically navigate to http://127.0.0.1:8000/application/he-tme . Don't ask the user to open the browser, but use openSimpleBrowser MCP too.

## Project Overview

The Aignostics Python SDK is a **computational pathology platform** providing multiple interfaces to process whole slide images (WSI) with AI/ML applications. It follows a **modulith architecture** with independent modules connected via dependency injection.

**Key Components:**
- **Launchpad**: Desktop GUI (NiceGUI + webview)
- **CLI**: Command-line interface (Typer)
- **Client Library**: Python API wrapper
- **Notebook Integration**: Marimo/Jupyter support

## Architecture Principles

### 1. Modulith Design Pattern
Each module follows a consistent three-layer structure:
```
module/
├── _service.py     # Business logic (inherits BaseService)
├── _cli.py         # CLI commands (Typer)
├── _gui.py         # GUI interface (NiceGUI)
├── _settings.py    # Configuration (Pydantic)
└── CLAUDE.md       # Detailed documentation
```

### 2. Service Discovery & Dependency Injection
- All services inherit from `BaseService` and implement `health()` and `info()` methods
- Use `locate_implementations(BaseService)` for runtime service discovery
- No decorators - pure runtime DI container pattern
- Services are singletons within the DI container

### 3. Presentation Layer Independence
```
CLI Layer ─┐
           ├─→ Service Layer
GUI Layer ─┘
```
CLI and GUI layers depend on Service layer, never on each other.

## Module Dependencies & Communication

**Foundation Layer:**
- `utils`: DI container, logging, settings, health checks

**API Layer:**
- `platform`: OAuth 2.0 auth, JWT tokens, API client

**Domain Modules:**
- `application`: ML run orchestration (depends on: platform, bucket, wsi, qupath optional)
- `wsi`: Medical image processing (OpenSlide, PyDICOM)
- `dataset`: IDC downloads with s5cmd
- `bucket`: Cloud storage (S3/GCS)

**Integration:**
- `qupath`: Bioimage analysis (requires `ijson`)
- `notebook`: Marimo server (requires `marimo`)
- `gui`: Desktop launchpad (aggregates all GUIs)
- `system`: Health monitoring (queries ALL services)

## Development Workflow Commands

**Primary Commands:**
```bash
make install          # Install dev deps + pre-commit hooks
make all             # Full CI pipeline (lint, test, docs, audit)
make test            # Run tests with coverage (85% minimum)
make test 3.12       # Run on specific Python version
make lint            # Ruff formatting + MyPy type checking
```

**Package Management:**
- Uses `uv` (not pip/poetry): `uv sync --all-extras`
- Add dependencies: `uv add <package>`

**Testing:**
- Pytest with markers: `sequential`, `long_running`, `scheduled`, `docker`, `skip_with_act`
- Run specific tests: `uv run pytest tests/path/test.py::test_function`
- Docker integration: `make test-docker`

## Code Patterns & Standards

### Service Implementation
```python
from aignostics.utils import BaseService, Health

class Service(BaseService):
    def __init__(self):
        super().__init__(SettingsClass)  # Optional settings
    
    def health(self) -> Health:
        return Health(status=Health.Code.UP)
    
    def info(self, mask_secrets: bool = True) -> dict:
        return {"version": "1.0.0"}
```

### CLI Pattern
```python
import typer
from ._service import Service

cli = typer.Typer(name="module", help="Module description")

@cli.command("action")
def action_command(param: str):
    """Command description."""
    service = Service()
    result = service.perform_action(param)
    console.print(result)
```

### GUI Pattern
```python
from nicegui import ui

def create_page():
    ui.label("Module Interface")
    # Components auto-register with GUI launcher
```

## Testing Conventions

**File Structure:**
- Tests in `tests/aignostics/<module>/`
- Use `conftest.py` fixtures for common setup
- Mock external dependencies

**Patterns:**
- Use `CliRunner` from `typer.testing` for CLI tests
- Use `normalize_output()` helper for cross-platform CLI output
- Cleanup fixtures for processes (e.g., `qupath_teardown`)

## Medical Domain Context

**Key Technologies:**
- **DICOM**: Medical imaging standard
- **WSI**: Gigapixel pathology images (pyramidal multi-resolution)
- **IDC**: NCI Imaging Data Commons for public datasets
- **QuPath**: Leading bioimage analysis platform
- **H&E**: Hematoxylin & Eosin histological staining

**Processing Patterns:**
- Tile-based processing for memory efficiency
- Streaming for large file transfers
- Chunked uploads/downloads (1MB/10MB chunks)
- Signed URLs for secure data access

## Security & Performance

**Authentication:**
- OAuth 2.0 device flow via `platform` module
- Tokens cached in `~/.aignostics/token.json`
- 5-minute refresh buffer before expiry

**Performance:**
- Lazy evaluation for large datasets
- Process management for subprocesses
- Memory-efficient WSI processing in tiles
- Async operations for I/O-bound tasks

## Configuration & Environment

**Settings Pattern:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_root: str = "https://platform.aignostics.com"
    
    class Config:
        env_prefix = "AIGNOSTICS_"
```

**Environment Variables:**
- `AIGNOSTICS_API_ROOT`: Platform endpoint
- `AIGNOSTICS_CLIENT_ID_DEVICE`: OAuth client ID
- `AIGNOSTICS_REFRESH_TOKEN`: Auth token

## Common Integration Points

**Application Run Workflow:**
```python
# 1. Authenticate
client = platform.Client()

# 2. Submit run
run = client.runs.create(
    application_id="heta",
    application_version="1.0.0",  # version number without 'v' prefix, omit for latest
    items=[platform.InputItem(...)]
)

# 3. Monitor & download
run.download_to_folder("./results")
```

**Service Health Monitoring:**
```python
from aignostics.utils import locate_implementations, BaseService

# Discover all services
services = locate_implementations(BaseService)

# Check health of all services
for service_class in services:
    service = service_class()
    health = service.health()
    print(f"{service.key()}: {health.status}")
```

## Important Notes

**Optional Dependencies:**
- GUI requires: `pip install "aignostics[gui]"`
- QuPath requires: `pip install "aignostics[qupath]"`
- Notebooks require: `pip install "aignostics[notebook]"`

**Platform Constraints:**
- Windows path length limitations
- Memory usage for large WSI files
- Token expiry handling (force refresh with `remove_cached_token()`)

**Build System:**
- Main config: `pyproject.toml`
- Build tasks: `noxfile.py` (not tox)
- Quality gates: Ruff (formatting/linting), MyPy (typing), 85% test coverage

Always conform to the coding styles defined in [CODE_STYLE.md](../CODE_STYLE.md) and development processes in [CONTRIBUTING.md](../CONTRIBUTING.md), and have a look at [OPERATIONAL_EXCELLENCE.md](../OPERATIONAL_EXCELLENCE.md) for release readiness.
