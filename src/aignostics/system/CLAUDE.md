# system — health, info and configuration utilities

Aggregates health and info across every SDK service, dumps/edits `.env`
configuration, and exposes the platform OpenAPI schema. The health aggregation
here is what gates run submission/upload elsewhere. See `../CLAUDE.md` for the
module map.

## Public API (`_service.py`)
`Service` (subclass of `utils.BaseService`); most methods are `@staticmethod`.
- `async health()` / `async health_static()` — aggregate `Health`. `health_static`
  is the callable other modules use (it just `await`s `Service().health()`).
- `async info(include_environ=False, mask_secrets=True) -> dict` — package /
  runtime / settings tree plus one key per other service.
- `openapi_schema() -> JsonType` — loads `codegen/in/openapi.json`; raises
  `OpenAPISchemaError` (in `_exceptions.py`, the module's only exception) on
  missing/invalid file.
- `dotenv_get/set/unset`, `dump_dot_env_file(destination)`,
  `remote_diagnostics_enable/disable`, `http_proxy_enable/disable` — read/write
  `.env` files (see behaviour below).
- `_collect_all_settings`, `_is_secret_key` — internal helpers (see below).

`__init__` also exports `Settings` and, when `nicegui` is importable, `PageBuilder`.

## CLI (`_cli.py`)
Root `system`:
- `system health [--output-format json|yaml]` — prints aggregate health; exits 1
  if unhealthy.
- `system info [--include-environ] [--mask-secrets/--no-mask-secrets] [--output-format]`.
- `system dump-dot-env-file [--destination .env.current]`.
- `system serve [--host --port --open-browser]` — NiceGUI web app; only registered
  when `find_spec("nicegui")` succeeds.
- `system openapi [--api-version v1] [--output-format]`.
- `system install` — placeholder, prints a message.
- `system config` sub-Typer: `get`, `set`, `unset`, `remote-diagnostics-enable`,
  `remote-diagnostics-disable`, `http-proxy-enable`, `http-proxy-disable`.

Both `health` and `info` are async and driven from the CLI via `asyncio.run`.
There is no `proxy-request` command.

## Behaviour worth knowing
- **Health aggregation**: `health()` iterates `locate_subclasses(BaseService)`
  (skipping `Service` itself), keying each by its fully-qualified dotted class path
  (e.g. `aignostics.platform._service.Service`), and adds a `"network"` component
  from `_determine_network_health()` (unauthenticated GET to `https://api.ipify.org`,
  5s timeout). Overall status derives from `_is_healthy()` (currently always `True`),
  so a child DOWN shows in components but the tree still reports per the parent rule
  in `utils/_health.py`.
- **Health gates run operations** — the module's real value:
  - CLI: `application/_cli.py:_abort_if_system_unhealthy()` calls
    `asyncio.run(SystemService.health_static())` and `sys.exit(1)` if unhealthy.
    Invoked before submit/upload/execute, skipped when the command's `--force`
    (`ForceOption`) is set.
  - GUI: `application/_gui/_page_application_describe.py` (~L210, L405-429) reads
    `await SystemService.health_static()`; when unhealthy it shows the tooltip
    "System is unhealthy, you cannot prepare a run at this time." and only offers
    the "Force (skip health check)" checkbox to `user_info.is_internal_user`, whose
    toggle hides/shows that tooltip.
  - Library: no automatic enforcement — call `health_static()` yourself.
- **Secret masking**: `_is_secret_key(key)` lower-cases the key, matches `"id"` on a
  word boundary (regex, so it won't hit `valid`/`middle`) plus a ~16-term substring
  list (`auth`, `bearer`, `cert`, `credential`, `hash`, `jwt`, `key`, `nonce`,
  `oauth`, `password`, `private`, `salt`, `secret`, `seed`, `session`, `signature`,
  `token`). Masked value is the literal `"*********"`. Applies to `info`'s `environ`
  block; settings masking is delegated to each `BaseSettings` serializer via the
  `UNHIDE_SENSITIVE_INFO` context flag. No regex pattern list.
- **`info` structure**: `package` / `runtime` (env, process, host os+cpu+memory+network,
  python) / `settings` (flattened `ENV_PREFIX+KEY` from all `BaseSettings`, sorted),
  then one extra key per other `BaseService.info()`. CPU/memory sampled over
  `MEASURE_INTERVAL_SECONDS = 2` via psutil, so `info` takes ~2s.
- **`.env` writes**: `dotenv_set` first unsets the key across all env files, then
  writes to the primary file (`__env_file__[0]`, `ValueError` if it doesn't exist)
  and updates `os.environ`. `remote_diagnostics_*` toggle the SENTRY/LOGFIRE enabled
  flags; `http_proxy_enable` writes HTTP(S)_PROXY and manages SSL cert / no-verify
  env vars (rejects setting both `ssl_cert_file` and `no_ssl_verify`).

## Dependencies & gotchas
Deps (`httpx`, `psutil`, `python-dotenv`, `pyyaml`, `typer`, …): see `pyproject.toml`.
`Settings` (`_settings.py`) holds only an optional `token` secret used by
`is_token_valid`. GUI (`_gui.py`) loads only under `find_spec("nicegui")`.
