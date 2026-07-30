# bucket — cloud storage on the Aignostics Platform

Upload/find/download/delete objects in the org's Google Cloud Storage bucket.
Used by the `application` module (input upload, result download) and via the
`bucket` CLI. See `../CLAUDE.md` for where this sits in the SDK.

Storage is GCS only, reached through a **boto3 S3-compatible client** pointed at
`storage.googleapis.com` (`ENDPOINT_URL_DEFAULT`) with HMAC keys. There is no
Azure and no `google-cloud-storage` dependency; `BucketProtocol` (`_settings.py`)
only defines `GS`/`S3`.

## Public API — `_service.py`
`Service()` takes no args. Credentials, bucket name, and region come from the
platform org settings (via `PlatformService.get_user_info().organization`), not
constructor args.

- `get_bucket_name()` — the org's bucket; raises `ValueError` if unset. All ops target it.
- `create_signed_upload_url(object_key, bucket_name=None)` / `create_signed_download_url(object_key, bucket_name=None)` — presigned URLs (`put_object`/`get_object`).
- `upload(source_path, destination_prefix, callback=None)` — file or directory (recursive glob). Returns `{"success": [...], "failed": [...]}` of object keys.
- `find(what, what_is_key=False, detail=False, include_signed_urls=False)` — `what` is a list of regex patterns (default `[".*"]`) or exact keys when `what_is_key=True`.
- `download(what, destination, what_is_key=False, progress_callback=None)` → `DownloadResult`.
- `delete(what, what_is_key=False, dry_run=True)` → count deleted. `dry_run=True` is the default.
- `*_static` variants (`find_static`, `download_static`, `delete_static`) just wrap `Service().<method>()` for one-shot calls.

## CLI — `_cli.py`
`upload`, `find`, `download`, `delete`, `purge`. (No `list`/`sign`.) `purge`
is `delete(what=None)` over the whole bucket. `delete`/`purge` default to
`--dry-run`; pass `--no-dry-run` to actually delete.

## Behaviour worth knowing
- `find` infers a common S3 `Prefix` from the patterns/keys (`_compute_s3_prefix`) to cut paginator pages on large buckets; invalid regex raises `ValueError` → CLI exits 2.
- Download skip is ETag-based only: if a local file's MD5 (computed in 100MB chunks, `ETAG_CHUNK_SIZE`) equals the object ETag, it is not re-downloaded. No Range/resume, no multipart.
- Upload streams via a presigned PUT in 1MB chunks (`UPLOAD_CHUNK_SIZE`); download streams in 10MB chunks. `callback(bytes, path)` on upload; `progress_callback(DownloadProgress)` on download.
- `upload` CLI `--destination-prefix` templates `{username}` and `{timestamp}`.
- No permission checks, server-side encryption, audit logging, or local cache — do not add docs for those.

## Dependencies & gotchas
`boto3`/`botocore` (imported lazily inside methods). See `pyproject.toml`.
Requires `aignostics_bucket_hmac_access_key_id` / `_secret_access_key` /
`aignostics_bucket_name` on the org, else `ValueError`. `_settings.py` holds
`region_name` and signed-URL expirations. `PageBuilder` (`_gui.py`) is exported
only when `nicegui` is installed (see `__init__.py`).
