---
name: sre-runbook
description: Repo-specific triage context for Aignostics Python SDK incidents
---

# Aignostics Python SDK -- SRE Triage Guide

## Incident Types

### "Scheduled Audit" incidents
- Cause: A dependency has a known CVE, or a license violation was detected.
- The audit runs hourly via .github/workflows/_scheduled-audit.yml.
- Tools used: pip-audit, pip-licenses, trivy.
- Common fix: bump the vulnerable dependency in pyproject.toml,
  then run `uv lock --upgrade-package <pkg>`.

### "Scheduled Testing" incidents (staging)
- Cause: Unit, integration, or e2e tests failed against staging.
- Runs every 6 hours via .github/workflows/_scheduled-test-hourly.yml.
- Check the workflow run logs for which test(s) failed.
- Common causes: flaky tests, dependency updates, API contract changes.

### "Scheduled Testing" incidents (production)
- Cause: Tests failed against production environment.
- Runs daily via .github/workflows/_scheduled-test-daily.yml.
- Common causes: platform API changes, credential expiry.
- These often require human intervention -- create an issue, not a PR.

## Repo-Specific Context
- Package manager: uv (not pip). Use `uv sync`, `uv add`, `uv run`.
- Linting: `make lint` (ruff + mypy + pyright)
- Testing: `make test_unit`, `make test_integration`, `make test_e2e`
- Security audit: `make audit` (pip-audit + pip-licenses + trivy)
- Dependency bumps: edit pyproject.toml, run `uv lock --upgrade-package <pkg>`
- CI workflows live in .github/workflows/
- Scheduled tests send heartbeats to BetterStack (see _scheduled-test-*.yml)

## PR Conventions
- Conventional commits: feat(...), fix(...), chore(deps): ...
- Always add labels: "sre-agent", "skip:test:long_running"
- Create DRAFT PRs only
