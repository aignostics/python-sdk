# CLAUDE.md - Platform Module

This file provides comprehensive guidance to Claude Code and human engineers when working with the `platform` module in this repository.

## Module Overview

The platform module serves as the foundational API client interface for the Aignostics Platform, providing secure, scalable, and enterprise-ready access to computational pathology services.

### Core Responsibilities

- **Authentication & Security**: OAuth 2.0 device flow, JWT validation, token lifecycle management
- **API Client Management**: Resource-oriented client with automatic retries, connection pooling, proxy support
- **Resource Abstraction**: Type-safe wrappers for applications, versions, runs with pagination
- **Environment Management**: Multi-environment support (dev/staging/production) with automatic detection
- **Error Recovery**: Comprehensive error handling with user guidance and automatic recovery strategies

### User Interfaces

**CLI Commands (`_cli.py`):**

- `login` - Authenticate with Aignostics Platform (device flow or browser)
- `logout` - Remove cached authentication token
- `whoami` - Display current user information and organization details

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

    def run(self, application_run_id: str) -> ApplicationRun:
        """Get specific run by ID."""
        return ApplicationRun(self._api, application_run_id)

    def application(self, application_id: str) -> Application:
        """Find application by ID (iterates through list)."""
        # NOTE: Currently no direct endpoint, iterates all apps
        for app in self.applications.list():
            if app.application_id == application_id:
                return app
        raise NotFoundException
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
        application_version_id: str | None = None,
        page_size: int = LIST_APPLICATION_RUNS_MAX_PAGE_SIZE
    ):
        """List runs with pagination."""
        if page_size > LIST_APPLICATION_RUNS_MAX_PAGE_SIZE:
            raise ValueError(f"page_size must be <= {LIST_APPLICATION_RUNS_MAX_PAGE_SIZE}")

        # Uses paginate helper internally
        # Returns generator of ApplicationRun instances
```

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

# Get specific run
run = client.run("run-id-123")

# List runs with custom page size
runs = client.runs.list(page_size=50)  # Max 100
for run in runs:
    print(f"Run: {run.application_run_id}")
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
    page1 = [Mock(spec=RunReadResponse, application_run_id=f"run-{i}")
             for i in range(PAGE_SIZE)]
    page2 = [Mock(spec=RunReadResponse, application_run_id=f"run-{i + PAGE_SIZE}")
             for i in range(5)]

    mock_api.list_application_runs_v1_runs_get.side_effect = [page1, page2]

    # Test pagination
    result = list(runs.list())
    assert len(result) == PAGE_SIZE + 5
    assert all(isinstance(run, ApplicationRun) for run in result)
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
```

## Module Dependencies

### Internal Dependencies

- `utils` - Logging via `get_logger()`
- `constants` - Not directly used in main client

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
