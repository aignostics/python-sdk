# application — application run orchestration

High-level orchestration for AI/ML application runs on the Aignostics Platform:
listing applications/versions, submitting runs, monitoring, and downloading
results (with optional QuPath integration). Bridges `platform`, `wsi`, `bucket`,
and `qupath`. See `../CLAUDE.md` for where this sits in the whole SDK.

## Public API (`_service.py`)

`Service` (aliased `ApplicationService`) methods — see the file for full signatures:

- `applications()` / `applications_static()` — list available applications.
- `application_version(application_id, application_version=None)` — retrieve one
  version; `application_version=None` returns the latest. Returns an
  `ApplicationVersion` whose attributes are `.application_id` and `.version_number`.
  The version string is validated as semver (no `v` prefix); an invalid string
  raises `ValueError` ("not compliant with semantic versioning").
- `application_versions(application_id)` / `application_versions_static(...)`.
- `application_run_submit(...)` / `application_run_submit_from_metadata(...)` —
  submit a run.
- `application_run_update_custom_metadata(...)` / `..._update_item_custom_metadata(...)`
  (+ `_static` variants) — see "Custom metadata" below.

Note the parameter name asymmetry: the request keyword is `application_version`,
while the returned object exposes it as `.version_number`.

## Models (`_models.py`)

`DownloadProgress` (Pydantic) tracks run/item/artifact download state plus
optional QuPath progress, with computed fields `total_artifact_count`,
`total_artifact_index`, `item_progress_normalized`, and
`artifact_progress_normalized` (0..1). `DownloadProgressState` (StrEnum) holds the
human-readable stage labels. QuPath fields are only present when the `aignostics`
package is installed (`has_qupath_extra = find_spec("aignostics")`). See `_models.py` for fields.

## Download helpers (`_download.py`)

- `extract_filename_from_url(url)` — filename from `gs://`/`http(s)://`.
- `download_url_to_file_with_progress(progress, url, destination_path, ...)` —
  streams in 1 MB chunks; converts `gs://` to a signed URL via
  `platform.generate_signed_url()`.
- `download_available_items(progress, application_run, destination_directory,
  downloaded_items, ...)` — only TERMINATED items with FULL output; skips items
  already in `downloaded_items` (by external_id).
- `download_item_artifact(progress, run, artifact, destination_directory, prefix="", ...)` —
  resolves a fresh presigned URL from `run`, verifies CRC32C, skips re-download
  when the local file already matches the checksum.

Constants (defined here): `APPLICATION_RUN_FILE_READ_CHUNK_SIZE` = 1 GB (checksum
reads), `APPLICATION_RUN_DOWNLOAD_CHUNK_SIZE` = 1 MB (streaming).

Progress is reported via a dual mechanism: a synchronous `download_progress_callable`
(CLI) and/or an async `download_progress_queue` (GUI); both may be set.

## CLI (`_cli.py`)

Top level: `list`, `dump-schemata`, `describe`.

`application run`: `execute`, `prepare`, `upload`, `submit`, `list`, `describe`,
`cancel`, `cancel-by-filter`, `dump-metadata`, `dump-item-metadata`,
`update-metadata`, `update-item-metadata`.

`application run result`: `download`, `delete`.
`application run share`: `status`; `share organization`: `list`/`grant`/`revoke`;
`share token`: `list`/`create`/`revoke`.
`application version`: version inspection; `version document`: `list`/`describe`/`download`.

## Behaviour worth knowing

**Health gating.** `execute`, `upload`, and `submit` call `_abort_if_system_unhealthy()`
first (`--force` overrides); it runs `asyncio.run(SystemService.health_static())`
and exits 1 when unhealthy. The GUI stepper disables progression on an unhealthy
system and offers a force-skip checkbox to internal orgs. Health enforcement
details are owned by `../system/CLAUDE.md`.

**Custom metadata (optimistic concurrency).** `run dump-metadata` /
`dump-item-metadata` take `--show-checksum` (wraps output as
`{"custom_metadata": ..., "custom_metadata_checksum": ...}`). `run update-metadata` /
`update-item-metadata` take `--checksum` and `--enrich-sdk-metadata` /
`--no-enrich-sdk-metadata`. Passing a stale `--checksum` makes the platform return
HTTP 412; the service raises `platform.ConcurrencyConflictError` (a `ValueError`
subclass) and the CLI exits with code 3 (distinct from code 2 for not-found /
invalid-ID). Read-modify-write example:

```bash
aignostics application run dump-metadata RUN_ID --show-checksum --pretty
# ... edit the dumped JSON ...
aignostics application run update-metadata RUN_ID "<edited json>" \
  --checksum <checksum-from-dump> --no-enrich-sdk-metadata
```

`enrich_sdk_metadata=False` forwards `custom_metadata` (including any `sdk` field)
verbatim, skipping the SDK-metadata merge/validation — use it when round-tripping
a previously dumped `sdk` field. See `../platform/CLAUDE.md` for full semantics.

**SDK metadata.** Every submitted run gets SDK metadata attached automatically via
`platform._sdk_metadata.build_run_sdk_metadata()`. Schema versions and details live
in `../platform/CLAUDE.md` / `platform/_sdk_metadata.py` — not duplicated here.

## Dependencies & gotchas

Internal: `platform` (API, signed URLs, SDK metadata), `wsi` (validation),
`bucket` (storage), `utils` (DI/logging), and optional `qupath` (gated on the
`aignostics` package). External deps and extras are declared in `pyproject.toml`;
QuPath features require the `aignostics` package installed alongside `aignostics-sdk`.

## Tests

`tests/aignostics/application/service_test.py` covers semver validation (valid/
invalid formats, latest-version fallback) and run lifecycle. Match the existing
style there (positional args, `pytest.raises(..., match=r"not compliant with
semantic versioning")`) when adding cases.
