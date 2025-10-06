# AGENTS.md - AI Agent Guide for Aignostics Python SDK

This document provides comprehensive guidance for AI coding agents (like Claude Code, GitHub Copilot, Cursor, etc.) working with the Aignostics Python SDK. It serves as a quick-start guide and central navigation hub for agent-specific workflows.

## 🎯 Quick Start for AI Agents

### First Steps (Always Do This)

1. **Read this file first** - You're doing it right now!
2. **Check [CLAUDE.md](CLAUDE.md)** - Root documentation with architecture overview and development commands
3. **Find the relevant module's CLAUDE.md** - Each module has detailed implementation guidance
4. **Follow [CODE_STYLE.md](CODE_STYLE.md)** - Strict requirements for all contributors (humans and agents)

### Essential Files for Every Task

| File | When to Read | Priority |
|------|-------------|----------|
| [CLAUDE.md](CLAUDE.md) | Every task - architecture, build commands, module index | **Critical** |
| [src/aignostics/CLAUDE.md](src/aignostics/CLAUDE.md) | Module overview and interaction patterns | **High** |
| [CODE_STYLE.md](CODE_STYLE.md) | Before writing any code | **Critical** |
| [tests/CLAUDE.md](tests/CLAUDE.md) | Before writing tests | **High** |
| Module-specific CLAUDE.md | When working on specific module | **Critical** |

## 📚 Documentation Map

### Core Documentation

```text
AGENTS.md (this file) ──► Quick start for AI agents
         │
         ├──► CLAUDE.md ──► Architecture, build system, module index
         │
         ├──► CODE_STYLE.md ──► Coding standards (MUST FOLLOW)
         │
         └──► Module CLAUDE.md files ──► Implementation details
                ├── src/aignostics/CLAUDE.md (Module index)
                ├── src/aignostics/platform/CLAUDE.md
                ├── src/aignostics/application/CLAUDE.md
                ├── src/aignostics/wsi/CLAUDE.md
                ├── src/aignostics/dataset/CLAUDE.md
                ├── src/aignostics/bucket/CLAUDE.md
                ├── src/aignostics/utils/CLAUDE.md
                ├── src/aignostics/gui/CLAUDE.md
                ├── src/aignostics/notebook/CLAUDE.md
                ├── src/aignostics/qupath/CLAUDE.md
                ├── src/aignostics/system/CLAUDE.md
                └── tests/CLAUDE.md
```

### Additional Resources

- [CONTRIBUTING.md](CONTRIBUTING.md) - Setup and contribution workflow
- [README.md](README.md) - User-facing documentation and quick start
- [SECURITY.md](SECURITY.md) - Security policies and vulnerability reporting
- [CLI_REFERENCE.md](CLI_REFERENCE.md) - Complete CLI command reference
- [API_REFERENCE_v1.md](API_REFERENCE_v1.md) - API specification

## 🏗️ Architecture Quick Reference

### Modulith Pattern

The SDK uses a **modulith architecture** - a single deployable unit with well-defined module boundaries.

```text
Foundation Layer:
    utils ──► Dependency injection, logging, settings, health checks

API Layer:
    platform ──► OAuth 2.0 authentication, API client, token management

Domain Modules:
    application ──► ML application orchestration, run management
    wsi ──► Whole slide image processing (OpenSlide, PyDICOM)
    dataset ──► IDC dataset downloads, high-performance transfers
    bucket ──► Cloud storage abstraction (S3/GCS)

Integration Modules:
    qupath ──► Bioimage analysis integration (optional, requires ijson)
    notebook ──► Marimo notebook server (optional, requires marimo)

System Modules:
    system ──► Diagnostics, health aggregation from all modules
    gui ──► Desktop launchpad aggregating all GUIs
```

### Module Pattern (Consistent Across All Modules)

```text
Module/
├── _service.py     # Business logic (inherits from BaseService)
├── _cli.py         # CLI commands (Typer framework)
├── _gui.py         # GUI interface (NiceGUI framework)
├── _settings.py    # Configuration (Pydantic models)
├── _utils.py       # Module-specific utilities
└── CLAUDE.md       # Comprehensive documentation for agents
```

**Key Pattern:**
```text
┌─────────────────┐     ┌─────────────────┐
│  CLI (_cli.py)  │     │  GUI (_gui.py)  │
└────────┬────────┘     └────────┬────────┘
         └──────────┬─────────────┘
                    ↓
         ┌────────────────────┐
         │ Service (_service) │  ◄── Inherits from BaseService
         └────────────────────┘
```

## 🛠️ Common Agent Tasks

### Task 1: Adding a New Feature to an Existing Module

**Steps:**

1. **Read the module's CLAUDE.md** (e.g., `src/aignostics/application/CLAUDE.md`)
2. **Identify the layer** - Service, CLI, or GUI?
3. **Follow the existing patterns** in that module
4. **Update tests** in `tests/aignostics/<module>/`
5. **Run linting and tests**: `make lint && make test`

**Example: Adding a new CLI command**

```python
# In src/aignostics/application/_cli.py
from ._service import Service

@cli.command("new-command")
def new_command_handler(param: str):
    """Description of new command."""
    service = Service()
    result = service.new_operation(param)
    console.print(result)
```

### Task 2: Adding a New Module

**Steps:**

1. **Follow the module pattern** from [CLAUDE.md](CLAUDE.md#adding-new-modules)
2. **Create module directory**: `src/aignostics/new_module/`
3. **Implement core files**:
   - `_service.py` - Inherit from `BaseService`
   - `_cli.py` - CLI commands (optional)
   - `_gui.py` - GUI components (optional)
   - `_settings.py` - Pydantic settings
   - `CLAUDE.md` - Documentation
4. **Add tests**: `tests/aignostics/new_module/`
5. **Update module index**: `src/aignostics/CLAUDE.md`

### Task 3: Fixing a Bug

**Steps:**

1. **Understand the bug** - Read the issue/error message
2. **Find the relevant code** - Use module CLAUDE.md files to navigate
3. **Check for tests** - Look in `tests/aignostics/<module>/`
4. **Write a failing test** that reproduces the bug
5. **Fix the bug** following code style guidelines
6. **Verify the test passes**: `make test`
7. **Run full suite**: `make all`

### Task 4: Improving Documentation

**Steps:**

1. **Identify what's unclear** - What needs better explanation?
2. **Find the right CLAUDE.md** - Module-specific or root
3. **Add concrete examples** - Show actual code from the codebase
4. **Verify accuracy** - Read the actual implementation
5. **Update this AGENTS.md** if workflow guidance needs improvement

### Task 5: Writing Tests

**Guidelines:**

1. **Read [tests/CLAUDE.md](tests/CLAUDE.md)** - Comprehensive test patterns
2. **Follow existing test patterns** in the module
3. **Minimum 85% coverage** - Target 95% for critical modules
4. **Use appropriate markers**:
   - `@pytest.mark.sequential` - Cannot run in parallel
   - `@pytest.mark.long_running` - Extended execution time
   - `@pytest.mark.docker` - Requires Docker
   - `@pytest.mark.scheduled` - Periodic validation

**Test File Pattern:**

```python
# tests/aignostics/module/feature_test.py
import pytest
from aignostics.module import Service

def test_feature_success():
    """Test successful feature execution."""
    service = Service()
    result = service.feature()
    assert result.status == "success"

def test_feature_error_handling():
    """Test feature handles errors correctly."""
    service = Service()
    with pytest.raises(ValueError, match="Invalid input"):
        service.feature(invalid_input)
```

## 🎨 Code Style Quick Reference

### Critical Requirements (from CODE_STYLE.md)

1. **Naming Conventions:**
   - Classes: `PascalCase`
   - Functions/variables: `snake_case`
   - Constants: `UPPER_SNAKE_CASE`
   - Private: `_private_name`

2. **Type Hints:**
   - **MyPy strict mode enforced**
   - All public APIs must have type hints
   - Use `from __future__ import annotations` for forward references

3. **Docstrings:**
   - Google-style docstrings required
   - Document all public APIs
   - Include Args, Returns, Raises sections

4. **Testing:**
   - 85% minimum coverage (85%+ enforced by CI)
   - 95% for critical modules (platform, application, utils)
   - Use pytest fixtures for test setup

5. **Import Organization:**
   - Standard library first
   - Third-party second
   - Local imports last
   - Use relative imports within modules (`from ._service import Service`)

### Formatting Tools

```bash
make lint          # Run ruff formatting + linting + mypy type checking
make test          # Run tests with coverage
make all           # Run full CI pipeline (lint + test + docs + audit)
```

## ⚠️ Common Pitfalls & Solutions

### Pitfall 1: Not Reading Module-Specific CLAUDE.md

**Problem:** Making changes without understanding module patterns

**Solution:** **Always** read `src/aignostics/<module>/CLAUDE.md` before modifying a module. Each module has specific patterns, dependencies, and gotchas documented.

### Pitfall 2: Ignoring Type Hints

**Problem:** MyPy strict mode failures in CI

**Solution:**
- Use type hints on all functions: `def func(x: int) -> str:`
- Import types: `from typing import Any, Optional, Union`
- Use `from __future__ import annotations` at top of file

### Pitfall 3: Breaking Semver in application Module

**Problem:** Version strings not validated correctly

**Solution:** Always use `v` prefix in versions: `app-id:v1.2.3` (NOT `app-id:1.2.3`)
- See `src/aignostics/application/CLAUDE.md` for semver validation details

### Pitfall 4: Memory Issues with WSI Processing

**Problem:** Loading entire slide into memory

**Solution:** Use tile-based processing
- See `src/aignostics/wsi/CLAUDE.md` for tile extraction patterns
- Never load full slide with `read_region()` at level 0

### Pitfall 5: Missing Optional Dependencies

**Problem:** QuPath or Marimo features not working

**Solution:**
- QuPath requires: `pip install ijson`
- Marimo requires: `pip install marimo`
- GUI requires: `pip install "aignostics[gui]"`

### Pitfall 6: Test Coverage Below 85%

**Problem:** CI fails due to coverage check

**Solution:**
- Run `make test` to check coverage
- Add tests for uncovered branches
- Use `pytest --cov-report=html` to see coverage report

### Pitfall 7: Circular Dependencies Between Modules

**Problem:** Import errors due to circular imports

**Solution:**
- Follow the dependency graph in [CLAUDE.md](CLAUDE.md#core-modules--dependencies)
- Never import from "higher" modules (e.g., utils should never import from application)
- Use late imports inside functions if absolutely necessary

## 🔍 Navigation Patterns

### Finding the Right File

**Scenario: "I need to add authentication logic"**
1. Authentication is in `platform` module
2. Read `src/aignostics/platform/CLAUDE.md`
3. Look for `_authentication.py` in that module
4. Check existing tests in `tests/aignostics/platform/authentication_test.py`

**Scenario: "I need to modify how WSI files are processed"**
1. WSI processing is in `wsi` module
2. Read `src/aignostics/wsi/CLAUDE.md`
3. Service logic in `src/aignostics/wsi/_service.py`
4. Format handlers in `_openslide_handler.py` and `_pydicom_handler.py`

**Scenario: "I need to understand how CLI commands work"**
1. Read root [CLAUDE.md](CLAUDE.md#cli-usage-examples)
2. Main CLI entrypoint: `src/aignostics/cli.py`
3. Module CLIs: `src/aignostics/<module>/_cli.py`
4. CLI utilities: `src/aignostics/utils/_cli.py` (prepare_cli function)

### Dependency Discovery

**Finding what a module depends on:**
1. Check module's `CLAUDE.md` under "Module Dependencies"
2. Look at imports in `_service.py`
3. Refer to dependency graph in root [CLAUDE.md](CLAUDE.md#dependency-graph)

**Example: application module dependencies:**
- `platform` - API client
- `bucket` - Cloud storage
- `wsi` - File validation
- `qupath` - Optional integration (requires ijson)
- `utils` - Infrastructure

## 🧪 Testing Strategies for Agents

### Test-Driven Development Flow

1. **Write failing test first:**
   ```bash
   pytest tests/aignostics/module/feature_test.py::test_new_feature -v
   ```

2. **Implement the feature**

3. **Run test until it passes**

4. **Run full module tests:**
   ```bash
   pytest tests/aignostics/module/ -v
   ```

5. **Check coverage:**
   ```bash
   pytest --cov=aignostics.module --cov-report=term-missing
   ```

6. **Run full suite:**
   ```bash
   make test
   ```

### Test Patterns by Module Type

**Service Layer Tests:**
```python
def test_service_operation():
    """Test service operation with mocked dependencies."""
    service = Service()
    result = service.operation()
    assert result.status == expected_status
```

**CLI Tests:**
```python
def test_cli_command(cli_runner):
    """Test CLI command execution."""
    result = cli_runner.invoke(cli, ["command", "--param", "value"])
    assert result.exit_code == 0
    assert "expected output" in result.output
```

**API Integration Tests:**
```python
@pytest.mark.integration
def test_api_integration(mock_api):
    """Test API integration with mocked client."""
    mock_api.get_resource.return_value = mock_data
    client = Client()
    result = client.resource.get()
    assert result == expected_result
```

## 🚀 Build System Quick Reference

### Essential Commands

```bash
# Development setup
make install          # Install dev dependencies + pre-commit hooks

# Testing
make test            # Run full test suite (all Python versions)
make test 3.12       # Run tests on Python 3.12 only
make test_sequential # Run sequential tests (marked with @pytest.mark.sequential)

# Code quality
make lint            # Ruff formatting + linting + MyPy

# Full pipeline
make all             # lint + test + docs + audit (full CI)

# Documentation
make docs            # Build Sphinx HTML documentation

# Security & compliance
make audit           # Security and license compliance checks
```

### Pre-commit Hooks

The SDK uses pre-commit hooks that run automatically on `git commit`:
- Ruff formatting and linting
- MyPy type checking
- detect-secrets scanning
- Trailing whitespace removal

**Bypass hooks (not recommended):**
```bash
git commit --no-verify
```

## 🔐 Security Considerations

### What NOT to Do

1. **Never commit secrets** - Use environment variables
2. **Never disable security checks** without explicit approval
3. **Never use `eval()` or `exec()` on user input
4. **Never store sensitive data in logs** - Use masking

### What TO Do

1. **Use Pydantic SecretStr** for sensitive settings
2. **Validate all inputs** with type hints and Pydantic
3. **Follow OAuth 2.0 patterns** in platform module
4. **Check [SECURITY.md](SECURITY.md)** for vulnerability reporting

## 📊 Module Capabilities Matrix

Quick reference for what each module provides:

| Module | Service | CLI | GUI | Key Features |
|--------|---------|-----|-----|--------------|
| **platform** | ✅ | ✅ | ❌ | OAuth 2.0 auth, API client, token management |
| **application** | ✅ | ✅ | ✅ | ML app orchestration, run lifecycle, semver |
| **wsi** | ✅ | ✅ | ✅ | Multi-format WSI processing, thumbnails, tiles |
| **dataset** | ✅ | ✅ | ✅ | IDC dataset downloads, s5cmd integration |
| **bucket** | ✅ | ✅ | ✅ | Cloud storage (S3/GCS), signed URLs, chunking |
| **utils** | ✅ | ❌ | ❌ | DI container, logging, settings, health checks |
| **gui** | ✅ | ❌ | ✅ | Desktop launchpad aggregating all GUIs |
| **notebook** | ✅ | ❌ | ✅ | Marimo notebook server, process management |
| **qupath** | ✅ | ✅ | ✅ | QuPath integration (requires ijson) |
| **system** | ✅ | ✅ | ✅ | System diagnostics, health aggregation |

## 🎓 Learning Path for New Agents

### Level 1: Understanding the Basics (30 minutes)

1. Read [AGENTS.md](AGENTS.md) (this file) - You're doing it!
2. Skim [CLAUDE.md](CLAUDE.md) - Focus on architecture section
3. Read [CODE_STYLE.md](CODE_STYLE.md) - Critical for all tasks
4. Review [src/aignostics/CLAUDE.md](src/aignostics/CLAUDE.md) - Module overview

### Level 2: Working with Modules (1 hour)

1. Pick a module you'll work with (e.g., application)
2. Read that module's CLAUDE.md in detail
3. Explore the module's code structure:
   - `_service.py` - Core business logic
   - `_cli.py` - CLI commands
   - `_gui.py` - GUI components (if exists)
4. Read corresponding tests in `tests/aignostics/<module>/`

### Level 3: Making Changes (Ongoing)

1. Start with small changes (documentation, simple bug fixes)
2. Always follow: **Read → Test → Implement → Test → Review**
3. Run `make all` before committing
4. Learn from code review feedback

## 🆘 Troubleshooting Guide

### Problem: "make install" fails

**Possible causes:**
- `uv` not installed or wrong version (need >=0.8.9)
- Python version mismatch (need 3.11+)

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Check Python version
python --version  # Should be 3.11, 3.12, or 3.13

# Try again
make install
```

### Problem: "Module not found" errors in tests

**Possible causes:**
- Missing optional dependencies
- Not running in virtual environment

**Solution:**
```bash
# Install all extras
uv sync --all-extras

# Activate environment (if using venv)
source .venv/bin/activate
```

### Problem: MyPy type checking failures

**Possible causes:**
- Missing type hints
- Incorrect type annotations
- Missing `from __future__ import annotations`

**Solution:**
1. Add type hints to all functions
2. Use `Any` for complex types if needed
3. Check module's CLAUDE.md for type patterns
4. Run `mypy src/aignostics/<module>/ --show-error-codes`

### Problem: Test coverage below 85%

**Possible causes:**
- Missing tests for new code
- Uncovered error handling branches
- Uncovered edge cases

**Solution:**
```bash
# Generate HTML coverage report
pytest --cov=aignostics --cov-report=html

# Open reports/coverage_html/index.html in browser
# Identify uncovered lines (shown in red)
# Add tests for those lines
```

### Problem: Pre-commit hooks failing

**Possible causes:**
- Code style violations
- Type checking failures
- Security issues detected

**Solution:**
```bash
# Run pre-commit manually to see errors
make pre_commit_run_all

# Fix issues shown in output
# Common fixes:
# - Ruff: make lint (auto-fixes most issues)
# - MyPy: Add type hints
# - detect-secrets: Remove or baseline secrets
```

## 🔄 Common Workflows

### Workflow 1: Adding a New CLI Command

```bash
# 1. Read module documentation
cat src/aignostics/<module>/CLAUDE.md

# 2. Edit CLI file
# Add new command to src/aignostics/<module>/_cli.py

# 3. Write test
# Add test to tests/aignostics/<module>/cli_test.py

# 4. Run tests
make test

# 5. Test manually
uv run aignostics <module> <new-command> --help

# 6. Lint and full check
make all
```

### Workflow 2: Fixing a Bug

```bash
# 1. Reproduce the bug
# Write a failing test first

# 2. Run the failing test
pytest tests/path/to/test.py::test_name -v

# 3. Fix the code
# Edit the relevant _service.py or other file

# 4. Verify fix
pytest tests/path/to/test.py::test_name -v

# 5. Run full module tests
pytest tests/aignostics/<module>/ -v

# 6. Check coverage
pytest --cov=aignostics.<module> --cov-report=term-missing

# 7. Full pipeline
make all
```

### Workflow 3: Updating Documentation

```bash
# 1. Identify what needs updating
# Check which CLAUDE.md file needs changes

# 2. Edit the documentation
# Add concrete examples from actual code

# 3. Verify accuracy
# Read the implementation to ensure docs are correct

# 4. Build docs to check formatting
make docs

# 5. Review HTML output
# Open docs/build/html/index.html in browser

# 6. Commit changes
git add *.md docs/
git commit -m "docs: update <module> guidance"
```

## 📝 Checklist Before Committing

Use this checklist for every change:

- [ ] Read relevant CLAUDE.md file(s)
- [ ] Followed [CODE_STYLE.md](CODE_STYLE.md) guidelines
- [ ] Added/updated type hints (MyPy strict mode)
- [ ] Added/updated tests (aim for 85%+ coverage)
- [ ] Added/updated docstrings (Google style)
- [ ] Ran `make lint` (passes without errors)
- [ ] Ran `make test` (passes with adequate coverage)
- [ ] Ran `make all` if making significant changes
- [ ] Updated relevant CLAUDE.md if patterns changed
- [ ] No secrets or sensitive data in code
- [ ] Import organization correct (stdlib → third-party → local)

## 🎯 Success Metrics for AI Agents

Good agent work is characterized by:

1. **Reading documentation first** - Before making changes
2. **Following existing patterns** - Consistency with codebase
3. **High test coverage** - 85%+ for all changes
4. **Type safety** - MyPy strict mode passes
5. **Clear commit messages** - Conventional commits format
6. **Documentation updates** - When patterns change
7. **No breaking changes** - Unless explicitly required
8. **Security awareness** - No secrets, proper validation

## 🔗 Quick Links

### Documentation
- [Root CLAUDE.md](CLAUDE.md) - Architecture and build system
- [Module Index](src/aignostics/CLAUDE.md) - All modules overview
- [Test Guide](tests/CLAUDE.md) - Comprehensive test patterns
- [Code Style](CODE_STYLE.md) - Strict requirements
- [Contributing](CONTRIBUTING.md) - Setup workflow

### Development
- [Makefile](Makefile) - All build commands
- [pyproject.toml](pyproject.toml) - Project configuration
- [noxfile.py](noxfile.py) - Test automation

### Module-Specific
- [platform](src/aignostics/platform/CLAUDE.md) - Authentication & API
- [application](src/aignostics/application/CLAUDE.md) - ML orchestration
- [wsi](src/aignostics/wsi/CLAUDE.md) - Image processing
- [dataset](src/aignostics/dataset/CLAUDE.md) - Dataset downloads
- [bucket](src/aignostics/bucket/CLAUDE.md) - Cloud storage
- [utils](src/aignostics/utils/CLAUDE.md) - Infrastructure
- [system](src/aignostics/system/CLAUDE.md) - Diagnostics
- [qupath](src/aignostics/qupath/CLAUDE.md) - QuPath integration
- [notebook](src/aignostics/notebook/CLAUDE.md) - Marimo notebooks
- [gui](src/aignostics/gui/CLAUDE.md) - Desktop interface

---

**Remember:** This SDK is built for medical/computational pathology with high quality and security standards. Always prioritize correctness, type safety, and test coverage. When in doubt, ask or read the relevant CLAUDE.md file!

*Built with love in Berlin 🐻*
