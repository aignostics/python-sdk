# dataset — download imaging datasets from IDC and Aignostics

Downloads public cancer imaging data from the NCI Imaging Data Commons (IDC)
and proprietary sample datasets from Aignostics buckets. CLI + GUI wrap a
static-method `Service`. See `../CLAUDE.md` for where this module sits in the SDK.

## Public API (`_service.py`)
`Service` (subclass of `utils.BaseService`) exposes static methods:
- `download_idc(source, target, target_layout=TARGET_LAYOUT_DEFAULT, dry_run=False) -> int` —
  synchronous IDC download; returns count of matched identifier types.
- `download_with_queue(queue, source, target, target_layout, dry_run)` — same as
  above but runs the actual download in a subprocess and pushes float progress
  (0.0–1.0) onto a `multiprocessing.Queue`; used by the GUI.
- `download_aignostics(source_url, destination_directory, download_progress_callable=None) -> Path` —
  streams one bucket object to a folder via a platform signed URL (`requests`,
  8192-byte chunks); callback gets `(len(chunk), total_size, filename)`.

`__init__` also re-exports `IDCClient` (from `aignostics.third_party.idc_index`)
and, when `nicegui` is importable, `PageBuilder`.

## CLI (`_cli.py`)
Root `dataset` with two sub-Typers:
- `dataset idc browse` — open the IDC portal in a browser.
- `dataset idc indices` — list `client.indices_overview` keys.
- `dataset idc columns [--index sm_instance_index]` — list columns of an index.
- `dataset idc query [SQL] [--indices ...]` — run a SQL query via `client.sql_query`.
- `dataset idc download SOURCE [TARGET] [--target-layout] [--dry-run]` — calls
  `Service.download_idc`.
- `dataset aignostics download SOURCE_URL [DEST]` — calls `Service.download_aignostics`
  with a rich progress bar.

There is no `collections` subcommand.

## Behaviour worth knowing
- **`source` matching**: `source` is a comma-separated list of IDs. Each ID list
  is matched, in order, against `collection_id`, `PatientID`, `StudyInstanceUID`,
  `SeriesInstanceUID`, then `SOPInstanceUID` (last uses `sm_instance_index`).
  A `download_from_selection` call fires per matched column. Zero matches across
  all columns raises `ValueError`.
- **How IDC bytes actually move**: `download_idc` calls
  `IDCClient.download_from_selection(..., use_s5cmd_sync=True)` directly.
  `download_with_queue` instead builds a small `python -c` script and runs it in a
  `subprocess.Popen` (or `sys.executable --exec-script` under PyInstaller) so
  progress can be scraped. s5cmd is invoked by idc-index internally — this module
  never calls the `s5cmd` binary itself.
- **Progress scraping**: `Service._capture_progress_output(process, queue, base_progress=0.5)`
  reads subprocess stderr one char at a time and matches `r"Downloading data:\s+(\d+)%"`,
  scaling the percentage into `[base_progress, 0.99]` and pushing `1.0` on completion.
  No throughput/ETA calculation.
- **Subprocess cleanup**: module-level `_active_processes` list + `atexit`-registered
  `_cleanup_processes()`; `_terminate_process()` does terminate → 0.5s grace → kill.
- **Exit codes**: `ValueError` (bad input) → exit 2; any other exception → exit 1.
- **Target dir must already exist** — `download_idc`/`download_with_queue` raise
  `ValueError` if it does not (CLI also enforces `exists=True`). `download_aignostics`
  creates the destination directory.
- `TARGET_LAYOUT_DEFAULT` and `PATH_LENGTH_MAX = 260` are defined in both
  `_service.py` and `_cli.py`. `PATH_LENGTH_MAX` is currently unused — there is no
  path-shortening helper.

## `IDCClient` (`../third_party/idc_index.py`)
Vendored + patched copy of the `idc-index` client. Use the
`IDCClient.client()` classmethod (cached per-class instance), not `IDCClient()`.
Patched to run behind corporate proxies and to retry transient HTTP failures via
`tenacity` (`_requests_get_with_retry`, 4 attempts, exponential jitter, retries
connection/timeout errors and HTTP 5xx). Requires the `s5cmd` binary on PATH (or
bundled with the package) — `__init__` raises `FileNotFoundError` otherwise.

## Dependencies & gotchas
Deps (`idc-index`, `s5cmd`, `pandas`, `requests`, …) and extras: see
`pyproject.toml`. `Service.info`/`health` are stubs (return `{}` / `UP`). GUI code
in `_gui.py` is imported only when `find_spec("nicegui")` succeeds (`__init__.py`).
`download_aignostics` signs the source URL via `platform.generate_signed_url`.
