---
itemId: SPEC-APPLICATION-SERVICE  
itemTitle: Application Module Specification
itemType: Software Item Spec  
itemFulfills: SWR-APPLICATION-1-1, SWR-APPLICATION-1-2  
Layer: Domain Service  
Module: Application  
Version: 0.2.106  
Date: September 9, 2025
---

## 1. Description

### 1.1 Purpose

The Application Module provides comprehensive management of AI applications and their execution lifecycle on the Aignostics Platform. It enables users to discover, submit, monitor, and retrieve results from computational pathology applications through a unified interface.

The module implements a domain service layer that orchestrates interactions between the platform API, local file systems, and multiple specialized services (WSI, bucket, QuPath) to provide a unified interface for AI application workflows. It abstracts the complexity of the underlying platform through a multi-modal approach, offering CLI, GUI, and programmatic interfaces that coordinate the complete lifecycle from data preparation through result analysis.

### 1.2 Functional Requirements

The Application Module shall:

- **FR-01** **Application Discovery**: List and browse available applications with filtering capabilities and detailed information retrieval
- **FR-02** **Data Preparation**: Automatically scan directories for whole slide images (WSI), extract comprehensive metadata, and validate file formats
- **FR-03** **File Upload Management**: Provide secure, chunked file upload to cloud storage with progress tracking and integrity verification
- **FR-04** **Run Lifecycle Management**: Submit, monitor, cancel, and delete application runs with real-time status updates
- **FR-05** **Result Download**: Progressive download of analysis results with resumable operations and organized directory hierarchies
- **FR-06** **QuPath Integration**: Automatic QuPath project creation with downloaded results for pathology analysis
- **FR-07** **Multi-Modal Interface**: Provide CLI, GUI, and programmatic interfaces for different user workflows

### 1.3 Non-Functional Requirements

- **Performance**: Handle multi-gigabyte whole slide images with memory-efficient streaming processing through bucket and WSI service integration
- **Security**: Implement data integrity verification, secure token-based authentication, and comprehensive input validation
- **Reliability**: Provide graceful error handling with typed exceptions, resumable operations after interruption, and partial failure handling for batch operations
- **Usability**: Offer real-time progress tracking, user-friendly error messages, and consistent interfaces across CLI/GUI/API
- **Scalability**: Support large-scale operations through integration with cloud storage and platform services

### 1.4 Constraints and Limitations

- Platform API compatibility requirements with auto-generated client integration
- File format support limited to major medical imaging formats (DICOM, TIFF, SVS)
- Memory management constraints for large file processing with configurable chunk sizes
- Optional QuPath integration requiring ijson dependency for full functionality

---

## 2. Architecture and Design

### 2.1 Module Structure

```
application/
├── _service.py          # Core business logic and application lifecycle management
├── _cli.py             # Command-line interface for application operations
├── _gui/               # Web-based GUI components
│   ├── _frame.py        # Main GUI application frame
│   ├── _page_index.py   # Application discovery and selection page
│   ├── _page_application_describe.py # Application details and description page
│   ├── _page_application_run_describe.py # Run details and management page
│   ├── _page_builder.py # Dynamic page builder utilities
│   ├── _utils.py        # GUI utility functions
│   └── assets/          # Static assets (images, animations, icons)
├── _settings.py        # Module-specific configuration and environment variables
├── _utils.py          # Helper functions for metadata processing and validation
└── __init__.py        # Module exports and public API
```

### 2.2 Key Components

| Component               | Type  | Purpose                                                        | Public API                                                                                                                                                                           |
| ----------------------- | ----- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `DownloadProgressState` | Enum  | Enumeration of download progress states                        | `INITIALIZING`, `QUPATH_ADD_INPUT`, `CHECKING`, `WAITING`, `DOWNLOADING`, `QUPATH_ADD_RESULTS`, `QUPATH_ANNOTATE_INPUT_WITH_RESULTS`, `COMPLETED`                                    |
| `DownloadProgress`      | Model | Progress tracking for download operations with computed fields | `total_artifact_count`, `total_artifact_index`, `item_progress_normalized`, `artifact_progress_normalized`                                                                           |
| `Service`               | Class | Main service class for application lifecycle management        | `applications()`, `application_run_submit()`, `application_run_download()`, `application_runs()`, `application_run()`, `application_run_cancel()`, `application_run_result_delete()` |

### 2.3 Design Patterns

- **Service Layer Pattern**: Core business logic encapsulated in ApplicationService with consistent interfaces
- **Dependency Injection**: Dynamic discovery and lazy initialization of platform clients and dependent services
- **Observer Pattern**: Progress tracking through queue-based communication and callback mechanisms
- **Strategy Pattern**: Multi-modal interface design with CLI, GUI, and programmatic access patterns

---

## 3. Inputs and Outputs

### 3.1 Inputs

| Input Type                 | Source        | Code Location                                                 |
| -------------------------- | ------------- | ------------------------------------------------------------- |
| **Supported WSI Files**    | CLI/GUI       | `WSI_SUPPORTED_FILE_EXTENSIONS` in `constants.py`             |
| **Application Version ID** | API           | `Service.application_run_submit(application_version_id: str)` |
| **Input Items**            | API           | `Service.application_run_submit(items: list[InputItem])`      |
| **Run ID**                 | API           | `Service.application_run_download(run_id: str)`               |
| **Upload Chunks**          | Configuration | Constants in `_service.py`                                    |

### 3.2 Outputs

| Output Type            | Destination      | Code Location                                    |
| ---------------------- | ---------------- | ------------------------------------------------ |
| **Application Runs**   | Platform API     | `Service.application_run_submit()` return value  |
| **Downloaded Results** | Local filesystem | `Service.application_run_download()` side effect |
| **QuPath Projects**    | Local filesystem | QuPath integration when `has_qupath_extra=True`  |
| **Progress Updates**   | Callback/GUI     | `DownloadProgress` model with computed fields    |
| **Metadata Reports**   | CLI/GUI          | CLI commands and service methods                 |

### 3.3 Data Flow

```mermaid
graph TD
    A[WSI Files] --> B[WSI Service]
    B --> C[Metadata Extraction]
    C --> D[Input Items Creation]

    D --> E[Bucket Service]
    E --> F[File Upload to Cloud Storage]
    F --> G[Platform API]
    G --> H[Application Run Submission]

    H --> I[Platform Processing]
    I --> J[Run Status Monitoring]
    J --> K{Run Complete?}
    K -->|No| J
    K -->|Yes| L[Result Download]

    L --> M[Bucket Service Download]
    M --> N[Local File System]
    N --> O{QuPath Available?}
    O -->|Yes| P[QuPath Integration]
    O -->|No| Q[Results Only]

    R[Settings/_settings.py] --> B
    R --> E
    R --> G

    S[Progress Tracking] --> F
    S --> L
    S --> P

    T[CLI/GUI Input] --> A
    U[DownloadProgress Model] --> S

    subgraph "Application Service Layer"
        V[Service.applications]
        W[Service.application_run_submit]
        X[Service.application_run_download]
        Y[Service.application_run_cancel]
    end

    D --> W
    L --> X
    J --> Y

    subgraph "External Dependencies"
        G
        E
        B
    end

    subgraph "Progress States"
        Z1[INITIALIZING]
        Z2[CHECKING]
        Z3[DOWNLOADING]
        Z4[QUPATH_ADD_RESULTS]
        Z5[COMPLETED]
    end

    S --> Z1
    Z1 --> Z2
    Z2 --> Z3
    Z3 --> Z4
    Z4 --> Z5
```

---

## 4. Interface Definitions

### 4.1 Public API

#### Core Service Interface

```python
class Service:
    """Service of the application module."""

    def applications(self) -> list[Application]:
        """List all available applications with filtering capabilities

        Returns:
            List of Application objects with metadata

        Raises:
            Exception: When application list cannot be retrieved
        """
        pass

    def application_run_submit(
        self,
        application_version_id: str,
        items: list[InputItem]
    ) -> ApplicationRun:
        """Submit application run with validated inputs

        Args:
            application_version_id: ID of the application version to run
            items: List of items to process with metadata

        Returns:
            ApplicationRun object with run details

        Raises:
            ValueError: When input validation fails
            RuntimeError: When submission fails
        """
        pass
    def application_run_download(
        self,
        run_id: str,
        output_dir: Path,
        progress_callback: Optional[Callable] = None
    ) -> DownloadProgress:
        """Download results with progress tracking

        Args:
            run_id: Application run identifier
            output_dir: Directory for downloaded results
            progress_callback: Optional callback for progress updates

        Returns:
            DownloadProgress object with completion status

        Raises:
            NotFoundException: When run ID is invalid
            RuntimeError: When download operation fails
        """
        pass
```

### 4.2 CLI Interface

**Command Structure:**

```bash
uvx aignostics application [subcommand] [options]
```

**Available Commands:**

- `list`: List all available applications with filtering
- `describe`: Get detailed information about a specific application
- `dump-schemata`: Export application schemata
- `run execute`: Combined prepare, upload, and submit workflow
- `run prepare`: Generate metadata from source directory
- `run upload`: Upload files to cloud storage
- `run submit`: Submit application run
- `run list`: List application runs
- `run describe`: Get detailed run information
- `run cancel`: Cancel running application
- `run result download`: Download run results
- `run result delete`: Delete run results

### 4.3 GUI Interface

- **Navigation**: Accessible through main application menu and dashboard
- **Key UI Components**:
  - Application discovery and selection interface
  - Interactive submission workflow with file management
  - Real-time progress tracking with visual indicators
  - Results management with download capabilities
  - Optional QuPath integration when available
- **User Workflows**:
  - Browse → Select → Upload → Submit → Monitor → Download → Analyze

---

## 5. Dependencies and Integration

### 5.1 Internal Dependencies

| Dependency Module | Usage Purpose                           | Interface Used                              |
| ----------------- | --------------------------------------- | ------------------------------------------- |
| Platform Service  | Core platform API communication         | Client initialization, authentication       |
| Bucket Service    | Cloud storage operations                | File upload/download, signed URL generation |
| WSI Service       | Medical image processing and metadata   | Format detection, metadata extraction       |
| Utils Module      | Settings, logging, dependency injection | Configuration management, service discovery |

### 5.2 External Dependencies

| Dependency    | Version  | Purpose                        | Optional/Required |
| ------------- | -------- | ------------------------------ | ----------------- |
| aignx-codegen | Latest   | Platform API client generation | Required          |
| ijson         | >=3.4.0  | QuPath integration             | Optional          |
| google-crc32c | >=1.7.1  | Data integrity verification    | Required          |
| humanize      | >=4.12.3 | Progress formatting            | Required          |
| tqdm          | >=4.67.1 | CLI progress indicators        | Required          |

### 5.3 Integration Points

- **Aignostics Platform API**: RESTful API integration for application management, run submission, and result retrieval
- **Cloud Storage Services**: Google Cloud Storage and AWS S3 integration through bucket service
- **QuPath Application**: Optional integration for pathology analysis and annotation management

---

## 6. Configuration and Settings

### 6.1 Configuration Parameters

Configuration is managed through environment variables with the prefix `AIGNOSTICS_APPLICATION_`. The module uses Pydantic settings for validation and secure credential handling.

| Parameter Pattern              | Type | Description                        | Required |
| ------------------------------ | ---- | ---------------------------------- | -------- |
| `AIGNOSTICS_APPLICATION_*`     | var  | Application-specific configuration | No       |
| Platform-specific chunk sizes  | int  | Configurable through platform API  | No       |
| Upload/download configurations | var  | Managed by bucket and WSI services | No       |

### 6.2 Environment Variables

| Variable                   | Purpose                            | Example Value                     |
| -------------------------- | ---------------------------------- | --------------------------------- |
| `AIGNOSTICS_APPLICATION_*` | Application-specific configuration | Various configuration parameters  |
| `AIGNOSTICS_PLATFORM_URL`  | Platform API endpoint              | `https://platform.aignostics.com` |
| `AIGNOSTICS_AUTH_TOKEN`    | Authentication token               | `eyJhbGciOiJSUzI1NiIs...`         |

---

## 7. Error Handling and Validation

### 7.1 Error Categories

| Error Type          | Cause                            | Handling Strategy              | User Impact                     |
| ------------------- | -------------------------------- | ------------------------------ | ------------------------------- |
| `ValueError`        | Invalid input data or metadata   | Input validation with feedback | Clear validation error messages |
| `RuntimeError`      | Platform API or operation errors | Retry with exponential backoff | Error details and guidance      |
| `NotFoundException` | Missing runs or applications     | Graceful rejection with info   | Clear resource not found info   |
| `FileNotFoundError` | Missing input files              | File validation before upload  | File path verification help     |
| `ApiException`      | Platform API failures            | Retry mechanism with recovery  | API error details and guidance  |

### 7.2 Input Validation

- **WSI Files**: Format validation, file existence, size limits, and metadata extraction verification
- **Application Metadata**: Schema validation against application-specific requirements with type checking
- **Directory Paths**: Path existence, read permissions, and recursive access validation

### 7.3 Graceful Degradation

- **When QuPath dependencies are unavailable**: QuPath integration features are disabled with informative messages
- **When platform API is unreachable**: Local operations continue with cached data where possible
- **When individual file uploads fail**: Batch operations continue with error reporting for failed items

---

## 8. Security Considerations

### 8.1 Data Protection

- **Authentication**: Token-based authentication with automatic session management and secure credential storage
- **Data Encryption**: HTTPS for all API communications and encrypted storage for sensitive configuration
- **Access Control**: Platform-based authorization with organization-level permissions and role-based access

### 8.2 Security Measures

- **Input Sanitization**: Comprehensive validation of all user inputs including file paths and metadata
- **Secret Management**: Secure handling of authentication tokens and API keys with automatic masking in logs
- **Audit Logging**: Security events logged including authentication, authorization, and data access operations

---

## 9. Implementation Details

### 9.1 Key Algorithms

- **Metadata Generation Pipeline**: Multi-stage pipeline for WSI file discovery, metadata extraction, and validation
- **Progress Tracking Algorithm**: Normalized progress calculation with multi-level aggregation across files and operations
- **Chunked Upload Algorithm**: Memory-efficient streaming upload with integrity verification and resume capability

### 9.2 State Management

- **Configuration State**: Environment-aware settings management with Pydantic validation and secure credential handling
- **Runtime State**: Progress tracking state persistence for resumable operations and error recovery
- **Cache Management**: Platform client caching with lazy initialization and automatic session management

### 9.3 Concurrency and Threading

- **Async Operations**: Asynchronous file upload/download operations with configurable concurrency limits
- **Thread Safety**: Thread-safe progress tracking and state management with queue-based communication
- **Resource Management**: Proper cleanup of network connections and file handles with context managers
