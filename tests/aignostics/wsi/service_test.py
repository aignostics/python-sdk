"""Tests of the wsi service and it's endpoints."""

import contextlib
import http.server
import os
import threading
from collections.abc import Callable
from io import BytesIO
from pathlib import Path

import pydicom
import pytest
from fastapi.testclient import TestClient
from nicegui import app
from nicegui.testing import User
from PIL import Image

from aignostics.wsi import Service as WSIService

CONTENT_LENGTH_FALLBACK = 32066  # Fallback image size in bytes


@pytest.mark.integration
def test_serve_thumbnail_fails_on_missing_file(user: User, record_property) -> None:
    """Test that the thumbnail fails on missing file."""
    record_property("tested-item-id", "SPEC-WSI-SERVICE")
    client = TestClient(app)

    test_dir = Path(__file__).parent
    resources_dir = test_dir.parent.parent / "resources"
    test_file_path = resources_dir / "not-found.dcm"

    response = client.get(f"/thumbnail?source={test_file_path.absolute()}")
    assert response.status_code == 200
    assert int(response.headers["Content-Length"]) == CONTENT_LENGTH_FALLBACK


@pytest.mark.integration
def test_serve_thumbnail_fails_on_unsupported_filetype(user: User, record_property) -> None:
    """Test that the thumbnail falls back on unsupported_filetype."""
    record_property("tested-item-id", "SPEC-WSI-SERVICE")
    client = TestClient(app)

    test_dir = Path(__file__).parent
    resources_dir = test_dir.parent.parent / "resources"
    test_file_path = resources_dir / "unsupported.any"

    response = client.get(f"/thumbnail?source={test_file_path.absolute()}")
    assert response.status_code == 200
    assert int(response.headers["Content-Length"]) == CONTENT_LENGTH_FALLBACK


@pytest.mark.integration
def test_serve_thumbnail_for_dicom_thumbnail(user: User, silent_logging, record_property) -> None:
    """Test that the thumbnail route works for non-pyramidal dicom thumbnail file."""
    record_property("tested-item-id", "SPEC-WSI-SERVICE")
    client = TestClient(app)

    test_dir = Path(__file__).parent
    resources_dir = test_dir.parent.parent / "resources"
    test_file_path = resources_dir / "sm-thumbnail.dcm"

    response = client.get(f"/thumbnail?source={test_file_path.absolute()}")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"

    content = response.content
    image = Image.open(BytesIO(content))
    assert image.format == "PNG"
    assert image.width > 0
    assert image.height > 0


@pytest.mark.integration
def test_serve_thumbnail_for_dicom_pyramidal_small(user: User, record_property) -> None:
    """Test that the thumbnail route works for small pyramidal dicom file."""
    record_property("tested-item-id", "SPEC-WSI-SERVICE")
    client = TestClient(app)

    test_dir = Path(__file__).parent
    resources_dir = test_dir.parent.parent / "resources" / "run"
    test_file_path = resources_dir / "small-pyramidal.dcm"

    response = client.get(f"/thumbnail?source={test_file_path.absolute()}")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"

    content = response.content
    image = Image.open(BytesIO(content))
    assert image.format == "PNG"
    assert image.width > 0
    assert image.height > 0


@pytest.mark.integration
def test_serve_thumbnail_for_tiff(user: User, record_property) -> None:
    """Test that the thumbnail route works for dicom file."""
    record_property("tested-item-id", "SPEC-WSI-SERVICE")
    client = TestClient(app)

    test_dir = Path(__file__).parent
    resources_dir = test_dir.parent.parent / "resources"
    test_file_path = resources_dir / "single-channel-ome.tiff"

    response = client.get(f"/thumbnail?source={test_file_path.absolute()}")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"

    content = response.content
    image = Image.open(BytesIO(content))
    assert image.format == "PNG"
    assert image.width > 0
    assert image.height > 0


@pytest.mark.integration
def test_serve_thumbnail_fails_on_incomplete_pyramid(user: User, silent_logging, record_property) -> None:
    """Test that thumbnail generation fails gracefully for DICOM with incomplete pyramid.

    The small-pyramidal.dcm test file has only 1 pyramid level at 2054x1529 pixels,
    with no smaller resolution levels available. By setting max_safe_dimension=1024
    via query parameter, we simulate the condition where the smallest available pyramid
    level is too large for safe thumbnail generation, which would normally cause OOM errors.
    """
    record_property("tested-item-id", "SPEC-WSI-SERVICE")

    client = TestClient(app)

    test_dir = Path(__file__).parent
    resources_dir = test_dir.parent.parent / "resources" / "run"
    test_file_path = resources_dir / "small-pyramidal.dcm"

    # Use low max_safe_dimension (1024) to trigger incomplete pyramid detection
    # The file has dimensions 2054x1529, which exceeds the threshold
    response = client.get(f"/thumbnail?source={test_file_path.absolute()}&max_safe_dimension=1024")

    # Should return 200 with fallback image (not crash with 500 or OOM)
    assert response.status_code == 200
    assert int(response.headers["Content-Length"]) == CONTENT_LENGTH_FALLBACK


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_serve_tiff_to_jpeg_fails_on_broken_url(user: User, record_property) -> None:
    """Test that the tiff route serves the expected jpeg.

    - Spin up local webserver serving tests/resources/single-channel-ome.tiff
    - Open the tiff and check that the response is a valid jpeg

    """
    record_property("tested-item-id", "SPEC-WSI-SERVICE")
    client = TestClient(app)

    response = client.get("/tiff?url=bla")
    assert response.status_code == 200
    assert int(response.headers["Content-Length"]) == CONTENT_LENGTH_FALLBACK


@contextlib.contextmanager
def _local_http_server(directory: Path) -> str:
    """Create a local HTTP server to serve test files.

    Args:
        directory: Directory to serve files from

    Yields:
        URL base for the server
    """

    class TestHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, directory=str(directory), **kwargs)

        def log_message(self, format_str, *args):
            # Suppress log messages
            pass

    server = http.server.HTTPServer(("localhost", 0), TestHTTPRequestHandler)
    server_port = server.server_port
    base_url = f"http://localhost:{server_port}"

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    try:
        yield base_url
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=1.0)
        if server_thread.is_alive():
            print("Warning: Server thread did not terminate within timeout")


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_serve_tiff_to_jpeg_serves(user: User, silent_logging, record_property) -> None:
    """Test that the tiff route serves the expected jpeg.

    - Spin up local webserver serving tests/resources/single-channel-ome.tiff
    - Open the tiff and check that the response is a valid jpeg

    """
    record_property("tested-item-id", "SPEC-WSI-SERVICE")
    client = TestClient(app)

    test_dir = Path(__file__).parent
    resources_dir = test_dir.parent.parent / "resources"
    test_file_path = resources_dir / "single-channel-ome.tiff"
    assert test_file_path.exists(), f"Test file not found: {test_file_path}"

    with _local_http_server(resources_dir) as base_url:
        test_file_url = f"{base_url}/single-channel-ome.tiff"
        response = client.get(f"/tiff?url={test_file_url}")

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/jpeg"

    content = response.content
    image = Image.open(BytesIO(content))
    assert image.format == "JPEG"
    assert image.width > 0
    assert image.height > 0


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_serve_tiff_to_jpeg_fails_on_broken_tiff(user: User, tmpdir, record_property) -> None:
    """Test that the tiff route falls back as expected on broken tiff.

    - Spin up local webserver serving 4711 random bytes
    - Open the tiff and check the response

    """
    record_property("tested-item-id", "SPEC-WSI-SERVICE")
    client = TestClient(app)

    random_file_path = Path(tmpdir) / "broken.tiff"
    random_bytes = os.urandom(4711)
    random_file_path.write_bytes(random_bytes)

    with _local_http_server(tmpdir) as base_url:
        test_file_url = f"{base_url}/broken.tiff"
        response = client.get(f"/tiff?url={test_file_url}")

    assert response.status_code == 200
    assert int(response.headers["Content-Length"]) == CONTENT_LENGTH_FALLBACK


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_serve_tiff_to_jpeg_fails_on_tiff_not_found(user: User, tmpdir, record_property) -> None:
    """Test that the tiff route falls back as expected on tiff not found.

    - Spin up local webserver
    - Open the unavailable tiff and check the response

    """
    record_property("tested-item-id", "SPEC-WSI-SERVICE")

    client = TestClient(app)

    random_file_path = Path(tmpdir) / "broken.tiff"
    random_bytes = os.urandom(4711)
    random_file_path.write_bytes(random_bytes)

    with _local_http_server(tmpdir) as base_url:
        test_file_url = f"{base_url}/not-found.tiff"
        response = client.get(f"/tiff?url={test_file_url}")

    assert response.status_code == 200
    assert int(response.headers["Content-Length"]) == CONTENT_LENGTH_FALLBACK


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_serve_tiff_to_jpeg_fails_on_tiff_url_broken(user: User, record_property) -> None:
    """Test that the tiff route falls back as expected on invalid url as arg.

    - Open the broken url and check the response

    """
    record_property("tested-item-id", "SPEC-WSI-SERVICE")

    client = TestClient(app)

    response = client.get("/tiff?url=https://")

    assert response.status_code == 200
    assert int(response.headers["Content-Length"]) == CONTENT_LENGTH_FALLBACK


@pytest.fixture
def dicom_factory() -> Callable[..., pydicom.Dataset]:
    """Factory fixture for creating DICOM datasets with custom parameters.

    The nested function returns a factory that lets us create multiple DICOMs
    with different parameters in each test (e.g., different pyramid UIDs,
    resolutions, and image types).
    """

    def _create_dicom(
        pyramid_uid: str | None,
        rows: int,
        cols: int,
        sop_class_uid: str = "1.2.840.10008.5.1.4.1.1.77.1.6",  # VL WSI by default
        image_type: list[str] | None = None,
    ) -> pydicom.Dataset:
        """Create a minimal but valid DICOM dataset for WSI.

        Args:
            pyramid_uid: The pyramid UID (None for standalone images)
            rows: Total image rows (TotalPixelMatrixRows) for the full WSI
            cols: Total image columns (TotalPixelMatrixColumns) for the full WSI
            sop_class_uid: SOP Class UID (defaults to VL WSI)
            image_type: Optional ImageType attribute

        Returns:
            A valid pydicom Dataset for whole slide imaging
        """
        ds = pydicom.Dataset()

        # File Meta Information
        ds.file_meta = pydicom.Dataset()
        ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        ds.file_meta.MediaStorageSOPClassUID = sop_class_uid
        ds.file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()

        # Required DICOM attributes
        ds.SOPInstanceUID = pydicom.uid.generate_uid()
        ds.SOPClassUID = sop_class_uid
        ds.StudyInstanceUID = pydicom.uid.generate_uid()
        ds.SeriesInstanceUID = pydicom.uid.generate_uid()
        ds.Modality = "SM"

        # Tile dimensions (typically 256x256 for WSI)
        ds.Rows = 256
        ds.Columns = 256

        # CRITICAL: Total image dimensions for whole slide imaging
        # These represent the full image size and are what differentiate pyramid levels
        ds.TotalPixelMatrixRows = rows
        ds.TotalPixelMatrixColumns = cols

        # Add PyramidUID if provided (optional for standalone images)
        if pyramid_uid:
            ds.PyramidUID = pyramid_uid

        # Add ImageType if provided
        if image_type:
            ds.ImageType = image_type

        return ds

    return _create_dicom


@pytest.mark.unit
def test_get_wsi_files_to_process_dicom_multi_file_pyramid(
    tmp_path: Path,
    dicom_factory: Callable[..., pydicom.Dataset],
) -> None:
    """Test service filters multi-file DICOM pyramid to highest resolution only."""
    pyramid_uid = "1.2.3.4.5"

    # Create low resolution (should be excluded)
    ds_low = dicom_factory(pyramid_uid, 512, 512, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file_low = tmp_path / "test_low.dcm"
    ds_low.save_as(dcm_file_low, write_like_original=False)

    # Create high resolution (should be kept)
    ds_high = dicom_factory(pyramid_uid, 2048, 2048, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file_high = tmp_path / "test_high.dcm"
    ds_high.save_as(dcm_file_high, write_like_original=False)

    # Get filtered files
    files = list(WSIService.get_wsi_files_to_process(tmp_path, ".dcm"))

    # Should include only highest resolution
    assert len(files) == 1
    assert dcm_file_high in files
    assert dcm_file_low not in files


@pytest.mark.unit
def test_get_wsi_files_to_process_dicom_excludes_thumbnails(
    tmp_path: Path,
    dicom_factory: Callable[..., pydicom.Dataset],
) -> None:
    """Test service excludes DICOM thumbnail images."""
    from aignostics.wsi import Service as WSIService

    # Create thumbnail (should be excluded)
    ds_thumb = dicom_factory(
        "1.2.3.4.5",
        256,
        256,
        image_type=["DERIVED", "PRIMARY", "THUMBNAIL"],
    )
    dcm_file_thumb = tmp_path / "thumbnail.dcm"
    ds_thumb.save_as(dcm_file_thumb, write_like_original=False)

    # Create volume image (should be kept)
    ds_volume = dicom_factory(
        "1.2.3.4.5",
        1024,
        1024,
        image_type=["DERIVED", "PRIMARY", "VOLUME"],
    )
    dcm_file_volume = tmp_path / "volume.dcm"
    ds_volume.save_as(dcm_file_volume, write_like_original=False)

    files = list(WSIService.get_wsi_files_to_process(tmp_path, ".dcm"))

    assert len(files) == 1
    assert dcm_file_volume in files
    assert dcm_file_thumb not in files


@pytest.mark.unit
def test_get_wsi_files_to_process_dicom_mixed_scenario(
    tmp_path: Path,
    dicom_factory: Callable[..., pydicom.Dataset],
) -> None:
    """Test service handles complex scenario with multiple pyramids and file types."""
    from aignostics.wsi import Service as WSIService

    # Pyramid 1: 2 levels (keep highest only)
    ds1_low = dicom_factory("pyramid1", 512, 512, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file1_low = tmp_path / "p1_low.dcm"
    ds1_low.save_as(dcm_file1_low, write_like_original=False)

    ds1_high = dicom_factory("pyramid1", 2048, 2048, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file1_high = tmp_path / "p1_high.dcm"
    ds1_high.save_as(dcm_file1_high, write_like_original=False)

    # Thumbnail file (exclude)
    ds_thumb = dicom_factory("pyramid1", 256, 256, image_type=["DERIVED", "PRIMARY", "THUMBNAIL"])
    dcm_file_thumb = tmp_path / "p1_thumb.dcm"
    ds_thumb.save_as(dcm_file_thumb, write_like_original=False)

    # Segmentation file (exclude by SOPClassUID)
    ds_seg = dicom_factory("pyramid1", 2048, 2048, sop_class_uid="1.2.840.10008.5.1.4.1.1.66.4")
    dcm_file_seg = tmp_path / "seg.dcm"
    ds_seg.save_as(dcm_file_seg, write_like_original=False)

    # Standalone WSI (keep)
    ds_standalone = dicom_factory(None, 1024, 1024, image_type=["DERIVED", "PRIMARY", "VOLUME"])
    dcm_file_standalone = tmp_path / "standalone.dcm"
    ds_standalone.save_as(dcm_file_standalone, write_like_original=False)

    files = list(WSIService.get_wsi_files_to_process(tmp_path, ".dcm"))

    # Should include: high-res from pyramid1, standalone
    assert len(files) == 2
    assert dcm_file1_high in files
    assert dcm_file_standalone in files

    # Should exclude: low-res, thumbnail, segmentation
    assert dcm_file1_low not in files
    assert dcm_file_thumb not in files
    assert dcm_file_seg not in files


@pytest.mark.unit
def test_get_wsi_files_to_process_non_dicom_passthrough(tmp_path: Path) -> None:
    """Test service passes through non-DICOM files without filtering."""
    from aignostics.wsi import Service as WSIService

    # Create some TIFF files
    tiff1 = tmp_path / "image1.tiff"
    tiff2 = tmp_path / "image2.tiff"
    tiff1.touch()
    tiff2.touch()

    # Non-DICOM files should all be returned
    files = list(WSIService.get_wsi_files_to_process(tmp_path, ".tiff"))

    assert len(files) == 2
    assert tiff1 in files
    assert tiff2 in files
