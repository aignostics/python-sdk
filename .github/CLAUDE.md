# CLAUDE.md — CI/CD & GitHub Actions

Guidance for working with the GitHub Actions workflows in `.github/workflows/`.
The YAML files are the source of truth; this doc orients you and calls out
non-obvious behaviour. When in doubt, read the workflow.

See root `CLAUDE.md` and `Makefile` for development commands and test markers.

## Workflow layout

Entry-point workflows (`+ …` names) are triggered by events; reusable
workflows (`> …`, prefixed `_`) are called via `uses:`.

| Entry point | Trigger | Calls |
|-------------|---------|-------|
| `ci-cd.yml` | push (main, release/v*, tag v*.*.*), PR (main, release/v*), release created, workflow_dispatch | `_lint`, `_docs`, `_audit`, `_test`, `_codeql`, `_ketryx_report_and_check`, `_package-publish`, `_docker-publish` |
| `prepare-release.yml` | workflow_dispatch | — |
| `publish-release.yml` | workflow_dispatch | — |
| `merge-release.yml` | workflow_dispatch | — |
| `build-native-only.yml` | push/PR/release when msg/label has `build:native:only` | `_build-native-only` |
| `claude-code-interactive.yml` | `@claude` mentions + workflow_dispatch | `_claude-code` (interactive) |
| `claude-code-automation-pr-review.yml` | PR with `claude` label or `ready_for_review` | `_claude-code` (automation) |
| `claude-code-automation-operational-excellence-weekly.yml` | schedule + workflow_dispatch | `_claude-code` (automation) |
| `scheduled-testing-staging-hourly.yml` | cron `17 * * * *` | `_scheduled-test-hourly` (staging) |
| `scheduled-testing-staging-daily.yml` | cron `31 12 * * *` | `_scheduled-test-daily` (staging) |
| `scheduled-testing-production-hourly.yml` | cron `17 * * * *` | `_scheduled-test-hourly` (production) |
| `scheduled-testing-production-daily.yml` | cron `31 12 * * *` | `_scheduled-test-daily` (production) |
| `scheduled-audit-hourly.yml` | cron `43 * * * *` | `_scheduled-audit` |
| `codeql-scheduled.yml` | cron `22 3 * * 2` (Tue 03:22) | `_codeql` |
| `labels-sync.yml` | push to label config | — |

Reusable: `_lint`, `_docs`, `_audit`, `_test`, `_codeql`,
`_ketryx_report_and_check`, `_package-publish`, `_docker-publish`,
`_build-native-only`, `_claude-code`, `_scheduled-audit`,
`_scheduled-test-hourly`, `_scheduled-test-daily`, `_scheduled-test-stress`.
(`stress-testing-staging.yml.paused` is currently disabled.)

## Main pipeline (`ci-cd.yml`)

**Triggers**: push to `main` / `release/v*` / tags `v*.*.*`; PR to `main` /
`release/v*`; `release` created; `workflow_dispatch` with a
`platform_environment` input (`staging` | `production`, default `staging`).

**Skip conditions** (checked per job): commit message or PR label contains
`skip:ci` or `build:native:only`.

**Jobs**: `get-commit-message` (extracts commit message + release version from
branch), `lint`, `docs`, `audit`, `test`, `codeql`, `sonarcloud`,
`ketryx_report_and_check`, `package_publish`, `docker_publish`.

**Dependency graph**:

```text
get-commit-message ──> lint, docs, audit, test, codeql
                       test ──> sonarcloud
lint, audit, test, codeql, sonarcloud, docs ──> ketryx_report_and_check
                                                 ├──> package_publish (tags only)
                                                 └──> docker_publish  (tags only)
```

`package_publish`/`docker_publish` run only on `refs/tags/v*`.
`ketryx_report_and_check` is skipped for `dependabot[bot]`.

## Test execution (`_test.yml`)

**Matrix axis is the runner/OS**, not the Python version. Python-version
iteration happens inside `nox`, driven by the `test_*_matrix` make targets.

`generate-matrix` builds the runner list:

- Always: `ubuntu-latest` (not experimental).
- Plus (unless `skip:test:matrix-runner` in commit message or PR label):
  `ubuntu-24.04-arm`, `macos-latest`, `macos-15-intel`, `windows-latest` — all
  `experimental: true` (job-level `continue-on-error`).

Each test category is a **step** using `./.github/actions/run-tests`, all with
`continue-on-error: true`, so every suite runs and Codecov always gets a
complete report. A final **`Assert no test failures`** gate step fails the job
if any category failed.

| Step | make target | Skip marker |
|------|-------------|-------------|
| unit | `test_unit_matrix` | `skip:test:unit` |
| integration | `test_integration_matrix` | `skip:test:integration` |
| e2e (regular) | `test_e2e_matrix` | `skip:test:e2e` |
| e2e long running | `test_long_running` | `skip:test:long_running` |
| e2e very long running | `test_very_long_running` | (opt-in, see below) |

**Very long running** runs only when enabled: `enable:test:very_long_running`
in commit message or PR label, or any push or manual dispatch
(`workflow_dispatch`) to a `release/v*` branch.

**Parallelism** is set by `XDIST_WORKER_FACTOR` (worker count =
`max(1, int(cpu_count * factor))`). CI runs the `*_matrix` targets — unit and
integration matrix use `0.5`, e2e matrix uses `1`. The non-matrix local targets
(`test_unit`=0.0, `test_integration`=0.2, `test_e2e`=1, long/very_long=2) run a
single Python version. See the `Makefile` for the authoritative values.

### Test markers

Every test **must** carry at least one of `unit`, `integration`, `e2e` or it
will not run in CI (the matrix targets filter by marker). The full marker list
(incl. `long_running`, `very_long_running`, `scheduled`, `scheduled_only`,
`sequential`) lives in `pyproject.toml` `[tool.pytest.ini_options]`.

Skip/enable labels & commit shortcuts: `skip:ci`, `build:native:only`,
`skip:test:matrix-runner`, `skip:test:{unit,integration,e2e,long_running}`,
`enable:test:very_long_running`, `skip:codecov`.

```bash
gh pr edit --add-label "skip:test:long_running"
git commit -m "fix: something skip:test:long_running"
```

## Native builds (`build-native-only.yml`)

Triggered by `build:native:only` in commit message or PR label; skips the main
pipeline and only builds native executables via `_build-native-only.yml`.
Runners: `ubuntu-latest` (stable) plus experimental `ubuntu-24.04-arm`,
`macos-latest`, `macos-15-intel`, `windows-latest` (UPX), `windows-11-arm`.
Output: `aignostics.7z` per platform. Local: `make dist_native`.

## Claude Code (`_claude-code.yml`)

One reusable workflow, two modes via the `mode` input:

- **interactive** — full git history (`fetch-depth: 0`).
  `claude-code-interactive.yml` triggers it on `@claude` mentions
  (issue/PR comments, reviews, issues, PRs) and `workflow_dispatch`. It passes
  only `mode` and `track_progress` — there are **no** `prompt`/`max_turns`/
  `environment` inputs to fill in.
- **automation** — shallow history (`fetch-depth: 1`), runs a fixed `prompt`.
  `claude-code-automation-pr-review.yml` triggers it when a PR carries the
  `claude` label or becomes `ready_for_review`. `max_turns` is not set, so it
  uses the `_claude-code.yml` default (200). Review tools include
  `mcp__github_inline_comment__create_inline_comment` and posts a
  `claude:review:passed` / `claude:review:failed` verdict label.

`_claude-code.yml` inputs: `mode` (required), `prompt`, `max_turns` (default
`200`), `allowed_tools` (default defined in the workflow — read it there rather
than copying), `track_progress`, `use_sticky_comment`. Model is
`claude-sonnet-4-5-20250929`.

**Setup**: installs `uv`, dev tools (`_install_dev_tools.bash`),
`uv sync --all-extras --frozen`, headless display. Only secret available is
`ANTHROPIC_API_KEY` — Claude Code workflows intentionally have **no** platform
or GCP credentials.

## Scheduled jobs

- **Testing** — staging and production each run **hourly** (`17 * * * *`, via
  `_scheduled-test-hourly.yml`) and **daily at 12:31 UTC** (`31 12 * * *`, via
  `_scheduled-test-daily.yml`). The crons avoid minute 0: GitHub documents
  that `schedule` events are delayed most at the start of every hour. Run
  `make test_scheduled`, send a BetterStack heartbeat. Staging → `https://platform-staging.aignostics.com`, production →
  `https://platform.aignostics.com`.
- **Audit** — hourly (`_scheduled-audit.yml`): `pip-audit`, `pip-licenses`,
  Trivy SBOM scan + BetterStack heartbeat.
- **CodeQL** — weekly Tue 03:22 (`_codeql.yml`).

### BetterStack heartbeats

Scheduled test/audit jobs POST a metadata JSON payload to
`{HEARTBEAT_URL}/{EXIT_CODE}` (0 = success) so BetterStack alerts on failures or
missed beats. If the URL secret is unset the step logs a warning and continues.
Secrets: `BETTERSTACK_AUDIT_HEARTBEAT_URL`,
`BETTERSTACK_HEARTBEAT_URL_{STAGING,PRODUCTION}` (hourly),
`BETTERSTACK_HEARTBEAT_URL_FLOWS_{STAGING,PRODUCTION}` (daily).

## Environments & secrets

**Staging** (`platform-staging.aignostics.com`) is the default for all PR CI and
E2E. **Production** (`platform.aignostics.com`) is used only by scheduled jobs
and release validation — never in PR CI.

GitHub secrets: `ANTHROPIC_API_KEY`,
`AIGNOSTICS_CLIENT_ID_DEVICE_{STAGING,PRODUCTION}`,
`AIGNOSTICS_REFRESH_TOKEN_{STAGING,PRODUCTION}`,
`GCP_CREDENTIALS_{STAGING,PRODUCTION}` (base64 JSON), the BetterStack URLs above,
`CODECOV_TOKEN`, `SONAR_TOKEN`, `SENTRY_DSN`/`SENTRY_AUTH_TOKEN`,
`UV_PUBLISH_TOKEN`, `DOCKER_USERNAME`/`DOCKER_PASSWORD`,
`KETRYX_PROJECT`/`KETRYX_API_KEY`, `SLACK_*_RELEASE_ANNOUNCEMENT`.

Local `.env` for E2E:

```bash
AIGNOSTICS_API_ROOT=https://platform-staging.aignostics.com
AIGNOSTICS_CLIENT_ID_DEVICE=your-staging-client-id
AIGNOSTICS_REFRESH_TOKEN=your-staging-refresh-token
```

## Releasing a version

Four-phase workflow triggered from a developer machine so Ketryx approvals are
collected *before* the tag (and thus before PyPI publish):

1. `make prepare-release 1.2.3` → `prepare-release.yml`: creates
   `release/vX.Y.Z` from `main`, bumps version + `uv.lock`, pushes. CI runs.
2. Point the Ketryx release at `release/vX.Y.Z`, collect approvals, ensure CI green.
3. `make publish-release` → `publish-release.yml`: generates `CHANGELOG.md`,
   creates annotated `vX.Y.Z` tag → CI/CD fires on tag → Ketryx check gates PyPI.
4. `make merge-release` → `merge-release.yml`: merges `release/vX.Y.Z` into
   `main` `--no-ff`, deletes the release branch.

`release/v*` branches should be protected so only `aignostics-release-bot[bot]`
can push.

## Debugging CI failures

Reproduce locally with the same make targets CI uses: `make lint`,
`make test_unit` / `test_integration` / `test_e2e` (E2E needs `.env`),
`make dist_native`, `uv run pip-audit`. Coverage minimum is enforced via
Codecov (see `codecov.yml`). For scheduled-job failures, check the BetterStack
dashboard and the workflow run logs (usual causes: API changes in the target
environment, expired credentials).

Run scheduled workflows manually:

```bash
gh workflow run scheduled-testing-staging-hourly.yml
gh workflow run scheduled-testing-production-daily.yml
```
