# CLAUDE.md - Aignostics SDK Modules Overview

This file provides a comprehensive overview of all modules in the Aignostics SDK, their core features, user interfaces, and interactions.

## Module Index

| Module | Core Purpose | CLI | GUI | Service |
|--------|-------------|-----|-----|---------|
| **platform** | Authentication & API client | ✅ | ❌ | ✅ |
| **application** | Application run orchestration | ✅ | ✅ | ✅ |
| **wsi** | Whole slide image processing | ✅ | ✅ | ✅ |
| **dataset** | IDC dataset downloads | ✅ | ✅ | ✅ |
| **bucket** | Cloud storage operations | ✅ | ✅ | ✅ |
| **utils** | Core utilities & DI | ❌ | ❌ | ✅ |
| **gui** | Desktop launchpad | ❌ | ✅ | ✅ |
| **notebook** | Marimo notebook server | ❌ | ✅ | ✅ |
| **qupath** | QuPath integration | ✅ | ✅ | ✅ |
| **system** | System information | ✅ | ✅ | ✅ |

## Module Descriptions

### 🔐 platform

**Foundation module providing authentication and API access**

- **Core Features**: OAuth 2.0 authentication, JWT token management, API client wrapper
- **CLI**: `login`, `logout`, `whoami` commands for authentication
- **Dependencies**: None (foundation layer)
- **Used By**: All modules requiring API access

### 🚀 application

**High-level orchestration for ML model execution**

- **Core Features**: Application run lifecycle, version management, progress tracking, result downloads
- **CLI**: Full CRUD for application runs (`list`, `submit`, `describe`, `download`)
- **GUI**: Rich interface for run submission and monitoring with real-time progress
- **Dependencies**: `platform` (API), `bucket` (storage), `wsi` (validation), `utils` (DI)
- **Optional**: `qupath` for WSI visualization (requires `ijson`)

### 🔬 wsi

**Medical image file handling and processing**

- **Core Features**: Format detection, thumbnail generation, metadata extraction
- **CLI**: `info`, `thumbnail` commands for WSI inspection
- **GUI**: Image viewer and metadata display
- **Handlers**: OpenSlide (.svs, .tiff), PyDICOM (DICOM files)
- **Dependencies**: `utils` (logging)

### 📦 dataset

**High-performance dataset downloads from IDC**

- **Core Features**: IDC integration, s5cmd parallel downloads, progress tracking
- **CLI**: Dataset search and download commands
- **GUI**: Dataset browser and download manager
- **Dependencies**: `platform` (auth), `utils` (process management)
- **External**: `s5cmd` binary for transfers

### ☁️ bucket

**Cloud storage abstraction layer**

- **Core Features**: S3/GCS operations, signed URLs, chunked transfers
- **CLI**: Upload/download commands
- **GUI**: Storage browser interface
- **Dependencies**: `platform` (credentials), `utils` (settings)
- **External**: `boto3` for AWS S3

### 🛠️ utils

**Core infrastructure and shared utilities**

- **Core Features**: Dependency injection, logging, settings, health checks
- **Service Discovery**: `locate_implementations()`, `locate_subclasses()`
- **No CLI/GUI**: Infrastructure module
- **Used By**: All modules

### 🖥️ gui

**Desktop application launchpad**

- **Core Features**: Module launcher, unified interface
- **GUI Only**: NiceGUI-based desktop interface
- **Dependencies**: All modules with GUI components
- **Launch**: `uvx --with aignostics[gui] aignostics gui`

### 📓 notebook

**Interactive Marimo notebook environment**

- **Core Features**: Reactive notebook server, data exploration, analysis workflows
- **GUI Only**: Embedded Marimo interface (no CLI)
- **Process Management**: Subprocess lifecycle with health monitoring
- **Dependencies**: `utils` (base service), `marimo` package
- **Requirements**: `pip install marimo`

### 🔍 qupath

**Bioimage analysis integration (optional)**

- **Core Features**: QuPath project management, WSI annotation
- **CLI**: Project creation and annotation commands
- **Requirements**: `ijson` package (`pip install aignostics[qupath]`)
- **Dependencies**: `utils` (base service)

### 💻 system

**System information and diagnostics**

- **Core Features**: Environment info, dependency checks
- **CLI**: `info` command for system diagnostics
- **Dependencies**: `utils` (logging)

## Module Interaction Patterns

### Architecture: Service Layer with Dual Presentation Layers

```text
┌─────────────────────────────────────────────────────────────┐
│                     GUI Launchpad (_gui/)                  │
│                  (Desktop Interface Aggregator)            │
└─────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────┐
│                    Per-Module Architecture                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐        ┌─────────────────┐           │
│  │   CLI (_cli.py) │        │  GUI (_gui.py)  │           │
│  │  Text Interface │        │   NiceGUI UI    │           │
│  └────────┬────────┘        └────────┬────────┘           │
│           │                           │                     │
│           └──────────┬────────────────┘                    │
│                      ↓                                      │
│         ┌──────────────────────────┐                       │
│         │   Service (_service.py)   │                      │
│         │    Business Logic Core    │                      │
│         └──────────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘

This pattern repeats for: platform, application, wsi, dataset,
bucket, qupath, system (each module has CLI + Service, most have GUI)
```

### Service Layer Dependencies

```text
                    ┌──────────────────┐
                    │   application    │
                    │    (service)     │
                    └──────┬───────────┘
                           │ uses
        ┌──────────┬───────┼────────┬──────────┐
        ↓          ↓       ↓        ↓          ↓
  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
  │   wsi   │ │ dataset │ │ bucket  │ │ qupath  │
  │(service)│ │(service)│ │(service)│ │(service)│
  └─────────┘ └─────────┘ └────┬────┘ └─────────┘
                                │
                                ↓
                        ┌──────────────┐
                        │   platform    │
                        │   (service)   │
                        └──────┬───────┘
                                │
                                ↓
                        ┌──────────────┐
                        │     utils     │
                        │(infrastructure)│
                        └───────────────┘
```

### Common Integration Patterns

**1. Application Run Workflow:**

```python
platform → authenticate
application → create run
bucket → upload WSI files
application → monitor progress
bucket → download results
qupath → visualize (optional)
```

**2. Dataset Processing:**

```python
platform → authenticate
dataset → download from IDC
wsi → validate files
application → batch process
```

**3. Service Discovery:**

```python
utils.locate_implementations(BaseService)
→ Finds all service implementations
→ Used by GUI to discover modules
```

## Module Communication

### Direct Dependencies

- **application** → `platform`, `bucket`, `wsi`, `utils`, `qupath` (optional)
- **dataset** → `platform`, `utils`
- **bucket** → `platform`, `utils`
- **wsi** → `utils`
- **gui** → All modules with GUI components
- **notebook** → `utils`, `marimo` (external)
- **qupath** → `utils`
- **system** → All modules (for health checks)

### Shared Resources

- **Authentication**: Token cached by `platform`, used by all API calls
- **Settings**: Managed by `utils`, consumed by all modules
- **Logging**: Centralized through `utils.get_logger()`
- **Health Checks**: All services implement `BaseService.health()`

## CLI Usage Examples

```bash
# Authenticate
aignostics user login

# List applications
aignostics application list

# Submit a run
aignostics application run submit --application-id heta --files slide.svs

# Download dataset
aignostics dataset download --collection-id TCGA-LUAD --output-dir ./data

# Get WSI info
aignostics wsi info slide.svs
```

## GUI Launch

```bash
# Install with GUI support
pip install "aignostics[gui]"

# Launch desktop interface
uvx --with "aignostics[gui]" aignostics gui

# Or if installed locally
aignostics gui
```

## Module-Specific Documentation

For detailed information about each module, see:

- [platform/CLAUDE.md](platform/CLAUDE.md) - Authentication and API details
- [application/CLAUDE.md](application/CLAUDE.md) - Application orchestration
- [wsi/CLAUDE.md](wsi/CLAUDE.md) - Image processing
- [dataset/CLAUDE.md](dataset/CLAUDE.md) - Dataset operations
- [bucket/CLAUDE.md](bucket/CLAUDE.md) - Storage management
- [utils/CLAUDE.md](utils/CLAUDE.md) - Infrastructure details
- [gui/CLAUDE.md](gui/CLAUDE.md) - Desktop interface
- [notebook/CLAUDE.md](notebook/CLAUDE.md) - Marimo notebook integration
- [qupath/CLAUDE.md](qupath/CLAUDE.md) - QuPath integration
- [system/CLAUDE.md](system/CLAUDE.md) - System diagnostics

## Development Guidelines

1. **New Module Checklist:**
   - Inherit from `BaseService` for service discovery
   - Implement `health()` and `info()` methods
   - Add `_cli.py` for CLI commands using Typer
   - Add `_gui.py` for GUI components using NiceGUI
   - Create `CLAUDE.md` documentation
   - Update this index

2. **Service Pattern:**

   ```python
   from aignostics.utils import BaseService

   class Service(BaseService):
       def health(self) -> Health:
           return Health(status=Health.Code.UP)

       def info(self, mask_secrets=True) -> dict:
           return {"version": "1.0.0"}
   ```

3. **CLI Pattern:**

   ```python
   import typer
   cli = typer.Typer(name="module", help="Module description")

   @cli.command("action")
   def action_command():
       """Action description."""
       service = Service()
       service.perform_action()
   ```

4. **GUI Pattern:**

   ```python
   from nicegui import ui

   def create_page():
       ui.label("Module Interface")
       # Add components
   ```

---

*This index provides a high-level map of the Aignostics SDK architecture. Each module's CLAUDE.md contains implementation details and usage examples.*
