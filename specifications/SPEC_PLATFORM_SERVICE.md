---
itemId: SPEC-PLATFORM-SERVICE
itemTitle: Platform Module Specification
itemType: Software Item Spec
itemFulfills: SWR-APPLICATION-1-1, SWR-APPLICATION-1-2, SWR-APPLICATION-2-1, SWR-APPLICATION-2-5, SWR-APPLICATION-2-6, SWR-APPLICATION-2-7, SWR-APPLICATION-2-9, SWR-APPLICATION-2-14, SWR-APPLICATION-2-15, SWR-APPLICATION-2-16, SWR-APPLICATION-3-1, SWR-APPLICATION-3-2, SWR-APPLICATION-3-3
Module: Platform
Layer: Platform Service
Version: 1.0.0
Date: 2025-09-09
---

## 1. Description

### 1.1 Purpose

The Platform Module provides the foundational authentication, API client management, and core service infrastructure for the Aignostics Python SDK. It enables secure communication with the Aignostics Platform API and serves as the primary entry point for all biomedical data analysis workflows. This module handles OAuth 2.0 authentication flows, token management, API client configuration, and provides the base infrastructure for higher-level application modules.

### 1.2 Functional Requirements

The Platform Module shall:

- **[FR-01]** Provide secure OAuth 2.0 authentication with support for both Authorization Code with PKCE and Device Authorization flows
- **[FR-02]** Manage JWT token lifecycle including acquisition, caching, validation, and refresh operations
- **[FR-03]** Configure and provide authenticated API clients for interaction with Aignostics Platform services
- **[FR-04]** Support multiple deployment environments (production, staging, development, test) with automatic endpoint configuration
- **[FR-05]** Provide CLI commands for user authentication operations (login, logout, whoami)
- **[FR-06]** Handle authentication errors with retry mechanisms and fallback flows
- **[FR-07]** Support proxy configurations and SSL certificate handling for enterprise environments
- **[FR-08]** Provide health monitoring for both public and authenticated API endpoints
- **[FR-09]** Manage application and application version resources with listing and filtering capabilities
- **[FR-10]** Create and manage application runs with status monitoring and result retrieval
- **[FR-11]** Download and verify file integrity using CRC32C checksums for run artifacts
- **[FR-12]** Generate signed URLs for secure Google Cloud Storage access
- **[FR-13]** Provide user and organization information retrieval with sensitive data masking options

### 1.3 Non-Functional Requirements

- **Performance**: 30s API timeout, 3s retry backoff, file-based token caching, 10-retry port availability checking
- **Security**: HTTPS-only communication, JWT validation (signature/audience/expiration), `SecretStr` protection, data masking, proxy/SSL support
- **Reliability**: Auto token refresh, browser-to-device flow fallback, re-authentication on failures, port conflict handling, socket reuse
- **Usability**: Predefined error messages, auto browser launch, device flow instructions, CLI commands (`login`/`logout`/`whoami`), environment auto-config
- **Scalability**: Token caching, configurable timeouts/retries, concurrent auth support, lazy API client initialization

### 1.4 Constraints and Limitations

- OAuth 2.0 dependency: Requires external Auth0 service for authentication, creating external dependency
- Browser dependency: Interactive flow requires web browser availability, limiting headless deployment options
- Network dependency: Requires internet connectivity for initial authentication and token validation
- Platform-specific: Designed specifically for Aignostics Platform API integration

---

## 2. Architecture and Design

### 2.1 Module Structure

```
platform/
├── _service.py          # Core service implementation with health monitoring
├── _client.py           # API client factory and configuration management
├── _authentication.py   # OAuth flows and token management
├── _cli.py             # Command-line interface for user operations
├── _settings.py        # Environment-specific configuration management
├── _constants.py       # Environment constants and endpoint definitions
├── _messages.py        # User-facing messages and error constants
├── _utils.py          # File operations, checksums, and GCS utilities
├── resources/         # Resource-specific implementations
│   ├── applications.py # Application and version management
│   ├── runs.py        # Application run lifecycle management
│   └── utils.py       # Shared resource utilities
└── __init__.py        # Public API exports and module interface
```

### 2.2 Key Components

| Component        | Type   | Purpose                                                 | Public API                                                                    |
| ---------------- | ------ | ------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `Client`         | Class  | Main entry point for authenticated API operations       | `__init__()`, `me()`, `application()`, `run()`<br/>Static: `get_api_client()` |
| `Service`        | Class  | Core service with health monitoring and user operations | `login()`, `logout()`, `get_user_info()`, `health()`, `info()`                |
| `Settings`       | Class  | Environment-aware configuration management              | Property accessors for all auth endpoints                                     |
| `Applications`   | Class  | Application resource management                         | `list()`, `versions` accessor                                                 |
| `ApplicationRun` | Class  | Run lifecycle and result management                     | `details()`, `cancel()`, `results()`, `download_to_folder()`                  |
| `Versions`       | Class  | Application version management                          | `list()`, `list_sorted()`, `latest()`, `details()`                            |
| `Runs`           | Class  | Application run management and creation                 | `create()`, `list()`, `list_data()`, `__call__()`                             |
| `utils`          | Module | Resource utility functions and pagination helpers       | `paginate()`                                                                  |

### 2.3 Design Patterns

- **Factory Pattern**: `Client.get_api_client()` creates configured API clients based on environment settings
- **Service Layer Pattern**: Business logic encapsulated in service classes with clean separation from API details
- **Strategy Pattern**: Multiple authentication flows (Authorization Code vs Device Flow) selected based on environment capabilities
- **Template Method Pattern**: Base authentication flow with specific implementations for different OAuth grant types

---

## 3. Inputs and Outputs

### 3.1 Inputs

| Input Type            | Source                  | Format/Type      | Validation Rules                                            | Code Location                                              |
| --------------------- | ----------------------- | ---------------- | ----------------------------------------------------------- | ---------------------------------------------------------- |
| Environment Variables | OS Environment          | String/SecretStr | Must match expected format for URLs and client IDs          | `_settings.py::Settings` class fields                      |
| Configuration Files   | .env files              | Key-value pairs  | Validated against Pydantic schema                           | `_settings.py::Settings` with pydantic-settings            |
| User Credentials      | Interactive/Device Flow | OAuth responses  | Validated against JWT specification                         | `_authentication.py::get_token()` OAuth flow handlers      |
| API Root URL          | Configuration           | URL string       | Must be valid HTTPS URL matching known endpoints            | `_settings.py::Settings.api_root` property                 |
| File Paths            | CLI/API                 | Path objects     | Must be valid filesystem paths with appropriate permissions | `_utils.py` file operations and `ApplicationRun` downloads |

### 3.2 Outputs

| Output Type      | Destination         | Format/Type            | Success Criteria                                    | Code Location                                        |
| ---------------- | ------------------- | ---------------------- | --------------------------------------------------- | ---------------------------------------------------- |
| JWT Access Token | Token cache/memory  | String                 | Valid JWT with required claims and unexpired        | `_authentication.py::get_token()` return value       |
| API Client       | Client applications | PublicApi object       | Authenticated and configured for target environment | `_client.py::Client.get_api_client()` factory method |
| User Information | CLI/Application     | UserInfo/Me objects    | Complete user and organization data                 | `_service.py::Service.get_user_info()` method        |
| Health Status    | Monitoring systems  | Health object          | Accurate service and dependency status              | `_service.py::Service.health()` method               |
| Downloaded Files | Local filesystem    | Binary/structured data | Verified checksums and complete downloads           | `_utils.py` download functions and `ApplicationRun`  |

### 3.3 Data Schemas

**Authentication Token Schema:**

```yaml
JWTToken:
  type: object
  properties:
    access_token:
      type: string
      description: JWT access token for API authentication
    token_type:
      type: string
      enum: ["Bearer"]
      description: Token type for authorization header
    expires_in:
      type: integer
      description: Token expiration time in seconds
    refresh_token:
      type: string
      description: Long-lived token for access token renewal
  required: [access_token, token_type, expires_in]
```

**User Information Schema:**

```yaml
UserInfo:
  type: object
  properties:
    user:
      type: object
      properties:
        id: { type: string }
        name: { type: string }
        email: { type: string }
        picture: { type: string, nullable: true }
    organization:
      type: object
      properties:
        id: { type: string }
        name: { type: string, nullable: true }
    role:
      type: string
      description: User role within organization
    token:
      type: object
      properties:
        expires_in: { type: integer }
  required: [user, organization, role, token]
```

### 3.4 Data Flow

```mermaid
graph TD
   A[User Request] --> B{Token Cached?}
   B -->|Yes| C[Use Cached Token]
   B -->|No| D[OAuth Authentication]

   D --> E{Browser Available?}
   E -->|Yes| F[Browser Login]
   E -->|No| G[Device Code Login]

   F --> H[Get JWT Token]
   G --> H
   C --> H

   H --> I[Create API Client]
   I --> J[Make API Request]
   J --> K[Return Results]

   L[Health Check] --> M[Check API Status]
```

---

## 4. Interface Definitions

### 4.1 Public API

#### Core Client Interface

```python
class Client:
    """Main client for interacting with the Aignostics Platform API."""

    def __init__(self, cache_token: bool = True) -> None:
        """Initializes authenticated API client with resource accessors."""

    def me(self) -> Me:
        """Retrieves current user and organization information."""

    def application(self, application_id: str) -> Application:
        """Finds specific application by ID."""

    def run(self, application_run_id: str) -> ApplicationRun:
        """Creates ApplicationRun instance for existing run."""

    @staticmethod
    def get_api_client(cache_token: bool = True) -> PublicApi:
        """Creates authenticated API client with proper configuration."""
```

#### Service Interface

```python
class Service(BaseService):
    """Core service for authentication and system operations."""

    def login(self, relogin: bool = False) -> bool:
        """Authenticates user and caches token."""

    def logout(self) -> bool:
        """Removes cached authentication token."""

    def get_user_info(self, relogin: bool = False) -> UserInfo:
        """Retrieves authenticated user information."""

    def health(self) -> Health:
        """Determines service and API health status."""

    def info(self, mask_secrets: bool = True) -> dict[str, Any]:
        """Returns service information including settings and user info."""
```

```python
class Applications:
    """Resource class for managing applications."""

    def __init__(self, api: PublicApi) -> None:
        """Initializes the Applications resource with the API client."""

    def list(self) -> Iterator[Application]:
        """Find all available applications."""

    @property
    def versions(self) -> Versions:
        """Access to application versions management."""
```

```python
class Versions:
    """Resource class for managing application versions."""

    def __init__(self, api: PublicApi) -> None:
        """Initializes the Versions resource with the API client."""

    def list(self, application: Application | str) -> Iterator[ApplicationVersion]:
        """Find all versions for a specific application."""

    def list_sorted(self, application: Application | str) -> list[ApplicationVersion]:
        """Get application versions sorted by semver, descending."""

    def latest(self, application: Application | str) -> ApplicationVersion | None:
        """Get latest version."""

    def details(self, application_version: ApplicationVersion | str) -> ApplicationVersion:
        """Retrieves details for a specific application version."""
```

```python
class Runs:
    """Resource class for managing application runs."""

    def __init__(self, api: PublicApi) -> None:
        """Initializes the Runs resource with the API client."""

    def create(self, application_version: str, items: list[ItemCreationRequest]) -> ApplicationRun:
        """Creates a new application run."""

    def list(self, for_application_version: str | None = None) -> Generator[ApplicationRun, Any, None]:
        """Find application runs, optionally filtered by application version."""

    def list_data(self, for_application_version: str | None = None, sort: str | None = None, page_size: int = 100) -> Iterator[ApplicationRunData]:
        """Fetch application runs data with optional filtering and sorting."""

    def __call__(self, application_run_id: str) -> ApplicationRun:
        """Retrieves an ApplicationRun instance for an existing run."""
```

```python
class ApplicationRun:
    """Represents a single application run."""

    def __init__(self, api: PublicApi, application_run_id: str) -> None:
        """Initializes an ApplicationRun instance."""

    @classmethod
    def for_application_run_id(cls, application_run_id: str) -> "ApplicationRun":
        """Creates an ApplicationRun instance for an existing run."""

    def details(self) -> ApplicationRunData:
        """Retrieves the current status of the application run."""

    def cancel(self) -> None:
        """Cancels the application run."""

    def results(
        self,
        nocache: bool = False,
        item_ids: list[str] | None = None,
        external_ids: list[str] | None = None,
    ) -> Iterator[ItemResultData]:
        """Retrieves the results of items in the run, optionally filtered by item or external IDs."""

    def item_status(self) -> dict[str, ItemStatus]:
        """Retrieves the status of all items in the run."""

    def download_to_folder(self, download_base: Path | str, checksum_attribute_key: str = "checksum_base64_crc32c") -> None:
        """Downloads all result artifacts to a folder."""
```

```python
class Settings(OpaqueSettings):
    """Configuration settings for the Aignostics SDK."""

    # Core API settings
    api_root: str
    audience: str
    authorization_base_url: str
    token_url: str
    device_url: str
    jws_json_url: str
    client_id_interactive: str

    # Optional settings
    client_id_device: SecretStr | None
    refresh_token: SecretStr | None
    cache_dir: str
    request_timeout_seconds: int
    authorization_backoff_seconds: int
```

### 4.2 CLI Interface

**Command Structure:**

```bash
uvx aignostics platform [subcommand] [options]
```

**Available Commands:**

- `login [--relogin]`: Authenticate user with platform
- `logout`: Remove authentication and clear cached tokens
- `whoami [--mask-secrets] [--relogin]`: Display current user information

### 4.3 GUI Interface

The Platform module provides foundational services but does not directly expose GUI components. It supports GUI applications by providing:

- **Authentication State**: Token validation and user information for GUI session management
- **API Client Factory**: Configured clients for GUI data operations
- **Health Monitoring**: Service status for GUI health indicators

---

## 5. Dependencies and Integration

### 5.1 Internal Dependencies

| Dependency Module | Usage Purpose                                        | Interface Used                                  |
| ----------------- | ---------------------------------------------------- | ----------------------------------------------- |
| Utils Module      | Logging, configuration loading, base service classes | `get_logger()`, `BaseService`, `OpaqueSettings` |

### 5.2 External Dependencies

| Dependency           | Version | Purpose                              | Optional/Required |
| -------------------- | ------- | ------------------------------------ | ----------------- |
| aignx.codegen        | ^X.X.X  | Auto-generated API client and models | Required          |
| requests             | ^2.31.0 | HTTP client for authentication flows | Required          |
| requests-oauthlib    | ^1.3.0  | OAuth 2.0 flow implementation        | Required          |
| PyJWT                | ^2.8.0  | JWT token validation and decoding    | Required          |
| crc32c               | ^2.7.0  | File integrity verification          | Required          |
| pydantic             | ^2.5.0  | Settings validation and data models  | Required          |
| pydantic-settings    | ^2.1.0  | Environment-based configuration      | Required          |
| google-cloud-storage | ^2.10.0 | Signed URL generation for downloads  | Optional          |
| typer                | ^0.9.0  | CLI framework                        | Required          |
| appdirs              | ^1.4.4  | Platform-appropriate cache directory | Required          |

### 5.3 Integration Points

- **Aignostics Platform API**: Primary integration via authenticated HTTP requests to platform endpoints
- **Auth0 Identity Service**: OAuth 2.0 flows for user authentication and token management
- **Google Cloud Storage**: Signed URL generation and secure file download capabilities
- **System Proxy Services**: Automatic proxy detection and configuration for enterprise environments

---

## 6. Configuration and Settings

### 6.1 Configuration Parameters

| Parameter                       | Type | Default                           | Description                  | Required |
| ------------------------------- | ---- | --------------------------------- | ---------------------------- | -------- |
| `api_root`                      | str  | `https://platform.aignostics.com` | Base URL of Aignostics API   | Yes      |
| `audience`                      | str  | Environment-specific              | OAuth audience claim         | Yes      |
| `scope`                         | str  | `offline_access`                  | OAuth scopes required        | Yes      |
| `organization_id`               | str  | None                              | Auth0 organization for OAuth | No       |
| `cache_dir`                     | str  | User cache directory              | Directory for token storage  | No       |
| `request_timeout_seconds`       | int  | 30                                | API request timeout          | No       |
| `authorization_backoff_seconds` | int  | 3                                 | Retry backoff time           | No       |

### 6.2 Environment Variables

| Variable                                   | Purpose                          | Example Value                                    |
| ------------------------------------------ | -------------------------------- | ------------------------------------------------ |
| `AIGNOSTICS_API_ROOT`                      | Override default API endpoint    | `https://platform-dev.aignostics.com`            |
| `AIGNOSTICS_CLIENT_ID_DEVICE`              | Device flow client ID            | `device_client_123`                              |
| `AIGNOSTICS_SCOPE`                         | OAuth scopes required            | `offline_access,read:data`                       |
| `AIGNOSTICS_AUDIENCE`                      | OAuth audience claim             | `https://custom-audience`                        |
| `AIGNOSTICS_AUTHORIZATION_BASE_URL`        | Custom authorization endpoint    | `https://custom.auth0.com/authorize`             |
| `AIGNOSTICS_TOKEN_URL`                     | Custom token endpoint            | `https://custom.auth0.com/oauth/token`           |
| `AIGNOSTICS_REDIRECT_URI`                  | Custom redirect URI              | `http://localhost:9000/`                         |
| `AIGNOSTICS_DEVICE_URL`                    | Custom device authorization URL  | `https://custom.auth0.com/oauth/device/code`     |
| `AIGNOSTICS_JWS_JSON_URL`                  | Custom JWS key set URL           | `https://custom.auth0.com/.well-known/jwks.json` |
| `AIGNOSTICS_CLIENT_ID_INTERACTIVE`         | Interactive flow client ID       | `interactive_client_123`                         |
| `AIGNOSTICS_ORGANIZATION_ID`               | Auth0 organization for OAuth     | `my-organization`                                |
| `AIGNOSTICS_REFRESH_TOKEN`                 | Long-lived refresh token         | `refresh_token_value`                            |
| `AIGNOSTICS_CACHE_DIR`                     | Custom cache directory           | `/custom/cache/path`                             |
| `AIGNOSTICS_REQUEST_TIMEOUT_SECONDS`       | API request timeout              | `60`                                             |
| `AIGNOSTICS_AUTHORIZATION_BACKOFF_SECONDS` | Authorization retry backoff time | `5`                                              |
| `AIGNOSTICS_ENV_FILE`                      | Custom .env file location        | `/path/to/custom/.env`                           |
| `REQUESTS_CA_BUNDLE`                       | SSL certificate bundle           | `/path/to/ca-bundle.crt`                         |

---

## 7. Error Handling and Validation

### 7.1 Error Categories

| Error Type            | Cause                                    | Handling Strategy                                   | User Impact                                  |
| --------------------- | ---------------------------------------- | --------------------------------------------------- | -------------------------------------------- |
| `AuthenticationError` | Invalid credentials or network issues    | Retry with exponential backoff; clear cached tokens | User prompted to re-authenticate             |
| `ConfigurationError`  | Invalid settings or missing endpoints    | Validate on startup; provide clear error messages   | Application fails fast with actionable error |
| `NetworkError`        | Connection timeouts or proxy issues      | Retry with backoff; fallback to device flow         | Automatic retry or alternative auth flow     |
| `TokenExpiredError`   | JWT token past expiration                | Automatic refresh using refresh token               | Transparent token renewal                    |
| `ValidationError`     | Invalid input parameters or file formats | Input sanitization and validation                   | Clear validation error messages              |

### 7.2 Input Validation

- **JWT Tokens**: Signature verification, expiration checking, audience validation, issuer verification
- **File Paths**: Existence validation, permission checking, path traversal protection
- **URLs**: Format validation, HTTPS requirement, endpoint whitelist checking
- **Configuration Values**: Type validation, range checking, required field validation

### 7.3 Graceful Degradation

- **When browser unavailable**: Automatically fallback to device authorization flow for headless environments
- **When authentication service unreachable**: Use cached tokens if available and not expired (with 5-minute buffer)
- **When callback port unavailable**: Retry port availability check with backoff, then fallback to device flow if port remains occupied
- **When proxy configuration fails**: Attempt direct connection using system proxy settings with fallback to no proxy
- **When token refresh fails**: Force new authentication flow while preserving user session context
- **When API health check fails**: Continue with cached authentication but report degraded service status

---

## 8. Security Considerations

### 8.1 Data Protection

- **Authentication**: OAuth 2.0 with PKCE for enhanced security; JWT tokens with short expiration times
- **Data Encryption**: HTTPS for all API communications; encrypted token storage with appropriate file permissions
- **Access Control**: Token-based API access; organization and role-based authorization claims

### 8.2 Security Measures

- **Input Sanitization**: URL validation, path traversal protection, parameter type checking
- **Secret Management**: SecretStr types for sensitive data; environment variable isolation; masked logging
- **Audit Logging**: Authentication events, token lifecycle, API access patterns
- **Token Security**: Automatic expiration, secure storage, validation on each use

---

## 9. Implementation Details

### 9.1 Key Algorithms and Business Logic

- **PKCE Flow**: OAuth 2.0 Authorization Code flow with Proof Key for Code Exchange for enhanced security in public clients. Supports optional `AIGNOSTICS_ORGANIZATION` parameter for Auth0 organization-specific authentication flows
- **Token Caching**: File-based token persistence with expiration tracking and automatic cleanup
- **Health Monitoring**: Multi-layer health checks including public endpoint availability and authenticated API access

### 9.2 State Management and Data Flow

- **Configuration State**: Pydantic-based settings with environment variable override hierarchy
- **Runtime State**: In-memory API client instances with lazy initialization
- **Cache Management**: File-based token cache with automatic expiration and cleanup

### 9.3 Performance and Scalability Considerations

- **Async Operations**: Synchronous design with thread-safe token operations
- **Thread Safety**: File-based locking for token cache operations; atomic file writes for token storage

---
