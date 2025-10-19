# CLAUDE.md - CI/CD & GitHub Actions Guide

This file provides comprehensive guidance for Claude Code and human engineers working with the CI/CD infrastructure and GitHub Actions workflows in this repository.

## Overview

The Aignostics Python SDK uses a **sophisticated multi-stage CI/CD pipeline** built on GitHub Actions with:
- **Reusable workflows** for modularity and maintainability
- **Environment-based testing** (staging/production)
- **Automated PR reviews** with Claude Code
- **Comprehensive quality gates** (lint, audit, test, CodeQL)
- **Automated releases** with package publishing
- **Scheduled testing** for continuous validation

## Workflow Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                       ci-cd.yml (Main Workflow)                │
│                    Triggered on: push, PR, release             │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────┐  ┌───────┐  ┌──────┐  ┌────────┐                 │
│  │  Lint  │  │ Audit │  │ Test │  │ CodeQL │                 │
│  │ (5 min)│  │(3 min)│  │(15m) │  │ (10m)  │                 │
│  └───┬────┘  └───┬───┘  └───┬──┘  └───┬────┘                 │
│      │           │          │         │                        │
│      └───────────┴──────────┴─────────┘                       │
│                      ↓                                          │
│            ┌─────────────────────┐                             │
│            │ Ketryx Report Check │                             │
│            └──────────┬──────────┘                             │
│                       ↓                                          │
│       ┌───────────────┴────────────────┐                       │
│       │                                  │                       │
│  ┌────────────┐                   ┌────────────┐               │
│  │  Package   │                   │   Docker   │               │
│  │  Publish   │                   │  Publish   │               │
│  │ (on tag)   │                   │ (on tag)   │               │
│  └────────────┘                   └────────────┘               │
└────────────────────────────────────────────────────────────────┘
```

## CI/CD Workflows

### 1. **ci-cd.yml** (Main Pipeline)

**Purpose**: Orchestrates the entire CI/CD pipeline for all branches, PRs, and releases.

**Triggers**:
- `push` to `main` branch
- `pull_request` to `main` (opened, synchronize, reopened)
- `release` created
- `tags` matching `v*.*.*`

**Concurrency Control**:
```yaml
group: ${{ github.workflow }}-${{ github.ref_name }}-${{ github.event.pull_request.number || github.sha }}
cancel-in-progress: true
```
Cancels in-progress runs when new commits are pushed to same PR/branch.

**Skip Conditions**:
- Commit message contains `skip:ci`
- Commit message contains `build:native:only`
- Commit starts with `Bump version:`
- PR has label `skip:ci` or `build:native:only`

**Job Dependencies**:
```
lint ──┐
audit ─┼──→ ketryx_report_and_check ──┬──→ package_publish
test ──┤                               └──→ docker_publish
codeql─┘
```

**Jobs**:

1. **lint** (~5 min):
   - Runs `_lint.yml`
   - Checks: ruff format, ruff lint, pyright, mypy

2. **audit** (~3 min):
   - Runs `_audit.yml`
   - Security: pip-audit (vulnerabilities)
   - License compliance: pip-licenses
   - SBOMs: CycloneDX, SPDX (via Trivy)

3. **test** (~15 min):
   - Runs `_test.yml`
   - Environment: staging (configurable)
   - Matrix: Python 3.11, 3.12, 3.13
   - Types: unit, integration, e2e
   - Uploads: coverage to Codecov, metrics to SonarCloud

4. **codeql** (~10 min):
   - Runs `_codeql.yml`
   - Security analysis with CodeQL

5. **ketryx_report_and_check**:
   - Medical device compliance reporting
   - Requires: all previous jobs to pass

6. **package_publish** (on tags only):
   - Builds and publishes to PyPI
   - Creates GitHub release
   - Sends Slack notification

7. **docker_publish** (on tags only):
   - Builds Docker images
   - Publishes to Docker Hub

### 2. **_claude-code.yml** (Reusable Claude Code Workflow)

**Purpose**: Enables Claude Code for PR reviews and automated coding tasks.

**Modes**:

**Interactive Mode**:
- Triggered manually or on PR events
- Claude can ask questions and iterate
- Full repository history available (`fetch-depth: 0`)

**Automation Mode**:
- Runs with predefined prompt
- Single-shot execution
- Shallow clone (`fetch-depth: 1`)

**Configuration**:
```yaml
inputs:
  platform_environment: 'staging' | 'production'  # Default: staging
  mode: 'interactive' | 'automation'               # Required
  prompt: 'string'                                 # For automation mode
  max_turns: '200'                                 # Default
  allowed_tools: 'comma,separated,list'            # Default includes file ops, git, gh
```

**Environment Setup**:
1. Installs `uv` (package manager)
2. Installs dev tools (`.github/workflows/_install_dev_tools.bash`)
3. Syncs Python dependencies (`uv sync --all-extras`)
4. Sets up headless display (for GUI tests)
5. Creates `.env` with Aignostics credentials
6. Configures GCP credentials for bucket access

**Claude Args**:
```bash
--max-turns 200
--model claude-sonnet-4-5-20250929
--allowed-tools "Read,Write,Edit,Glob,Grep,Bash(git:*),Bash(uv:*),Bash(make:*),..."
--system-prompt "Read the CLAUDE.md file and apply guidance therein"
```

**Secrets Required**:
- `ANTHROPIC_API_KEY` - For Claude Code
- `AIGNOSTICS_CLIENT_ID_DEVICE_{STAGING|PRODUCTION}`
- `AIGNOSTICS_REFRESH_TOKEN_{STAGING|PRODUCTION}`
- `GCP_CREDENTIALS_{STAGING|PRODUCTION}`

### 3. **claude-code-automation-pr-review.yml**

**Purpose**: Automated PR reviews by Claude Code on every PR.

**Triggers**:
- `pull_request` (opened, synchronize)
- Excludes: dependabot, renovate

**What It Does**:
- Calls `_claude-code.yml` in **automation mode**
- Prompt: "Review this PR thoroughly. Check code quality, test coverage, security, and adherence to CLAUDE.md guidelines."
- Posts review comments inline
- Maximum 100 turns

**Tool Access**:
- `mcp__github_inline_comment__create_inline_comment` - For PR comments
- File operations: Read, Write, Edit, Glob, Grep
- Git/GitHub: `Bash(git:*)`, `Bash(gh:*)`

### 4. **claude-code-interactive.yml**

**Purpose**: Manual Claude Code sessions for development assistance.

**Triggers**:
- `workflow_dispatch` (manual trigger)

**Inputs**:
- `prompt`: What you want Claude to work on
- `max_turns`: How many iterations (default 200)
- `platform_environment`: staging (default) or production

**Use Cases**:
- "Refactor module X for better testability"
- "Add comprehensive tests for feature Y"
- "Update documentation for API changes"

### 5. **_test.yml** (Test Execution)

**Purpose**: Comprehensive test suite execution with parallel matrix testing.

**Python Versions**:
- 3.11.9, 3.12.12, 3.13.7
- Windows ARM: Excludes 3.12.12 (instability)

**Test Stages** (Sequential):

1. **Unit Tests** (~3 min):
   ```bash
   pytest -m "unit and not long_running and not very_long_running"
   ```
   - XDIST_WORKER_FACTOR=0.0 (no parallelization)
   - Fast, isolated tests

2. **Integration Tests** (~5 min):
   ```bash
   pytest -m "integration and not long_running and not very_long_running"
   ```
   - XDIST_WORKER_FACTOR=0.2
   - Tests with mocked external services

3. **E2E Tests** (~7 min):
   ```bash
   pytest -m "e2e and not long_running and not very_long_running"
   ```
   - XDIST_WORKER_FACTOR=1.0
   - Real API calls to staging environment

**Test Distribution**:
- Parallel: `-n logical --dist worksteal` (all non-sequential tests)
- Sequential: `-m sequential` (tests requiring order)

**Coverage**:
- Minimum: 85%
- Reports: Codecov, SonarCloud
- Formats: XML, Markdown, HTML

**Artifacts**:
- JUnit XML: `reports/junit_*.xml`
- Coverage: `reports/coverage*`
- Markdown reports: `reports/pytest_*.md`

### 6. **test-scheduled-{staging|production}.yml**

**Purpose**: Continuous validation against live environments.

**Schedule**:
- Staging: Every 6 hours
- Production: Every 24 hours

**Tests Run**:
```bash
pytest -m "(scheduled or scheduled_only)"
```

**Purpose**:
- Detect API regressions
- Validate against real data
- Early warning system

### 7. **audit-scheduled.yml**

**Purpose**: Weekly security and license compliance checks.

**Schedule**: Every Monday at 3 AM UTC

**Checks**:
- pip-audit: CVE scanning
- pip-licenses: License compliance
- Trivy: SBOM vulnerability scanning

## Environment Configuration

### **Staging Environment**

**API Root**: `https://platform-staging.aignostics.com`

**Secrets**:
- `AIGNOSTICS_CLIENT_ID_DEVICE_STAGING`
- `AIGNOSTICS_REFRESH_TOKEN_STAGING`
- `GCP_CREDENTIALS_STAGING`

**Use Cases**:
- PR testing
- Feature validation
- Safe experimentation

### **Production Environment**

**API Root**: `https://platform.aignostics.com`

**Secrets**:
- `AIGNOSTICS_CLIENT_ID_DEVICE_PRODUCTION`
- `AIGNOSTICS_REFRESH_TOKEN_PRODUCTION`
- `GCP_CREDENTIALS_PRODUCTION`

**Use Cases**:
- Scheduled tests only
- Release validation
- Critical bug verification

## Claude Code Integration

### **How to Use Claude Code on GitHub**

**1. Automated PR Reviews**:
- Automatic on every PR
- Claude reviews code, tests, docs
- Posts inline comments

**2. Manual Interactive Sessions**:
```bash
# From GitHub UI:
Actions → Claude Code Interactive → Run workflow
  Prompt: "Your task here"
  Max turns: 200
  Environment: staging
```

**3. Workflow Integration**:
```yaml
jobs:
  claude-assist:
    uses: ./.github/workflows/_claude-code.yml
    with:
      mode: 'automation'
      prompt: 'Refactor authentication module'
      platform_environment: 'staging'
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### **Best Practices for Claude Code**

**DO**:
- ✅ Use `--system-prompt` referencing CLAUDE.md
- ✅ Limit tool access (`--allowed-tools`)
- ✅ Set reasonable `--max-turns`
- ✅ Use staging environment for development
- ✅ Review Claude's changes before merging

**DON'T**:
- ❌ Grant unrestricted tool access
- ❌ Skip CLAUDE.md system prompt
- ❌ Test against production without approval
- ❌ Merge without human review

## Debugging CI Failures

### **Lint Failures**

**Check**:
```bash
make lint
```

**Common Issues**:
- Ruff formatting: Run `ruff format .`
- Ruff linting: Check `ruff check .`
- PyRight: Type errors
- MyPy: Type errors

**Fix**:
```bash
ruff format .
ruff check . --fix
```

### **Test Failures**

**Reproduce Locally**:
```bash
# Unit tests
make test_unit

# Integration tests
make test_integration

# E2E tests (requires credentials)
make test_e2e

# Specific test
uv run pytest tests/path/to/test.py::test_name -v
```

**Check Coverage**:
```bash
uv run coverage report
```

**Debug**:
```bash
# Verbose output
uv run pytest tests/test_file.py -vv

# Show print statements
uv run pytest tests/test_file.py -s

# Drop into debugger
uv run pytest tests/test_file.py --pdb
```

### **Audit Failures**

**Security Vulnerabilities**:
```bash
uv run pip-audit
```
Fix: Update vulnerable dependencies in `pyproject.toml`

**License Violations**:
```bash
uv run pip-licenses --allow-only="MIT;Apache-2.0;BSD;..."
```
Fix: Replace non-compliant dependencies

## PR Labels

### **Skip CI**
- `skip:ci` - Skip all CI jobs
- `build:native:only` - Only build native app

### **Test Control**
- `skip:test_long_running` - Skip long-running tests (automatic)

## Secrets Management

**GitHub Secrets** (Required):
- `ANTHROPIC_API_KEY` - Claude Code
- `AIGNOSTICS_CLIENT_ID_DEVICE_{STAGING|PRODUCTION}`
- `AIGNOSTICS_REFRESH_TOKEN_{STAGING|PRODUCTION}`
- `GCP_CREDENTIALS_{STAGING|PRODUCTION}`
- `CODECOV_TOKEN` - Coverage reporting
- `SONAR_TOKEN` - Code quality
- `UV_PUBLISH_TOKEN` - PyPI publishing
- `DOCKER_USERNAME`, `DOCKER_PASSWORD` - Docker Hub
- `KETRYX_PROJECT`, `KETRYX_API_KEY` - Compliance
- `SLACK_WEBHOOK_URL_RELEASE_ANNOUNCEMENT` - Release notifications

**Local Secrets** (`.env` file):
```bash
AIGNOSTICS_API_ROOT=https://platform-staging.aignostics.com
AIGNOSTICS_CLIENT_ID_DEVICE=your-client-id
AIGNOSTICS_REFRESH_TOKEN=your-refresh-token
```

## Performance & Optimization

**Parallel Testing**:
- CPU-based distribution: `-n logical`
- Work stealing: `--dist worksteal`
- XDIST_WORKER_FACTOR controls parallelism (0.0-2.0)

**Caching**:
- `uv` dependencies cached via `astral-sh/setup-uv`
- Docker layers cached
- Nox virtualenvs reused (`nox.options.reuse_existing_virtualenvs = True`)

**Typical Run Times**:
- Lint: ~5 minutes
- Audit: ~3 minutes
- Test (per Python version): ~5 minutes
- Test (full matrix): ~15 minutes
- Full CI pipeline: ~20 minutes

## Workflow Files Reference

| File | Purpose | Trigger | Duration |
|------|---------|---------|----------|
| `ci-cd.yml` | Main pipeline orchestration | push, PR, release | ~20 min |
| `_claude-code.yml` | Claude Code execution | workflow_call | varies |
| `claude-code-automation-pr-review.yml` | Automated PR reviews | PR opened/updated | ~10 min |
| `claude-code-interactive.yml` | Manual Claude sessions | workflow_dispatch | varies |
| `_lint.yml` | Code quality checks | called by ci-cd | ~5 min |
| `_audit.yml` | Security & license | called by ci-cd | ~3 min |
| `_test.yml` | Test execution | called by ci-cd | ~15 min |
| `_codeql.yml` | Security scanning | called by ci-cd | ~10 min |
| `_package-publish.yml` | PyPI release | called by ci-cd (tags) | ~3 min |
| `_docker-publish.yml` | Docker release | called by ci-cd (tags) | ~5 min |
| `test-scheduled-staging.yml` | Continuous validation | schedule (6h) | ~10 min |
| `test-scheduled-production.yml` | Production validation | schedule (24h) | ~10 min |
| `audit-scheduled.yml` | Weekly security scan | schedule (weekly) | ~5 min |

## Common Workflows

### **Creating a PR**

1. Create feature branch
2. Make changes
3. Commit with conventional commits
4. Push to GitHub
5. Create PR → Triggers:
   - Lint
   - Audit
   - Test (staging)
   - CodeQL
   - Claude Code review

### **Releasing a Version**

1. Ensure `main` is clean
2. Run version bump:
   ```bash
   make bump patch  # or minor, major
   ```
3. Push with tags:
   ```bash
   git push --follow-tags
   ```
4. CI creates release → Triggers:
   - Full CI pipeline
   - Package publish (PyPI)
   - Docker publish
   - Slack notification

### **Manual Testing with Claude**

1. Go to: Actions → Claude Code Interactive
2. Click "Run workflow"
3. Enter prompt and settings
4. Monitor execution
5. Review changes in PR

---

**Built with operational excellence in mind for medical device software development.**
