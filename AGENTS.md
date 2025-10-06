# AGENTS.md - AI Coding Agents Guidance

This document provides comprehensive guidance for AI coding agents (GitHub Copilot, Claude Code, ChatGPT, and other LLMs) when working with the Aignostics Python SDK repository.

## Table of Contents

- [Quick Reference](#quick-reference)
- [Repository Architecture](#repository-architecture)
- [Development Workflow](#development-workflow)
- [Code Patterns](#code-patterns)
- [Testing Strategy](#testing-strategy)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)
- [AI-Specific Guidance](#ai-specific-guidance)

## Quick Reference

### Essential Files to Read First

1. **[CODE_STYLE.md](CODE_STYLE.md)** - Mandatory coding standards for all generated code
2. **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development workflow and build process
3. **[CLAUDE.md](CLAUDE.md)** - Comprehensive SDK architecture overview
4. **[src/aignostics/CLAUDE.md](src/aignostics/CLAUDE.md)** - Module architecture and interaction patterns
5. **[tests/CLAUDE.md](tests/CLAUDE.md)** - Testing patterns and requirements

### Primary Commands

```bash
# Setup
make install              # Install dev dependencies + pre-commit hooks

# Development
make lint                 # Ruff formatting + linting + MyPy type checking
make test                 # Run tests with coverage (requires 85% minimum)
make all                  # Run full CI pipeline (lint, test, docs, audit)

# Testing variants
make test 3.12            # Run tests on specific Python version
make test_sequential      # Run sequential-only tests
make test_long_running    # Run long-running tests
make test_scheduled       # Run scheduled validation tests

# Documentation
make docs                 # Build Sphinx documentation
make docs pdf             # Build PDF documentation

# Other
make help                 # Show all available targets
```

### Package Management

This project uses **uv** (not pip or poetry):

```bash
uv sync                   # Install dependencies
uv add <package>          # Add new dependency
uv run pytest             # Run commands in virtual environment
```

### Critical Constraints

- **Python Version**: 3.11, 3.12, 3.13 (check `.python-version`)
- **Line Length**: 120 characters maximum
- **Test Coverage**: 85% minimum (95% for critical modules)
- **Type Checking**: MyPy strict mode enforced
- **Commit Format**: Conventional commits required (e.g., `feat(module): description`)

## Repository Architecture

### Project Structure

```
aignostics-python-sdk/
├── src/aignostics/          # Source code (modulith architecture)
│   ├── utils/               # Foundation layer (DI, logging, settings)
│   ├── platform/            # API layer (authentication, clients)
│   ├── application/         # Domain modules
│   ├── wsi/                 # (Whole slide images)
│   ├── dataset/             # (Dataset operations)
│   ├── bucket/              # (Cloud storage)
│   ├── qupath/              # Integration modules
│   ├── notebook/            # (Marimo notebooks)
│   ├── gui/                 # System modules
│   └── system/              # (Diagnostics)
├── tests/                   # Test suite (mirrors src structure)
├── docs/                    # Sphinx documentation
│   ├── partials/            # Markdown partials for compilation
│   └── source/              # reStructuredText files
├── examples/                # Usage examples (notebooks, scripts)
├── reports/                 # Compliance reports (coverage, audit)
├── Makefile                 # Build automation
├── noxfile.py               # Multi-Python test orchestration
├── pyproject.toml           # Project configuration
└── .github/                 # GitHub Actions workflows
```

### Modulith Architecture Pattern

Each module follows a three-layer architecture:

```
module/
├── _service.py      # Business logic (inherits from BaseService)
├── _cli.py          # CLI commands (Typer framework)
├── _gui.py          # GUI components (NiceGUI framework)
├── _settings.py     # Configuration (Pydantic models)
└── CLAUDE.md        # Module documentation
```

**Layer Dependencies:**

```
┌─────────────┐     ┌─────────────┐
│  CLI Layer  │     │  GUI Layer  │
│  (_cli.py)  │     │  (_gui.py)  │
└──────┬──────┘     └──────┬──────┘
       └──────────┬─────────┘
                  ↓
         ┌────────────────┐
         │  Service Layer │
         │ (_service.py)  │
         └────────────────┘
```

**Critical Rules:**
- CLI and GUI layers **never** depend on each other
- All business logic lives in Service layer
- Services inherit from `BaseService` for dependency injection
- Services implement `health()` and `info()` methods

### Module Dependency Graph

```
system (monitors ALL modules)
  │
  ├── application
  │   ├── platform (auth)
  │   ├── bucket (storage)
  │   ├── wsi (images)
  │   └── qupath (optional)
  │
  ├── dataset → platform
  ├── bucket → platform
  ├── wsi → utils
  ├── notebook → utils
  ├── qupath → utils
  └── gui (aggregates all GUI modules)
```

**Foundation Layer:**
- `utils` - Infrastructure (DI, logging, settings, health checks)
- Must not depend on any other SDK module

**API Layer:**
- `platform` - Authentication and API gateway
- Depends only on `utils`

**Domain Modules:**
- `application`, `wsi`, `dataset`, `bucket` - Core functionality
- May depend on platform and utils

**Integration Modules:**
- `qupath`, `notebook` - Optional integrations
- Conditional loading based on dependencies

**System Modules:**
- `system` - Aggregates health from ALL modules
- `gui` - Aggregates all GUI components

## Development Workflow

### Initial Setup

```bash
# Clone repository
git clone git@github.com:aignostics/python-sdk.git
cd python-sdk

# Install dependencies
make install

# Setup environment (create .env from .env.example)
make setup
```

### Making Changes

1. **Before writing code:**
   - Read [CODE_STYLE.md](CODE_STYLE.md) for mandatory requirements
   - Check module-specific CLAUDE.md for patterns
   - Run existing tests to understand baseline

2. **Write code:**
   - Follow modulith patterns (see above)
   - Add type hints for all public APIs
   - Use Google-style docstrings
   - Handle errors explicitly

3. **Test changes:**
   ```bash
   make lint                    # Format and check code
   make test                    # Run test suite
   pytest tests/path/to/test.py::test_function  # Specific test
   ```

4. **Commit changes:**
   ```bash
   git add .
   git commit -m "feat(module): description"  # Conventional commits
   git push
   ```

   Pre-commit hooks will automatically:
   - Format code with ruff
   - Check types with mypy
   - Detect secrets
   - Validate commit message format

### CI/CD Pipeline

GitHub Actions runs on every push:

1. **Lint**: Ruff formatting, MyPy type checking
2. **Test**: Multi-Python version testing (3.11, 3.12, 3.13)
3. **Docs**: Sphinx documentation build
4. **Audit**: Security scanning, license compliance

**Skip CI**: Add `skip:ci` to commit message
**Skip specific tests**: `skip:test:long-running`, `skip:test:regular`, `skip:test:matrix-runner`

## Code Patterns

### Adding a New Module

1. **Create module directory:**
   ```bash
   mkdir -p src/aignostics/newmodule
   ```

2. **Implement service layer:**
   ```python
   # src/aignostics/newmodule/_service.py
   from aignostics.utils import BaseService, Health
   
   class Service(BaseService):
       """Module service implementation."""
       
       def health(self) -> Health:
           """Health check implementation."""
           return Health(status=Health.Code.UP)
       
       def info(self, mask_secrets: bool = True) -> dict:
           """Service information."""
           return {"version": "1.0.0", "module": "newmodule"}
       
       def perform_operation(self, param: str) -> str:
           """Business logic method."""
           return f"Processed: {param}"
   ```

3. **Add CLI commands:**
   ```python
   # src/aignostics/newmodule/_cli.py
   import typer
   from ._service import Service
   
   cli = typer.Typer(name="newmodule", help="New module operations")
   
   @cli.command("operation")
   def operation_command(param: str):
       """Perform operation via CLI."""
       service = Service()
       result = service.perform_operation(param)
       typer.echo(result)
   ```

4. **Add GUI interface (optional):**
   ```python
   # src/aignostics/newmodule/_gui.py
   from nicegui import ui
   from ._service import Service
   
   def create_page():
       """Create NiceGUI page for this module."""
       service = Service()
       
       ui.label("New Module Interface")
       
       with ui.card():
           param_input = ui.input(label="Parameter")
           result_label = ui.label()
           
           def on_click():
               result = service.perform_operation(param_input.value)
               result_label.text = result
           
           ui.button("Execute", on_click=on_click)
   ```

5. **Add settings:**
   ```python
   # src/aignostics/newmodule/_settings.py
   from pydantic_settings import BaseSettings
   
   class Settings(BaseSettings):
       """Module configuration."""
       
       api_endpoint: str = "https://api.example.com"
       timeout: int = 30
       
       class Config:
           env_prefix = "NEWMODULE_"
   ```

6. **Create documentation:**
   ```bash
   # src/aignostics/newmodule/CLAUDE.md
   # Document module purpose, API, patterns, examples
   ```

7. **Add tests:**
   ```python
   # tests/aignostics/newmodule/service_test.py
   import pytest
   from aignostics.newmodule._service import Service
   
   def test_perform_operation():
       service = Service()
       result = service.perform_operation("test")
       assert result == "Processed: test"
   
   def test_health():
       service = Service()
       health = service.health()
       assert health.status == Health.Code.UP
   ```

8. **Update module index:**
   - Add entry to `src/aignostics/CLAUDE.md`
   - Update dependency graph if needed

### Service Discovery Pattern

```python
from aignostics.utils import locate_implementations, BaseService

# Find all service implementations
services = locate_implementations(BaseService)

# Each service provides standard interface
for service_class in services:
    service = service_class()
    health = service.health()
    info = service.info(mask_secrets=True)
    print(f"{service_class.__name__}: {health.status}")
```

### Authentication Pattern

```python
from aignostics import platform

# Create authenticated client
client = platform.Client()

# Token automatically cached in ~/.aignostics/token.json
# Format: "token:expiry_timestamp"
# Refresh buffer: 5 minutes before expiry

# List resources
apps = client.applications.list()
runs = client.runs.list()

# Force token refresh
from aignostics.platform._authentication import remove_cached_token
remove_cached_token()
```

### Error Handling Pattern

```python
from aignostics.system._exceptions import AignosticsError

class ModuleError(AignosticsError):
    """Module-specific error."""
    pass

def risky_operation():
    try:
        # Perform operation
        result = external_api_call()
    except ExternalAPIError as e:
        # Wrap external errors
        raise ModuleError(f"Operation failed: {e}") from e
    except Exception as e:
        # Log unexpected errors
        logger.exception("Unexpected error in risky_operation")
        raise
    
    return result
```

### Logging Pattern

```python
from aignostics.utils import get_logger

logger = get_logger(__name__)

def operation():
    logger.info("Starting operation", extra={
        "correlation_id": "abc123",
        "user_id": "user456"
    })
    
    try:
        result = perform_work()
        logger.debug("Operation successful", extra={
            "result_size": len(result)
        })
        return result
    except Exception as e:
        logger.error("Operation failed", extra={
            "error": str(e),
            "stack_trace": traceback.format_exc()
        }, exc_info=True)
        raise
```

## Testing Strategy

### Test Organization

```
tests/
├── conftest.py                    # Global fixtures
├── aignostics/
│   ├── module/
│   │   ├── service_test.py       # Service layer tests
│   │   ├── cli_test.py           # CLI command tests
│   │   └── gui_test.py           # GUI component tests
│   └── fixtures/                 # Test data
└── resources/                     # Test resources
```

### Test Markers

```python
@pytest.mark.docker          # Requires Docker
@pytest.mark.scheduled       # Periodic validation
@pytest.mark.long_running    # Extended execution (>5 minutes)
@pytest.mark.sequential      # Cannot run in parallel
@pytest.mark.skip_with_act   # Skip in GitHub Act
```

### Writing Tests

**Service Tests:**

```python
# tests/aignostics/module/service_test.py
import pytest
from aignostics.module._service import Service

class TestService:
    """Test service layer."""
    
    def test_health(self):
        """Verify health check."""
        service = Service()
        health = service.health()
        assert health.status == "UP"
    
    def test_operation(self):
        """Test business logic."""
        service = Service()
        result = service.perform_operation("input")
        assert result == "expected"
    
    def test_error_handling(self):
        """Verify error handling."""
        service = Service()
        with pytest.raises(ValueError):
            service.perform_operation(None)
```

**CLI Tests:**

```python
# tests/aignostics/module/cli_test.py
from typer.testing import CliRunner
from aignostics.module._cli import cli

runner = CliRunner()

def test_cli_command():
    """Test CLI command execution."""
    result = runner.invoke(cli, ["operation", "--param", "value"])
    assert result.exit_code == 0
    assert "expected output" in result.stdout
```

**GUI Tests (NiceGUI):**

```python
# tests/aignostics/module/gui_test.py
from nicegui.testing import User
from aignostics.module._gui import create_page

def test_gui_interaction(user: User):
    """Test GUI component."""
    create_page()
    
    # Interact with components
    user.find("Parameter").type("test input")
    user.find("Execute").click()
    
    # Verify results
    assert user.find("Result").text == "expected"
```

### Coverage Requirements

- **Minimum**: 85% overall coverage
- **Critical modules**: 95% coverage
  - `platform` (authentication)
  - `utils` (infrastructure)
  - `application` (core workflows)

```bash
# Generate coverage report
make test                              # Run with coverage
open reports/coverage_html/index.html  # View HTML report

# Check specific module
pytest tests/aignostics/module/ --cov=aignostics.module --cov-report=term
```

### Mock Patterns

**API Client Mocking:**

```python
from unittest.mock import Mock, patch

@pytest.fixture
def mock_api():
    api = Mock(spec=PublicApi)
    api.list_applications.return_value = [...]
    return api

def test_with_mock_api(mock_api):
    with patch("aignostics.platform.Client._api", mock_api):
        # Test with mocked API
        pass
```

**File System Mocking:**

```python
def test_file_operation(tmp_path):
    """Use pytest's tmp_path fixture."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    
    # Test with temporary file
    result = process_file(test_file)
    assert result == expected
```

**Network Response Mocking:**

```python
import responses

@responses.activate
def test_api_call():
    responses.add(
        responses.GET,
        "https://api.aignostics.com/v1/endpoint",
        json={"data": "value"},
        status=200
    )
    
    # Test with mocked network response
    result = make_api_call()
    assert result["data"] == "value"
```

## Common Tasks

### Task 1: Add New CLI Command to Existing Module

1. **Open module's `_cli.py`:**
   ```python
   # src/aignostics/module/_cli.py
   
   @cli.command("newcmd")
   def new_command(
       param: str = typer.Option(..., help="Parameter description"),
       flag: bool = typer.Option(False, help="Flag description")
   ):
       """Command description shown in help."""
       service = Service()
       result = service.new_operation(param, flag)
       typer.echo(result)
   ```

2. **Add service method:**
   ```python
   # src/aignostics/module/_service.py
   
   def new_operation(self, param: str, flag: bool) -> str:
       """New operation implementation."""
       # Business logic here
       return result
   ```

3. **Add tests:**
   ```python
   # tests/aignostics/module/cli_test.py
   
   def test_new_command():
       result = runner.invoke(cli, ["newcmd", "--param", "value"])
       assert result.exit_code == 0
   ```

4. **Update CLI reference:**
   ```bash
   make docs  # Regenerates CLI_REFERENCE.md
   ```

### Task 2: Add New Dependency

1. **Add to pyproject.toml:**
   ```bash
   uv add package-name
   # Or for dev dependency:
   uv add --dev package-name
   # Or for optional dependency:
   uv add --optional feature-name package-name
   ```

2. **Update lock file:**
   ```bash
   uv sync
   ```

3. **Test:**
   ```bash
   make test
   ```

4. **Document optional dependencies:**
   Update README.md with installation instructions

### Task 3: Fix Failing Test

1. **Run specific test:**
   ```bash
   pytest tests/path/to/test.py::test_name -vvv
   ```

2. **Debug with breakpoint:**
   ```python
   def test_something():
       result = function_under_test()
       import pdb; pdb.set_trace()  # Breakpoint
       assert result == expected
   ```

3. **Check coverage:**
   ```bash
   pytest tests/path/to/test.py --cov=aignostics.module --cov-report=term-missing
   ```

4. **Verify fix:**
   ```bash
   make test  # Run full suite
   ```

### Task 4: Update Documentation

1. **For README changes:**
   ```bash
   # Edit docs/partials/README_*.md
   make docs  # Compiles README.md from partials
   ```

2. **For API documentation:**
   ```python
   # Update docstrings in source code
   def function(param: str) -> int:
       """Function description.
       
       Args:
           param: Parameter description
           
       Returns:
           Return value description
           
       Raises:
           ValueError: Error condition
       """
   ```

3. **For CLI documentation:**
   ```bash
   make docs  # Auto-generates CLI_REFERENCE.md
   ```

4. **For Sphinx documentation:**
   ```bash
   # Edit docs/source/*.rst
   make docs       # Build HTML
   make docs pdf   # Build PDF
   ```

### Task 5: Debug Authentication Issues

1. **Check token cache:**
   ```bash
   cat ~/.aignostics/token.json
   # Format: "token:timestamp"
   ```

2. **Force token refresh:**
   ```python
   from aignostics.platform._authentication import remove_cached_token
   remove_cached_token()
   ```

3. **Test authentication:**
   ```bash
   uv run aignostics user login
   uv run aignostics user whoami
   ```

4. **Check environment:**
   ```bash
   # Verify .env file exists
   cat .env
   
   # Check required variables
   echo $AIGNOSTICS_CLIENT_ID
   echo $AIGNOSTICS_CLIENT_SECRET
   ```

### Task 6: Run Tests in Docker

1. **Start test containers:**
   ```bash
   pytest -m docker
   ```

2. **Manual Docker testing:**
   ```bash
   docker compose up --build -d
   docker compose logs -f
   docker compose down
   ```

3. **Cleanup Docker resources:**
   ```bash
   docker compose ls --format json | \
     jq -r '.[].Name' | \
     grep ^pytest | \
     xargs -I {} docker compose -p {} down
   ```

## Troubleshooting

### Common Issues

#### Issue: Import Errors for Optional Dependencies

**Symptom:**
```python
ModuleNotFoundError: No module named 'ijson'
```

**Solution:**
```bash
# Install optional dependencies
uv sync --extra qupath    # For QuPath
uv sync --extra gui       # For GUI
uv sync --extra marimo    # For notebooks
uv sync --all-extras      # For all optional features
```

#### Issue: Token Expiry

**Symptom:**
```
AuthenticationError: Token expired
```

**Solution:**
```python
from aignostics.platform._authentication import remove_cached_token
remove_cached_token()
# Then re-authenticate
```

#### Issue: Test Coverage Below Threshold

**Symptom:**
```
FAIL Required test coverage of 85% not reached. Total coverage: 82.5%
```

**Solution:**
```bash
# Find uncovered lines
pytest --cov=aignostics --cov-report=term-missing

# Focus on specific module
pytest tests/aignostics/module/ --cov=aignostics.module --cov-report=html
open reports/coverage_html/index.html
```

#### Issue: Type Checking Errors

**Symptom:**
```
error: Incompatible return value type (got "str", expected "int")
```

**Solution:**
1. Add explicit type hints
2. Use `from __future__ import annotations` for forward references
3. Check MyPy configuration in `pyproject.toml`

```python
from __future__ import annotations
from typing import Optional

def function(param: str) -> Optional[int]:
    """Properly typed function."""
    if not param:
        return None
    return int(param)
```

#### Issue: Pre-commit Hook Failures

**Symptom:**
```
ruff....................................................................Failed
```

**Solution:**
```bash
# Run manually to see details
make pre_commit_run_all

# Fix specific issues
uv run ruff check --fix
uv run ruff format

# Update hooks
uv run pre-commit autoupdate
```

#### Issue: Memory Issues with Large WSI Files

**Symptom:**
```
MemoryError: Unable to allocate array
```

**Solution:**
- Process in tiles, not full image
- Use streaming for file operations
- Implement chunked transfers

```python
# Good: Tile-based processing
for tile in wsi.tiles(size=1024):
    process_tile(tile)

# Bad: Loading full image
full_image = wsi.read()  # Don't do this
```

#### Issue: Windows Path Length Limitations

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory
```

**Solution:**
- Use relative paths when possible
- Enable long path support on Windows
- Keep directory nesting shallow

### Getting Help

1. **Check existing documentation:**
   - [CLAUDE.md](CLAUDE.md) - Architecture overview
   - [CODE_STYLE.md](CODE_STYLE.md) - Style guide
   - [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide
   - Module-specific CLAUDE.md files

2. **Search issues:**
   - [GitHub Issues](https://github.com/aignostics/python-sdk/issues)
   - Look for similar problems

3. **Check CI/CD logs:**
   - GitHub Actions workflows
   - SonarCloud reports
   - CodeQL analysis

4. **Debug mode:**
   ```bash
   # Enable verbose logging
   export AIGNOSTICS_LOG_LEVEL=DEBUG
   
   # Run with maximum verbosity
   pytest -vvv --tb=long
   ```

## AI-Specific Guidance

### For GitHub Copilot

- **Context files**: `.github/copilot-instructions.md`, `CODE_STYLE.md`, this file
- **Inline suggestions**: Follow patterns from surrounding code
- **Code completion**: Use type hints to improve suggestions
- **Test generation**: Use `@pytest` decorators and fixtures from `conftest.py`

### For Claude Code

- **Module documentation**: Read `CLAUDE.md` files in each module
- **Architecture awareness**: Understand modulith pattern before changes
- **Dependency injection**: Use `locate_implementations()` for service discovery
- **Testing patterns**: Follow examples in `tests/CLAUDE.md`

### For ChatGPT and Other LLMs

- **Context window**: Start with this file, then dive into specific modules
- **Code style**: Always reference `CODE_STYLE.md` before generating code
- **Testing**: Reference `tests/CLAUDE.md` for comprehensive testing patterns
- **Architecture**: Use dependency graph in `src/aignostics/CLAUDE.md`

### Best Practices for AI Agents

1. **Read before writing**: Always check existing patterns first
2. **Type safety**: Add type hints to all generated code
3. **Test coverage**: Generate tests alongside implementation
4. **Documentation**: Update docstrings and CLAUDE.md files
5. **Error handling**: Use explicit exception handling
6. **Logging**: Add appropriate log statements
7. **Security**: Never commit secrets, validate inputs
8. **Performance**: Consider memory and CPU implications
9. **Compatibility**: Support Python 3.11, 3.12, 3.13
10. **Code review**: Self-review against style guide

### Anti-Patterns to Avoid

1. **Circular dependencies**: Check module dependency graph
2. **Global state**: Use dependency injection instead
3. **Hard-coded secrets**: Use environment variables
4. **Missing type hints**: MyPy strict mode will fail
5. **No tests**: Coverage below 85% fails CI
6. **Long functions**: Break into smaller methods
7. **Generic errors**: Use specific exception types
8. **Blocking I/O**: Use async when appropriate
9. **Large files in memory**: Use streaming
10. **Platform-specific code**: Check cross-platform compatibility

### Code Review Checklist for AI Agents

Before submitting changes, verify:

- [ ] Code follows patterns in `CODE_STYLE.md`
- [ ] Type hints on all public APIs
- [ ] Google-style docstrings on public methods
- [ ] Tests written (unit + integration if applicable)
- [ ] Test coverage ≥ 85%
- [ ] All tests pass (`make test`)
- [ ] Code formatted (`make lint`)
- [ ] Type checking passes (MyPy strict)
- [ ] No secrets in code
- [ ] Documentation updated (README.md, CLAUDE.md)
- [ ] Conventional commit message
- [ ] Module dependency graph still valid
- [ ] No new circular dependencies
- [ ] Error handling implemented
- [ ] Logging added where appropriate
- [ ] Performance considerations addressed
- [ ] Cross-platform compatibility checked
- [ ] Optional dependencies documented
- [ ] CI/CD will pass (simulate with `make all`)

## Summary

This document provides comprehensive guidance for AI coding agents working with the Aignostics Python SDK. Key takeaways:

1. **Architecture**: Modulith with strict layer separation
2. **Standards**: Strict adherence to `CODE_STYLE.md` required
3. **Testing**: 85% minimum coverage, comprehensive test suite
4. **Tools**: Use `uv` for packages, `make` for builds
5. **Documentation**: Keep CLAUDE.md files updated
6. **Dependencies**: Follow dependency graph, avoid circular refs
7. **Patterns**: Service layer, dependency injection, explicit errors

For detailed module information, consult the module-specific CLAUDE.md files:
- [src/aignostics/CLAUDE.md](src/aignostics/CLAUDE.md) - Module overview
- [src/aignostics/platform/CLAUDE.md](src/aignostics/platform/CLAUDE.md) - Authentication
- [src/aignostics/application/CLAUDE.md](src/aignostics/application/CLAUDE.md) - Application orchestration
- [src/aignostics/wsi/CLAUDE.md](src/aignostics/wsi/CLAUDE.md) - Image processing
- [tests/CLAUDE.md](tests/CLAUDE.md) - Testing patterns

---

*This guidance is regularly updated to reflect evolving best practices. Last updated: 2025*
