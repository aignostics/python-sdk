# CLAUDE.md - Platform Module

This file provides comprehensive guidance to Claude Code and human engineers when working with the `platform` module in this repository.

## Module Overview

The platform module serves as the foundational API client interface for the Aignostics Platform, providing secure, scalable, and enterprise-ready access to computational pathology services.

### Core Responsibilities

**Authentication & API Access:**

- **OAuth 2.0 Authentication**: Device flow, JWT validation, token lifecycle management with 5-minute refresh buffer
- **Environment Management**: Multi-environment support (dev/staging/production) with automatic endpoint detection
- **Resource Abstraction**: Type-safe wrappers for applications, versions, runs with memory-efficient pagination

**Performance & Reliability (NEW in v1.0.0-beta.7):**

- **Operation Caching**: Token-aware caching for read operations with configurable TTLs (5-15 min)
- **Retry Logic**: Exponential backoff with jitter for transient failures (4 attempts default)
- **Timeout Management**: Per-operation timeouts (30s default, configurable 0.1s-300s)
- **Cache Invalidation**: Automatic global cache clearing on mutations for consistency

**Observability & Tracking (NEW in v1.0.0-beta.7):**

- **SDK Metadata System**: Automatic tracking of execution context, user, CI/CD environment for all runs
- **JSON Schema Validation**: Pydantic-based validation with versioned schemas (v0.0.1)
- **Enhanced User Agent**: Context-aware user agent with pytest and GitHub Actions integration
- **Structured Logging**: Retry warnings, cache hits/misses, performance metrics

**API v1.0.0-beta.7 Support:**

- **State Models**: Enum-based RunState, ItemState, ArtifactState with termination reasons
- **Statistics Tracking**: Aggregate RunItemStatistics for progress monitoring
- **Error Handling**: Comprehensive error recovery with user guidance

### User Interfaces

**CLI Commands (`_cli.py`):**

User authentication commands:

- `user login` - Authenticate with Aignostics Platform (device flow or browser)
- `user logout` - Remove cached authentication token
- `user whoami` - Display current user information and organization details

SDK metadata commands:

- `sdk metadata-schema` - Display or export the JSON Schema for SDK metadata (supports `--pretty` flag)

**Service Layer (`_service.py`):**

The service provides authentication management used by both CLI and other modules:

- Token caching and refresh
- User information retrieval
- Login/logout operations

## Architecture & Design Patterns

### Layered Architecture

```
┌─────────────────────────────────────────────┐
│            Public API (Client)              │
├─────────────────────────────────────────────┤
│         Resources (Applications, Runs)      │
├─────────────────────────────────────────────┤
│      Authentication & Token Management      │
├─────────────────────────────────────────────┤
│        Generated API Client (aignx)         │
├─────────────────────────────────────────────┤
│         HTTP Client (urllib3)               │
└─────────────────────────────────────────────┘
```

### Resource Pattern

Each resource follows consistent REST conventions:

- `list()` - Returns generator for memory-efficient pagination
- `get(id)` - Retrieves single resource
- Methods follow REST conventions

## Critical Implementation Details

### Client Implementation (`_client.py`)

**Main Client Class:**

```python
class Client:
    """Main client with resource accessors."""

    applications: Applications
    runs: Runs
    # Note: No separate 'versions' accessor - versions accessed via applications

    def __init__(self, cache_token: bool = True):
        self._api = Client.get_api_client(cache_token=cache_token)
        self.applications = Applications(self._api)
        self.runs = Runs(self._api)

    def me(self) -> Me:
        """Get current user info."""
        return self._api.get_me_v1_me_get()

    def run(self, run_id: str) -> Run:
        """Get specific run by ID."""
        return Run(self._api, run_id)

    def application(self, application_id: str) -> Application:
        """Find application by ID (iterates through list)."""
        # NOTE: Currently no direct endpoint, iterates all apps
        for app in self.applications.list():
            if app.application_id == application_id:
                return app
        raise NotFoundException
    
    def application_version(self, application_id: str, 
                          version_number: str | None = None) -> ApplicationVersion:
        """Get application version details.
        
        Args:
            application_id: The ID of the application (e.g., 'heta')
            version_number: The semantic version number (e.g., '1.0.0')
                          If None, returns the latest version
        
        Returns:
            ApplicationVersion with application_id and version_number attributes
        """
        return Versions(self._api).details(
            application_id=application_id, 
            application_version=version_number
        )
```

### Authentication Flow (`_authentication.py`)

**Token Management (Actual Implementation):**

```python
def get_token(use_cache: bool = True, use_device_flow: bool = False) -> str:
    """Get authentication token with caching."""

    token = None

    # Check cached token
    if use_cache and settings().token_file.exists():
        stored_token = Path(settings().token_file).read_text()
        # Format: "token:expiry_timestamp"
        cached_token, expiry_str = stored_token.split(":")
        expiry = datetime.fromtimestamp(int(expiry_str), tz=UTC)

        # Valid if more than 5 minutes remaining
        if datetime.now(tz=UTC) + timedelta(minutes=5) < expiry:
            token = cached_token

    # Get new token if needed
    if token is None:
        token = _authenticate(use_device_flow)
        claims = verify_and_decode_token(token)

        # Cache with expiry
        if use_cache:
            timestamp = claims["exp"]
            settings().token_file.parent.mkdir(parents=True, exist_ok=True)
            Path(settings().token_file).write_text(f"{token}:{timestamp}")

    _inform_sentry_about_user(token)
    return token
```

**Key Points:**

- Token cached as `token:expiry_timestamp` format (NOT just token)
- 5-minute buffer before expiry for refresh
- No PKCE implementation visible in current code
- Device flow is available but implementation details vary

### Resource Pagination (`resources/runs.py`, `resources/utils.py`)

**Actual Pagination Constants:**

```python
# In resources/runs.py
LIST_APPLICATION_RUNS_MAX_PAGE_SIZE = 100
LIST_APPLICATION_RUNS_MIN_PAGE_SIZE = 5

# In resources/utils.py
PAGE_SIZE = 20  # Default for general pagination

def paginate(func, *args, page_size=PAGE_SIZE, **kwargs):
    """Generic pagination helper."""
    page = 1
    while True:
        results = func(*args, page=page, page_size=page_size, **kwargs)
        yield from results
        if len(results) < page_size:
            break
        page += 1
```

**Runs List Implementation:**

```python
class Runs:
    def list(
        self,
        application_id: str | None = None,
        application_version: str | None = None,
        page_size: int = LIST_APPLICATION_RUNS_MAX_PAGE_SIZE
    ):
        """List runs with pagination.
        
        Args:
            application_id: Optional filter by application ID
            application_version: Optional filter by version number (not version_id)
            page_size: Number of results per page (max 100)
        
        Returns:
            Iterator[Run] Iterator of Run instances
        """
        if page_size > LIST_APPLICATION_RUNS_MAX_PAGE_SIZE:
            raise ValueError(f"page_size must be <= {LIST_APPLICATION_RUNS_MAX_PAGE_SIZE}")

        # Uses paginate helper internally
        # Returns iterator of run instances
        # Each run has application_id and version_number attributes
```

### SDK Metadata System (`_sdk_metadata.py`)

**NEW FEATURE (as of v1.0.0-beta.7):** The SDK now automatically attaches structured metadata to every application run, providing comprehensive tracking of execution context, user information, and CI/CD environment details.

**Architecture:**

```
┌────────────────────────────────────────────────────┐
│           SDK Metadata System                      │
├────────────────────────────────────────────────────┤
│  Pydantic Models (Validation + Schema Generation) │
│  ├─ SdkMetadata (root model)                      │
│  ├─ SubmissionMetadata (how/when submitted)       │
│  ├─ UserMetadata (organization/user info)         │
│  ├─ CIMetadata (GitHub Actions + pytest)          │
│  ├─ WorkflowMetadata (control flags)              │
│  └─ SchedulingMetadata (due dates/deadlines)      │
├────────────────────────────────────────────────────┤
│  Runtime Functions                                 │
│  ├─ build_sdk_metadata() → dict                   │
│  ├─ validate_sdk_metadata(metadata) → bool        │
│  ├─ validate_sdk_metadata_silent(metadata) → bool │
│  └─ get_sdk_metadata_json_schema() → dict         │
├────────────────────────────────────────────────────┤
│  JSON Schema (Versioned)                           │
│  └─ Schema version: 0.0.1                          │
│     Published at: docs/source/_static/             │
│     URL: github.com/.../sdk_metadata_schema_*.json │
└────────────────────────────────────────────────────┘
```

**Schema Version:** `0.0.1`

**Core Pydantic Models:**

```python
# From _sdk_metadata.py (actual implementation)

class SubmissionMetadata(BaseModel):
    """Metadata about how the SDK was invoked."""
    date: str  # ISO 8601 timestamp
    interface: Literal["script", "cli", "launchpad"]  # How SDK was accessed
    source: Literal["user", "test", "bridge"]  # Who initiated the run

class UserMetadata(BaseModel):
    """User information metadata."""
    organization_id: str
    organization_name: str
    user_email: str
    user_id: str

class GitHubCIMetadata(BaseModel):
    """GitHub Actions CI metadata."""
    action: str | None
    job: str | None
    ref: str | None
    ref_name: str | None
    ref_type: str | None  # branch or tag
    repository: str  # owner/repo
    run_attempt: str | None
    run_id: str
    run_number: str | None
    run_url: str  # Full URL to workflow run
    runner_arch: str | None  # x64, ARM64, etc.
    runner_os: str | None  # Linux, Windows, macOS
    sha: str | None  # Git commit SHA
    workflow: str | None
    workflow_ref: str | None

class PytestCIMetadata(BaseModel):
    """Pytest test execution metadata."""
    current_test: str  # Test name being executed
    markers: list[str] | None  # Pytest markers applied

class CIMetadata(BaseModel):
    """CI/CD environment metadata."""
    github: GitHubCIMetadata | None
    pytest: PytestCIMetadata | None

class WorkflowMetadata(BaseModel):
    """Workflow control metadata."""
    onboard_to_aignostics_portal: bool = False
    validate_only: bool = False

class SchedulingMetadata(BaseModel):
    """Scheduling metadata for run execution."""
    due_date: str | None  # ISO 8601, requested completion time
    deadline: str | None  # ISO 8601, hard deadline

class SdkMetadata(BaseModel):
    """Complete SDK metadata schema."""
    schema_version: str  # Currently "0.0.1"
    submission: SubmissionMetadata
    user_agent: str  # Enhanced user agent from utils module
    user: UserMetadata | None  # Present if authenticated
    ci: CIMetadata | None  # Present if running in CI
    note: str | None  # Optional user note
    workflow: WorkflowMetadata | None  # Optional workflow control
    scheduling: SchedulingMetadata | None  # Optional scheduling info

    model_config = {"extra": "forbid"}  # Strict validation
```

**Automatic Metadata Generation:**

```python
def build_sdk_metadata() -> dict[str, Any]:
    """Build SDK metadata automatically attached to runs.

    Detection Logic:
    - Interface: Detects script vs CLI vs launchpad (NiceGUI)
    - Source: Detects user vs test (pytest) vs bridge
    - User info: Fetches from Client().me() if authenticated
    - GitHub CI: Reads GITHUB_* environment variables
    - Pytest: Reads PYTEST_CURRENT_TEST environment variable

    Returns:
        dict with complete metadata structure
    """
    # Interface detection
    if "typer" in sys.argv[0] or "aignostics" in sys.argv[0]:
        interface = "cli"
    elif os.getenv("NICEGUI_HOST"):
        interface = "launchpad"
    else:
        interface = "script"

    # Source detection
    if os.environ.get("AIGNOSTICS_BRIDGE_VERSION"):
        source = "bridge"
    elif os.environ.get("PYTEST_CURRENT_TEST"):
        source = "test"
    else:
        source = "user"

    # Build metadata structure
    metadata = {
        "schema_version": "0.0.1",
        "submission": {
            "date": datetime.now(UTC).isoformat(timespec="seconds"),
            "interface": interface,
            "source": source,
        },
        "user_agent": user_agent(),  # From utils module
    }

    # Add user info if authenticated
    try:
        me = Client().me()
        metadata["user"] = {
            "organization_id": me.organization.id,
            "organization_name": me.organization.name,
            "user_email": me.user.email,
            "user_id": me.user.id,
        }
    except Exception:
        pass  # User info optional

    # Add GitHub CI metadata if present
    if os.environ.get("GITHUB_RUN_ID"):
        metadata["ci"] = {"github": {...}}  # Populated from env vars

    # Add pytest metadata if running in test
    if os.environ.get("PYTEST_CURRENT_TEST"):
        metadata["ci"] = metadata.get("ci", {})
        metadata["ci"]["pytest"] = {
            "current_test": os.environ["PYTEST_CURRENT_TEST"],
            "markers": os.environ.get("PYTEST_MARKERS", "").split(",")
        }

    return metadata
```

**Integration with Run Submission:**

```python
# From resources/runs.py (actual implementation)

def submit(self, application_id: str, items: list, custom_metadata: dict = None):
    """Submit run with automatic SDK metadata attachment."""

    # Build SDK metadata automatically
    sdk_metadata = build_sdk_metadata()

    # Validate SDK metadata
    validate_sdk_metadata(sdk_metadata)

    # Merge with custom metadata under 'sdk' key
    if custom_metadata is None:
        custom_metadata = {}

    custom_metadata.setdefault("sdk", {})
    custom_metadata["sdk"].update(sdk_metadata)

    # Submit run with merged metadata
    return self._api.create_run(
        application_id=application_id,
        items=items,
        custom_metadata=custom_metadata
    )
```

**JSON Schema Generation:**

The SDK provides versioned JSON Schemas for metadata validation:

```bash
# Via CLI
aignostics sdk metadata-schema --pretty > schema.json

# Schema location (in repository)
docs/source/_static/sdk_metadata_schema_v0.0.1.json
docs/source/_static/sdk_metadata_schema_latest.json

# Public URL
https://raw.githubusercontent.com/aignostics/python-sdk/main/docs/source/_static/sdk_metadata_schema_latest.json
```

**Schema Generation (Noxfile Task):**

```python
# From noxfile.py
def _generate_sdk_metadata_schema(session: nox.Session) -> None:
    """Generate SDK metadata JSON schema with versioned filename."""

    # Generate schema by calling CLI
    session.run(
        "aignostics",
        "sdk",
        "metadata-schema",
        "--no-pretty",
        stdout=output_file,
        external=True,
    )

    # Extract version from schema $id
    schema = json.load(output_file)
    version = extract_version_from_id(schema["$id"])

    # Write to both versioned and latest files
    Path(f"docs/source/_static/sdk_metadata_schema_{version}.json").write(schema)
    Path("docs/source/_static/sdk_metadata_schema_latest.json").write(schema)
```

**Validation Functions:**

```python
def validate_sdk_metadata(metadata: dict[str, Any]) -> bool:
    """Validate SDK metadata and raise ValidationError if invalid."""
    try:
        SdkMetadata.model_validate(metadata)
        return True
    except ValidationError:
        logger.exception("SDK metadata validation failed")
        raise

def validate_sdk_metadata_silent(metadata: dict[str, Any]) -> bool:
    """Validate SDK metadata without raising exceptions."""
    try:
        SdkMetadata.model_validate(metadata)
        return True
    except ValidationError:
        return False

def get_sdk_metadata_json_schema() -> dict[str, Any]:
    """Get JSON Schema for SDK metadata with $schema and $id fields."""
    schema = SdkMetadata.model_json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = (
        f"https://raw.githubusercontent.com/aignostics/python-sdk/main/"
        f"docs/source/_static/sdk_metadata_schema_v{SDK_METADATA_SCHEMA_VERSION}.json"
    )
    return schema
```

**Key Features:**

1. **Automatic Attachment** - SDK metadata added to every run submission without user action
2. **Environment Detection** - Automatically detects script/CLI/GUI, user/test/bridge contexts
3. **CI/CD Integration** - Captures GitHub Actions workflow details and pytest test context
4. **User Agent Integration** - Uses enhanced user_agent() from utils module
5. **Strict Validation** - Pydantic models with `extra="forbid"` ensure data quality
6. **Versioned Schema** - JSON Schema published with semantic versioning
7. **Silent Fallback** - User info and CI data are optional, won't fail if unavailable
8. **Custom Metadata Support** - Users can add custom fields alongside SDK metadata

**Testing:**

Comprehensive test suite in `tests/aignostics/platform/sdk_metadata_test.py`:

- Metadata building in various environments
- Schema validation (valid and invalid cases)
- GitHub CI metadata extraction
- Pytest metadata extraction
- Interface and source detection
- User agent integration
- JSON Schema generation

### Operation Caching System (`_operation_cache.py`)

**NEW FEATURE (as of v1.0.0-beta.7):** The platform client now implements intelligent operation caching to reduce redundant API calls and improve performance.

**Architecture:**

```
┌────────────────────────────────────────────────────┐
│           Operation Caching System                  │
├────────────────────────────────────────────────────┤
│  Cache Storage: dict[cache_key, (result, expiry)]  │
│  ├─ Token-aware caching (per-user isolation)      │
│  ├─ TTL-based expiration                           │
│  └─ Automatic invalidation on mutations            │
├────────────────────────────────────────────────────┤
│  Decorator: @cached_operation                      │
│  ├─ ttl: Time-to-live in seconds                  │
│  ├─ use_token: Include auth token in key         │
│  └─ instance_attrs: Per-instance caching          │
├────────────────────────────────────────────────────┤
│  Cache Key Generation                              │
│  ├─ cache_key(): func_name:args:kwargs            │
│  └─ cache_key_with_token(): token_hash:...        │
├────────────────────────────────────────────────────┤
│  Cache Invalidation                                │
│  └─ operation_cache_clear(): Clear on mutations   │
└────────────────────────────────────────────────────┘
```

**Core Implementation:**

```python
# From _operation_cache.py (actual implementation)

# Global cache storage
_operation_cache: dict[str, tuple[Any, float]] = {}

def cached_operation(
    ttl: int, *, use_token: bool = True, instance_attrs: tuple[str, ...] | None = None
) -> Callable:
    """Decorator for caching function results with TTL.

    Args:
        ttl: Time-to-live for cache in seconds
        use_token: Include authentication token in cache key for per-user isolation
        instance_attrs: Instance attributes to include in key (e.g., 'run_id')

    Behavior:
        - Generates unique cache key from function name, args, kwargs, and optional token
        - Returns cached result if present and not expired
        - Deletes expired entries automatically
        - Stores new results with expiry timestamp
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Build cache key
            func_qualified_name = func.__qualname__  # e.g., "Client.me"

            if use_token:
                token_hash = hashlib.sha256(get_token().encode()).hexdigest()[:16]
                key = f"{token_hash}:{func_qualified_name}:{args}:{sorted(kwargs.items())}"
            else:
                key = f"{func_qualified_name}:{args}:{sorted(kwargs.items())}"

            # Check cache
            if key in _operation_cache:
                result, expiry = _operation_cache[key]
                if time.time() < expiry:
                    return result
                del _operation_cache[key]

            # Call function and cache result
            result = func(*args, **kwargs)
            _operation_cache[key] = (result, time.time() + ttl)
            return result
        return wrapper
    return decorator

def operation_cache_clear(func: Callable | list[Callable] | None = None) -> int:
    """Clear operation cache, optionally filtering by function(s).

    Args:
        func: Function(s) to clear, or None to clear all entries

    Returns:
        Number of cache entries removed

    Usage:
        operation_cache_clear()  # Clear all
        operation_cache_clear(Client.me)  # Clear specific function
        operation_cache_clear([Client.me, Client.application])  # Clear multiple
    """
    if func is None:
        removed_count = len(_operation_cache)
        _operation_cache.clear()
        return removed_count

    # Filter by function qualified name(s)
    func_list = func if isinstance(func, list) else [func]
    func_qualified_names = [f.__qualname__ for f in func_list]

    keys_to_remove = [
        key for key in _operation_cache
        if any(name in key for name in func_qualified_names)
    ]

    for key in keys_to_remove:
        del _operation_cache[key]

    return len(keys_to_remove)
```

**Cache TTL Configuration (from Settings):**

```python
# Default cache TTLs (from _settings.py)
CACHE_TTL_DEFAULT = 60 * 5  # 5 minutes (most operations)
RUN_CACHE_TTL_DEFAULT = 15  # 15 seconds (runs change frequently)
AUTH_JWK_SET_CACHE_TTL_DEFAULT = 60 * 60 * 24  # 1 day (JWK sets rarely change)

# Configurable per operation type
me_cache_ttl: int = 300  # 5 minutes
application_cache_ttl: int = 300  # 5 minutes
application_version_cache_ttl: int = 300  # 5 minutes
run_cache_ttl: int = 15  # 15 seconds
auth_jwk_set_cache_ttl: int = 86400  # 1 day
```

**Usage in Client Methods:**

```python
# From _client.py
@cached_operation(ttl=settings().me_cache_ttl, use_token=True)
def me_with_retry() -> Me:
    return Retrying(...)(
        lambda: self._api.get_me_v1_me_get(...)
    )

# From resources/runs.py
@cached_operation(ttl=settings().run_cache_ttl, use_token=True)
def details_with_retry(run_id: str) -> RunData:
    return Retrying(...)(
        lambda: self._api.get_run_v1_runs_run_id_get(run_id, ...)
    )
```

**Cache Invalidation Strategy:**

**Automatic Invalidation on Mutations:**

```python
# From resources/runs.py - Submit operation
def submit(...) -> Run:
    # Clear ALL caches before mutation
    operation_cache_clear()

    # Perform mutation
    res = self._api.create_run_v1_runs_post(...)
    return Run(self._api, res.run_id)

# Cancel operation
def cancel(self) -> None:
    operation_cache_clear()  # Clear all caches
    self._api.cancel_run_v1_runs_run_id_cancel_post(...)

# Delete operation
def delete(self) -> None:
    operation_cache_clear()  # Clear all caches
    self._api.delete_run_items_v1_runs_run_id_artifacts_delete(...)
```

**Key Design Decisions:**

1. **Global Cache Clearing**: All caches are cleared on ANY mutation to ensure consistency
2. **Token-Aware**: Caching is per-user by default (use_token=True), preventing data leakage
3. **No Partial Invalidation**: Simplicity over optimization - clear everything on write
4. **TTL-Based Expiration**: Stale data automatically expires after configured TTL
5. **Token Changes**: Cache keys include token hash, so token refresh creates new cache namespace

**Operations That Are Cached:**

- ✅ `Client.me()` - User information (5 min TTL)
- ✅ `Client.application()` - Application details (5 min TTL)
- ✅ `Client.application_version()` - Version details (5 min TTL)
- ✅ `Applications.list()` - Application list (5 min TTL)
- ✅ `Applications.details()` - Application details (5 min TTL)
- ✅ `Runs.details()` - Run details (15 sec TTL)
- ✅ `Runs.results()` - Run results (15 sec TTL)
- ✅ `Runs.list()` - Run list (15 sec TTL)

**Operations That Clear Cache:**

- ❌ `Runs.submit()` - Creates new run
- ❌ `Run.cancel()` - Changes run state
- ❌ `Run.delete()` - Removes run data

**Performance Impact:**

- **Cache Hit**: ~0.1ms (dictionary lookup + expiry check)
- **Cache Miss**: Full API roundtrip (~50-500ms depending on operation)
- **Typical Benefit**: 100-1000x speedup for repeated reads within TTL
- **Memory Usage**: Minimal (~1KB per cached operation result)

**Configuration:**

All cache TTLs are configurable via environment variables or `.env` file:

```bash
# Example .env configuration
AIGNOSTICS_ME_CACHE_TTL=300  # 5 minutes
AIGNOSTICS_APPLICATION_CACHE_TTL=300  # 5 minutes
AIGNOSTICS_RUN_CACHE_TTL=15  # 15 seconds
AIGNOSTICS_AUTH_JWK_SET_CACHE_TTL=86400  # 1 day
```

**Testing:**

Comprehensive test suite in `tests/aignostics/platform/client_cache_test.py`:

- Cache hit/miss scenarios
- TTL expiration
- Token-aware caching
- Cache invalidation on mutations
- Concurrent access patterns

### Retry Logic and Timeout System

**NEW FEATURE (as of v1.0.0-beta.7):** All read operations now include intelligent retry logic with exponential backoff and configurable timeouts.

**Architecture:**

```
┌────────────────────────────────────────────────────┐
│         Retry and Timeout System (Tenacity)       │
├────────────────────────────────────────────────────┤
│  Retry Policy                                      │
│  ├─ Exponential backoff with jitter               │
│  ├─ Configurable max attempts (default: 4)        │
│  ├─ Configurable wait times (0.1s - 60s)         │
│  └─ Logs warnings before sleep                    │
├────────────────────────────────────────────────────┤
│  Retryable Exceptions                              │
│  ├─ ServiceException (5xx errors)                 │
│  ├─ Urllib3TimeoutError                           │
│  ├─ PoolError                                     │
│  ├─ IncompleteRead                                │
│  ├─ ProtocolError                                 │
│  └─ ProxyError                                    │
├────────────────────────────────────────────────────┤
│  Timeout Configuration                             │
│  ├─ Per-operation timeouts (default: 30s)        │
│  ├─ Range: 0.1s - 300s                           │
│  └─ Separate timeouts for mutating ops            │
└────────────────────────────────────────────────────┘
```

**Retryable Exceptions:**

```python
# From _client.py and resources/*.py
RETRYABLE_EXCEPTIONS = (
    ServiceException,      # 5xx server errors
    Urllib3TimeoutError,   # Connection timeout
    PoolError,            # Connection pool exhausted
    IncompleteRead,       # Partial response received
    ProtocolError,        # Protocol violation
    ProxyError,           # Proxy connection failed
)
```

**Retry Implementation Pattern:**

```python
# Standard retry pattern used throughout the codebase
@cached_operation(ttl=settings().me_cache_ttl, use_token=True)
def me_with_retry() -> Me:
    return Retrying(
        retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
        stop=stop_after_attempt(settings().me_retry_attempts),  # Max 4 attempts
        wait=wait_exponential_jitter(
            initial=settings().me_retry_wait_min,  # 0.1s
            max=settings().me_retry_wait_max       # 60s
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,  # Re-raise after all attempts exhausted
    )(
        lambda: self._api.get_me_v1_me_get(
            _request_timeout=settings().me_timeout,  # 30s
            _headers={"User-Agent": user_agent()}
        )
    )
```

**Retry Configuration (from Settings):**

```python
# Defaults (from _settings.py)
RETRY_ATTEMPTS_DEFAULT = 4
RETRY_WAIT_MIN_DEFAULT = 0.1   # seconds
RETRY_WAIT_MAX_DEFAULT = 60.0  # seconds
TIMEOUT_DEFAULT = 30.0  # seconds

# Per-operation configuration
auth_retry_attempts: int = 4
auth_retry_wait_min: float = 0.1
auth_retry_wait_max: float = 60.0
auth_timeout: float = 30.0

me_retry_attempts: int = 4
me_retry_wait_min: float = 0.1
me_retry_wait_max: float = 60.0
me_timeout: float = 30.0

application_retry_attempts: int = 4
application_retry_wait_min: float = 0.1
application_retry_wait_max: float = 60.0
application_timeout: float = 30.0

run_retry_attempts: int = 4
run_retry_wait_min: float = 0.1
run_retry_wait_max: float = 60.0
run_timeout: float = 30.0

# Special timeouts for mutating operations
run_submit_timeout: float = 30.0
run_cancel_timeout: float = 30.0
run_delete_timeout: float = 30.0
```

**Exponential Backoff with Jitter:**

```
Attempt 1: 0ms wait (first attempt)
Attempt 2: ~100ms wait (initial)
Attempt 3: ~200-400ms wait (exponential + jitter)
Attempt 4: ~400-800ms wait (exponential + jitter)
Max wait capped at: 60s (retry_wait_max)
```

**Environment Variable Configuration:**

```bash
# Example .env configuration
AIGNOSTICS_ME_RETRY_ATTEMPTS=4
AIGNOSTICS_ME_RETRY_WAIT_MIN=0.1
AIGNOSTICS_ME_RETRY_WAIT_MAX=60.0
AIGNOSTICS_ME_TIMEOUT=30.0

AIGNOSTICS_RUN_RETRY_ATTEMPTS=4
AIGNOSTICS_RUN_RETRY_WAIT_MIN=0.1
AIGNOSTICS_RUN_RETRY_WAIT_MAX=60.0
AIGNOSTICS_RUN_TIMEOUT=30.0
```

**Operations with Retry Logic:**

**Read Operations (All have retry + cache):**

- ✅ `Client.me()` - 4 retries, 30s timeout
- ✅ `Client.application()` - 4 retries, 30s timeout
- ✅ `Client.application_version()` - 4 retries, 30s timeout
- ✅ `Applications.list()` - 4 retries, 30s timeout
- ✅ `Runs.details()` - 4 retries, 30s timeout
- ✅ `Runs.results()` - 4 retries, 30s timeout
- ✅ `Runs.list()` - 4 retries, 30s timeout

**Write Operations (No retry, no cache):**

- ❌ `Runs.submit()` - No retry (idempotency concerns), 30s timeout
- ❌ `Run.cancel()` - No retry, 30s timeout
- ❌ `Run.delete()` - No retry, 30s timeout

**Key Design Decisions:**

1. **Read-Only Retries**: Only read operations retry (mutations could have side effects)
2. **Exponential Backoff**: Reduces load on failing servers
3. **Jitter**: Prevents thundering herd problem
4. **Logging**: Warnings logged before retry sleeps for observability
5. **Re-raise**: After exhausting retries, original exception is re-raised

**Logging Output:**

```
WARNING - Retrying aignostics.platform._client.Client.me in 0.123 seconds
          (attempt 1/4, ServiceException: 503 Service Unavailable)
WARNING - Retrying aignostics.platform._client.Client.me in 0.456 seconds
          (attempt 2/4, Urllib3TimeoutError)
WARNING - Retrying aignostics.platform._client.Client.me in 1.234 seconds
          (attempt 3/4, PoolError)
ERROR - Failed after 4 attempts: ServiceException: 503 Service Unavailable
```

**Testing:**

Comprehensive test suite in `tests/aignostics/platform/client_me_retry_test.py`:

- Retry on transient errors
- Exponential backoff timing
- Max attempts enforcement
- Timeout behavior
- Exception re-raising

### API v1.0.0-beta.7 State Models

**MAJOR CHANGE (as of v1.0.0-beta.7):** Complete refactoring of run, item, and artifact state management with new enum-based state models.

**New State Enums:**

```python
# From codegen/out/aignx/codegen/models/

class RunState(str, Enum):
    """Run lifecycle states."""
    PENDING = 'PENDING'        # Run created, waiting to start
    PROCESSING = 'PROCESSING'  # Run actively processing items
    TERMINATED = 'TERMINATED'  # Run completed (check termination_reason)

class ItemState(str, Enum):
    """Item (slide) processing states."""
    PENDING = 'PENDING'        # Item queued for processing
    PROCESSING = 'PROCESSING'  # Item being analyzed
    TERMINATED = 'TERMINATED'  # Item processing done (check termination_reason)

class ArtifactState(str, Enum):
    """Individual artifact processing states."""
    PENDING = 'PENDING'        # Artifact generation pending
    PROCESSING = 'PROCESSING'  # Artifact being created
    TERMINATED = 'TERMINATED'  # Artifact ready or failed
```

**New Termination Reason Enums:**

```python
class RunTerminationReason(str, Enum):
    """Why a run terminated."""
    ALL_ITEMS_PROCESSED = 'ALL_ITEMS_PROCESSED'  # Normal completion
    CANCELED_BY_SYSTEM = 'CANCELED_BY_SYSTEM'    # System initiated cancellation
    CANCELED_BY_USER = 'CANCELED_BY_USER'        # User canceled the run

class ItemTerminationReason(str, Enum):
    """Why an item terminated."""
    SUCCEEDED = 'SUCCEEDED'      # Item processed successfully
    USER_ERROR = 'USER_ERROR'    # Input validation or user-caused error
    SYSTEM_ERROR = 'SYSTEM_ERROR'  # Infrastructure or application error
    SKIPPED = 'SKIPPED'          # Item skipped (e.g., duplicate)

class ArtifactTerminationReason(str, Enum):
    """Why an artifact terminated."""
    SUCCEEDED = 'SUCCEEDED'      # Artifact created successfully
    USER_ERROR = 'USER_ERROR'    # Input validation error
    SYSTEM_ERROR = 'SYSTEM_ERROR'  # Generation failed due to system issue
```

**State Machine Architecture:**

```
Run State Machine:
PENDING → PROCESSING → TERMINATED
                          ↓
                    [termination_reason]
                          ├─ ALL_ITEMS_PROCESSED (success)
                          ├─ CANCELED_BY_USER
                          └─ CANCELED_BY_SYSTEM

Item State Machine (per slide):
PENDING → PROCESSING → TERMINATED
                          ↓
                    [termination_reason]
                          ├─ SUCCEEDED (normal)
                          ├─ USER_ERROR (bad input)
                          ├─ SYSTEM_ERROR (internal)
                          └─ SKIPPED (duplicate, etc)

Artifact State Machine (per output file):
PENDING → PROCESSING → TERMINATED
                          ↓
                    [termination_reason]
                          ├─ SUCCEEDED
                          ├─ USER_ERROR
                          └─ SYSTEM_ERROR
```

**New Output Models:**

```python
class RunOutput(BaseModel):
    """Run execution results summary."""
    state: RunState
    termination_reason: RunTerminationReason | None
    statistics: RunItemStatistics  # NEW: Aggregate item counts
    # ... other fields

class ItemOutput(BaseModel):
    """Individual item processing results."""
    state: ItemState
    termination_reason: ItemTerminationReason | None
    artifacts: list[ArtifactOutput]  # List of output artifacts
    # ... other fields

class ArtifactOutput(BaseModel):
    """Individual artifact details."""
    state: ArtifactState
    termination_reason: ArtifactTerminationReason | None
    download_url: str | None  # Available when SUCCEEDED
    # ... other fields

class RunItemStatistics(BaseModel):
    """NEW: Aggregate statistics for run."""
    total: int        # Total items in run
    succeeded: int    # Successfully processed
    user_error: int   # Failed due to user errors
    system_error: int # Failed due to system errors
    skipped: int      # Skipped items
    pending: int      # Not yet started
    processing: int   # Currently processing
```

**Model Migrations (Deleted Models):**

**Deleted in v1.0.0-beta.7:**

- ❌ `UserPayload` - Replaced with structured user/organization models
- ❌ `PayloadItem` - Replaced with `ItemOutput`
- ❌ `ApplicationVersionReadResponse` - Renamed to `ApplicationVersion`
- ❌ `InputArtifactReadResponse` - Simplified artifact handling
- ❌ `TransferUrls` - Merged into artifact models

**New Models in v1.0.0-beta.7:**

- ✅ `Auth0User` - Structured user information
- ✅ `Auth0Organization` - Structured organization information
- ✅ `ApplicationReadShortResponse` - Lightweight application summary
- ✅ `ApplicationVersion` - Complete version details with metadata
- ✅ `RunItemStatistics` - Aggregate item statistics
- ✅ `CustomMetadataUpdateRequest` - Metadata update payload

**Usage Patterns:**

**Checking Run Status:**

```python
run = client.run("run-123")
details = run.details()

# Check run state
if details.output.state == RunState.TERMINATED:
    # Check how it terminated
    if details.output.termination_reason == RunTerminationReason.ALL_ITEMS_PROCESSED:
        print("Run completed successfully!")
        print(f"Items succeeded: {details.output.statistics.succeeded}")
        print(f"Items failed: {details.output.statistics.user_error + details.output.statistics.system_error}")
    elif details.output.termination_reason == RunTerminationReason.CANCELED_BY_USER:
        print("Run was canceled")
elif details.output.state == RunState.PROCESSING:
    print(f"Run in progress: {details.output.statistics.processing} items processing")
```

**Checking Item Status:**

```python
for item in run.results():
    if item.output.state == ItemState.TERMINATED:
        if item.output.termination_reason == ItemTerminationReason.SUCCEEDED:
            print(f"Item {item.item_id} succeeded")
            # Access artifacts
            for artifact in item.output.artifacts:
                if artifact.state == ArtifactState.TERMINATED:
                    if artifact.termination_reason == ArtifactTerminationReason.SUCCEEDED:
                        print(f"  - Artifact ready: {artifact.download_url}")
        elif item.output.termination_reason == ItemTerminationReason.USER_ERROR:
            print(f"Item {item.item_id} failed: user error")
        elif item.output.termination_reason == ItemTerminationReason.SYSTEM_ERROR:
            print(f"Item {item.item_id} failed: system error")
```

**Migration Guide (v1.0.0-beta.6 → v1.0.0-beta.7):**

**Before (v1.0.0-beta.6):**

```python
# Old status checking (hypothetical old API)
if run.status == "COMPLETED":
    ...
```

**After (v1.0.0-beta.7):**

```python
# New state + termination reason pattern
if run.output.state == RunState.TERMINATED:
    if run.output.termination_reason == RunTerminationReason.ALL_ITEMS_PROCESSED:
        ...
```

**Key Benefits of New State Models:**

1. **Type Safety**: Enum-based states prevent typos and invalid states
2. **Clear Semantics**: Separate state and termination_reason clarifies "what" vs "why"
3. **Granular Error Handling**: Distinguish user errors from system errors
4. **Consistent Pattern**: Same state machine pattern across runs, items, and artifacts
5. **Better Observability**: RunItemStatistics provides aggregate view of run progress

**Testing:**

Updated test suite in `tests/aignostics/platform/e2e_test.py`:

- State transitions
- Termination reason validation
- Statistics accuracy
- Error scenarios (user_error vs system_error)

## Usage Patterns & Best Practices

### Basic Client Usage

```python
from aignostics.platform import Client

# Initialize with automatic authentication
client = Client(cache_token=True)

# Get user info
me = client.me()
print(f"User: {me.email}, Organization: {me.organization.name}")

# List applications
for app in client.applications.list():
    print(f"App: {app.application_id}")

# Get application version
app_version = client.application_version(
    application_id="heta",
    version_number="1.0.0"  # Omit for latest version
)
print(f"Application: {app_version.application_id}")
print(f"Version: {app_version.version_number}")

# Get latest version
latest = client.application_version(
    application_id="heta",
    version_number=None
)

# Get specific run
run = client.run("run-id-123")
# Access application info from run
print(f"Run application: {run.payload.application_id}")
print(f"Run version: {run.payload.version_number}")

# List runs with custom page size
runs = client.runs.list(page_size=50)  # Max 100
for run in runs:
    print(f"Run: {run.run_id}")
```

### SDK Metadata Usage

```python
from aignostics.platform import Client
from aignostics.platform._sdk_metadata import (
    build_sdk_metadata,
    validate_sdk_metadata,
    get_sdk_metadata_json_schema
)

# SDK metadata is AUTOMATICALLY attached to every run submission
client = Client()

# Submit run - SDK metadata added automatically
run = client.runs.submit(
    application_id="heta",
    items=[...],
    custom_metadata={
        "experiment_id": "exp-123",
        "dataset_version": "v2.1",
        # SDK metadata will be added under "sdk" key automatically
    }
)

# Access SDK metadata from run
sdk_metadata = run.payload.custom_metadata.get("sdk", {})
print(f"Submitted via: {sdk_metadata['submission']['interface']}")  # cli, script, or launchpad
print(f"Submitted by: {sdk_metadata['submission']['initiator']}")  # user, test, or bridge
print(f"User: {sdk_metadata['user']['user_email']}")  # if authenticated
if "ci" in sdk_metadata:
    print(f"GitHub Run: {sdk_metadata['ci']['github']['run_url']}")  # if in CI

# Manually build and validate metadata (for testing or inspection)
metadata = build_sdk_metadata()
assert validate_sdk_metadata(metadata)

# Get JSON Schema for documentation or external validation
schema = get_sdk_metadata_json_schema()
print(f"Schema version: {schema['$id']}")
```

### Error Handling

```python
from aignostics.platform import NotFoundException, ApiException

try:
    app = client.application("app-id")
except NotFoundException:
    logger.error("Application not found")
except ApiException as e:
    logger.error(f"API error: {e}")
```

## Testing Strategies

### Authentication Testing (`authentication_test.py`)

**Mock Setup (Actual Test Pattern):**

```python
@pytest.fixture
def mock_settings():
    with patch("aignostics.platform._authentication.settings") as mock:
        settings = MagicMock()
        settings.token_file = Path("mock_token")
        settings.client_id_interactive = SecretStr("test-client")
        # Other settings...
        mock.return_value = settings
        yield mock

@pytest.fixture(autouse=True)
def mock_can_open_browser():
    """Prevent browser opening in tests."""
    with patch("aignostics.platform._authentication._can_open_browser", return_value=False):
        yield

@pytest.fixture(autouse=True)
def mock_webbrowser():
    """Prevent actual browser launch."""
    with patch("webbrowser.open_new") as mock:
        yield mock
```

**Token Format Testing:**

```python
def valid_token_with_expiry() -> str:
    """Create test token with future expiry."""
    future_time = int((datetime.now(tz=UTC) + timedelta(hours=1)).timestamp())
    return f"valid.jwt.token:{future_time}"

def expired_token() -> str:
    """Create expired test token."""
    past_time = int((datetime.now(tz=UTC) - timedelta(hours=1)).timestamp())
    return f"expired.jwt.token:{past_time}"
```

### Resource Testing (`runs_test.py`)

**Pagination Test Pattern:**

```python
def test_runs_list_with_pagination(runs, mock_api):
    # Setup pages
    page1 = [Mock(spec=RunReadResponse, run_id=f"run-{i}")
             for i in range(PAGE_SIZE)]
    page2 = [Mock(spec=RunReadResponse, run_id=f"run-{i + PAGE_SIZE}")
             for i in range(5)]

    mock_api.list_application_runs_v1_runs_get.side_effect = [page1, page2]

    # Test pagination
    result = list(runs.list())
    assert len(result) == PAGE_SIZE + 5
    assert all(isinstance(run, Run) for run in result)
```

## Operational Requirements

### Monitoring & Observability

**Key Metrics:**

- Authentication success/failure rates
- Token refresh timing (5-minute buffer)
- API call latency
- Pagination efficiency (pages fetched vs items needed)

**Logging (Actual Pattern from Code):**

```python
logger = get_logger(__name__)

logger.debug("Initializing client with cache_token=%s", cache_token)
logger.debug("Client initialized successfully.")
logger.exception("Failed to initialize client.")
logger.warning("Application with ID '%s' not found.", application_id)
```

### Security & Compliance

**Token Storage:**

- Stored in `~/.aignostics/token.json` (or configured path)
- Format: `token:expiry_timestamp`
- File permissions should be restricted (user-only)
- No refresh tokens stored

**Network Configuration:**

- Proxy support via `getproxies()` from urllib
- SSL/TLS handled by underlying libraries
- Certificate validation per system configuration

## Common Pitfalls & Solutions

### Token Expiry

**Problem:** Token expires during long operations

**Solution:**

```python
# Check remaining time before long operation
token = get_token()
claims = verify_and_decode_token(token)
expires_at = datetime.fromtimestamp(claims["exp"], tz=UTC)
time_remaining = expires_at - datetime.now(tz=UTC)

if time_remaining < timedelta(minutes=10):
    # Force refresh
    remove_cached_token()
    token = get_token()
```

### Pagination Limits

**Problem:** Trying to use page_size > 100

**Solution:**

```python
# Maximum page size is 100 for runs
MAX_PAGE_SIZE = 100
page_size = min(requested_size, MAX_PAGE_SIZE)
runs = client.runs.list(page_size=page_size)
```

### Application Lookup Performance

**Problem:** `client.application(id)` iterates all applications

**Solution:**

```python
# Cache applications list if doing multiple lookups
all_apps = list(client.applications.list())
app_dict = {app.application_id: app for app in all_apps}
# Now lookups are O(1)
app = app_dict.get("app-id")

# For version lookups, use direct API call
version = client.application_version(
    application_id="heta",
    version_number="1.0.0"  # or None for latest
)
# Access version attributes
print(f"App: {version.application_id}, Version: {version.version_number}")
```

## Module Dependencies

### Internal Dependencies

- `utils` - Logging via `get_logger()`, user agent generation via `user_agent()`
- `utils._constants` - Project metadata and environment detection
- `constants` - API versioning (not directly used in main client)

### External Dependencies

- `aignx.codegen` - Generated API client (OpenAPI)
- `requests-oauthlib` - OAuth2 session management
- `pyjwt` - JWT token validation
- `urllib3` - HTTP client (via generated client)

### Generated Code Structure

```python
from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.api_client import ApiClient
from aignx.codegen.configuration import Configuration
from aignx.codegen.exceptions import NotFoundException, ApiException
from aignx.codegen.models import (
    ApplicationReadResponse,
    MeReadResponse,
    RunReadResponse,
    # ... other models
)
```

## Development Guidelines

### Adding New Resources

1. Create resource class in `resources/` directory
2. Follow existing pattern (Applications, Runs)
3. Use `paginate` helper from `resources/utils.py`
4. Add to Client class as property
5. Write tests following existing patterns
6. Update this documentation

### Error Handling

```python
# Use specific exceptions from aignx.codegen
from aignx.codegen.exceptions import NotFoundException, ApiException

# Log appropriately
logger.warning("Resource not found: %s", resource_id)
logger.exception("Unexpected API error")

# Raise meaningful errors
raise ValueError(f"Invalid page_size: {page_size}, max is {MAX_PAGE_SIZE}")
```

## Performance Notes

### Current Limitations

1. **No connection pooling configuration** visible in current implementation
2. **No retry logic** in base client (may be in generated code)
3. **Application lookup is O(n)** - iterates all applications
4. **No caching** beyond token caching

### Optimization Opportunities

1. Add application caching layer
2. Implement connection pooling configuration
3. Add retry decorators for transient failures
4. Consider cursor-based pagination for large datasets

---

*This documentation reflects the actual implementation as of the current codebase version.*
