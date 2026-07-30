# qupath — install, drive & script the QuPath desktop app

Downloads/installs QuPath, launches it (usually headless to run Groovy scripts),
and manages its processes. Project creation, adding images, and annotating all
happen by running bundled Groovy scripts inside QuPath — this module does not
author `.qpproj`/`.qpdata` files itself. Consumed by `application` for result
visualization; depends only on `aignostics.utils` plus ijson/psutil/
platformdirs/requests/packaging. See `../CLAUDE.md` for placement.

## Public API (`_service.py`, `Service`, mostly `@staticmethod`)

- `install_qupath(version=QUPATH_VERSION, path=None, reinstall=True, platform_system, platform_machine, download_progress, extract_progress, progress_queue)` → app dir.
- `execute_qupath(quiet=True, project=None, image=None, script=None, script_args=None)` → pid or None. The core primitive; everything below builds on it.
- `add(project, paths, progress_callable=None)` → count. Runs `scripts/add.groovy`.
- `annotate(project, image, annotations, progress_callable=None)` → count. Runs `scripts/annotate.groovy`.
- `inspect(project)` → `QuPathProject`. Runs `scripts/inspect.groovy`.
- `get_qupath_processes()` / `terminate_qupath_processes(wait_before_kill=3)`.
- `install`/`uninstall` helpers: `uninstall_qupath(...)`, `find_qupath_executable`, `get_version`, `get_expected_version`, `is_qupath_installed`, `is_installed`, `get_installation_path`, `get_app_dir`.

There is no `launch_qupath` / `run_script` / `list_processes` / `terminate_all` /
`create_project` / `add_images_to_project` on the service — the CLI command
`launch` maps to `execute_qupath`, `processes` to `get_qupath_processes`, etc.

`QUPATH_VERSION = "0.6.0"` lives in `_service.py`; reference it rather than
hardcoding. `get_installation_path()` returns `platformdirs.user_data_dir(
__project_name__)` (NOT `~/.aignostics/qupath`).

## CLI (`_cli.py`)

- `qupath install [--version] [--path] [--reinstall] [--platform-system] [--platform-machine]`
- `qupath launch [--project] [--image] [--script]`
- `qupath processes [--json/-j]`
- `qupath terminate`
- `qupath uninstall [--version] [--path] [--platform-system] [--platform-machine]`
- `qupath add PROJECT PATH...` — positional project dir then one or more image/dir paths.
- `qupath annotate PROJECT IMAGE ANNOTATIONS` — three positionals; annotations is GeoJSON.
- `qupath inspect PROJECT` — prints `QuPathProject` as JSON.
- `qupath run-script SCRIPT [--project/-p] [--image/-i] [--args/-a ...]` — SCRIPT is
  positional; `--args`/`-a` is a REPEATABLE plain-string option (not JSON), each
  value passed through as a separate `-a` to QuPath.

Exit codes: commands `sys.exit(2)` for "nothing found / not installed" states
(e.g. `terminate` with no processes, `launch` when QuPath isn't installed) and
`sys.exit(1)` on failure.

## Behaviour worth knowing

- **`execute_qupath` builds the QuPath argv by hand** and blocks reading stdout:
  when a `script` is given it waits up to `QUPATH_SCRIPT_MAX_EXECUTION_TIME`
  (2h) for exit code 0; without a script it waits up to
  `QUPATH_LAUNCH_MAX_WAIT_TIME` (30s) for the "Starting QuPath" log line.
  Returns the pid on success, `None` on timeout/failure.
- **Groovy is the integration boundary.** `add`/`annotate`/`inspect` write inputs
  to temp JSON files, invoke a script from `scripts/` via `execute_qupath`, then
  read the script's JSON output back. Temp files use `delete=False` and are
  unlinked in `finally` (works around Windows file locking). `annotate` counts
  features by streaming with `ijson` before invoking the script.
- **Download URL is per-OS** (`_download_qupath`): Linux `tar.xz`, Darwin `pkg`,
  Windows `zip`. Archive name is version-gated — for ≥0.4.4 it's
  `QuPath-v{version}-{Linux|Windows|Mac-arm64|Mac-x64}`; older branches differ.
  Final URL: `https://github.com/qupath/qupath/releases/download/{version}/{name}.{ext}`.
  There is no flat `platform_map` producing `.zip` everywhere.
- **Extraction is per-OS** (`_extract_qupath`): tar.xz for Linux, `pkgutil --expand`
  (or `7z` off-mac) + cpio for the Darwin `.pkg`, zipfile for Windows.
- `get_qupath_processes` only reports processes whose exe lives under the managed
  installation path; `terminate` won't touch a QuPath the user launched elsewhere.

## Progress dataclasses (`_service.py`, Pydantic models)

- `AddProgress(status, image_count, image_index, image_path)`
- `AnnotateProgress(status, image_path, annotation_count, annotation_index, annotation_path)`
- `InstallProgress(status, archive_*...)`

The field is `status` (a `*ProgressState` StrEnum), NOT `state`. `AddProgress`
and `AnnotateProgress` both expose a computed `progress_normalized` (0..1);
`InstallProgress` exposes `archive_download_progress_normalized`. Read the models
for exact fields rather than copying them.

## Dependencies & gating

`__init__.py` only exports the module (cli, PageBuilder, Service, ...) when BOTH
`find_spec("ijson")` and `find_spec("nicegui")` succeed; otherwise it silently
exports nothing (no ImportError raised). See `pyproject.toml` for the `qupath`
extra and dependency versions. External runtime needs: a Java-bearing QuPath
release from GitHub (installed by this module) and, on non-mac for `.pkg`
handling, `7z`.
