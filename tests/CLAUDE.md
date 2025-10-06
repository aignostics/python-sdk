# CLAUDE.md - Test Suite

This file provides comprehensive guidance for working with the test suite of the Aignostics Python SDK.

> **🧪 Quick Start for AI Agents:** For test-driven development workflows and common testing tasks, see [AGENTS.md](../AGENTS.md#-testing-strategies-for-agents). This file provides detailed test patterns and strategies.

## Test Architecture Overview

The test suite follows production-grade testing practices with comprehensive coverage across unit, integration, and end-to-end scenarios.

### Test Organization

```
tests/
├── conftest.py              # Global fixtures and configuration
├── aignostics/
│   ├── platform/           # Platform module tests
│   │   ├── authentication_test.py  # OAuth flow testing
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
    valid = [
        "app:v1.0.0",
        "app:v1.0.0-alpha",
        "app:v1.0.0+meta",
        "app:v1.0.0-rc.1+meta"
    ]

    invalid = [
        "app:1.0.0",  # Missing v
        "app:v1.0",   # Incomplete
        ":v1.0.0",    # Missing app
    ]

    for v in valid:
        assert service.application_version(v)

    for v in invalid:
        with pytest.raises(ValueError):
            service.application_version(v)
```

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
    page2 = [Mock(id=f"run-{i+50}") for i in range(5)]
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
    for proc in psutil.process_iter(['name']):
        if 'QuPath' in proc.info['name']:
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
    responses.add(
        responses.GET,
        "https://api.aignostics.com/v1/runs",
        json={"runs": []},
        status=200
    )
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
            check=lambda: requests.get("http://localhost:8080/health"),
            timeout=30.0,
            pause=0.5
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
@pytest.mark.parametrize("version,expected", [
    ("v1.0.0", True),
    ("1.0.0", False),
    ("v1.0", False),
])
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
    import pdb; pdb.set_trace()  # Breakpoint
    assert result.status == "success"
```

## Test Maintenance

### Regular Tasks

1. **Weekly**: Run `make test_scheduled` for API compatibility
2. **Monthly**: Update test fixtures from production samples
3. **Quarterly**: Review and update coverage requirements
4. **Release**: Full regression suite including long_running tests

### Test Hygiene

- Remove obsolete tests
- Update mocks when API changes
- Maintain test documentation
- Regular dependency updates

---

*This test suite has been battle-tested across thousands of CI/CD runs and provides confidence for production deployments.*
