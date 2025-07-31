---
itemId: ADR-1-APPLICATION-DISCOVERY-SERVICE
itemTitle: Application Discovery and Navigation Service
itemType: Software Item Spec
itemFulfills: SWR-APPLICATION-1, SWR-APPLICATION-2, SWR-APPLICATION-3, SWR-APPLICATION-4
owner: engineering@aignostics.com
approvers: product@aignostics.com, architecture@aignostics.com
informed: stakeholders@aignostics.com
date: 2025-07-31
status: accepted
product: Platform
platform: Platform
components: 
  - src/aignostics/application/service.py
  - src/aignostics/application/cli.py
  - src/aignostics/platform/client.py
risk: low
sop: SW-SOP-01
---

# ADR-1: Application Discovery Service Architecture Pattern

## Status

Accepted

## Context

The Aignostics Python SDK requires a robust application discovery mechanism to enable users to:

* Browse available AI applications in the platform ecosystem
* Retrieve detailed application metadata including input/output specifications
* Navigate seamlessly between application discovery and execution workflows

Currently, application data is distributed across the Platform API (`/api/v1/applications`) with no centralized discovery service in the SDK. Users need both programmatic access (Python API) and command-line interfaces to discover and inspect applications before executing workflows.

The challenge is designing an architecture that provides consistent, performant access to application metadata while maintaining separation of concerns and testability.

## Decision Drivers

* **Developer Experience**: SDK users need intuitive programmatic and CLI access to application discovery
* **Consistency**: Identical data formats and error handling across all interface types (CLI, Python API, future GUI)
* **Maintainability**: Clear separation between business logic, API communication, and presentation layers
* **Platform Integration**: Leverage existing Platform API endpoints and OAuth2 authentication infrastructure
* **Testability**: Enable comprehensive unit and integration testing with mockable dependencies

## Considered Options

### Option 1: Service Layer Pattern with Platform API Client

Implement a dedicated ApplicationService that orchestrates application discovery operations while delegating Platform API communication to a specialized PlatformClient.

### Option 2: Direct API Integration Pattern

CLI and Python API interfaces make direct calls to Platform API endpoints without an intermediate service layer.

## Decision

We will implement **Option 1: Service Layer Pattern with Platform API Client**.

## Rationale

After evaluating the options against our decision drivers, the service layer pattern provides the optimal balance of maintainability, testability, and developer experience:

**Architecture Benefits:**
* **Clear Separation of Concerns**: Business logic (ApplicationService) separated from API communication (PlatformClient) and presentation layers (CLI/Python API)
* **Testability**: Service layer enables comprehensive unit testing with mocked Platform API responses
* **Consistency**: Single source of truth for application data formatting and error handling across all interfaces
* **Platform Integration**: Leverages existing OAuth2 authentication and `/api/v1/applications` endpoints

**Developer Experience:**
* **Intuitive API**: Clean `applications()` and `application(id)` methods for programmatic access
* **Rich CLI**: Commands like `aignostics application list --verbose` with standardized output formats
* **Consistent Error Handling**: Uniform error messages and exit codes across interfaces

**Performance Characteristics:**
* **Authenticated Caching**: OAuth2 tokens cached to minimize authentication overhead
* **Client Reuse**: Platform client instances reused within service lifecycle
* **No Data Caching**: Fresh API calls ensure real-time application availability (acceptable trade-off for current scale)

## Consequences

### Positive

* **Maintainable Architecture**: Clear boundaries between service logic, API communication, and presentation
* **Comprehensive Testing**: Service layer enables unit tests with mocked dependencies plus integration tests against real APIs
* **Consistent Interfaces**: Identical data formats and error handling across CLI and Python API
* **Platform Alignment**: Builds on existing `aignostics.application.Service` and `aignostics.platform.Client` patterns
* **Future Extensibility**: Service layer provides natural extension point for caching, filtering, and enhanced discovery features

### Negative

* **Network Dependency**: All operations require Platform API connectivity (no offline mode)
* **Authentication Overhead**: Users must authenticate before accessing application discovery
* **Additional Abstraction**: Service layer adds complexity compared to direct API calls
* **No Caching**: Each request makes fresh API calls, potential performance impact at scale

### Risks and Mitigation

* **Platform API Availability**: Risk mitigated by comprehensive error handling and clear user feedback
* **Authentication Token Expiration**: Risk mitigated by automatic token refresh in PlatformClient
* **API Rate Limits**: Risk mitigated by client-side respect for rate limiting headers

## Implementation Notes

### Architecture Overview

```mermaid
flowchart TB
    CLI[CLI Interface<br/>`aignostics application list`] --> AppService[ApplicationService<br/>Business Logic Layer]
    PythonAPI[Python API<br/>`sdk.applications()`] --> AppService

    %% Service Layer
    AppService --> PlatformClient[PlatformClient<br/>API Communication Layer]

    %% External Dependencies
    PlatformClient --> |OAuth2| Auth[Auth0 Authentication]
    PlatformClient --> |HTTPS| PlatformAPI[Platform API<br/>/api/v1/applications]

    %% Data Flow
    PlatformAPI --> ApplicationData[(Application Metadata)]

    classDef interface fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef service fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef external fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef data fill:#fff3e0,stroke:#f57c00,stroke-width:2px

    class CLI,PythonAPI interface
    class AppService,PlatformClient service
    class Auth,PlatformAPI external
    class ApplicationData data
```

### Core Components

**ApplicationService** (`aignostics.application.Service`)
* **Purpose**: Orchestrates application discovery operations with consistent business logic
* **Key Methods**: `applications()` for listing, `application(id)` for details
* **Responsibilities**: Data formatting, error handling, business rule enforcement

**PlatformClient** (`aignostics.platform.Client`)
* **Purpose**: Handles authenticated communication with Platform API endpoints
* **Key Features**: OAuth2 token management, automatic retry logic, rate limit handling
* **API Endpoints**: `/api/v1/applications`, `/api/v1/applications/{id}/versions`

### Interface Specifications

**CLI Interface**

```bash
# List all applications
aignostics application list
# Output: he-tme, test-app, ...

# List with verbose details
aignostics application list --verbose
# Output: he-tme (Artifacts: 2 input(s), 1 output(s))

# Describe specific application
aignostics application describe he-tme
# Output: Detailed application information with artifacts
```

**Python API Interface**

```python
from aignostics import ApplicationService

service = ApplicationService()

# List applications
apps = service.applications()
# Returns: [Application(id='he-tme', ...), Application(id='test-app', ...)]

# Get application details
app = service.application('he-tme')
# Returns: Application with full metadata

# Handle missing applications
try:
    app = service.application('nonexistent')
except NotFoundException as e:
    print(f"Error: {e}")  # "Application with ID 'nonexistent' not found."
```

### Error Handling Strategy

**Exception Hierarchy**

```python
class NotFoundException(Exception):
    """Raised when requested application cannot be found."""
    pass

class AuthenticationError(Exception):
    """Raised when Platform API authentication fails."""
    pass
```

**Error Translation**
* Service layer: Raises domain-specific exceptions (NotFoundException)
* CLI layer: Translates to appropriate exit codes (0=success, 2=not found)
* Python API: Propagates exceptions with clear error messages

### Testing Strategy

**Unit Tests**
* Service layer methods with mocked PlatformClient
* Error handling scenarios with controlled exceptions
* Data formatting and business logic validation

**Integration Tests**
* End-to-end CLI commands against test Platform API
* Authentication flow validation
* Real API response handling

**Contract Tests**
* Platform API response format validation
* Backward compatibility with API changes

### Alternative Options Considered

**Option 2: Direct API Integration**
* *Pros*: Simpler architecture, no abstraction overhead
* *Cons*: Code duplication across interfaces, harder testing, maintenance overhead
* *Rejected*: Fails maintainability and consistency requirements

## Related Decisions

* **Future ADR**: Caching strategy for application metadata (when performance requirements change)
* **Future ADR**: Application filtering and search capabilities
* **Future ADR**: GUI integration patterns for application discovery

## References

* [Platform API Documentation](docs/API_REFERENCE_v1.md)
* [CLI Implementation](src/aignostics/application/cli.py)
* [Service Implementation](src/aignostics/application/service.py)
* [Amazon ADR Template](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/)