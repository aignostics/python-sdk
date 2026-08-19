# CLAUDE.md — Test Suite

Guidance for working with the tests. Point up to the root `CLAUDE.md` and
`src/aignostics/CLAUDE.md` for architecture and the module index.

## Layout

Tests mirror the source package under `tests/aignostics/<module>/`, with one
`<name>_test.py` per source unit and a per-module `conftest.py` where needed.
Regenerate the current tree with `find tests -name '*_test.py'`; the main areas:

- `tests/aignostics/` — `application/`, `bucket/`, `dataset/`, `notebook/`,
  `platform/` (+ `platform/resources/`), `qupath/`, `system/`, `utils/`, `wsi/`.
- Top level: `conftest.py` (global fixtures), `constants_test.py`, `main.py`.
- `tests/fixtures/` — package dir, currently only `__init__.py`.
- `tests/resources/` — the actual test data (see below).

### Test data (`tests/resources/`)

Real fixtures live here, not in `fixtures/`:

- `cells.json`, `cells_broken.json` — valid / malformed cell payloads.
- `single-channel-ome.tiff`, `sm-thumbnail.dcm`, `unsupported.any` — WSI / DICOM inputs.
- `run/small-pyramidal.dcm` — small pyramidal DICOM for run tests.
- `mcp_dummy_plugin/` — installable dummy MCP plugin (has its own `pyproject.toml`).

## Markers

Every test needs at least one of `unit`, `integration`, `e2e` or it will not run
in CI. The authoritative marker list and descriptions live in `pyproject.toml`
`[tool.pytest.ini_options]` (also `long_running`, `very_long_running`,
`scheduled`, `scheduled_only`, `sequential`, `stress`, `stress_only`, `docker`,
`no_extras`, `skip_with_act`). See `.github/CLAUDE.md` for how CI selects them
and the `Makefile` for the `test_*` targets.

```bash
pytest -m sequential
pytest -m "unit and not long_running"
```

## Fixtures worth knowing

Global fixtures are in `tests/conftest.py`; module-specific ones in the nearest
`conftest.py`. A few non-obvious ones:

- **NiceGUI plugin** is auto-registered only when installed:
  `if find_spec("nicegui"): pytest_plugins = ("nicegui.testing.plugin",)`.
- **`clean_env`** (`platform/sdk_metadata_test.py`) uses
  `monkeypatch` to strip `GITHUB_*` / `PYTEST_*` / `NICEGUI_*` / `AIGNOSTICS_*`
  before building SDK metadata — use it whenever env detection matters.
- QuPath / subprocess tests terminate leftover processes in teardown; don't
  disable that or CI runners leak processes.

## SDK metadata tests (`platform/sdk_metadata_test.py`)

Cover metadata building, strict Pydantic validation (extra fields forbidden),
GitHub/pytest CI context capture, interface/source detection, and JSON-schema
generation. Do **not** hardcode the schema version — it comes from
`SDK_METADATA_SCHEMA_VERSION` / `ITEM_SDK_METADATA_SCHEMA_VERSION` in
`src/aignostics/platform/_sdk_metadata.py`. Assert against those constants:

```python
from aignostics.platform._sdk_metadata import (
    SDK_METADATA_SCHEMA_VERSION,
    build_run_sdk_metadata,
)

metadata = build_run_sdk_metadata()
assert metadata["schema_version"] == SDK_METADATA_SCHEMA_VERSION
```

## Cache-bypass tests (`platform/nocache_test.py`)

`cached_operation` (in `src/aignostics/platform/_operation_cache.py`) takes a
`nocache=True` kwarg that skips the cache read but still writes the fresh result.
The decorator intercepts `nocache` and does not pass it to the wrapped function.
`Client.me()`, `Runs.list()`, etc. expose the same kwarg. Minimal check:

```python
@cached_operation(ttl=60)
def f() -> int: ...


f()  # populates cache
f()  # cache hit, f not re-run
f(nocache=True)  # re-runs f, refreshes cache
```

See `nocache_test.py` for the full decorator / client / edge-case coverage.

## Coverage

Enforced by Codecov, not by any in-repo dict: project target 70%, patch target
75% (`codecov.yml`). Local report:

```bash
uv run pytest --cov=aignostics --cov-report=html
```

## NiceGUI 3.0+ troubleshooting

### Element state lost after user interaction

**Symptom:** inside an `@ui.refreshable`, UI element state (button
enabled/disabled, input values) resets after an interaction.

**Cause:** NiceGUI 3.0 added observable props/classes/styles. Setting `.value` on
an element inside `@ui.refreshable` can trigger element recreation, resetting
local variables. `ui.state()` makes it worse for parameterised refreshables:
its setter calls `refresh()` with **no** arguments, so the refreshable's
parameters fall back to their defaults.

**Fix:** for an `@ui.refreshable` that takes parameters, hold state in a mutable
dict rather than `ui.state()`, so updating state does not trigger a refresh:

```python
@ui.refreshable
def dialog_content(qupath_project: bool = False) -> None:
    folder_state: dict[str, str] = {"value": ""}
    selected_folder = ui.input("Folder", value=folder_state["value"])
    download_button = ui.button("Download")
    if not folder_state["value"]:
        download_button.disable()

    def on_select() -> None:
        folder_state["value"] = "/path/to/folder"  # no refresh triggered
        selected_folder.value = folder_state["value"]
        download_button.enable()
```

| Pattern | Use when |
|---------|----------|
| `ui.state()` | refreshable takes no parameters, or reset-on-refresh is fine |
| Mutable dict | refreshable takes parameters that must survive state updates |

Ref: <https://github.com/zauberzeug/nicegui/releases/tag/v3.0.0>
