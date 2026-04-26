# CLAUDE.md - Test Suite

This file provides comprehensive guidance for working with the test suite of the Aignostics Python SDK.

## Test Architecture Overview

The test suite follows production-grade testing practices with comprehensive coverage across unit, integration, and end-to-end scenarios.

### Test Organization

```
tests/
├── conftest.py              # Global fixtures and configuration
├── aignostics/
│   ├── platform/           # Platform module tests
│   │   ├── authentication_test.py  # OAuth flow testing
│   │   ├── sdk_metadata_test.py    # SDK metadata system tests (NEW)
│   │   ├── cli_test.py            # CLI command testing (includes metadata schema)
│   │   ├── resources/      # Resource-specific tests
│   │   └── scheduled_test.py      # Periodic validation
│   ├── application/        # Application orchestration tests
│   │   ├── service_test.py # Semver validation, workflows
│   │   ├── cli_test.py     # CLI command testing
│   │   └── gui_test.py     # NiceGUI component tests
│   ├── dataset/            # Dataset download tests
│   ├── wsi/               # Image processing tests
│   ├── utils/             # Infrastructure tests
│   └── docker_test.py     # Container integration
├── fixtures/              # Test data and mock files
└── resources/            # Test resources (WSI samples, configs)
```

## Critical Test Patterns

### Authentication Testing (`platform/authentication_test.py`)

**Mock Strategy:**

```python
@pytest.fixture
def mock_settings():
    """Mock authentication settings to prevent real OAuth flows."""
    with patch("aignostics.platform._authentication.settings") as mock:
        settings = MagicMock()
        settings.token_file = Path("mock_token")
        settings.client_id_interactive = SecretStr("test-client")
        mock.return_value = settings
        yield mock


@pytest.fixture(autouse=True)
def mock_can_open_browser():
    """Prevent browser opening in CI/CD."""
    with patch("_can_open_browser", return_value=False):
        yield
```

**Token Lifecycle Testing:**

```python
def test_token_refresh_timing():
    """Verify token refreshes 5 minutes before expiry."""
    future_time = int((datetime.now(tz=UTC) + timedelta(hours=1)).timestamp())
    valid_token = f"token:{future_time}"

    # Should not refresh
    assert get_token(use_cache=True) == "token"

    # Should refresh when < 5 minutes left
    near_expiry = int((datetime.now(tz=UTC) + timedelta(minutes=4)).timestamp())
    expiring_token = f"token:{near_expiry}"
    # Verify refresh triggered
```

### Semver Validation Testing (`application/service_test.py`)

**Comprehensive Format Testing:**

```python
def test_application_version_formats():
    """Test all valid and invalid semver formats."""
    valid = ["1.0.0", "1.0.0-alpha", "1.0.0+meta", "1.0.0-rc.1+meta"]

    invalid = [
        "v1.0.0",  # 'v' prefix not allowed
        "1.0",  # Incomplete
        "",  # Empty string
    ]

    for v in valid:
        assert service.application_version("test-app", v)

    for v in invalid:
        with pytest.raises(ValueError):
            service.application_version("test-app", v)
```

### SDK Metadata Testing (`platform/sdk_metadata_test.py`)

**ENHANCED FEATURE TESTS (Run v0.0.4, Item v0.0.3):** Comprehensive testing of the SDK metadata system with separate Run and Item metadata schemas, tags support, and timestamps.

**Test Coverage:**

1. **Metadata Building Tests** - Verify automatic metadata generation in various environments
2. **Schema Validation Tests** - Ensure strict Pydantic validation catches invalid data
3. **CI/CD Integration Tests** - Test GitHub Actions and pytest context capture
4. **Environment Detection Tests** - Verify interface and source detection logic
5. **JSON Schema Generation Tests** - Validate schema structure and versioning

**Clean Environment Fixture:**

```python
@pytest.fixture
def clean_env():
    """Clean environment for SDK metadata tests."""
    # Save original environment
    original_env = os.environ.copy()

    # Clear SDK-related variables
    for key in list(os.environ.keys()):
        if key.startswith(("GITHUB_", "PYTEST_", "NICEGUI_", "AIGNOSTICS_")):
            del os.environ[key]

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
```

**Metadata Building Tests:**

```python
class TestBuildSdkMetadata:
    """Test cases for build_sdk_metadata function."""

    def test_build_metadata_minimal(clean_env: None) -> None:
        """Test metadata building with minimal environment."""
        metadata = build_sdk_metadata()

        # Required fields always present
        assert "schema_version" in metadata
        assert metadata["schema_version"] == "0.0.1"
        assert "submission" in metadata
        assert "user_agent" in metadata
        assert metadata["submission"]["interface"] in ["script", "cli", "launchpad"]
        assert metadata["submission"]["initiator"] in ["user", "test", "bridge"]
        assert "date" in metadata["submission"]

        # Optional fields may be absent
        # user, ci, note, workflow, scheduling are optional

    def test_build_metadata_with_github_ci(clean_env: None) -> None:
        """Test metadata with GitHub Actions environment."""
        # Set GitHub Actions environment variables
        os.environ["GITHUB_RUN_ID"] = "12345"
        os.environ["GITHUB_REPOSITORY"] = "aignostics/python-sdk"
        os.environ["GITHUB_SHA"] = "abc123def456"  # pragma: allowlist secret
        os.environ["GITHUB_REF"] = "refs/heads/main"
        os.environ["GITHUB_WORKFLOW"] = "CI/CD"

        metadata = build_sdk_metadata()

        # GitHub CI metadata should be present
        assert "ci" in metadata
        assert "github" in metadata["ci"]
        assert metadata["ci"]["github"]["run_id"] == "12345"
        assert metadata["ci"]["github"]["repository"] == "aignostics/python-sdk"
        assert metadata["ci"]["github"]["sha"] == "abc123def456"  # pragma: allowlist secret
        assert metadata["ci"]["github"]["run_url"] == ("https://github.com/aignostics/python-sdk/actions/runs/12345")

    def test_build_metadata_with_pytest(clean_env: None) -> None:
        """Test metadata with pytest environment."""
        os.environ["PYTEST_CURRENT_TEST"] = "tests/platform/sdk_metadata_test.py::test_foo"
        os.environ["PYTEST_MARKERS"] = "unit,sequential"

        metadata = build_sdk_metadata()

        # Pytest CI metadata should be present
        assert "ci" in metadata
        assert "pytest" in metadata["ci"]
        assert metadata["ci"]["pytest"]["current_test"] == ("tests/platform/sdk_metadata_test.py::test_foo")
        assert metadata["ci"]["pytest"]["markers"] == ["unit", "sequential"]

    def test_interface_detection_cli(clean_env: None) -> None:
        """Test CLI interface detection."""
        with patch("sys.argv", ["aignostics", "user", "login"]):
            metadata = build_sdk_metadata()
            assert metadata["submission"]["interface"] == "cli"

    def test_interface_detection_launchpad(clean_env: None) -> None:
        """Test launchpad (GUI) interface detection."""
        os.environ["NICEGUI_HOST"] = "localhost"
        metadata = build_sdk_metadata()
        assert metadata["submission"]["interface"] == "launchpad"

    def test_source_detection_test(clean_env: None) -> None:
        """Test source detection for pytest."""
        os.environ["PYTEST_CURRENT_TEST"] = "test.py::test_foo"
        metadata = build_sdk_metadata()
        assert metadata["submission"]["initiator"] == "test"

    def test_source_detection_bridge(clean_env: None) -> None:
        """Test source detection for bridge."""
        os.environ["AIGNOSTICS_BRIDGE_VERSION"] = "1.0.0"
        metadata = build_sdk_metadata()
        assert metadata["submission"]["initiator"] == "bridge"
```

**Validation Tests:**

```python
class TestValidateSdkMetadata:
    """Test SDK metadata validation."""

    def test_validate_valid_metadata(clean_env: None) -> None:
        """Test validation of valid metadata."""
        metadata = build_sdk_metadata()
        assert validate_sdk_metadata(metadata) is True
        assert validate_sdk_metadata_silent(metadata) is True

    def test_validate_missing_required_field() -> None:
        """Test validation fails for missing required fields."""
        metadata = {
            # Missing schema_version
            "submission": {
                "date": "2025-10-19T12:00:00Z",
                "interface": "script",
                "source": "user",
            },
            "user_agent": "test/1.0.0",
        }

        with pytest.raises(ValidationError):
            validate_sdk_metadata(metadata)

        assert validate_sdk_metadata_silent(metadata) is False

    def test_validate_invalid_enum_value() -> None:
        """Test validation fails for invalid enum values."""
        metadata = {
            "schema_version": "0.0.1",
            "submission": {
                "date": "2025-10-19T12:00:00Z",
                "interface": "invalid_interface",  # Invalid enum value
                "source": "user",
            },
            "user_agent": "test/1.0.0",
        }

        with pytest.raises(ValidationError):
            validate_sdk_metadata(metadata)

    def test_validate_extra_fields_forbidden() -> None:
        """Test validation fails when extra fields are present."""
        metadata = build_sdk_metadata()
        metadata["unknown_field"] = "value"  # Extra field

        with pytest.raises(ValidationError, match="extra fields not permitted"):
            validate_sdk_metadata(metadata)
```

**JSON Schema Tests:**

```python
class TestGetSdkMetadataJsonSchema:
    """Test JSON schema generation."""

    def test_schema_structure() -> None:
        """Test JSON schema has required fields."""
        schema = get_sdk_metadata_json_schema()

        assert "$schema" in schema
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"

        assert "$id" in schema
        assert (
            schema["$id"] == f"https://raw.githubusercontent.com/aignostics/python-sdk/main/"
            f"docs/source/_static/sdk_metadata_schema_v{SDK_METADATA_SCHEMA_VERSION}.json"
        )

        assert "properties" in schema
        assert "required" in schema

    def test_schema_validates_built_metadata(clean_env: None) -> None:
        """Test that generated schema validates built metadata."""
        import jsonschema

        schema = get_sdk_metadata_json_schema()
        metadata = build_sdk_metadata()

        # Should not raise ValidationError
        jsonschema.validate(instance=metadata, schema=schema)
```

**CLI Tests (`platform/cli_test.py`):**

```python
class TestSdkMetadataSchemaCommand:
    """Test SDK metadata schema CLI command."""

    def test_sdk_metadata_schema_pretty(runner: CliRunner) -> None:
        """Test schema output with pretty printing."""
        result = runner.invoke(cli_sdk, ["metadata-schema", "--pretty"])

        assert result.exit_code == 0
        assert "$schema" in result.output
        assert "$id" in result.output
        assert "sdk_metadata_schema" in result.output

        # Should be valid JSON
        schema = json.loads(result.output)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"

    def test_sdk_metadata_schema_no_pretty(runner: CliRunner) -> None:
        """Test schema output without pretty printing (compact)."""
        result = runner.invoke(cli_sdk, ["metadata-schema", "--no-pretty"])

        assert result.exit_code == 0
        # Compact JSON (no indentation)
        assert "\n  " not in result.output or result.output.count("\n") < 10

        # Should still be valid JSON
        schema = json.loads(result.output)
        assert "$schema" in schema
```

**Integration with Run Submission:**

Tested in `application/service_test.py` and `application/cli_test.py` to ensure SDK metadata is automatically attached to all run submissions.

**Key Testing Principles:**

1. **Clean Environment**: Use `clean_env` fixture to ensure test isolation
2. **Environment Simulation**: Mock GitHub Actions and pytest environments
3. **Validation Strictness**: Test both valid and invalid metadata structures
4. **Schema Consistency**: Verify generated schema validates built metadata
5. **CLI Integration**: Test schema export command
6. **Optional Fields**: Verify system works with missing optional fields
7. **Error Cases**: Test validation catches all invalid inputs

### Cache Bypass Testing (`platform/nocache_test.py` - NEW in v1.0.0-beta.7)

**Comprehensive testing of the nocache parameter** for cache bypass functionality across all cached operations.

**Test Coverage:**

1. **Decorator Behavior Tests** - Verify @cached_operation decorator handles nocache correctly
2. **Client Method Tests** - Test nocache on Client.me(), Client.application(), Client.application_version()
3. **Resource Method Tests** - Test nocache on Runs.list(), Run.details(), Applications.list()
4. **Edge Case Tests** - Expired cache entries, multiple consecutive nocache calls, interleaved usage
5. **Cache Clear Integration** - Test interaction between nocache and cache clearing

**Core Testing Principles:**

```python
class TestNocacheDecoratorBehavior:
    """Test the nocache parameter handling in the cached_operation decorator."""

    def test_decorator_without_nocache_uses_cache() -> None:
        """Verify default behavior uses cache."""
        call_count = 0

        @cached_operation(ttl=60, use_token=False)
        def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # First call - executes function
        result1 = test_func()
        assert result1 == 1
        assert call_count == 1

        # Second call - uses cache
        result2 = test_func()
        assert result2 == 1  # Same value from cache
        assert call_count == 1  # Function NOT called again

    def test_decorator_with_nocache_true_skips_reading_cache() -> None:
        """Verify nocache=True skips cache read."""
        call_count = 0

        @cached_operation(ttl=60, use_token=False)
        def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # First call - populates cache
        result1 = test_func()
        assert result1 == 1

        # Second call with nocache=True - skips cache, executes function
        result2 = test_func(nocache=True)
        assert result2 == 2  # NEW value, not from cache
        assert call_count == 2  # Function called again

    def test_decorator_with_nocache_true_still_writes_to_cache() -> None:
        """Verify nocache=True still writes result to cache."""
        call_count = 0

        @cached_operation(ttl=60, use_token=False)
        def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # First call - populates cache
        result1 = test_func()
        assert result1 == 1

        # Second call with nocache=True - skips read, writes new value
        result2 = test_func(nocache=True)
        assert result2 == 2

        # Third call without nocache - uses value cached by second call
        result3 = test_func()
        assert result3 == 2  # Uses value from second call
        assert call_count == 2  # Function NOT called again

    def test_decorator_nocache_parameter_not_passed_to_function() -> None:
        """Verify nocache is intercepted and not passed to decorated function."""
        received_kwargs = {}

        @cached_operation(ttl=60, use_token=False)
        def test_func(**kwargs: bool) -> dict:
            nonlocal received_kwargs
            received_kwargs = kwargs
            return {"called": True}

        # Call with nocache=True
        test_func(nocache=True)

        # The decorated function should NOT receive nocache in kwargs
        assert "nocache" not in received_kwargs
```

**Client Method Testing:**

```python
class TestClientMeNocache:
    """Test nocache parameter for Client.me() method."""

    def test_me_default_uses_cache(client_with_mock_api: Client, mock_api_client: MagicMock) -> None:
        """Verify me() uses cache by default."""
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response

        # First call
        result1 = client_with_mock_api.me()
        assert result1 == mock_me_response
        assert mock_api_client.get_me_v1_me_get.call_count == 1

        # Second call - should use cache
        result2 = client_with_mock_api.me()
        assert result2 == mock_me_response
        assert mock_api_client.get_me_v1_me_get.call_count == 1  # No additional call

    def test_me_nocache_true_fetches_fresh_data(client_with_mock_api: Client, mock_api_client: MagicMock) -> None:
        """Verify me(nocache=True) fetches fresh data."""
        mock_me_response_1 = {"user_id": "user-1"}
        mock_me_response_2 = {"user_id": "user-2"}

        # First call - populates cache
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response_1
        result1 = client_with_mock_api.me()
        assert result1 == mock_me_response_1

        # Change API response
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response_2

        # Second call with nocache=True - fetches fresh data
        result2 = client_with_mock_api.me(nocache=True)
        assert result2 == mock_me_response_2
        assert mock_api_client.get_me_v1_me_get.call_count == 2  # Additional call made

    def test_me_nocache_true_updates_cache(client_with_mock_api: Client, mock_api_client: MagicMock) -> None:
        """Verify me(nocache=True) updates cache with fresh data."""
        mock_me_response_1 = {"user_id": "user-1"}
        mock_me_response_2 = {"user_id": "user-2"}

        # First call - populates cache
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response_1
        result1 = client_with_mock_api.me()

        # Change API response
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response_2

        # Second call with nocache=True - fetches and caches new data
        result2 = client_with_mock_api.me(nocache=True)
        assert result2 == mock_me_response_2

        # Third call without nocache - uses updated cache
        result3 = client_with_mock_api.me()
        assert result3 == mock_me_response_2  # Uses new cached value
        assert mock_api_client.get_me_v1_me_get.call_count == 2  # No additional call
```

**Edge Case Testing:**

```python
class TestNocacheEdgeCases:
    """Test edge cases and special scenarios."""

    def test_nocache_with_expired_cache_entry() -> None:
        """Test nocache behavior when cache entry expired."""

        @cached_operation(ttl=1, use_token=False)  # 1 second TTL
        def test_func() -> int:
            return time.time_ns()

        # First call - populates cache
        result1 = test_func()

        # Wait for cache to expire
        time.sleep(1.1)

        # Call with nocache=True on expired entry
        result2 = test_func(nocache=True)
        assert result2 != result1  # Different value

    def test_multiple_consecutive_nocache_calls() -> None:
        """Test multiple consecutive calls with nocache=True."""
        call_count = 0

        @cached_operation(ttl=60, use_token=False)
        def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # Multiple calls with nocache=True
        assert test_func(nocache=True) == 1
        assert test_func(nocache=True) == 2
        assert test_func(nocache=True) == 3
        assert call_count == 3

        # Last call without nocache uses cached value from third call
        assert test_func() == 3
        assert call_count == 3

    def test_nocache_interleaved_with_normal_calls() -> None:
        """Test interleaving nocache=True with normal cached calls."""
        call_count = 0

        @cached_operation(ttl=60, use_token=False)
        def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # Normal call - populates cache
        assert test_func() == 1
        assert call_count == 1

        # Normal call - uses cache
        assert test_func() == 1
        assert call_count == 1

        # Nocache call - skips cache, updates it
        assert test_func(nocache=True) == 2
        assert call_count == 2

        # Normal call - uses updated cache
        assert test_func() == 2
        assert call_count == 2
```

**Key Testing Principles:**

1. **Cache Read Bypass**: nocache=True skips reading from cache
2. **Cache Write Preserved**: nocache=True still writes to cache
3. **Parameter Interception**: nocache parameter intercepted by decorator, not passed to function
4. **Cache Key Isolation**: nocache respects different cache keys (different function args)
5. **Edge Case Coverage**: Expired entries, multiple consecutive calls, interleaved usage
6. **Integration Testing**: Test across all cached Client and Resource methods
7. **Signature Verification**: Test method signatures include nocache parameter with correct type hints

**Use Cases Tested:**

* **Testing**: Avoid race conditions from stale cached data
* **Real-time Monitoring**: Ensure latest status in dashboards
* **After Mutations**: Get fresh data immediately after updates
* **Cache Refresh**: Force cache update without full cache clear

### Process Management Testing (`dataset/service_test.py`)

**Subprocess Cleanup Verification:**

```python
def test_cleanup_processes_terminates_running():
    """Verify orphaned processes are terminated."""
    mock_running = MagicMock(spec=subprocess.Popen)
    mock_running.poll.return_value = None  # Still running

    _active_processes.append(mock_running)
    _cleanup_processes()

    # Verify termination sequence
    mock_running.terminate.assert_called_once()
    if still_running:
        mock_running.kill.assert_called_once()
```

### Pagination Testing (`platform/resources/runs_test.py`)

**Memory-Efficient Generator Testing:**

```python
def test_pagination_generator():
    """Verify pagination doesn't materialize full result set."""
    page1 = [Mock(id=f"run-{i}") for i in range(50)]
    page2 = [Mock(id=f"run-{i + 50}") for i in range(5)]
    mock_api.list_runs.side_effect = [page1, page2]

    result_gen = runs.list()  # Generator, not list
    assert not isinstance(result_gen, list)

    # Consume generator
    results = list(result_gen)
    assert len(results) == 55
    assert mock_api.list_runs.call_count == 2
```

## Test Fixtures & Utilities

### Global Fixtures (`conftest.py`)

**Cross-Platform Output Normalization:**

```python
def normalize_output(output: str) -> str:
    """Handle Windows/Unix line endings in CLI tests."""
    return output.replace("\r\n", "").replace("\n", "")
```

**QuPath Cleanup:**

```python
@pytest.fixture
def qupath_teardown():
    """Ensure QuPath processes cleaned up."""
    yield
    # Kill any remaining QuPath processes
    for proc in psutil.process_iter(["name"]):
        if "QuPath" in proc.info["name"]:
            proc.terminate()
            proc.wait(timeout=5)
```

**NiceGUI Testing:**

```python
# Auto-discovered plugin for GUI testing
if find_spec("nicegui"):
    pytest_plugins = ("nicegui.testing.plugin",)
```

## Test Markers & Categories

### Marker Definitions

```python
@pytest.mark.docker       # Requires Docker
@pytest.mark.scheduled    # Periodic validation
@pytest.mark.long_running # Extended execution time
@pytest.mark.sequential   # Cannot run in parallel
@pytest.mark.skip_with_act # Skip in GitHub Act
```

### Test Execution Strategies

**Parallel Execution:**

```bash
# Run tests in parallel (default)
pytest -n auto

# Sequential tests only
pytest -m sequential

# Long-running tests
pytest -m long_running --cov-append
```

**Docker Integration:**

```bash
# Tests requiring Docker services
pytest -m docker

# Cleanup Docker containers after tests
docker compose ls --format json | jq -r '.[].Name' | grep ^pytest | xargs -I {} docker compose -p {} down
```

## Mock Strategies

### API Client Mocking

```python
@pytest.fixture
def mock_api():
    """Mock aignx.codegen API client."""
    api = Mock(spec=PublicApi)
    api.list_applications.return_value = [...]
    return api


@pytest.fixture
def mock_client(mock_api):
    """Mock platform Client."""
    client = Mock(spec=Client)
    client._api = mock_api
    return client
```

### File System Mocking

```python
@pytest.fixture
def mock_wsi_file(tmp_path):
    """Create mock WSI file."""
    wsi = tmp_path / "test.svs"
    wsi.write_bytes(b"mock_wsi_data")
    return wsi
```

### Network Response Mocking

```python
@responses.activate
def test_api_call():
    responses.add(responses.GET, "https://api.aignostics.com/v1/runs", json={"runs": []}, status=200)
```

## Test Coverage Requirements

### Module Coverage Targets

```python
# Minimum coverage: 85%
# Critical modules: 95%

COVERAGE_REQUIREMENTS = {
    "platform": 95,  # Critical auth/API
    "application": 90,  # Core workflows
    "utils": 95,  # Infrastructure
    "dataset": 85,  # External dependencies
    "wsi": 85,  # Binary processing
}
```

### Coverage Reporting

```bash
# Generate coverage report
pytest --cov=aignostics --cov-report=html

# Check coverage thresholds
pytest --cov=aignostics --cov-fail-under=85
```

## Performance Testing

### Load Testing Patterns

```python
@pytest.mark.long_running
def test_concurrent_runs():
    """Test 100 concurrent application runs."""
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(create_run) for _ in range(100)]
        results = [f.result(timeout=60) for f in futures]
        assert len(results) == 100
```

### Memory Leak Detection

```python
@pytest.mark.long_running
def test_memory_usage():
    """Verify no memory leaks in long operations."""
    import tracemalloc

    tracemalloc.start()

    # Run operations
    for _ in range(1000):
        process_large_file()

    current, peak = tracemalloc.get_traced_memory()
    assert peak < 1024 * 1024 * 500  # < 500MB
```

## Integration Testing

### Docker-Based Testing

```python
@pytest.mark.docker
class TestPlatformIntegration:
    @pytest.fixture
    def platform_container(self, docker_services):
        """Start mock platform API."""
        docker_services.start("platform-mock")
        docker_services.wait_until_responsive(
            check=lambda: requests.get("http://localhost:8080/health"), timeout=30.0, pause=0.5
        )

    def test_full_workflow(self, platform_container):
        """Test complete application workflow."""
        # Test against containerized services
```

### End-to-End Testing

```python
@pytest.mark.scheduled
def test_production_connectivity():
    """Verify production API accessibility."""
    client = Client()
    assert client.applications.list()  # Should not fail
```

## Test Data Management

### Fixture Organization

```
fixtures/
├── wsi/
│   ├── small.svs      # 10MB test file
│   ├── large.tiff     # 1GB test file
│   └── invalid.dcm    # Corrupted for error testing
├── configs/
│   ├── test_settings.json
│   └── mock_credentials.json
└── responses/
    ├── api_responses.json
    └── error_responses.json
```

### Test Data Generation

```python
def create_test_wsi(size_mb: int = 10) -> Path:
    """Generate test WSI file of specified size."""
    data = os.urandom(size_mb * 1024 * 1024)
    path = Path(f"test_{size_mb}mb.svs")
    path.write_bytes(data)
    return path
```

## CI/CD Integration

### GitHub Actions Configuration

```yaml
- name: Run Tests
  run: |
    make test
    make test_long_running
    make test_scheduled

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./reports/coverage.xml
    fail_ci_if_error: true
```

### Pre-commit Hooks

```yaml
- repo: local
  hooks:
    - id: pytest-check
      name: pytest-check
      entry: pytest tests/ -x --tb=short
      language: system
      pass_filenames: false
      always_run: true
```

## Common Test Patterns

### Parameterized Testing

```python
@pytest.mark.parametrize(
    "version,expected",
    [
        ("v1.0.0", True),
        ("1.0.0", False),
        ("v1.0", False),
    ],
)
def test_version_validation(version, expected):
    assert is_valid_semver(version) == expected
```

### Async Testing

```python
@pytest.mark.asyncio
async def test_async_api_call():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.aignostics.com")
        assert response.status_code == 200
```

### Snapshot Testing

```python
def test_api_response_structure(snapshot):
    response = client.applications.list()
    snapshot.assert_match(response.json())
```

## NiceGUI Troubleshooting

### Symptom: Element State Lost After User Interaction (NiceGUI 3.0+)

**Problem:** After upgrading to NiceGUI 3.0+, tests fail because UI element state (e.g., button enabled/disabled, input values) is lost after user interactions inside `@ui.refreshable` functions.

**Root Cause:** NiceGUI 3.0.0 introduced observable props/classes/styles that automatically sync UI updates. When modifying `.value` on elements inside `@ui.refreshable`, the framework may trigger element recreation, causing local variables to reset.

**Symptom Example:**

```python
@ui.refreshable
def dialog_content() -> None:
    selected_folder = ui.input("Folder", value="")  # Local variable resets on recreation!
    download_button = ui.button("Download").props("disabled")

    def on_select():
        selected_folder.value = "/path/to/folder"  # This may trigger refresh
        download_button.enable()  # Button recreated, enable() lost
```

**Solution:** Use a mutable dictionary container instead of `ui.state()` when the `@ui.refreshable` function has parameters that must be preserved:

```python
@ui.refreshable
def dialog_content(qupath_project: bool = False) -> None:
    # Use mutable dict instead of ui.state() to avoid triggering refresh
    # which would reset qupath_project to its default value.
    # ui.state() triggers refresh() internally when set_folder() is called,
    # but refresh() without arguments uses the original call arguments.
    folder_state: dict[str, str] = {"value": ""}

    selected_folder = ui.input("Folder", value=folder_state["value"])
    download_button = ui.button("Download")
    if not folder_state["value"]:
        download_button.disable()

    def on_select():
        folder_value = "/path/to/folder"
        folder_state["value"] = folder_value  # Update dict without triggering refresh
        selected_folder.value = folder_value
        download_button.enable()
```

**Why This Works:**

1. Mutable dict container stores state without triggering `refresh()`
2. `ui.state()` internally calls `refresh()` when setter is invoked, which uses **original** function arguments
3. For `@ui.refreshable` functions with parameters, `ui.state()` setter can reset those parameters to defaults
4. The dict pattern preserves both local state AND function arguments

**CRITICAL:** Do NOT use `ui.state()` in `@ui.refreshable` functions that accept parameters and are called with `refresh(param=value)`. The `set_state()` function triggers `refresh()` without arguments, resetting all parameters to their defaults.

**When to use each pattern:**

| Pattern | Use Case |
|---------|----------|
| `ui.state()` | `@ui.refreshable` with no parameters or when refresh resets are acceptable |
| Mutable dict | `@ui.refreshable` with parameters that must be preserved after state updates |

**Reference:** [NiceGUI 3.0.0 Release Notes](https://github.com/zauberzeug/nicegui/releases/tag/v3.0.0)

---

## Debugging Test Failures

### Verbose Output

```bash
# Maximum verbosity
pytest -vvv --tb=long

# Show print statements
pytest -s

# Stop on first failure
pytest -x
```

### Test Isolation

```bash
# Run specific test
pytest tests/aignostics/platform/authentication_test.py::test_token_refresh

# Run tests matching pattern
pytest -k "token"
```

### Debug Mode

```python
# Enable breakpoint in test
def test_complex_logic():
    result = complex_function()
    import pdb

    pdb.set_trace()  # Breakpoint
    assert result.status == "success"
```

## Test Maintenance

### Regular Tasks

1. **Weekly**: Run `make test_scheduled` for API compatibility
2. **Monthly**: Update test fixtures from production samples
3. **Quarterly**: Review and update coverage requirements
4. **Release**: Full regression suite including long_running tests

### Test Hygiene

* Remove obsolete tests
* Update mocks when API changes
* Maintain test documentation
* Regular dependency updates

---

*This test suite has been battle-tested across thousands of CI/CD runs and provides confidence for production deployments.*
