"""Tests of the notebook service and it's endpoint."""

import re

from fastapi.testclient import TestClient
from nicegui import app
from nicegui.testing import User

from aignostics.utils import gui_register_pages


def test_serve_notebook(user: User) -> None:
    """Test that the thumbnail fails on unsupported_filetype."""
    gui_register_pages()
    client = TestClient(app)

    response = client.get("/notebook/4711")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "iframe" in content
    assert "iframe src" in content
    # Look for the encoded iframe in the innerHTML property
    iframe_html = re.search(r'innerHTML":"&lt;iframe src=\\"([^"]+)\\"', content)
    assert iframe_html is not None, f"iframe src not found in response: {content}"

    # Extract the URL from the iframe src attribute
    notebook_url = iframe_html.group(1)
    assert "localhost" in notebook_url, f"localhost not found in iframe src: {notebook_url}"
    assert "run_id=4711" in notebook_url, f"run_id not found in iframe src: {notebook_url}"
