# AGENTS.md - AI Agent Guidance

This document provides comprehensive guidance for AI coding agents (GitHub Copilot, Claude Code, Cursor, etc.) working with the Aignostics Python SDK repository.

> 💡 **Quick Start for Agents**: This repository uses **uv** for package management, **nox** for task automation, **pytest** for testing, and follows a **modulith architecture** with service discovery. Always run `uv run aignostics --help` to explore CLI functionality.

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Architecture & Design Patterns](#architecture--design-patterns)
4. [Common Agent Tasks](#common-agent-tasks)
5. [Testing Guidelines](#testing-guidelines)
6. [Code Standards & Style](#code-standards--style)
7. [CI/CD & Workflows](#cicd--workflows)
8. [Documentation Standards](#documentation-standards)
9. [Troubleshooting](#troubleshooting)

---

## Repository Overview

### Project Structure

```
aignostics-python-sdk/
├── src/aignostics/          # Source code
│   ├── platform/            # Authentication & API client
│   ├── application/         # Application run orchestration
│   ├── wsi/                 # Whole slide image processing
│   ├── dataset/             # Dataset downloads (IDC)
│   ├── bucket/              # Cloud storage operations
│   ├── qupath/              # QuPath integration
│   ├── notebook/            # Marimo notebook server
│   ├── gui/                 # Desktop launchpad (NiceGUI)
│   ├── system/              # System diagnostics
│   ├── utils/               # Core infrastructure (DI, logging, settings)
│   ├── cli.py               # CLI entrypoint (auto-registration)
│   └── constants.py         # Package constants
├── tests/                   # Test suite (mirrors src structure)
│   ├── aignostics/          # Module-specific tests
│   ├── conftest.py          # Global pytest fixtures
│   └── fixtures/            # Test data
├── docs/                    # Sphinx documentation
│   ├── source/              # reStructuredText files
│   └── partials/            # Markdown partials for README
├── .github/                 # GitHub workflows & config
│   ├── workflows/           # CI/CD workflows
│   └── copilot-instructions.md
├── Makefile                 # Primary build entrypoint
├── noxfile.py               # Task automation (test, lint, docs, etc.)
├── pyproject.toml           # Project metadata & dependencies
├── CODE_STYLE.md            # Coding standards (MANDATORY)
├── CONTRIBUTING.md          # Contribution guidelines
├── CLAUDE.md                # Claude-specific guidance
└── AGENTS.md                # This file
```

### Key Technologies

- **Language**: Python 3.11+ (currently 3.13)
- **Package Manager**: `uv` (not pip/poetry)
- **Task Runner**: `nox` (not make alone, though Makefile wraps nox)
- **Testing**: `pytest` with 85% minimum coverage
- **Linting**: `ruff` (formatting + linting)
- **Type Checking**: `mypy` (strict mode)
- **CLI Framework**: `typer`
- **GUI Framework**: `nicegui`
- **Documentation**: `sphinx` (HTML + PDF)

---

## Development Environment Setup

### Prerequisites

1. **Python 3.13** (specified in `.python-version`)
2. **uv package manager** (install: `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)
3. **Git** with signed commits enabled

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/aignostics/python-sdk.git
cd python-sdk

# Install development dependencies and pre-commit hooks
make install
# Or manually:
# sh install.sh
# uv run pre-commit install

# Create .env file from example
cp .env.example .env
# Edit .env with your configuration

# Verify setup
uv run aignostics --help
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
uv run pytest tests/aignostics/utils/health_test.py -v

# Run tests with specific marker
make test_sequential        # Tests marked 'sequential'
make test_long_running      # Tests marked 'long_running'
make test_scheduled         # Tests marked 'scheduled'

# Run tests for specific Python version
make test 3.13

# Run single test by name
uv run pytest -k test_health_default_status -v
```

### Running the CLI

```bash
# Basic CLI usage
uv run aignostics --help
uv run aignostics system health
uv run aignostics user login

# With all extras installed
uv run --all-extras aignostics launchpad

# With specific extras
uvx --with "aignostics[qupath,marimo]" aignostics launchpad
```

### Building & Linting

```bash
# Full build pipeline (lint, test, docs, audit)
make all

# Individual tasks
make lint       # Ruff + MyPy
make docs       # Build Sphinx documentation
make audit      # Security & license checks
make dist       # Build wheel

# Quick format & lint
uv run ruff format .
uv run ruff check .
uv run mypy src/
```

---

## Architecture & Design Patterns

### Modulith Architecture

This SDK uses a **modulith architecture** - a single deployable unit with well-defined module boundaries:

- **High cohesion within modules** - each module is self-contained
- **Loose coupling between modules** - clear dependency hierarchy
- **No circular dependencies** - enforced by design

### Module Structure Pattern

Every module follows a consistent three-layer architecture:

```python
module/
├── _service.py      # Business logic (core operations)
├── _cli.py          # CLI commands (Typer)
├── _gui.py          # GUI interface (NiceGUI)
├── _settings.py     # Configuration (Pydantic)
├── _utils.py        # Module-specific utilities (optional)
└── CLAUDE.md        # Module documentation
```

**Dependency Flow**: CLI/GUI → Service → Utils/Platform

### Service Discovery Pattern

All services inherit from `BaseService` and are discovered at runtime:

```python
from aignostics.utils import BaseService, Health, locate_subclasses

class MyService(BaseService):
    """Module service implementation."""

    def health(self) -> Health:
        """Health check implementation."""
        return Health(status=Health.Code.UP)

    def info(self, mask_secrets: bool = True) -> dict:
        """Service information."""
        return {"version": "1.0.0"}

# Automatic discovery
services = locate_subclasses(BaseService)
```

### Key Architectural Principles

1. **No decorators for service registration** - uses runtime discovery
2. **Dependency Injection** via `_di.py` module
3. **Settings via Pydantic** with environment variable support
4. **Structured logging** with correlation IDs
5. **Health checks** for all services
6. **Observability** via Logfire (optional) and Sentry (optional)

---

## Common Agent Tasks

### Task 1: Adding a New Module

```bash
# 1. Create module directory
mkdir -p src/aignostics/mymodule
cd src/aignostics/mymodule

# 2. Create required files
touch __init__.py _service.py _cli.py _gui.py _settings.py CLAUDE.md

# 3. Implement service (inherits from BaseService)
# See src/aignostics/utils/_service.py for interface

# 4. Add CLI commands (using Typer)
# See src/aignostics/system/_cli.py for examples

# 5. Add GUI interface (using NiceGUI)
# See src/aignostics/system/_gui.py for examples

# 6. Create tests
mkdir -p tests/aignostics/mymodule
touch tests/aignostics/mymodule/__init__.py
touch tests/aignostics/mymodule/service_test.py
touch tests/aignostics/mymodule/cli_test.py

# 7. Update documentation
# - Add entry to src/aignostics/CLAUDE.md
# - Write comprehensive module CLAUDE.md
# - Update README if user-facing

# 8. Test and lint
make test
make lint
```

### Task 2: Fixing a Bug

```bash
# 1. Understand the issue
uv run pytest tests/path/to/failing_test.py -v

# 2. Create a minimal reproduction test if needed
# Add test to appropriate test file

# 3. Make minimal code changes
# Follow CODE_STYLE.md guidelines

# 4. Verify fix
uv run pytest tests/path/to/test.py -v
make lint

# 5. Check coverage
uv run pytest --cov=src/aignostics --cov-report=term-missing

# 6. Update documentation if needed
```

### Task 3: Adding a New CLI Command

```python
# In module/_cli.py

import typer
from aignostics.mymodule._service import Service

cli = typer.Typer(name="mymodule", help="Module description")

@cli.command("mycommand")
def my_command(
    arg: str = typer.Argument(..., help="Argument description"),
    option: bool = typer.Option(False, "--flag", help="Option description"),
) -> None:
    """Command description (shows in help)."""
    service = Service()
    result = service.do_something(arg, option)
    typer.echo(f"Result: {result}")
```

Commands are **auto-registered** via service discovery in `src/aignostics/cli.py`.

### Task 4: Adding Tests

```python
# tests/aignostics/mymodule/service_test.py

import pytest
from aignostics.mymodule._service import Service

@pytest.fixture
def service():
    """Fixture providing service instance."""
    return Service()

def test_basic_functionality(service):
    """Test basic service operation."""
    result = service.do_something("input")
    assert result == "expected"

def test_error_handling(service):
    """Test error cases."""
    with pytest.raises(ValueError, match="Invalid input"):
        service.do_something(None)

@pytest.mark.long_running
def test_slow_operation(service):
    """Test that takes >2 minutes."""
    result = service.slow_operation()
    assert result is not None
```

### Task 5: Updating Documentation

```bash
# 1. Update module CLAUDE.md
# - Keep consistent structure with other modules
# - Include usage examples, architecture, critical details

# 2. Update README partials
# docs/partials/README_*.md files are concatenated

# 3. Build and verify
make docs
# Check docs/build/html/index.html

# 4. Generate CLI reference
uv run nox -s docs
# Updates CLI_REFERENCE.md automatically
```

---

## Testing Guidelines

### Test Organization

```
tests/
├── conftest.py                    # Global fixtures
├── aignostics/
│   ├── module/
│   │   ├── service_test.py       # Service layer tests
│   │   ├── cli_test.py           # CLI command tests
│   │   ├── gui_test.py           # GUI component tests
│   │   └── settings_test.py      # Configuration tests
│   └── docker_test.py            # Docker integration tests
└── fixtures/                      # Test data
```

### Test Markers

- `@pytest.mark.sequential` - Tests that must run sequentially
- `@pytest.mark.long_running` - Tests taking >2 minutes
- `@pytest.mark.scheduled` - Scheduled periodic tests
- `@pytest.mark.docker` - Docker-based integration tests
- `@pytest.mark.skip_with_act` - Skip when running with act locally

### Coverage Requirements

- **Minimum**: 85% overall coverage (enforced in CI)
- **Target**: 100% coverage on new code
- Run: `uv run pytest --cov=src/aignostics --cov-report=term-missing`

### Mock & Fixture Patterns

```python
# Common fixture patterns

@pytest.fixture
def mock_settings():
    """Mock settings to prevent real API calls."""
    with patch("aignostics.module._service.settings") as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture(autouse=True)
def prevent_browser_open():
    """Prevent browser opening in tests."""
    with patch("webbrowser.open", return_value=False):
        yield

@pytest.fixture
def temp_file(tmp_path):
    """Provide temporary file for testing."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")
    return file_path
```

---

## Code Standards & Style

### Mandatory Requirements

**READ AND FOLLOW**: [CODE_STYLE.md](CODE_STYLE.md) defines **strict requirements** for all code.

### Quick Reference

**Naming Conventions**:
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_underscore_prefix`
- Booleans: `is_`, `has_`, `should_` prefix

**Type Hints**:
- Required for all public APIs
- Use `from __future__ import annotations` for forward references
- MyPy strict mode enforced

**Docstrings**:
- Google style with typed Args and Returns
- Required for all public classes/functions
- Example:

```python
def process_file(path: str, validate: bool = True) -> dict:
    """Process a file and return metadata.

    Args:
        path: Absolute path to the file
        validate: Whether to validate file format

    Returns:
        Dictionary containing file metadata

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file format is invalid
    """
    ...
```

**Imports**:
- Standard library first, then third-party, then local
- Use absolute imports: `from aignostics.module import Class`
- Avoid wildcard imports

**Error Handling**:
- Use specific exceptions, not generic `Exception`
- Include context in error messages
- Log errors with appropriate level

---

## CI/CD & Workflows

### Workflow Files

Located in `.github/workflows/`:
- `ci-cd.yml` - Main CI/CD pipeline (triggers other workflows)
- `_test.yml` - Test execution (matrix across Python versions)
- `_lint.yml` - Linting and type checking
- `_audit.yml` - Security and license auditing
- `_docker-publish.yml` - Docker image builds
- `_package-publish.yml` - PyPI publishing
- `_scheduled-test.yml` - Nightly test runs
- `_scheduled-audit.yml` - Weekly security scans

### Workflow Triggers

- **Push to main**: Full CI/CD pipeline
- **Pull requests**: Tests, linting, auditing
- **Schedule**: Nightly tests, weekly security scans
- **Manual**: Workflow dispatch available

### Skip CI

Include in commit message to skip workflows:
- `skip:ci` - Skip all workflows
- `skip:test:regular` - Skip regular tests
- `skip:test:long-running` - Skip long-running tests
- `skip:test:matrix-runner` - Skip matrix tests

### Local CI Execution

```bash
# Run GitHub Actions locally with act
make act

# Requires Docker and act installed
# See: https://github.com/nektos/act
```

---

## Documentation Standards

### Documentation Files

1. **CODE_STYLE.md** - Coding standards (mandatory for all contributors)
2. **CONTRIBUTING.md** - Setup, build, release guidelines
3. **CLAUDE.md** - Claude-specific guidance with full architecture
4. **AGENTS.md** - This file (comprehensive agent guidance)
5. **README.md** - User-facing documentation (compiled from partials)
6. **Module CLAUDE.md** - Per-module detailed documentation

### CLAUDE.md Structure

Each module should have a CLAUDE.md with:
- Module overview and responsibilities
- User interfaces (CLI, GUI, Service)
- Architecture & design patterns
- Critical implementation details
- Usage patterns and examples
- Testing considerations
- Common pitfalls

### Documentation Commands

```bash
# Build all documentation
make docs

# Build PDF (requires LaTeX)
uv run nox -s docs_pdf

# Generate CLI reference
# Automatically done by docs session
uv run typer aignostics.cli utils docs --output CLI_REFERENCE.md

# View documentation locally
open docs/build/html/index.html
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Symptom**: `ModuleNotFoundError` when running tests/CLI

**Solution**:
```bash
# Ensure environment is synced
uv sync --all-extras

# Check virtual environment is activated
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows
```

#### 2. Test Failures

**Symptom**: Tests pass locally but fail in CI

**Solution**:
- Check for environment variable dependencies
- Verify no hard-coded paths (use `tmp_path` fixture)
- Ensure tests are isolated (no shared state)
- Check test markers are appropriate

#### 3. Pre-commit Hook Failures

**Symptom**: Commit rejected by pre-commit hooks

**Solution**:
```bash
# Run all hooks manually
uv run pre-commit run --all-files

# Skip hooks if needed (use sparingly)
git commit --no-verify
```

#### 4. Type Checking Errors

**Symptom**: MyPy fails in CI but not locally

**Solution**:
```bash
# Run MyPy with same settings as CI
uv run mypy src/

# Check pyproject.toml for MyPy configuration
```

#### 5. Coverage Below Threshold

**Symptom**: Coverage drops below 85%

**Solution**:
- Add tests for uncovered lines
- Check coverage report: `reports/coverage_html/index.html`
- Use `# pragma: no cover` sparingly for defensive code

### Getting Help

1. **Check existing documentation**:
   - [CODE_STYLE.md](CODE_STYLE.md) - Coding standards
   - [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide
   - [CLAUDE.md](CLAUDE.md) - Architecture overview
   - Module CLAUDE.md files - Detailed module docs

2. **Explore examples**:
   - Look at similar existing modules
   - Check test files for usage patterns
   - Review CLI commands in `_cli.py` files

3. **Run tests**:
   - Tests document expected behavior
   - Use `-v` flag for verbose output
   - Use `-k` to run specific tests

4. **Ask for clarification**:
   - Include error messages
   - Show what you've tried
   - Reference specific files/lines

---

## AI Agent Best Practices

### DO

✅ Read [CODE_STYLE.md](CODE_STYLE.md) before generating code
✅ Follow existing module patterns and structure
✅ Write tests for all new functionality
✅ Use type hints for all public APIs
✅ Keep changes minimal and focused
✅ Run linting and tests before committing
✅ Update documentation when adding features
✅ Use existing utilities from `aignostics.utils`
✅ Check module CLAUDE.md for implementation details
✅ Follow the modulith architecture principles

### DON'T

❌ Create circular dependencies between modules
❌ Use decorators for service registration (use BaseService inheritance)
❌ Hard-code paths or credentials
❌ Skip type hints or docstrings
❌ Remove or modify working tests without understanding them
❌ Ignore linting or type checking errors
❌ Create duplicate functionality (check utils first)
❌ Break the three-layer module architecture
❌ Commit without running tests locally
❌ Use `pip` instead of `uv`

---

## Quick Command Reference

```bash
# Setup
make install                          # Install deps + hooks
cp .env.example .env                  # Create environment file

# Development
uv run aignostics --help              # Run CLI
make lint                             # Format + lint + type check
make test                             # Run tests
make all                              # Full build pipeline

# Testing
uv run pytest tests/path/test.py      # Run specific test
uv run pytest -k test_name            # Run by name
uv run pytest --cov=src/aignostics    # With coverage
make test_sequential                  # Sequential tests
make test_long_running                # Long-running tests

# Documentation
make docs                             # Build HTML docs
open docs/build/html/index.html       # View docs

# Build & Release
make dist                             # Build wheel
make bump                             # Patch release
make minor                            # Minor release
make major                            # Major release

# Utilities
make clean                            # Clean build artifacts
make docker_build                     # Build Docker images
make act                              # Run CI locally
```

---

## Related Documentation

- **[CODE_STYLE.md](CODE_STYLE.md)** - Mandatory coding standards
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development workflow
- **[CLAUDE.md](CLAUDE.md)** - Claude-specific comprehensive guide
- **[src/aignostics/CLAUDE.md](src/aignostics/CLAUDE.md)** - Module index
- **[tests/CLAUDE.md](tests/CLAUDE.md)** - Test suite documentation
- **[OPERATIONAL_EXCELLENCE.md](OPERATIONAL_EXCELLENCE.md)** - Quality & security

---

*This document is maintained for AI coding agents. Last updated: 2025.*
