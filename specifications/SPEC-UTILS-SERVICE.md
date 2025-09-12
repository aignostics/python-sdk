# Software Item Specification: Utils Module

---

**Item ID:** SPEC-UTILS-SERVICE  
**Item Type:** Software Item Spec  
**Item Fulfills:** TBD  
**Module:** Utils  
**Layer:** Infrastructure Service  
**Version:** 0.2.105  
**Date:** September 11, 2025

## 1. Description

### 1.1 Purpose

The Utils Module provides foundational infrastructure utilities for the Aignostics Python SDK. It serves as the core infrastructure layer that enables configuration management, dependency injection, logging, health monitoring, CLI preparation, GUI framework support, and cross-cutting concerns for all other modules in the SDK.

### 1.2 Functional Requirements

The Utils Module shall:

- **[FR-01]** Provide environment detection and configuration management with automatic .env file loading
- **[FR-02]** Implement dependency injection mechanisms for dynamic service discovery and registration
- **[FR-03]** Provide centralized logging infrastructure with configurable settings and external service integration
- **[FR-04]** Implement health monitoring models and status propagation for service health checks
- **[FR-05]** Support CLI preparation and dynamic command registration for typer-based interfaces
- **[FR-06]** Provide GUI framework abstractions and page builder patterns for web interface development
- **[FR-07]** Implement settings management with validation, serialization, and sensitive data handling
- **[FR-08]** Provide file system utilities for user data directory management and path sanitization
- **[FR-09]** Support process information gathering and runtime environment detection

### 1.3 Non-Functional Requirements

- **Performance**: Lightweight initialization with lazy loading of optional dependencies, efficient caching of discovered services
- **Security**: Secure handling of sensitive configuration data, proper sanitization of file paths, environment-based security controls
- **Reliability**: Graceful degradation when optional dependencies unavailable, robust error handling in service discovery
- **Usability**: Simple API surface with sensible defaults, comprehensive logging and debugging support
- **Scalability**: Efficient service discovery caching, support for dynamic module loading and registration

### 1.4 Constraints and Limitations

- **Optional Dependency Constraints**: Full functionality requires optional packages (nicegui, logfire, sentry, marimo)
- **Environment Detection**: Some features disabled in containerized or read-only environments
- **Configuration Dependency**: Relies on .env files and environment variables for configuration

---

## 2. Architecture and Design

### 2.1 Module Structure

```
utils/
├── __init__.py          # Module exports and conditional loading
├── _constants.py        # Runtime environment detection and project constants
├── _service.py          # Base service class with settings integration
├── _di.py              # Dependency injection and service discovery
├── _settings.py        # Pydantic settings utilities and validation
├── _health.py          # Health monitoring models and status propagation
├── _log.py             # Logging configuration and logger factory
├── _cli.py             # CLI preparation and dynamic command registration
├── _gui.py             # GUI framework abstractions and page builders
├── _fs.py              # File system utilities and path management
├── _process.py         # Process information and runtime detection
├── _console.py         # Rich console configuration
├── _logfire.py         # Logfire integration (optional)
├── _sentry.py          # Sentry integration (optional)
├── _notebook.py        # Marimo notebook utilities (optional)
└── boot.py            # Application bootstrap and initialization
```

### 2.2 Key Components

| Component         | Type  | Purpose                                | Public Interface                            | Dependencies |
| ----------------- | ----- | -------------------------------------- | ------------------------------------------- | ------------ |
| `BaseService`     | Class | Abstract base for all service classes  | Settings integration, health interface      | Pydantic     |
| `BasePageBuilder` | Class | Abstract base for GUI page builders    | Abstract page registration interface        | NiceGUI      |
| `Health`          | Class | Health status modeling and propagation | Status computation with component hierarchy | Pydantic     |
| `LogSettings`     | Class | Logging configuration management       | Environment-based logging configuration     | Rich         |
| `OpaqueSettings`  | Class | Base for settings with sensitive data  | Controlled serialization for sensitive data | Pydantic     |
| `ProcessInfo`     | Class | Process and runtime information        | System and environment metadata collection  | Core         |

_Note: For detailed implementation, refer to the source code in the `src/aignostics/utils/` directory._

### 2.3 Design Patterns

- **Abstract Base Class Pattern**: `BaseService` and `BasePageBuilder` provide standardized interfaces for extension across all SDK modules
- **Dependency Injection Pattern**: Dynamic discovery and registration of services using reflection-based service location
- **Settings Pattern**: Centralized configuration management using Pydantic settings with environment variable binding
- **Health Check Pattern**: Hierarchical health status modeling with automatic propagation of failure states
- **Factory Pattern**: Logger factory and service instantiation with settings injection

---

## 3. Inputs and Outputs

### 3.1 Inputs

| Input Type            | Source           | Data Type/Format      | Validation Rules                     | Business Rules              |
| --------------------- | ---------------- | --------------------- | ------------------------------------ | --------------------------- |
| Environment Variables | System/Container | Key-value strings     | Project-specific prefix validation   | Optional configuration      |
| Configuration Files   | Filesystem       | .env format           | Key-value pairs, optional file       | Fallback to defaults        |
| Settings Classes      | Code             | BaseSettings types    | Pydantic validation rules            | Must inherit from base      |
| Service Classes       | Code             | BaseService types     | Must inherit from BaseService        | Auto-discovery enabled      |
| PageBuilder Classes   | Code             | BasePageBuilder types | Must implement register_pages()      | GUI registration required   |
| Health Components     | Services         | Health objects        | Valid status and reason combinations | Component hierarchy support |

### 3.2 Outputs

| Output Type       | Destination      | Data Type/Format | Success Criteria                      | Error Conditions          |
| ----------------- | ---------------- | ---------------- | ------------------------------------- | ------------------------- |
| Logger Instances  | Application      | logging.Logger   | Configured logger with proper level   | Configuration errors      |
| Service Instances | Dependency Graph | BaseService      | Properly initialized with settings    | Settings validation fails |
| Health Status     | Monitoring       | Health objects   | Valid status with component hierarchy | Component failures        |
| GUI Application   | Web Browser      | NiceGUI app      | Running web application               | Port conflicts            |
| CLI Application   | Terminal         | Configured Typer | Registered commands available         | Command conflicts         |
| Settings Objects  | Services         | BaseSettings     | Validated configuration objects       | Environment errors        |
| File Paths        | Application      | Path objects     | Sanitized and validated paths         | Permission denied         |

### 3.3 Data Schemas

**Settings Schema:**

```yaml
# Source: Based on BaseSettings and OpaqueSettings contracts
settings:
  type: object
  description: Configuration object with environment binding
  properties:
    sensitive_fields:
      type: array
      description: Fields to exclude from serialization
    validation_rules:
      type: object
      description: Pydantic validators applied
  environment_binding: true
```

**Health Status Schema:**

```yaml
# Source: Health model in _health.py
health:
  type: object
  required: [status]
  properties:
    status:
      type: string
      enum: [UP, DOWN]
      description: Service health status
    reason:
      type: string
      nullable: true
      description: Optional reason for status
    components:
      type: object
      description: Hierarchical component health
      additionalProperties:
        $ref: "#/health"
```

_Note: Complete schemas available in implementation docstrings and type hints._

### 3.4 Data Flow

```
Environment/Config → Settings Loading → Service Initialization → Health Monitoring
Service Discovery → Dependency Injection → Component Registration → Application Ready
```

---

## 4. Interface Definitions

### 4.1 Public API

#### Core Service Interface

**BaseService Class**

- **Purpose**: Provides standardized service pattern for all SDK modules with settings integration
- **Key Capabilities**:
  - Settings-based initialization with automatic validation
  - Health status reporting with component hierarchy
  - Module identification for service discovery

**Input/Output Contracts**:

- **Initialization**: Accepts optional settings class, performs validation
- **Health Reporting**: Returns structured health status with components
- **Service Identity**: Provides module-based service identification

#### Dependency Injection Interface

**Service Discovery Functions**

- **locate_subclasses()**: Discovers all subclasses of given base class
- **locate_implementations()**: Creates instances of discovered service classes

#### Health Monitoring Interface

**Health Status Management**

- **Purpose**: Hierarchical health status modeling with automatic propagation
- **Capabilities**: Component health aggregation, status computation, failure propagation

_Note: For detailed method signatures, refer to the module's `__init__.py` and implementation files._

### 4.2 CLI Interface

**Command Structure:**

```bash
uvx aignostics [module-name] [subcommand] [options]
```

**CLI Preparation:**

| Function         | Purpose                       | Input Requirements | Output Format          |
| ---------------- | ----------------------------- | ------------------ | ---------------------- |
| `prepare_cli()`  | Dynamic command registration  | Typer instance     | Configured CLI         |
| Service commands | Module-specific functionality | Service parameters | Module-specific output |

### 4.3 GUI Interface

**GUI Framework Support:**

| Component         | Purpose                   | Requirements            | Integration        |
| ----------------- | ------------------------- | ----------------------- | ------------------ |
| `BasePageBuilder` | Page registration pattern | Abstract method impl    | NiceGUI framework  |
| `gui_run()`       | Application launcher      | Optional configuration  | Web browser launch |
| Page registration | Module UI integration     | PageBuilder inheritance | Dynamic discovery  |

---

## 5. Dependencies and Integration

### 5.1 Internal Dependencies

| Dependency Module | Usage Purpose              | Interface/Contract Used      | Criticality |
| ----------------- | -------------------------- | ---------------------------- | ----------- |
| None              | Utils is foundation module | Provides base classes to all | Required    |

### 5.2 External Dependencies

| Dependency          | Min Version | Purpose                            | Optional/Required | Fallback Behavior          |
| ------------------- | ----------- | ---------------------------------- | ----------------- | -------------------------- |
| `pydantic`          | ^2.0        | Settings validation and modeling   | Required          | N/A - core functionality   |
| `pydantic-settings` | ^2.0        | Environment-based configuration    | Required          | N/A - core functionality   |
| `rich`              | ^13.0       | Console output and formatting      | Required          | Basic console output       |
| `typer`             | ^0.12       | CLI framework and command handling | Required          | N/A - CLI functionality    |
| `python-dotenv`     | ^1.0        | Environment file loading           | Required          | Environment variables only |
| `nicegui`           | ^1.0        | GUI framework support              | Optional          | CLI-only mode              |
| `logfire`           | ^0.41       | Observability and monitoring       | Optional          | Standard logging           |
| `sentry-sdk`        | ^2.0        | Error tracking and performance     | Optional          | Local error handling       |
| `marimo`            | ^0.8        | Notebook utilities                 | Optional          | Notebook features disabled |

_Note: For exact version requirements, refer to `pyproject.toml` and dependency lock files._

### 5.3 Integration Points

- **All SDK Modules**: Provides foundational services through BaseService pattern
- **CLI Integration**: Dynamic command discovery and registration for all module CLIs
- **GUI Integration**: Page builder pattern for modular web interface development
- **External Monitoring**: Integration with Logfire and Sentry for observability

---

## 6. Configuration and Settings

### 6.1 Configuration Parameters

| Parameter                                 | Type | Default     | Description                              | Required |
| ----------------------------------------- | ---- | ----------- | ---------------------------------------- | -------- |
| `UNHIDE_SENSITIVE_INFO`                   | str  | N/A         | Context key for revealing sensitive data | No       |
| `__is_development_mode__`                 | bool | auto-detect | Development vs production mode           | No       |
| `__is_running_in_container__`             | bool | auto-detect | Container environment detection          | No       |
| `__is_running_in_read_only_environment__` | bool | auto-detect | Read-only environment detection          | No       |

### 6.2 Environment Variables

| Variable                          | Purpose                        | Example Value         |
| --------------------------------- | ------------------------------ | --------------------- |
| `AIGNOSTICS_ENV_FILE`             | Custom environment file path   | `/path/to/custom.env` |
| `AIGNOSTICS_RUNNING_IN_CONTAINER` | Container environment flag     | `true`                |
| `VERCEL_ENV`                      | Vercel deployment environment  | `production`          |
| `RAILWAY_ENVIRONMENT`             | Railway deployment environment | `production`          |

---

## 7. Error Handling and Validation

### 7.1 Error Categories

| Error Type          | Cause                               | Handling Strategy       | User Impact            |
| ------------------- | ----------------------------------- | ----------------------- | ---------------------- |
| `ValidationError`   | Invalid settings configuration      | Log error, fail fast    | Configuration required |
| `ImportError`       | Missing optional dependencies       | Graceful degradation    | Feature unavailable    |
| `FileNotFoundError` | Missing configuration files         | Use defaults            | Continue with defaults |
| `TypeError`         | Invalid service/builder inheritance | Log error, skip service | Service unavailable    |

### 7.2 Input Validation

- **Settings Classes**: Pydantic validation with custom validators for sensitive data
- **File Paths**: Sanitization and validation of user data directory paths
- **Environment Variables**: Type coercion and validation of environment configuration
- **Service Discovery**: Type checking for proper inheritance from base classes

### 7.3 Graceful Degradation

- **When NiceGUI unavailable**: GUI features disabled, CLI-only mode
- **When Logfire unavailable**: Standard logging without observability features
- **When Sentry unavailable**: Error tracking disabled, local logging only
- **When Marimo unavailable**: Notebook features disabled

---

## 8. Security Considerations

### 8.1 Data Protection

- **Sensitive Settings**: OpaqueSettings base class with controlled serialization excludes sensitive data from logs and exports
- **Environment Variables**: Secure loading and validation of configuration with proper access controls
- **File System Access**: Path sanitization and validation prevents directory traversal attacks

### 8.2 Security Measures

- **Input Sanitization**: Path component and full path sanitization with Windows drive letter preservation, prevents malicious path injection
- **Secret Management**: Controlled serialization of sensitive data with `OpaqueSettings.serialize_sensitive_info()` method
- **Environment Isolation**: Environment-specific behavior with container and read-only environment detection

---

## 9. Implementation Details

### 9.1 Key Algorithms and Business Logic

- **Service Discovery**: Reflection-based discovery with performance-optimized caching for dynamic service location
- **Health Propagation**: Recursive tree traversal algorithm for computing hierarchical health status with failure propagation
- **Settings Loading**: Environment variable binding with validation, type coercion, and sensitive data protection
- **Path Sanitization**: Security-focused path validation and normalization to prevent directory traversal

### 9.2 State Management and Data Flow

- **State Type**: Primarily stateless design with cached discovery results for performance
- **Data Persistence**: No persistent state maintained; configuration loaded from environment and constants
- **Cache Strategy**: In-memory caching of service discovery results with thread-safe access patterns

### 9.3 Performance and Scalability Considerations

- **Performance Characteristics**: Efficient lazy loading of optional dependencies, cached service discovery for repeated operations
- **Scalability Patterns**: Thread-safe service discovery enables concurrent access, stateless design supports horizontal scaling
- **Resource Management**: Memory-efficient caching with automatic cleanup, lightweight service initialization
- **Concurrency Model**: Thread-safe discovery caches, async-compatible patterns for GUI and web components

---

## Documentation Maintenance

### Verification and Updates

**Last Verified**: September 11, 2025  
**Verification Method**: Code review against implementation in `src/aignostics/utils/`  
**Next Review Date**: December 11, 2025

### Change Management

**Interface Changes**: Changes to BaseService or BasePageBuilder APIs require spec updates and version bumps  
**Implementation Changes**: Internal discovery algorithms don't require spec updates unless behavior changes  
**Dependency Changes**: Optional dependency changes should be reflected in fallback behavior section

### References

**Implementation**: See `src/aignostics/utils/` for current implementation  
**Tests**: See `tests/aignostics/utils/` for usage examples and verification  
**API Documentation**: Auto-generated from docstrings and type hints
