# CLAUDE.md - CI/CD & GitHub Actions Complete Guide

This file provides comprehensive guidance for Claude Code and human engineers working with the CI/CD infrastructure and GitHub Actions workflows in this repository.

## Overview

The Aignostics Python SDK uses a **sophisticated multi-stage CI/CD pipeline** built on GitHub Actions with:

* **Multiple workflow files**, including both entry-point and reusable workflows
* **Reusable workflow architecture** for modularity and maintainability
* **Environment-based testing** (staging/production with scheduled validation)
* **Multi-category test execution** (unit, integration, e2e, long_running, very_long_running, scheduled)
* **Automated PR reviews** with Claude Code
* **Comprehensive quality gates** (lint, audit, test, CodeQL)
* **Native executable builds** for 6 platforms
* **Automated releases** with package publishing
* **External monitoring** via BetterStack heartbeats

## Workflow Architecture

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    ci-cd.yml (Main Orchestrator)                    │
│   Triggered on: push to main/release/v*, PR, release, tag v*.*.*   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────┐  ┌───────┐  ┌────────────────┐  ┌────────┐           │
│  │  Lint  │  │ Audit │  │      Test      │  │ CodeQL │           │
│  │ (5 min)│  │(3 min)│  │ (Multi-stage)  │  │ (10m)  │           │
│  └───┬────┘  └───┬───┘  └───┬────────────┘  └───┬────┘           │
│      │           │          │                    │                 │
│      │           │    ┌─────┴──────┐            │                 │
│      │           │    │ unit (3m)  │            │                 │
│      │           │    │ integ (5m) │            │                 │
│      │           │    │ e2e (7m)   │            │                 │
│      │           │    │ long (opt) │            │                 │
│      │           │    │ vlong(opt) │            │                 │
│      │           │    └────────────┘            │                 │
│      │           │          │                    │                 │
│      └───────────┴──────────┴────────────────────┘                 │
│                      ↓                                              │
│            ┌──────────────────────┐                                │
│            │ Ketryx Report Check  │                                │
│            │ (Medical Compliance) │                                │
│            └──────────┬───────────┘                                │
│                       ↓                                              │
│       ┌───────────────┴─────────────────┐                          │
│       │                                   │                          │
│  ┌────────────┐                     ┌────────────┐                 │
│  │  Package   │                     │   Docker   │                 │
│  │  Publish   │                     │  Publish   │                 │
│  │ (on tag)   │                     │ (on tag)   │                 │
│  └────────────┘                     └────────────┘                 │
└─────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│                    Parallel Entry Points                       │
├───────────────────────────────────────────────────────────────┤
│  prepare-release.yml      → Create release branch             │
│  publish-release.yml      → Tag + changelog → CI/CD publish   │
│  merge-release.yml        → Merge branch into main            │
│  build-native-only.yml    → Native executables (6 platforms)  │
│  claude-code-*.yml        → PR reviews + interactive sessions  │
│  test-scheduled-*.yml     → Staging (6h) + Production (24h)   │
│  audit-scheduled.yml      → Security audit (hourly)            │
│  codeql-scheduled.yml     → CodeQL scan (weekly)               │
└───────────────────────────────────────────────────────────────┘
```

## All Workflows Reference

### Entry Point Workflows (Triggered Directly)

| Workflow | Triggers | Purpose | Calls |
|----------|----------|---------|-------|
| **ci-cd.yml** | push(main, release/v*), PR, release, tag | Main CI/CD pipeline | _lint,_audit, _test,_codeql, _ketryx,_package-publish, _docker-publish |
| **prepare-release.yml** | workflow_dispatch | Create release branch + bump version | — |
| **publish-release.yml** | workflow_dispatch | Generate changelog, tag, push → CI/CD | — |
| **merge-release.yml** | workflow_dispatch | Merge release branch into main | — |
| **build-native-only.yml** | push, PR, release (if msg contains `build:native:only`) | Native executable builds | _build-native-only |
| **claude-code-interactive.yml** | workflow_dispatch (manual) | Manual Claude sessions | _claude-code (interactive) |
| **claude-code-automation-pr-review.yml** | PR opened/sync (excludes bots) | Automated PR reviews | _claude-code (automation) |
| **test-scheduled-staging.yml** | schedule (every 6h) | Continuous staging validation | _scheduled-test (staging) |
| **test-scheduled-production.yml** | schedule (every 24h) | Daily production validation | _scheduled-test (production) |
| **audit-scheduled.yml** | schedule (hourly) | Security & license audit | _scheduled-audit |
| **codeql-scheduled.yml** | schedule (Tue 3:22 AM) | Weekly CodeQL scan | _codeql |

### Reusable Workflows (Called by Others)

| Workflow | Purpose | Duration | Key Outputs |
|----------|---------|----------|-------------|
| **_lint.yml** | Code quality (ruff, pyright, mypy) | ~5 min | Formatted code, type safety |
| **_docs.yml** | Documentation build (Sphinx) | ~3 min | HTML docs, validation |
| **_audit.yml** | Security + license compliance | ~3 min | SBOM (CycloneDX, SPDX), vulnerabilities, licenses |
| **_test.yml** | Multi-stage test execution | ~15 min | Coverage reports, JUnit XML |
| **_codeql.yml** | Security vulnerability scanning | ~10 min | CodeQL SARIF results |
| **_ketryx_report_and_check.yml** | Medical device compliance | ~2 min | Ketryx project report |
| **_package-publish.yml** | PyPI package publishing | ~3 min | Wheel/sdist on PyPI, GitHub release |
| **_docker-publish.yml** | Docker image publishing | ~5 min | Multi-arch Docker images |
| **_build-native-only.yml** | Native executable builds | ~10 min/platform | aignostics.7z per platform |
| **_claude-code.yml** | Claude Code execution | varies | Code changes, analysis |
| **_scheduled-audit.yml** | Scheduled audit runner | ~5 min | Audit reports + BetterStack heartbeat |
| **_scheduled-test.yml** | Scheduled test runner | ~10 min | Test reports + BetterStack heartbeat |

## Test Execution Strategy

### Test Categories

The SDK has **7 test categories** with different execution strategies.

**CRITICAL REQUIREMENT**: Every test **MUST** be marked with at least one of: `unit`, `integration`, or `e2e`. Tests without these markers will **NOT run in CI** because the pipeline explicitly filters by these markers.

```python
# ✅ CORRECT - Has category marker
@pytest.mark.unit
def test_something():
    pass


# ❌ INCORRECT - No category marker, will NOT run in CI
def test_something_else():
    pass


# ✅ CORRECT - Multiple markers including category
@pytest.mark.e2e
@pytest.mark.long_running
def test_complex_workflow():
    pass
```

#### 1. Unit Tests

**Marker**: `unit`

**Characteristics**:

* Fast, isolated tests with no external dependencies
* No API calls, no file I/O (except temp files)
* ~3 minutes total execution time

**Parallelization**: `XDIST_WORKER_FACTOR=0.0` (sequential execution)

* Fast enough that parallelization overhead reduces performance
* Single worker for predictable execution

**CI Behavior**: Always run in all CI contexts

**Run locally**:

```bash
make test_unit
# Or directly:
uv run pytest -m "unit and not long_running and not very_long_running" -v
```

#### 2. Integration Tests

**Marker**: `integration`

**Characteristics**:

* Tests with mocked external services (API responses, S3 calls)
* Some I/O but mostly CPU-bound
* ~5 minutes total execution time

**Parallelization**: `XDIST_WORKER_FACTOR=0.2` (20% of logical CPUs)

* Limited parallelism due to CPU-bound nature
* Example: 8 CPU machine → max(1, int(8 * 0.2)) = 1 worker

**CI Behavior**: Always run in all CI contexts

**Run locally**:

```bash
make test_integration
# Or directly:
uv run pytest -m "integration and not long_running and not very_long_running" -v
```

#### 3. E2E Tests (Regular)

**Marker**: `e2e` (excluding `long_running` and `very_long_running`)

**Characteristics**:

* Real API calls to staging environment
* Network I/O bound
* ~7 minutes total execution time

**Parallelization**: `XDIST_WORKER_FACTOR=1.0` (100% of logical CPUs)

* Full parallelization maximizes throughput for I/O-bound tests
* Example: 8 CPU machine → 8 workers

**CI Behavior**: Always run in all CI contexts

**Requirements**: `.env` file with staging credentials

**Run locally**:

```bash
make test_e2e
# Or directly:
uv run pytest -m "e2e and not long_running and not very_long_running" -v
```

#### 4. Long Running Tests

**Marker**: `long_running`

**Characteristics**:

* E2E tests taking >30 seconds each
* Typically involve large file operations or complex workflows
* Variable duration (5-15 minutes total)

**Parallelization**: `XDIST_WORKER_FACTOR=2.0` (200% of logical CPUs)

* Aggressive parallelization to reduce wall-clock time
* Example: 8 CPU machine → 16 workers

**CI Behavior**:

* **Draft PRs**: Always skipped
* **Non-draft PRs**: Run by default UNLESS:
  * PR has label `skip:test:long_running`, OR
  * Commit message contains `skip:test:long_running`
* **Main branch**: Always run
* **Releases**: Always run

**Skip in PR**:

```bash
# Add label
gh pr edit --add-label "skip:test:long_running"

# Or commit message
git commit -m "fix: something skip:test:long_running"
```

**Run locally**:

```bash
make test_long_running
# Or directly:
uv run pytest -m long_running -v
```

#### 5. Very Long Running Tests

**Marker**: `very_long_running`

**Characteristics**:

* E2E tests taking >5 minutes each
* Extremely resource-intensive operations
* 15+ minutes total execution time

**Parallelization**: `XDIST_WORKER_FACTOR=2.0` (200% of logical CPUs)

**CI Behavior**:

* **Automatically run on every push to `release/v*` branches** (no opt-in needed)
* **Otherwise never run by default** — must be explicitly enabled via:
  * PR label `enable:test:very_long_running`, OR
  * Commit message contains `enable:test:very_long_running`

**Enable in PR**:

```bash
# Add label
gh pr edit --add-label "enable:test:very_long_running"

# Or commit message
git commit -m "test: enable very long tests enable:test:very_long_running"
```

**Run locally**:

```bash
make test_very_long_running
# Or directly:
uv run pytest -m very_long_running -v
```

#### 6. Sequential Tests

**Marker**: `sequential`

**Characteristics**:

* Tests that must run in specific order
* Have interdependencies or shared state
* Cannot be parallelized

**Parallelization**: None (single worker)

**CI Behavior**: Always run in CI (as part of test suite)

**Run locally**:

```bash
make test_sequential
# Or directly:
uv run pytest -m sequential -v
```

#### 7. Scheduled Tests

**Markers**: `scheduled` or `scheduled_only`

**Characteristics**:

* Tests designed for continuous validation against live environments
* May have different behavior in staging vs production
* Validate API contract stability

**CI Behavior**:

* **`scheduled`**: Run in scheduled jobs AND can run in regular CI
* **`scheduled_only`**: ONLY run in scheduled jobs (never in PR CI)

**Scheduling**:

* **Staging**: Every 6 hours (`test-scheduled-staging.yml`)
* **Production**: Every 24 hours (`test-scheduled-production.yml`)

**Run locally**:

```bash
make test_scheduled
# Or directly:
uv run pytest -m "(scheduled or scheduled_only)" -v
```

### Test Execution Flow in CI

**Standard PR Flow** (_test.yml):

```text
1. Unit Tests (3 min)
   ├─ Python 3.11 ─┐
   ├─ Python 3.12 ─┼─ Parallel execution
   ├─ Python 3.13 ─┤
   └─ Python 3.14 ─┘

2. Integration Tests (5 min)
   ├─ Python 3.11 ─┐
   ├─ Python 3.12 ─┼─ Parallel execution
   ├─ Python 3.13 ─┤
   └─ Python 3.14 ─┘

3. E2E Regular (7 min)
   ├─ Python 3.11 ─┐
   ├─ Python 3.12 ─┼─ Parallel execution
   ├─ Python 3.13 ─┤
   └─ Python 3.14 ─┘

4. Long Running (if not skipped)
   └─ Python 3.14 only (single version)

5. Very Long Running (if explicitly enabled)
   └─ Python 3.14 only (single version)
```

**Matrix Testing**:

* Unit, Integration, E2E run on **all four Python versions** (3.11, 3.12, 3.13, 3.14)
* Long running and very long running run on **Python 3.14 only** to save CI time

### Skip Markers System

**PR Labels** (preferred method):

* `skip:ci` - Skip entire CI pipeline
* `build:native:only` - Only build native executables
* `skip:test:long_running` - Skip long-running tests
* `enable:test:very_long_running` - Enable very long running tests
* `skip:test:unit` - Skip unit tests (not recommended)
* `skip:test:integration` - Skip integration tests (not recommended)
* `skip:test:e2e` - Skip e2e tests (not recommended)

**Commit Message Shortcuts**:

* `skip:ci` - Skip entire CI pipeline
* `build:native:only` - Only build native executables
* `skip:test:long_running` - Skip long-running tests
* `enable:test:very_long_running` - Enable very long running tests

**Usage**:

```bash
# Add label to PR
gh pr edit --add-label "skip:test:long_running"

# Or in commit message
git commit -m "fix: issue skip:test:long_running"
```

## Main CI/CD Pipeline (ci-cd.yml)

**Purpose**: Orchestrates the entire CI/CD pipeline for all branches, PRs, and releases.

**Triggers**:

* `push` to `main` branch
* `push` to `release/v*` branches (release branch CI)
* `pull_request` to `main` (opened, synchronize, reopened)
* `release` created
* `tags` matching `v*.*.*`

**Concurrency Control**:

```yaml
group: ${{ github.workflow }}-${{ github.ref_name }}-${{ github.event.pull_request.number || github.sha }}
cancel-in-progress: true
```

Cancels in-progress runs when new commits are pushed to same PR/branch.

**Skip Conditions**:

* Commit message contains `skip:ci`
* Commit message contains `build:native:only`
* PR has label `skip:ci` or `build:native:only`

**Job Dependencies**:

```text
lint ──┐
audit ─┼──→ ketryx_report_and_check ──┬──→ package_publish (tags only)
test ──┤                               └──→ docker_publish (tags only)
codeql─┘
```

**Jobs**:

1. **lint** (~5 min): Code quality checks (ruff, pyright, mypy)
2. **audit** (~3 min): Security audit (pip-audit, pip-licenses, SBOMs)
3. **test** (~15 min): Multi-stage test suite (unit, integration, e2e, long_running, very_long_running)
4. **codeql** (~10 min): CodeQL security analysis
5. **ketryx_report_and_check**: Medical device compliance reporting
6. **package_publish** (tags only): Build and publish to PyPI, create GitHub release, send Slack notification
7. **docker_publish** (tags only): Build and publish Docker images to Docker Hub

## Native Build System

### Purpose

Build standalone native executables for distribution without Python runtime dependency.

### Supported Platforms

| Platform | Runner | Status | Notes |
|----------|--------|--------|-------|
| **Linux x86_64** | ubuntu-latest | ✅ Stable | Primary platform |
| **Linux ARM64** | ubuntu-24.04-arm | ⚠️ Experimental | continue-on-error |
| **macOS ARM (M1+)** | macos-latest | ⚠️ Experimental | Apple Silicon |
| **macOS Intel** | macos-15-intel | ⚠️ Experimental | Intel chips |
| **Windows x86_64** | windows-latest | ⚠️ Experimental | With UPX compression |
| **Windows ARM64** | windows-11-arm | ⚠️ Experimental | ARM-based Windows |

### Build Process

1. **Setup**: Install uv package manager
2. **Windows Only**: Install UPX compression tool via chocolatey
3. **Build**: Run `make dist_native`
   * Uses PyInstaller to create standalone executable
   * Bundles Python runtime and all dependencies
   * Compresses with UPX (Windows only)
4. **Package**: Creates `aignostics.7z` archive
5. **Upload**: Artifacts stored for 1 day with retention

### Triggering Native Builds

**Automatic**: Add commit message or PR label:

```bash
git commit -m "build:native:only: create native builds"
# Or
gh pr edit --add-label "build:native:only"
```

**Effect**: Skips main CI/CD pipeline, only runs native builds.

**Local Build**:

```bash
make dist_native
# Output: dist_native/aignostics.7z
```

## Claude Code Integration

### Overview

Claude Code is integrated into the CI/CD pipeline for:

1. **Automated PR Reviews** - Every PR gets automatic code review
2. **Interactive Sessions** - Manual Claude assistance for development tasks

### Workflow: _claude-code.yml

**Two Execution Modes**:

#### 1. Interactive Mode

* **Use Case**: Manual Claude sessions for development assistance
* **Behavior**: Iterative conversation, Claude can ask questions
* **Git History**: Full (`fetch-depth: 0`)
* **Duration**: Variable (controlled by `max_turns`)

**Trigger**:

```bash
# GitHub Actions UI: Actions → Claude Code Interactive → Run workflow
# Inputs:
#   - prompt: "Your task description"
#   - max_turns: 200 (default)
```

#### 2. Automation Mode

* **Use Case**: Single-shot automated tasks (PR reviews, automated fixes)
* **Behavior**: Non-interactive, runs predefined prompt
* **Git History**: Shallow (`fetch-depth: 1`)
* **Duration**: Typically 5-10 minutes

**Triggered by**: `claude-code-automation-pr-review.yml` on PR events

### Configuration

**Inputs**:

```yaml
mode: 'interactive' | 'automation'               # Required
prompt: 'string'                                 # For automation mode
max_turns: '200'                                 # Default: 200
allowed_tools: 'comma,separated,list'            # Default: Read,Write,Edit,Glob,Grep,Bash(git:*),Bash(uv:*),Bash(make:*)
```

**Environment Setup**:

1. Installs `uv` package manager
2. Installs dev tools (`.github/workflows/_install_dev_tools.bash`)
3. Syncs Python dependencies (`uv sync --all-extras`)
4. Sets up headless display (for GUI tests)

**Note**: Claude Code workflows intentionally do NOT have access to Aignostics platform credentials or GCP credentials to prevent accidental credential leakage.

**Claude Configuration**:

```bash
claude \
  --max-turns 200 \
  --model claude-sonnet-4-5-20250929 \
  --allowed-tools "Read,Write,Edit,Glob,Grep,Bash(git:*),Bash(uv:*),Bash(make:*),Bash(gh:*),..." \
  --system-prompt "Read the CLAUDE.md file and apply guidance therein" \
  --prompt "${{ inputs.prompt }}"
```

**Secrets Required**:

* `ANTHROPIC_API_KEY` - For Claude Code (only secret available to Claude Code workflows)

### Automated PR Review (claude-code-automation-pr-review.yml)

**Purpose**: Automated code review by Claude on every PR.

**Triggers**:

* `pull_request` (opened, synchronize)
* **Excludes**: dependabot, renovate PRs

**Review Prompt**:

```text
Review this PR thoroughly. Check code quality, test coverage, security,
and adherence to CLAUDE.md guidelines.
```

**Features**:

* Posts inline comments on code
* Checks for common issues
* Validates test coverage
* Reviews documentation
* Maximum 100 turns

**Tool Access**:

* `mcp__github_inline_comment__create_inline_comment` - For PR comments
* File operations: `Read`, `Write`, `Edit`, `Glob`, `Grep`
* Git/GitHub: `Bash(git:*)`, `Bash(gh:*)`

### Manual Claude Sessions (claude-code-interactive.yml)

**Purpose**: On-demand Claude assistance for complex development tasks.

**Trigger**: `workflow_dispatch` (manual)

**Inputs**:

* `prompt`: What you want Claude to work on
* `max_turns`: How many iterations (default 200)

**Example Use Cases**:

* "Refactor module X for better testability"
* "Add comprehensive tests for feature Y"
* "Update documentation for API changes"
* "Debug failing tests in TestClass"

**Access**: GitHub Actions UI → Claude Code Interactive → Run workflow

### Best Practices for Claude Code

**DO**:

* ✅ Use `--system-prompt` referencing CLAUDE.md
* ✅ Limit tool access (`--allowed-tools`)
* ✅ Set reasonable `--max-turns`
* ✅ Review Claude's changes before merging
* ✅ Let Claude explore workflows and test strategies

**DON'T**:

* ❌ Grant unrestricted tool access
* ❌ Skip CLAUDE.md system prompt
* ❌ Merge without human review
* ❌ Add platform/GCP credentials to Claude Code workflows (security risk)

## Scheduled Jobs

### Test Validation (Staging & Production)

**Purpose**: Continuous validation of SDK against live environments.

#### test-scheduled-staging.yml

**Schedule**: Every 6 hours

**Environment**: `https://platform-staging.aignostics.com`

**Purpose**:

* Early detection of API regressions
* Validate against latest staging deployment
* Fast feedback loop for breaking changes

#### test-scheduled-production.yml

**Schedule**: Every 24 hours

**Environment**: `https://platform.aignostics.com`

**Purpose**:

* Validate SDK works with production API
* Catch discrepancies between staging and production
* Safety net for production deployments

**Both workflows**:

* Use `_scheduled-test.yml` reusable workflow
* Run `make test_scheduled` (tests marked `scheduled` or `scheduled_only`)
* Send BetterStack heartbeat for monitoring
* Upload test results and coverage reports

### Audit Validation (audit-scheduled.yml)

**Schedule**: Every hour (`0 * * * *`)

**Purpose**: Continuous security and license compliance monitoring

**Checks**:

* `pip-audit`: CVE scanning for known vulnerabilities
* `pip-licenses`: License compliance verification
* Trivy: SBOM vulnerability scanning (CycloneDX + SPDX formats)

**Workflow**: Uses `_scheduled-audit.yml`

**Outputs**:

* SBOM files (JSON, SPDX)
* License reports (CSV, JSON, grouped JSON)
* Vulnerability reports (JSON)
* BetterStack heartbeat

### CodeQL Scanning (codeql-scheduled.yml)

**Schedule**: Weekly on Tuesdays at 3:22 AM

**Purpose**: Comprehensive security analysis with CodeQL

**Workflow**: Uses `_codeql.yml`

**Analysis**: Static analysis for Python security vulnerabilities

## BetterStack Monitoring

### Purpose

External monitoring and alerting for scheduled jobs to detect failures outside GitHub.

### Heartbeat System

**Implemented in**:

* `_scheduled-audit.yml` - Audit job monitoring
* `_scheduled-test.yml` - Test job monitoring (staging & production)

**Functionality**:

1. Job runs (audit or test)
2. Captures exit code (0 = success, non-zero = failure)
3. Constructs JSON payload with metadata
4. Sends POST request to BetterStack heartbeat URL with exit code appended
5. BetterStack tracks heartbeat and alerts on failures or missed beats

**Payload Structure**:

```json
{
  "github": {
    "workflow": "Scheduled Test - Staging",
    "run_url": "https://github.com/org/repo/actions/runs/12345",
    "run_id": "12345",
    "job": "test-scheduled",
    "sha": "abc123...",
    "actor": "github-actions",
    "repository": "org/repo",
    "ref": "refs/heads/main",
    "event_name": "schedule"
  },
  "job": {
    "status": "success"
  },
  "timestamp": "2025-10-19T14:30:00Z"
}
```

**URL Format**: `{HEARTBEAT_URL}/{EXIT_CODE}`

**Required Secrets**:

* `BETTERSTACK_AUDIT_HEARTBEAT_URL` - For audit jobs
* `BETTERSTACK_HEARTBEAT_URL_STAGING` - For staging test jobs
* `BETTERSTACK_HEARTBEAT_URL_PRODUCTION` - For production test jobs

**Behavior**:

* If heartbeat URL is configured: Sends heartbeat regardless of job success/failure
* If heartbeat URL is NOT configured: Logs warning and continues
* Exit code passed to URL allows BetterStack to distinguish success (0) from failures

## Environment Configuration

### Staging Environment

**API Root**: `https://platform-staging.aignostics.com`

**Secrets**:

* `AIGNOSTICS_CLIENT_ID_DEVICE_STAGING`
* `AIGNOSTICS_REFRESH_TOKEN_STAGING`
* `GCP_CREDENTIALS_STAGING`
* `BETTERSTACK_HEARTBEAT_URL_STAGING`

**Use Cases**:

* PR testing (default for all PRs)
* E2E test execution
* Feature validation
* Claude Code development sessions
* Scheduled validation (every 6 hours)

### Production Environment

**API Root**: `https://platform.aignostics.com`

**Secrets**:

* `AIGNOSTICS_CLIENT_ID_DEVICE_PRODUCTION`
* `AIGNOSTICS_REFRESH_TOKEN_PRODUCTION`
* `GCP_CREDENTIALS_PRODUCTION`
* `BETTERSTACK_HEARTBEAT_URL_PRODUCTION`

**Use Cases**:

* Scheduled tests only (every 24 hours)
* Release validation
* Critical bug verification
* **NEVER use in PR CI** (staging only)

## Secrets Management

**GitHub Secrets** (Required):

* `ANTHROPIC_API_KEY` - Claude Code
* `AIGNOSTICS_CLIENT_ID_DEVICE_{STAGING|PRODUCTION}`
* `AIGNOSTICS_REFRESH_TOKEN_{STAGING|PRODUCTION}`
* `GCP_CREDENTIALS_{STAGING|PRODUCTION}` - Base64 encoded JSON
* `BETTERSTACK_AUDIT_HEARTBEAT_URL` - Audit monitoring
* `BETTERSTACK_HEARTBEAT_URL_{STAGING|PRODUCTION}` - Test monitoring
* `CODECOV_TOKEN` - Coverage reporting to Codecov
* `SONAR_TOKEN` - Code quality reporting to SonarCloud
* `UV_PUBLISH_TOKEN` - PyPI publishing token
* `DOCKER_USERNAME`, `DOCKER_PASSWORD` - Docker Hub credentials
* `KETRYX_PROJECT`, `KETRYX_API_KEY` - Medical device compliance
* `SLACK_WEBHOOK_URL_RELEASE_ANNOUNCEMENT` - Release notifications

**Local Secrets** (`.env` file for E2E tests):

```bash
AIGNOSTICS_API_ROOT=https://platform-staging.aignostics.com
AIGNOSTICS_CLIENT_ID_DEVICE=your-staging-client-id
AIGNOSTICS_REFRESH_TOKEN=your-staging-refresh-token
```

**GCP Credentials** (for bucket access):

```bash
# In CI: base64 encoded and stored as secret
echo "$GCP_CREDENTIALS" | base64 -d > credentials.json
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/credentials.json
```

## Debugging CI Failures

### Lint Failures

**Reproduce locally**:

```bash
make lint
```

**Common Issues**:

* Ruff formatting: Run `ruff format .`
* Ruff linting: Check `ruff check .` and fix with `--fix`
* PyRight: Type errors (basic mode, see `pyrightconfig.json`)
* MyPy: Type errors (strict mode)

**Fix**:

```bash
ruff format .
ruff check . --fix
```

### Test Failures

**Reproduce locally**:

```bash
# Unit tests
make test_unit

# Integration tests
make test_integration

# E2E tests (requires .env with credentials)
make test_e2e

# Specific test
uv run pytest tests/path/to/test.py::test_name -vv
```

**Debug**:

```bash
# Verbose output
uv run pytest tests/test_file.py -vv

# Show print statements
uv run pytest tests/test_file.py -s

# Drop into debugger on failure
uv run pytest tests/test_file.py --pdb

# Run single test
uv run pytest tests/test_file.py::test_function -v
```

**Check Coverage**:

```bash
uv run coverage report
uv run coverage html
open htmlcov/index.html
```

**Minimum**: 85% coverage required

### Audit Failures

**Security Vulnerabilities**:

```bash
uv run pip-audit
```

**Fix**: Update vulnerable dependencies in `pyproject.toml`

**License Violations**:

```bash
uv run pip-licenses --allow-only="MIT;Apache-2.0;BSD-3-Clause;..."
```

**Fix**: Replace non-compliant dependencies or get approval for license

### Native Build Failures

**Platform-specific issues**:

* Check runner compatibility
* Verify UPX installation (Windows)
* Check PyInstaller compatibility with dependencies

**Local reproduction**:

```bash
make dist_native
```

**Note**: Experimental platforms (continue-on-error) won't block CI

### Scheduled Job Failures

**BetterStack Alerts**: Check BetterStack dashboard for heartbeat failures

**Investigate**:

1. Go to GitHub Actions → Scheduled workflow
2. Check recent run logs
3. Look for API changes or credential issues

**Common causes**:

* API breaking changes in staging/production
* Expired credentials
* Network issues
* Dependency updates

## Performance & Optimization

### Parallel Testing

**CPU-based distribution**: `-n logical` (uses all logical CPUs)

**Work stealing**: `--dist worksteal` (dynamic load balancing)

**XDIST_WORKER_FACTOR**: Controls parallelism (0.0-2.0)

* 0.0 = Sequential (1 worker)
* 0.2 = 20% of CPUs
* 1.0 = 100% of CPUs
* 2.0 = 200% of CPUs (aggressive for I/O-bound)

**Calculation**: `max(1, int(cpu_count * factor))`

**Example** (8 CPU machine):

* unit: 0.0 → 1 worker (sequential)
* integration: 0.2 → max(1, int(8 * 0.2)) = 1 worker
* e2e: 1.0 → 8 workers
* long_running: 2.0 → 16 workers

### Caching

* **uv dependencies**: Cached via `astral-sh/setup-uv` action
* **Docker layers**: Cached by Docker build action
* **Nox virtualenvs**: Reused when possible (`nox.options.reuse_existing_virtualenvs = True`)

### Typical Run Times

| Job | Duration | Notes |
|-----|----------|-------|
| Lint | ~5 min | Ruff, PyRight, MyPy |
| Audit | ~3 min | pip-audit, licenses, SBOMs |
| Test (per Python version) | ~5 min | Unit + Integration + E2E (no long_running) |
| Test (full matrix) | ~15 min | All 3 Python versions parallel |
| Test (with long_running) | ~25 min | Adds 10 min for long tests |
| CodeQL | ~10 min | Static analysis |
| Full CI pipeline | ~20-30 min | Depends on test configuration |
| Native builds | ~10 min/platform | 6 platforms in parallel |
| Package publish | ~3 min | Build + upload to PyPI |
| Docker publish | ~5 min | Multi-arch build |

## Common Workflows

### Creating a PR

1. Create feature branch
2. Make changes
3. Run `make lint` and `make test` locally
4. Commit with conventional commit message
5. Push to GitHub
6. Create PR → Triggers:
   * Lint checks
   * Audit checks
   * Test suite (unit, integration, e2e)
   * CodeQL scan
   * Claude Code automated review
7. **Important**: Add label `skip:test:long_running` to save CI time (unless you need long tests)
8. Address review feedback
9. Merge when all checks pass

### Releasing a Version

Releases use a four-phase workflow triggered from the developer's machine via `gh workflow run`. This lets Ketryx compliance approvals be collected *before* the tag (and thus before publishing to PyPI).

**Phase 1 — Prepare the release branch** (triggers `prepare-release.yml`):

```bash
make prepare-release 1.2.3   # explicit version
```

Creates `release/vX.Y.Z` from `main`, commits version bump + `uv.lock`, pushes. CI runs on the branch automatically.

**Phase 2 — Collect Ketryx approvals:**

Point the Ketryx release to `release/vX.Y.Z` and collect approvals. Ensure CI is green.

**Phase 3 — Publish** (triggers `publish-release.yml`):

```bash
make publish-release             # auto-detects release/v* branch
make publish-release release/v1.2.3  # explicit branch
```

Generates `CHANGELOG.md`, creates annotated `vX.Y.Z` tag, pushes → CI/CD fires on tag → Ketryx check must pass before PyPI publish.

**Phase 4 — Merge back to main** (triggers `merge-release.yml`):

```bash
make merge-release             # auto-detects release/v* branch
make merge-release release/v1.2.3  # explicit branch
```

Merges `release/vX.Y.Z` into `main` with `--no-ff`, pushes `main`, deletes the release branch.

**Note on branch protection**: `release/v*` branches should be protected so that only the GitHub Actions bot (`aignostics-release-bot[bot]`) can push to them. This enforces the server-side workflow. Configure in GitHub Settings → Branches → Branch protection rules.

### Manual Testing with Claude

1. Go to: Actions → Claude Code Interactive
2. Click "Run workflow"
3. Fill in:
   * **Prompt**: Describe your task
   * **Max turns**: 200 (default)
   * **Environment**: staging (default)
4. Click "Run workflow"
5. Monitor execution in Actions tab
6. Review changes and create PR if needed

### Running Scheduled Tests Manually

```bash
# Staging tests
gh workflow run test-scheduled-staging.yml

# Production tests (use with caution)
gh workflow run test-scheduled-production.yml
```

### Building Native Executables

**Via CI**:

```bash
git commit -m "build:native:only: create native binaries"
git push
```

**Locally**:

```bash
make dist_native
# Output: dist_native/aignostics.7z
```

## Workflow Files Summary

| File | Type | Purpose | Duration |
|------|------|---------|----------|
| `ci-cd.yml` | Entry | Main pipeline orchestration | ~20 min |
| `prepare-release.yml` | Entry | Create release branch + bump version | ~2 min |
| `publish-release.yml` | Entry | Generate changelog, create tag, push | ~2 min |
| `merge-release.yml` | Entry | Merge release branch into main | ~1 min |
| `build-native-only.yml` | Entry | Native build trigger | ~60 min (6 platforms) |
| `claude-code-interactive.yml` | Entry | Manual Claude sessions | varies |
| `claude-code-automation-pr-review.yml` | Entry | Automated PR reviews | ~10 min |
| `test-scheduled-staging.yml` | Entry | Staging validation | ~10 min |
| `test-scheduled-production.yml` | Entry | Production validation | ~10 min |
| `audit-scheduled.yml` | Entry | Security audit | ~5 min |
| `codeql-scheduled.yml` | Entry | CodeQL scan | ~10 min |
| `_lint.yml` | Reusable | Code quality checks | ~5 min |
| `_docs.yml` | Reusable | Documentation build | ~3 min |
| `_audit.yml` | Reusable | Security & license | ~3 min |
| `_test.yml` | Reusable | Test execution | ~15 min |
| `_codeql.yml` | Reusable | Security scanning | ~10 min |
| `_ketryx_report_and_check.yml` | Reusable | Compliance reporting | ~2 min |
| `_package-publish.yml` | Reusable | PyPI publishing | ~3 min |
| `_docker-publish.yml` | Reusable | Docker publishing | ~5 min |
| `_build-native-only.yml` | Reusable | Native builds | ~10 min/platform |
| `_claude-code.yml` | Reusable | Claude Code execution | varies |
| `_scheduled-audit.yml` | Reusable | Scheduled audit runner | ~5 min |
| `_scheduled-test.yml` | Reusable | Scheduled test runner | ~10 min |

---

**Built with operational excellence for medical device software development.**

**Note**: See root `CLAUDE.md` and `Makefile` for development commands. This document focuses on CI/CD workflows and GitHub Actions.
