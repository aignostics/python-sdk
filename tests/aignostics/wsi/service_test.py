"""Tests of the wsi service and it's endpoints."""

import contextlib
import http.server
import os
import threading
from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from nicegui import app
from nicegui.testing import User
from PIL import Image

from aignostics.utils import gui_register_pages

CONTENT_LENGTH_FALLBACK = 32066  # Fallback image size in bytes


def test_serve_thumbnail_fails_on_missing_file(user: User) -> None:
    """Test that the thumbnail falls back on missing file."""
    gui_register_pages()
    client = TestClient(app)

    test_dir = Path(__file__).parent
    resources_dir = test_dir.parent.parent / "resources"
    test_file_path = resources_dir / "not-found.dcm"

    response = client.get(f"/thumbnail?source={test_file_path.absolute()}")
    assert response.status_code == 200
    assert int(response.headers["Content-Length"]) == CONTENT_LENGTH_FALLBACK


def test_serve_thumbnail_fails_on_unsupported_filetype(user: User) -> None:
    """Test that the thumbnail falls back on unsupported_filetype."""
    gui_register_pages()
    client = TestClient(app)

    test_dir = Path(__file__).parent
    resources_dir = test_dir.parent.parent / "resources"
    test_file_path = resources_dir / "unsupported.any"

    response = client.get(f"/thumbnail?source={test_file_path.absolute()}")
    assert response.status_code == 200
    assert int(response.headers["Content-Length"]) == CONTENT_LENGTH_FALLBACK


def test_serve_thumbnail_for_dicom_thumbnail(user: User) -> None:
    """Test that the thumbnail route works for non-pyramidal dicom thumbnail file."""
    gui_register_pages()
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


def test_serve_thumbnail_for_dicom_pyramidal_small(user: User) -> None:
    """Test that the thumbnail route works for small pyramidal dicom file."""
    gui_register_pages()
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


def test_serve_thumbnail_for_tiff(user: User) -> None:
    """Test that the thumbnail route works for dicom file."""
    gui_register_pages()
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


def test_serve_tiff_to_jpeg_fails_on_broken_url(user: User) -> None:
    """Test that the tiff route serves the expected jpeg.

    - Spin up local webserver serving tests/resources/single-channel-ome.tiff
    - Open the tiff and check that the response is a valid jpeg

    """
    gui_register_pages()
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


def test_serve_tiff_to_jpeg(user: User) -> None:
    """Test that the tiff route serves the expected jpeg.

    - Spin up local webserver serving tests/resources/single-channel-ome.tiff
    - Open the tiff and check that the response is a valid jpeg

    """
    gui_register_pages()
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


def test_serve_tiff_to_jpeg_fails_on_broken_tiff(user: User, tmpdir) -> None:
    """Test that the tiff route falls back as expected on broken tiff.

    - Spin up local webserver serving 4711 random bytes
    - Open the tiff and check the response

    """
    gui_register_pages()
    client = TestClient(app)

    random_file_path = Path(tmpdir) / "broken.tiff"
    random_bytes = os.urandom(4711)
    random_file_path.write_bytes(random_bytes)

    with _local_http_server(tmpdir) as base_url:
        test_file_url = f"{base_url}/broken.tiff"
        response = client.get(f"/tiff?url={test_file_url}")

    assert response.status_code == 200
    assert int(response.headers["Content-Length"]) == CONTENT_LENGTH_FALLBACK


def test_serve_tiff_to_jpeg_fails_on_tiff_not_found(user: User, tmpdir) -> None:
    """Test that the tiff route falls back as expected on tiff not found.

    - Spin up local webserver
    - Open the unavailable tiff and check the response

    """
    gui_register_pages()
    client = TestClient(app)

    random_file_path = Path(tmpdir) / "broken.tiff"
    random_bytes = os.urandom(4711)
    random_file_path.write_bytes(random_bytes)

    with _local_http_server(tmpdir) as base_url:
        test_file_url = f"{base_url}/not-found.tiff"
        response = client.get(f"/tiff?url={test_file_url}")

    assert response.status_code == 200
    assert int(response.headers["Content-Length"]) == CONTENT_LENGTH_FALLBACK


def test_serve_tiff_to_jpeg_fails_on_tiff_url_broken(user: User) -> None:
    """Test that the tiff route falls back as expected on invalid url as arg.

    - Open the broken url and check the response

    """
    gui_register_pages()
    client = TestClient(app)

    response = client.get("/tiff?url=https://")

    assert response.status_code == 200
    assert int(response.headers["Content-Length"]) == CONTENT_LENGTH_FALLBACK
