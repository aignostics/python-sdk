# notebook — embedded Marimo notebook server

Launches a local [Marimo](https://marimo.io/) server running a single fixed
notebook, embedded in the GUI for exploring application results. GUI-only, no
CLI. See `../CLAUDE.md` for placement in the SDK.

The whole module is gated in `__init__.py` on
`find_spec("marimo") and find_spec("nicegui")` — if either is missing it exports
nothing and is silently skipped (no error).

## Public API — `_service.py`
- Module singleton `runner: _Runner | None` + `_get_runner()` (lazy init). `_Runner` owns the subprocess, monitor thread, and URL state.
- `Service(BaseService)` is a thin facade over the singleton:
  - `start()` — no args; starts the server (if not already running) and returns its URL.
  - `stop()`, `health()`, `is_marimo_server_running()`, `is_monitor_thread_alive()`.

## GUI — `_gui.py`
`PageBuilder(BasePageBuilder)` registers two pages:
- `/notebook` — landing card with a launch link.
- `/notebook/{run_id}` — calls `Service().start()` and embeds `server_url` in an
  `<iframe>`, passing `run_id` and `results_folder` as query params. On failure
  shows an error label + Retry.

(There is no `create_notebook_interface` function.)

## Behaviour worth knowing
- Launch command is `marimo edit --headless --skip-update-check --no-sandbox --no-token <notebook>`, run via `python -m marimo` (or `python --run-module marimo` when `sys.frozen`). **Host/port are not controllable** — no `--host`/`--port` flags.
- On first start it copies `_notebook.py` (the `NOTEBOOK_DEFAULT` constant, header `requires-python = ">=3.13"`) to `get_user_data_directory("notebooks")/notebook.py`. Always this one fixed file; extension is `.py`, not `.marimo.py`.
- URL detection: `_capture_output(process)` reads stdout **char by char**, and per line matches `r"URL:\s+((?:http|https)://[^\s]{1,100})"`; the first match sets `_server_url` and fires the ready `Event`.
- Startup blocks up to `MARIMO_SERVER_STARTUP_TIMEOUT = 60`s; on timeout it kills the process and raises `RuntimeError`.
- Cleanup: `_Runner.__init__` registers `stop` with `atexit` (terminate → wait 2s → kill).
- `health()` reports `UP` before first `start()`; afterwards it reflects the subprocess and monitor-thread liveness as components.

## Dependencies & gotchas
`marimo` + `nicegui` (gate above). `NOTEBOOK_DEFAULT` comes from
`aignostics.constants`; subprocess flags from `aignostics.utils`
(`SUBPROCESS_CREATION_FLAGS`). See `pyproject.toml` for extras.
