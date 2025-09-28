# CLAUDE.md - WSI Module

This file provides comprehensive guidance to Claude Code and human engineers when working with the `wsi` (Whole Slide Image) module in this repository.

## Module Overview

The WSI module provides comprehensive support for medical imaging files, particularly whole slide images used in computational pathology, handling multiple formats with high-performance processing capabilities.

### Core Responsibilities

- **Multi-format Support**: DICOM, TIFF, SVS, NDPI, and other medical imaging formats
- **Thumbnail Generation**: Fast preview image creation at multiple resolutions
- **Metadata Extraction**: Image properties, medical metadata, and DICOM tags
- **Format Validation**: File type detection and compatibility checking
- **Image Processing**: Tile extraction, region of interest handling

### User Interfaces

**CLI Commands (`_cli.py`):**

- `wsi inspect` - Display WSI file metadata and properties
- `wsi dicom-inspect` - Inspect DICOM-specific metadata
- `wsi dicom-geojson-import` - Import GeoJSON annotations to DICOM

**GUI Component (`_gui.py`):**

- WSI viewer with zoom/pan controls
- Metadata explorer interface
- Thumbnail gallery
- Format compatibility checker

**Service Layer (`_service.py`):**

Core WSI operations:
- Thumbnail generation with PIL
- Format detection and validation
- Metadata extraction
- Handler dispatch (OpenSlide vs PyDICOM)
- Memory-efficient tile processing

## Architecture & Design Patterns

### Handler Pattern

```python
# Format-specific handlers
class WSIHandler(ABC):
    @abstractmethod
    def open(self, path: Path) -> WSIFile:
        pass

    @abstractmethod
    def get_thumbnail(self, wsi: WSIFile, size: tuple[int, int]) -> Image:
        pass

    @abstractmethod
    def get_metadata(self, wsi: WSIFile) -> dict:
        pass

# OpenSlide handler for .svs, .tiff, .ndpi
class OpenSlideHandler(WSIHandler):
    def open(self, path: Path) -> OpenSlide:
        return openslide.OpenSlide(str(path))

# PyDICOM handler for DICOM files
class PyDICOMHandler(WSIHandler):
    def open(self, path: Path) -> Dataset:
        return pydicom.dcmread(str(path))
```

### Format Detection

```python
WSI_SUPPORTED_FILE_EXTENSIONS = {
    ".svs",    # Aperio
    ".tiff",   # Generic TIFF
    ".tif",    # Generic TIFF
    ".ndpi",   # Hamamatsu
    ".vms",    # Hamamatsu
    ".vmu",    # Hamamatsu
    ".scn",    # Leica
    ".mrxs",   # MIRAX
    ".bif",    # Ventana
    ".dcm",    # DICOM
    ".dicom"   # DICOM
}

def get_handler(file_path: Path) -> WSIHandler:
    """Get appropriate handler based on file extension."""
    ext = file_path.suffix.lower()

    if ext in {".dcm", ".dicom"}:
        return PyDICOMHandler()
    elif ext in WSI_SUPPORTED_FILE_EXTENSIONS:
        return OpenSlideHandler()
    else:
        raise UnsupportedFormatError(f"Unsupported format: {ext}")
```

## Critical Implementation Details

### Thumbnail Generation

**Memory-Efficient Processing:**

```python
def get_thumbnail(self, wsi_path: Path, size: tuple[int, int] = (512, 512)) -> Image:
    """Generate thumbnail with memory efficiency."""

    handler = self.get_handler(wsi_path)

    # OpenSlide has built-in thumbnail
    if isinstance(handler, OpenSlideHandler):
        slide = handler.open(wsi_path)
        thumbnail = slide.get_thumbnail(size)

    # DICOM needs custom processing
    elif isinstance(handler, PyDICOMHandler):
        ds = handler.open(wsi_path)
        pixel_array = ds.pixel_array

        # Handle multi-frame DICOM
        if len(pixel_array.shape) == 3:
            # Use middle frame for thumbnail
            frame = pixel_array[len(pixel_array) // 2]
        else:
            frame = pixel_array

        # Create PIL Image and resize
        image = Image.fromarray(frame)
        image.thumbnail(size, Image.Resampling.LANCZOS)
        thumbnail = image

    return thumbnail
```

### Metadata Extraction

**Comprehensive Metadata Collection:**

```python
def get_metadata(self, wsi_path: Path) -> dict:
    """Extract all available metadata."""

    handler = self.get_handler(wsi_path)
    metadata = {
        "file_path": str(wsi_path),
        "file_size": wsi_path.stat().st_size,
        "format": wsi_path.suffix.lower()
    }

    if isinstance(handler, OpenSlideHandler):
        slide = handler.open(wsi_path)
        metadata.update({
            "dimensions": slide.dimensions,
            "level_count": slide.level_count,
            "level_dimensions": slide.level_dimensions,
            "level_downsamples": slide.level_downsamples,
            "properties": dict(slide.properties),
            "vendor": slide.properties.get("openslide.vendor", "Unknown")
        })

    elif isinstance(handler, PyDICOMHandler):
        ds = handler.open(wsi_path)
        metadata.update({
            "patient_name": str(ds.get("PatientName", "")),
            "study_date": str(ds.get("StudyDate", "")),
            "modality": str(ds.get("Modality", "")),
            "rows": ds.get("Rows", 0),
            "columns": ds.get("Columns", 0),
            "number_of_frames": ds.get("NumberOfFrames", 1),
            "photometric_interpretation": str(ds.get("PhotometricInterpretation", ""))
        })

    return metadata
```

### Tile Processing

**Region of Interest Extraction:**

```python
def get_tile(
    self,
    wsi_path: Path,
    x: int,
    y: int,
    width: int,
    height: int,
    level: int = 0
) -> Image:
    """Extract tile from WSI at specified coordinates."""

    handler = self.get_handler(wsi_path)

    if isinstance(handler, OpenSlideHandler):
        slide = handler.open(wsi_path)

        # Convert to level 0 coordinates
        downsample = slide.level_downsamples[level]
        x_0 = int(x * downsample)
        y_0 = int(y * downsample)

        # Read region
        tile = slide.read_region((x_0, y_0), level, (width, height))

    elif isinstance(handler, PyDICOMHandler):
        raise NotImplementedError("Tile extraction not supported for DICOM")

    return tile
```

## Usage Patterns

### Basic WSI Operations

```python
from aignostics.wsi import Service
from pathlib import Path

service = Service()

# Get WSI metadata
wsi_path = Path("slide.svs")
metadata = service.get_metadata(wsi_path)
print(f"Dimensions: {metadata['dimensions']}")
print(f"Levels: {metadata['level_count']}")

# Generate thumbnail
thumbnail = service.get_thumbnail(wsi_path, size=(256, 256))
thumbnail.save("preview.jpg")

# Validate format
if service.is_supported_format(wsi_path):
    print("Format supported")
```

### Advanced Processing

```python
# Extract specific region
tile = service.get_tile(
    wsi_path,
    x=1000, y=2000,
    width=512, height=512,
    level=0
)
tile.save("tile.jpg")

# Process multiple WSI files
wsi_files = Path("slides").glob("*.svs")
for wsi in wsi_files:
    try:
        thumbnail = service.get_thumbnail(wsi)
        thumbnail.save(f"thumbnails/{wsi.stem}.jpg")
    except Exception as e:
        logger.error(f"Failed to process {wsi}: {e}")
```

### CLI Usage Examples

```bash
# Inspect WSI file
aignostics wsi inspect slide.svs

# Inspect DICOM metadata
aignostics wsi dicom-inspect scan.dcm

# Import GeoJSON annotations
aignostics wsi dicom-geojson-import \
    --dicom-file scan.dcm \
    --geojson-file annotations.json \
    --output annotated.dcm
```

## Dependencies & Integration

### Internal Dependencies

- `utils` - Logging, base service infrastructure
- `application` - WSI validation before processing
- `qupath` - WSI format compatibility checks

### External Dependencies

- `openslide-python` - Core WSI reading functionality
- `Pillow` - Image processing and thumbnail generation
- `pydicom` - DICOM file handling
- `numpy` - Array manipulation for pixel data

### Format Support Matrix

| Format | Extension | Handler | Full Support | Thumbnail | Tiles |
|--------|-----------|---------|--------------|-----------|-------|
| Aperio | .svs | OpenSlide | ✅ | ✅ | ✅ |
| Generic TIFF | .tiff/.tif | OpenSlide | ✅ | ✅ | ✅ |
| Hamamatsu | .ndpi | OpenSlide | ✅ | ✅ | ✅ |
| Leica | .scn | OpenSlide | ✅ | ✅ | ✅ |
| MIRAX | .mrxs | OpenSlide | ✅ | ✅ | ✅ |
| Ventana | .bif | OpenSlide | Partial | ✅ | ✅ |
| DICOM | .dcm/.dicom | PyDICOM | ✅ | ✅ | ❌ |

## Operational Requirements

### Memory Management

- **Thumbnail generation**: ~100MB per image
- **Tile extraction**: ~50MB per tile
- **Full slide loading**: Can exceed 10GB for large slides
- **Recommended RAM**: 8GB minimum, 16GB+ for production

### Performance Optimization

```python
# Use level appropriate for display
def get_display_image(wsi_path: Path, max_dimension: int = 2048) -> Image:
    """Get image at appropriate level for display."""

    slide = openslide.OpenSlide(str(wsi_path))

    # Find best level
    for level, dimensions in enumerate(slide.level_dimensions):
        if max(dimensions) <= max_dimension:
            return slide.read_region((0, 0), level, dimensions)

    # Use highest level if all too large
    level = slide.level_count - 1
    return slide.read_region((0, 0), level, slide.level_dimensions[level])
```

## Common Pitfalls & Solutions

### OpenSlide Installation Issues

**Problem:** OpenSlide library not found

**Solution:**
```bash
# macOS
brew install openslide

# Ubuntu/Debian
sudo apt-get install openslide-tools

# Windows
# Download from https://openslide.org/download/
```

### Memory Overflow with Large Images

**Problem:** OutOfMemoryError when processing large WSI

**Solution:**
```python
def process_wsi_in_tiles(wsi_path: Path, tile_size: int = 1024):
    """Process WSI in memory-efficient tiles."""

    slide = openslide.OpenSlide(str(wsi_path))
    width, height = slide.dimensions

    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            tile = slide.read_region((x, y), 0, (tile_size, tile_size))
            # Process tile
            process_tile(tile)
            # Garbage collect
            del tile
```

### Format Detection Failures

**Problem:** File format not recognized

**Solution:**
```python
def detect_format_by_content(file_path: Path) -> str:
    """Detect format by file content."""

    with open(file_path, "rb") as f:
        header = f.read(132)

    # Check for DICOM
    if b"DICM" in header[128:132]:
        return "dicom"

    # Check for TIFF
    if header[:2] in [b"II", b"MM"]:
        return "tiff"

    # Try OpenSlide
    try:
        slide = openslide.OpenSlide(str(file_path))
        return "openslide"
    except:
        return "unknown"
```

## Testing Strategies

### Unit Testing

```python
@pytest.fixture
def sample_wsi():
    """Provide sample WSI for testing."""
    return Path("tests/fixtures/sample.svs")

def test_thumbnail_generation(sample_wsi):
    """Test thumbnail generation."""
    service = Service()
    thumbnail = service.get_thumbnail(sample_wsi, size=(256, 256))

    assert thumbnail.size == (256, 256)
    assert thumbnail.mode in ["RGB", "RGBA"]

def test_metadata_extraction(sample_wsi):
    """Test metadata extraction."""
    service = Service()
    metadata = service.get_metadata(sample_wsi)

    assert "dimensions" in metadata
    assert "level_count" in metadata
    assert metadata["format"] == ".svs"
```

### Integration Testing

```python
@pytest.mark.integration
def test_dicom_processing():
    """Test DICOM file processing."""
    service = Service()
    dicom_path = Path("tests/fixtures/sample.dcm")

    # Test metadata
    metadata = service.get_metadata(dicom_path)
    assert metadata["modality"] in ["SM", "WSI"]

    # Test thumbnail
    thumbnail = service.get_thumbnail(dicom_path)
    assert thumbnail is not None
```

## Development Guidelines

### Adding New Format Support

1. Create new handler class inheriting from `WSIHandler`
2. Implement required methods (open, get_thumbnail, get_metadata)
3. Register extension in `WSI_SUPPORTED_FILE_EXTENSIONS`
4. Update format detection logic
5. Add tests for new format

### Performance Profiling

```python
import cProfile
import pstats

def profile_wsi_processing():
    """Profile WSI processing performance."""

    profiler = cProfile.Profile()
    profiler.enable()

    # Process WSI
    service = Service()
    service.get_thumbnail(Path("large_slide.svs"))

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
```

---

*This module provides comprehensive whole slide image processing capabilities for digital pathology workflows in the Aignostics Platform.*
