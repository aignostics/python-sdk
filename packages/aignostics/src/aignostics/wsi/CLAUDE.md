# wsi — whole slide image thumbnails, metadata & DICOM file selection

Reads WSI files to produce thumbnails and metadata, and picks which DICOM
files in a directory are worth processing. Consumed by `application` (metadata
generation, upload prep) and `qupath`; depends only on `aignostics` (constants)
and `aignostics.utils`. See `../CLAUDE.md` for where this sits in the SDK.

## Supported formats

`WSI_SUPPORTED_FILE_EXTENSIONS = {".dcm", ".tiff", ".tif", ".svs"}` — defined in
`aignostics/constants.py`, re-exported from `aignostics/__init__.py`. That set
is the single source of truth; `Service` rejects anything else. Note `.dicom`
is NOT accepted (only `.dcm`).

## Public API (`_service.py`, all `@staticmethod` on `Service`)

- `get_thumbnail(path, max_safe_dimension=DEFAULT_MAX_SAFE_DIMENSION)` → PIL Image.
- `get_thumbnail_bytes(path, ...)` → PNG bytes (wraps `get_thumbnail`).
- `get_metadata(path)` → nested dict (see below).
- `get_tiff_as_jpg(url)` → JPEG bytes fetched from a URL.
- `get_wsi_files_to_process(path, extension)` → iterable of paths to process.

All of `get_thumbnail`/`get_metadata` raise `ValueError` on missing file or
unsupported suffix, `RuntimeError` on processing failure. `info()`/`health()`
are the standard `BaseService` methods (health is always UP).

Handlers:
- `OpenSlideHandler` (`_openslide_handler.py`, `from_file()` classmethod) — used
  by `Service` for ALL thumbnail/metadata work, including `.dcm` (OpenSlide reads
  DICOM WSI).
- `PydicomHandler` (`_pydicom_handler.py`, note the casing, `from_file()`
  classmethod) — used ONLY by the `dicom` CLI subcommands, not by `Service`.

There is no handler ABC, no `get_handler()`, no `is_supported_format()`, no
`get_tile()`, no `UnsupportedFormatError`.

## CLI (`_cli.py`)

- `wsi inspect PATH` — print format, dimensions, MPP, and per-level structure via
  `Service.get_metadata`.
- `wsi dicom inspect PATH [--verbose] [--summary] [--wsi-only]` — walk DICOM
  study/slide/series hierarchy via `PydicomHandler`.
- `wsi dicom geojson_import DICOM_PATH GEOJSON_PATH` — write GeoJSON polygons/points
  into a DICOM ANN instance.

The two `dicom` subcommands require `highdicom`, which is unavailable on Python
3.14+ (`_cli.py` gates via `_check_highdicom_available()` and exits 1 with a
"run with 3.13" message). `wsi inspect` and everything in `Service` work on all
supported Python versions.

## Metadata shape

`get_metadata` returns a NESTED dict built in `OpenSlideHandler.get_metadata`.
Key paths a caller relies on (see `_cli.py inspect` for real usage):
`metadata["format"]`, `["file"]["path"|"size"|"size_human"]`,
`["dimensions"]["width"|"height"]`, `["resolution"]["mpp_x"|"mpp_y"|...]`,
`["levels"]["count"]` and `["levels"]["data"]` (list of per-level dicts, each
with `index`, `dimensions`, `downsample`, `resolution`, `tile.grid`).
Optional keys: `properties.image` (parsed libvips XML), `vendor`,
`associated_images`, `generator`. Full construction is in `_openslide_handler.py`
— read it there rather than trusting a copy here.

## Behaviour worth knowing

- **Thumbnails are a fixed 256×256** (`slide.get_thumbnail((256, 256))`); there is
  no size parameter. `max_safe_dimension` (default `DEFAULT_MAX_SAFE_DIMENSION =
  4096`) is an incomplete-pyramid guard: if the SMALLEST pyramid level still
  exceeds it, `get_thumbnail` raises `RuntimeError` rather than blow up memory.
- `get_tiff_as_jpg` only accepts URLs starting with `http://localhost` or
  `https://` (rejects others with `ValueError`); converts to RGB, JPEG quality 90.
- `get_wsi_files_to_process`: for `.dcm` it delegates to `select_dicom_files`
  (filtering below); for every other extension it just `path.glob("**/*{ext}")`
  with no filtering.

## DICOM file selection (`_utils.select_dicom_files`, ~234-310)

The real value-add. A DICOM WSI directory contains many `.dcm` files —
pyramid levels, thumbnails, labels, segmentations, annotations. This picks only
the files worth handing to OpenSlide (one highest-resolution file per pyramid),
since OpenSlide finds the sibling levels itself.

Pipeline per `**/*.dcm`:
1. Keep only `SOPClassUID == "1.2.840.10008.5.1.4.1.1.77.1.6"` (VL Whole Slide
   Microscopy Image Storage); everything else is skipped.
2. If `ImageType` has ≥3 values, require value 3 == `VOLUME` (drops THUMBNAIL /
   LABEL / OVERVIEW). Missing ImageType[2] → logged, treated as standalone.
3. Group files that have a `PyramidUID` by that UID, recording
   `TotalPixelMatrixRows`/`Columns`. Files without `PyramidUID` are kept as
   standalone immediately.
4. `_find_highest_resolution_files`: per pyramid group keep the max
   rows×cols file; single-file groups kept as-is.

Gotchas the signature won't tell you:
- Any read error or missing attribute → `continue` (silently skipped, DEBUG log).
  A file with a `PyramidUID` but missing `TotalPixelMatrix*` raises inside the
  try and is therefore SKIPPED entirely — not kept as standalone.
- Depends only on `pydicom` (not `highdicom`), so it runs on Python 3.14+.

`PydicomHandler._get_files_to_process` also calls `select_dicom_files` when
`wsi_only=True`; otherwise it uses `rglob("*.dcm")`.

## GUI (`_gui.py`)

`PageBuilder` (a `BasePageBuilder`) registers two FastAPI routes on the NiceGUI
app: `GET /thumbnail?source=...` (serves PNG via `get_thumbnail_bytes`) and
`GET /tiff?url=...` (serves JPEG via `get_tiff_as_jpg`). Both redirect to
`/wsi_assets/fallback.png` on `ValueError`/`RuntimeError`. No viewer, no gallery.
Only imported when `nicegui` is installed (`__init__.py` `find_spec` gate).

## Dependencies

See `pyproject.toml` for versions (`openslide-python`, `pydicom`, `highdicom`,
`Pillow`, `defusedxml`, `shapely`, `humanize`). `highdicom` is the only
Python-3.14-incompatible one and is needed just for the `dicom` CLI subcommands.
