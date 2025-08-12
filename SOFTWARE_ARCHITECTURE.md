# Software Architecture Document

**Aignostics Python SDK**

**Version:** 0.2.105  
**Date:** August 12, 2025  
**Status:** Draft

---

## 1. Overview

### 1.1 Context

The Aignostics Python SDK is a comprehensive client library that provides programmatic access to the Aignostics AI Platform services. It serves as a bridge between local development environments and cloud-based AI services, enabling developers to interact with applications, manage data buckets, process datasets, and utilize various AI-powered tools through both command-line and graphical interfaces.

The SDK is designed to support data scientists, researchers, and developers working with digital pathology, whole slide imaging (WSI), and pathological applications in the life pathology domain.

### 1.2 General Architecture and Patterns Applied

The SDK follows a **Modulith Architecture** pattern, organizing functionality into cohesive modules while maintaining a monolithic deployment structure. This approach provides the benefits of modular design (clear boundaries, focused responsibilities) while avoiding the complexity of distributed systems.

**Key Architectural Patterns:**

- **Modulith Pattern**: Self-contained modules with clear boundaries and minimal inter-module dependencies
- **Dependency Injection**: Dynamic discovery and registration of services, CLI commands, and GUI pages
- **Service Layer Pattern**: Core business logic encapsulated in service classes with consistent interfaces
- **Dual Presentation Layers**:
  - (a) **CLI Layer**: Command-line interface using Typer framework
  - (b) **GUI Layer**: Web-based graphical interface using NiceGUI framework
- **Settings-based Configuration**: Environment-aware configuration management using Pydantic Settings
- **Plugin Architecture**: Optional modules that can be enabled/disabled based on available dependencies

```mermaid
graph TB
    subgraph "Presentation Layer"
        CLI[CLI Interface<br/>Typer]
        GUI[GUI Interface<br/>NiceGUI/Launchpad]
        NOTEBOOK[Notebook Server<br/>Marimo/FastAPI]
    end

    subgraph "Domain Services"
        AS[Application Service]
        BS[Bucket Service]
        DS[Dataset Service]
        NS[Notebook Service]
        WS[WSI Service]
        QS[QuPath Service]
        SS[System Service]
    end

    subgraph "Platform Layer"
        PS[Platform Service<br/>API Client]
        AUTH[Authentication]
        CLIENT[HTTP Client]
    end

    subgraph "Infrastructure Layer"
        DI[Dependency Injection<br/>Auto-discovery]
        SETTINGS[Settings Management<br/>Pydantic]
        LOGGING[Logging & Monitoring<br/>Sentry/Logfire]
        BOOT[Boot Sequence]
    end

    subgraph "External Services"
        PLATFORM_API[Aignostics Platform API]
        CLOUD_STORAGE[Cloud Storage<br/>Google Cloud/S3]
        IDC[NCI Image Data Commons]
    end

    subgraph "Third-party Integration"
        QUPATH_EXT[QuPath Integration]
        IDC_INDEX[IDC Index]
        BOTTLE[Embedded Web Server]
    end

    %% Presentation to Services
    CLI --> AS
    CLI --> BS
    CLI --> DS
    CLI --> NS
    CLI --> WS
    CLI --> QS
    CLI --> SS

    GUI --> AS
    GUI --> BS
    GUI --> DS
    GUI --> WS
    GUI --> SS

    NOTEBOOK --> AS
    NOTEBOOK --> BS

    %% Inter-service Dependencies (verified from code)
    AS --> BS
    AS --> PS
    AS --> WS
    AS --> QS

    %% Platform connections
    PS --> AUTH
    PS --> CLIENT

    %% Infrastructure connections
    DI --> CLI
    DI --> GUI
    BOOT --> DI
    BOOT --> LOGGING
    BOOT --> SETTINGS

    %% External connections (verified from README/code)
    CLIENT --> PLATFORM_API
    BS --> CLOUD_STORAGE
    DS --> IDC

    %% Third-party integrations
    QS --> QUPATH_EXT
    DS --> IDC_INDEX

    %% Settings injection (all services use settings)
    SETTINGS -.-> AS
    SETTINGS -.-> BS
    SETTINGS -.-> DS
    SETTINGS -.-> PS
```

### 1.3 Language and Frameworks

**Core Technologies:**

- **[Python 3.11+](https://www.python.org/)**: Primary programming language with full type hints and modern features
- **[Typer](https://typer.tiangolo.com/)**: CLI framework for building intuitive command-line interfaces with automatic help generation
- **[NiceGUI](https://nicegui.io/)**: Modern web-based GUI framework for creating responsive user interfaces
- **[FastAPI](https://fastapi.tiangolo.com/)**: High-performance web framework for API endpoints (inherited from template)
- **[Pydantic](https://docs.pydantic.dev/)**: Data validation and settings management with type safety
- **[Requests](https://docs.python-requests.org/)**: HTTP client library for API communication

**Key Dependencies:**

- **[aignx-codegen](https://github.com/aignostics/aignx-codegen)**: Auto-generated API client for Aignostics Platform
- **[Marimo](https://marimo.io/)**: Interactive notebook environment for data exploration
- **[Google CRC32C](https://github.com/googleapis/python-crc32c)**: Data integrity verification for file transfers
- **[Humanize](https://github.com/python-humanize/humanize)**: Human-readable formatting for file sizes, dates, and progress

**Optional Extensions:**

- **[QuPath](https://qupath.github.io/) Integration**: Advanced pathology image analysis capabilities
- **WSI Processing**: Whole slide image format support and processing
- **[Jupyter Notebook](https://jupyter.org/)**: Alternative notebook environment support

### 1.4 Build Chain and CI/CD

The project implements a comprehensive DevOps pipeline with multiple quality gates and automated processes:

```mermaid
flowchart TD
    %% Triggers
    PUSH[Push to Branch]
    TAG[Tag v*.*.*]
    PR[Pull Request]
    SCHEDULED[Scheduled Events]

    %% Quality Gates - Always Run
    LINT[Lint<br/>Ruff + MyPy]
    AUDIT[Audit<br/>Security + Licenses]
    TEST[Test Matrix<br/>Multi-OS + Python 3.11-3.13]
    CODEQL[CodeQL<br/>Security Analysis]

    %% Compliance - Always After Quality Gates
    KETRYX[Ketryx Integration<br/>Compliance Reporting]

    %% Build & Package - Only on Tags
    PACKAGE_PUBLISH[Package Publish<br/>PyPI + Native Builds]
    DOCKER_PUBLISH[Docker Publish<br/>All + Slim variants]

    %% Publishing Outputs
    PYPI[PyPI Release]
    DOCKER_HUB[Docker Hub]
    GHCR[GitHub Registry]
    DOCS[Documentation]

    %% Security & Monitoring
    TRIVY[Trivy Scanning]
    SENTRY[Sentry Monitoring]
    LOGFIRE[Logfire Observability]

    %% Trigger connections to Quality Gates
    PUSH --> LINT
    PUSH --> AUDIT
    PUSH --> TEST
    PUSH --> CODEQL

    TAG --> LINT
    TAG --> AUDIT
    TAG --> TEST
    TAG --> CODEQL

    PR --> LINT
    PR --> AUDIT
    PR --> TEST
    PR --> CODEQL

    SCHEDULED --> AUDIT
    SCHEDULED --> TEST
    SCHEDULED --> CODEQL

    %% Quality Gates to Compliance
    LINT --> KETRYX
    AUDIT --> KETRYX
    TEST --> KETRYX
    CODEQL --> KETRYX

    %% Build/Publish - Only on Tags after Compliance
    KETRYX -->|Only on Tags| PACKAGE_PUBLISH
    KETRYX -->|Only on Tags| DOCKER_PUBLISH

    %% Publishing Outputs
    PACKAGE_PUBLISH --> PYPI
    PACKAGE_PUBLISH --> DOCS
    DOCKER_PUBLISH --> DOCKER_HUB
    DOCKER_PUBLISH --> GHCR

    %% Security & Monitoring
    DOCKER_PUBLISH --> TRIVY
    PYPI --> SENTRY
    DOCKER_HUB --> LOGFIRE

    %% Styling
    classDef trigger fill:#e3f2fd,stroke:#1976d2
    classDef quality fill:#e8f5e8,stroke:#388e3c
    classDef compliance fill:#fff3e0,stroke:#f57c00
    classDef build fill:#f3e5f5,stroke:#7b1fa2
    classDef publish fill:#ffebee,stroke:#d32f2f
    classDef monitor fill:#fce4ec,stroke:#c2185b

    class PUSH,TAG,PR,SCHEDULED trigger
    class LINT,AUDIT,TEST,CODEQL quality
    class KETRYX compliance
    class PACKAGE_PUBLISH,DOCKER_PUBLISH build
    class PYPI,DOCKER_HUB,GHCR,DOCS publish
    class TRIVY,SENTRY,LOGFIRE monitor
```

**Build Chain and CI/CD:**

- **Code Generation**: Automated API client generation from OpenAPI specifications

**Code Quality & Analysis:**

- **Linting with Ruff**: Fast Python linter and formatter following Black code style
- **Static Type Checking with MyPy**: Strict type checking in all code paths
- **Pre-commit Hooks**: Automated quality checks including `detect-secrets` and `pygrep`
- **Code Quality Analysis**: SonarQube and GitHub CodeQL integration

**Testing & Coverage:**

- **Unit and E2E Testing with pytest**: Comprehensive test suite with parallel execution
- **Matrix Testing with Nox**: Multi-environment testing across Python versions
- **Test Coverage Reporting**: Codecov integration with coverage artifacts
- **Regression Testing**: Automated detection of breaking changes

**Security & Compliance:**

- **Dependency Monitoring**: Renovate and GitHub Dependabot for automated updates
- **Vulnerability Scanning**: `pip-audit` and Trivy security analysis
- **License Compliance**: `pip-licenses` with allowlist validation and attribution generation
- **SBOM Generation**: Software Bill of Materials in CycloneDX and SPDX formats

**Documentation & Release:**

- **Documentation with Sphinx**: Automated generation of HTML/PDF documentation
- **API Documentation**: Interactive OpenAPI specification with Swagger UI
- **Version Management**: `bump-my-version` for semantic versioning
- **Changelog Generation**: `git-cliff` for automated release notes
- **Multi-format Publishing**: PyPI packages, Docker images, and Read The Docs

**Monitoring & Observability:**

- **Error Monitoring**: Sentry integration for production error tracking
- **Logging & Metrics**: Logfire integration for structured logging and performance monitoring
- **Uptime Monitoring**: Prepared integration with monitoring services

**Deployment & Distribution:**

- **Multi-stage Docker Builds**: Fat (all extras) and slim (core only) variants
- **Multi-architecture Support**: ARM64 and AMD64 container images
- **Container Security**: Non-root execution within immutable containers
- **Registry Publishing**: Docker.io and GitHub Container Registry with attestations

**Development Environment:**

- **Dev Containers**: One-click development environments with GitHub Codespaces
- **VSCode Integration**: Optimized settings and extensions for development all found under ./vscode directory
- **GitHub Copilot**: Custom instructions and prompts for AI-assisted development
- **Local CI/CD**: Act integration for running GitHub Actions locally

### 1.5 Layers and Modules

```mermaid
graph TB
    subgraph "Presentation Interfaces"
        CLI[CLI Interface<br/>Typer Commands]
        GUI[GUI Interface<br/>NiceGUI/Launchpad]
        NOTEBOOK[Notebook Interface<br/>Marimo Server]
    end

    subgraph "Domain Modules"
        APPLICATION[Application Module<br/>AI Application Management]
        BUCKET[Bucket Module<br/>Cloud File Storage]
        DATASET[Dataset Module<br/>Dataset Management]
        WSI[WSI Module<br/>Whole Slide Imaging]
        QUPATH[QuPath Module<br/>Pathology Integration]
        SYSTEM[System Module<br/>Health & Diagnostics]
        NOTEBOOK_MOD[Notebook Module<br/>Interactive Computing]
    end

    subgraph "Platform Layer"
        PLATFORM[Platform Module<br/>API Client & Auth]
    end

    subgraph "Infrastructure Layer"
        UTILS[Utils Module<br/>DI, Settings, Logging]
    end

    subgraph "Third-party Modules"
        THIRDPARTY[Third-party Module<br/>External Integrations]
    end

    %% Presentation to Domain Dependencies
    CLI --> APPLICATION
    CLI --> BUCKET
    CLI --> DATASET
    CLI --> WSI
    CLI --> QUPATH
    CLI --> SYSTEM
    CLI --> NOTEBOOK_MOD

    GUI --> APPLICATION
    GUI --> BUCKET
    GUI --> DATASET
    GUI --> WSI
    GUI --> SYSTEM
    GUI --> NOTEBOOK_MOD

    NOTEBOOK --> APPLICATION
    NOTEBOOK --> BUCKET
    NOTEBOOK --> DATASET

    %% Inter-module Dependencies (based on actual imports)
    APPLICATION --> PLATFORM
    APPLICATION --> BUCKET
    APPLICATION --> WSI
    APPLICATION --> QUPATH

    BUCKET --> PLATFORM
    DATASET --> PLATFORM
    WSI --> PLATFORM
    QUPATH --> THIRDPARTY
    NOTEBOOK_MOD --> PLATFORM

    %% Infrastructure Dependencies
    APPLICATION --> UTILS
    BUCKET --> UTILS
    DATASET --> UTILS
    WSI --> UTILS
    QUPATH --> UTILS
    SYSTEM --> UTILS
    NOTEBOOK_MOD --> UTILS
    PLATFORM --> UTILS

    %% Platform Dependencies
    PLATFORM --> UTILS

    %% Third-party Integrations
    DATASET --> THIRDPARTY
    THIRDPARTY --> UTILS

    %% Styling
    classDef presentation fill:#e3f2fd
    classDef domain fill:#e8f5e8
    classDef platform fill:#fff3e0
    classDef infrastructure fill:#fce4ec
    classDef thirdparty fill:#f3e5f5

    class CLI,GUI,NOTEBOOK presentation
    class APPLICATION,BUCKET,DATASET,WSI,QUPATH,SYSTEM,NOTEBOOK_MOD domain
    class PLATFORM platform
    class UTILS infrastructure
    class THIRDPARTY thirdparty
```

The SDK is organized into distinct layers, each with specific responsibilities:

#### Infrastructure Layer (`utils/`)

**Core Utilities and Cross-cutting Concerns:**

- **Boot Sequence**: Application initialization and dependency injection setup
- **Dependency Injection**: Dynamic discovery and registration of services and UI components
- **Settings Management**: Environment-aware configuration using Pydantic Settings
- **Logging & Monitoring**: Structured logging with Logfire and Sentry integration
- **Authentication**: Token-based authentication with caching mechanisms
- **Health Monitoring**: Service health checks and status reporting

#### Platform Layer (`platform/`)

**Foundation Services:**

- **API Client**: Auto-generated client for Aignostics Platform REST API
- **Authentication Service**: OAuth/JWT token management and renewal
- **Core Resources**: Applications, versions, runs, and user management
- **Exception Handling**: Standardized error handling and API response processing
- **Configuration**: Platform-specific settings and endpoint management

#### Domain Modules

Each domain module follows a consistent internal structure:

**Application Module (`application/`)**

- **Service** (`_service.py`): Core business logic for application management and execution
- **CLI** (`_cli.py`): Command-line interface for application operations
- **GUI** (`_gui/`): Web-based interface for application management
- **Settings** (`_settings.py`): Module-specific configuration
- **Utilities** (`_utils.py`): Helper functions and data transformations

**Bucket Module (`bucket/`)**

- **Service**: Cloud storage operations, file upload/download with progress tracking
- **CLI**: Command-line file management operations
- **GUI**: Drag-and-drop file manager interface
- **Settings**: Storage configuration and authentication

**Dataset Module (`dataset/`)**

- **Service**: Dataset creation, validation, and metadata management
- **CLI**: Batch dataset operations and validation
- **GUI**: Interactive dataset builder and explorer
- **Settings**: Dataset processing configuration

**WSI Module (`wsi/`)**

- **Service**: Whole slide image processing and format conversion
- **Utilities**: Image format detection and metadata extraction
- **Integration**: Support for various medical imaging formats (DICOM, TIFF, SVS)

**QuPath Module (`qupath/`)**

- **Service**: Integration with QuPath for advanced pathology analysis
- **Annotation Processing**: Import/export of pathology annotations
- **Project Management**: QuPath project creation and synchronization

**Notebook Module (`notebook/`)**

- **Service**: Marimo notebook server management
- **Templates**: Pre-configured notebook templates for common workflows
- **Integration**: Seamless data flow between notebooks and platform services

**System Module (`system/`)**

- **Service**: System diagnostics and environment information
- **Health Checks**: Comprehensive system health monitoring
- **Configuration**: System-level settings and capability detection

**Third-Party Integration (`third_party/`)**

- **Embedded Dependencies**: Vendored third-party libraries for reliability
- **IDC Index**: Integration with Image Data Commons for medical imaging datasets
- **Bottle.py**: Lightweight WSGI micro web-framework for specific use cases

#### Presentation Layer

**CLI Interface (`cli.py`)**

- Auto-discovery and registration of module CLI commands
- Consistent help text and error handling across all commands
- Progress indicators and interactive prompts
- Support for both interactive and scripted usage

**GUI Interface (`gui/`)**

- Responsive web-based interface using NiceGUI
- Consistent theming and layout across all modules
- Real-time progress tracking and status updates
- File drag-and-drop capabilities and interactive forms

## 2. Design Principles

### 2.1 Modular Architecture

Each module is designed as a self-contained unit with:

- **Clear Boundaries**: Well-defined interfaces and minimal coupling
- **Consistent Structure**: Standardized organization across all modules
- **Independent Testing**: Module-specific test suites with isolated dependencies
- **Optional Dependencies**: Graceful degradation when optional features are unavailable

### 2.2 Dependency Injection

The SDK uses a sophisticated dependency injection system:

- **Automatic Discovery**: Services and UI components are automatically registered
- **Dynamic Loading**: Modules are loaded on-demand based on available dependencies
- **Lifecycle Management**: Proper initialization and cleanup of resources
- **Configuration Injection**: Settings are automatically injected into services

### 2.3 Configuration Management

Hierarchical configuration system:

- **Environment Variables**: Platform and module-specific environment variables
- **Settings Files**: `.env` files for local development configuration
- **Default Values**: Sensible defaults for all configuration options
- **Validation**: Type-safe configuration with Pydantic validation

### 2.4 Error Handling and Resilience

Comprehensive error handling strategy:

- **Typed Exceptions**: Domain-specific exception hierarchies
- **Graceful Degradation**: Fallback behavior when services are unavailable
- **Retry Logic**: Automatic retry with exponential backoff for transient failures
- **User-Friendly Messages**: Clear error messages with actionable guidance

### 2.5 Security and Privacy

Security-first design principles:

- **Token-based Authentication**: Secure API authentication with automatic refresh
- **Sensitive Data Protection**: Automatic masking of secrets in logs and outputs
- **Input Validation**: Comprehensive validation of all user inputs and API responses
- **Secure Defaults**: All security settings default to the most secure option

## 3. Integration Patterns

### 3.1 Platform API Integration

The SDK integrates with the Aignostics Platform through:

- **Auto-generated Client**: Type-safe API client generated from OpenAPI specifications
- **Authentication Handling**: Automatic token management and renewal
- **Request/Response Transformation**: Conversion between API models and SDK objects
- **Error Mapping**: Platform API errors mapped to SDK-specific exceptions

### 3.2 File System Integration

Comprehensive file system operations:

- **Progress Tracking**: Real-time progress for large file operations
- **Integrity Verification**: CRC32C checksums for data integrity
- **Resume Capability**: Ability to resume interrupted file transfers
- **Cross-platform Compatibility**: Consistent behavior across operating systems

### 3.3 External Tool Integration

Seamless integration with external tools:

- **QuPath**: Direct integration for pathology image analysis
- **Jupyter/Marimo**: Notebook environments for interactive data exploration
- **File Managers**: Native file manager integration for easy file access
- **Web Browsers**: Embedded browser components for rich user interfaces

## 4. Quality Assurance

### 4.1 Testing Strategy

Multi-layered testing approach:

- **Unit Tests**: Individual component testing with >85% coverage requirement using **[pytest](https://docs.pytest.org/)** with **[pytest-cov](https://pytest-cov.readthedocs.io/)** for coverage reporting
- **Integration Tests**: Module interaction testing with real API calls using **[pytest](https://docs.pytest.org/)** and **[pytest-docker](https://pytest-docker.readthedocs.io/)** for container-based testing
- **End-to-End Tests**: Complete workflow testing from CLI and GUI using **[pytest](https://docs.pytest.org/)** with **[NiceGUI testing plugin](https://nicegui.io/documentation/section_testing)** and **[pytest-selenium](https://pytest-selenium.readthedocs.io/)**
- **Performance Tests**: Benchmarking of critical operations using **[scalene](https://github.com/plasma-umass/scalene)** profiler and **[pytest-timeout](https://pypi.org/project/pytest-timeout/)**
- **Security Tests**: Vulnerability scanning using **[pip-audit](https://github.com/pypa/pip-audit)** and **[detect-secrets](https://github.com/Yelp/detect-secrets)** pre-commit hooks
- **Regression Tests**: Automated detection of breaking changes using **[pytest-regressions](https://pytest-regressions.readthedocs.io/)**
- **Parallel Execution**: Multi-process test execution using **[pytest-xdist](https://pytest-xdist.readthedocs.io/)**
- **Async Testing**: Asynchronous code testing using **[pytest-asyncio](https://pytest-asyncio.readthedocs.io/)**
- **Long-running Tests**: Scheduled integration tests marked with `@pytest.mark.long_running` and `@pytest.mark.scheduled`

### 4.2 Code Quality

Automated code quality enforcement:

- **Style Consistency**: Automated formatting with Ruff/Black
- **Type Safety**: 100% type annotation coverage with MyPy strict mode
- **Complexity Monitoring**: Cyclomatic complexity limits and code metrics
- **Security Scanning**: Automated detection of security vulnerabilities

### 4.3 Documentation Standards

Comprehensive documentation requirements:

- **API Documentation**: Auto-generated from type hints and docstrings
- **User Guides**: Step-by-step tutorials for common workflows
- **Architecture Documentation**: This document and module-specific designs
- **Release Notes**: Automated changelog generation from commit messages

## 5. Deployment and Operations

### 5.1 Distribution Channels

Multiple distribution methods:

- **PyPI Package**: Standard Python package installation via pip/uv
- **Docker Images**: Containerized deployment with multiple variants
- **Source Installation**: Direct installation from GitHub repository
- **Development Setup**: One-click development environment setup

### 5.2 Configuration Management

Environment-aware configuration:

- **Development**: Local `.env` files with development defaults
- **Testing**: Isolated test configuration with mock services
- **Production**: Environment variables with validation and defaults
- **Container**: Container-specific configuration and health checks

### 5.3 Monitoring and Observability

Production monitoring capabilities:

- **Health Endpoints**: Service health checks for monitoring systems
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Metrics Collection**: Performance metrics and usage analytics
- **Error Tracking**: Automatic error reporting to monitoring services

---

This architecture document reflects the current state of the Aignostics Python SDK as of August 2025. The design emphasizes modularity, maintainability, and extensibility while providing a consistent developer experience across different interaction modes (CLI, GUI, API).
