"""Tests of the bucket service."""

from typing import Any
from unittest import mock

import pytest

from aignostics.bucket._service import Service

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_page(keys: list[str]) -> dict[str, Any]:
    """Build a mock S3 ListObjectsV2 page response with the given object keys."""
    return {
        "Contents": [
            {"Key": k, "Size": 1024, "LastModified": None, "ETag": '"abc123"', "StorageClass": "STANDARD"} for k in keys
        ]
    }


def _setup_find(mock_get_s3_client: mock.MagicMock, pages: list[dict[str, Any]]) -> tuple["Service", mock.MagicMock]:
    """Wire up a Service with a mock S3 paginator returning the given pages."""
    mock_s3c = mock.MagicMock()
    mock_paginator = mock.MagicMock()
    mock_s3c.get_paginator.return_value = mock_paginator
    mock_paginator.paginate.return_value = pages
    mock_get_s3_client.return_value = mock_s3c

    service = Service()
    service.get_bucket_name = mock.MagicMock(return_value="test-bucket")  # type: ignore[method-assign]
    return service, mock_paginator


@pytest.mark.integration
@mock.patch("aignostics.bucket._service.Service._get_s3_client")
def test_create_signed_upload_url_expires_in_3600_seconds(mock_get_s3_client: mock.MagicMock) -> None:
    """Test that create_signed_upload_url calls generate_presigned_url with ExpiresIn of 3600 seconds."""
    # Arrange
    mock_s3_client = mock.MagicMock()
    mock_s3_client.generate_presigned_url.return_value = "https://example.com/signed-upload-url"
    mock_get_s3_client.return_value = mock_s3_client

    service = Service()
    service._settings = mock.MagicMock()
    service._settings.upload_signed_url_expiration_seconds = 2 * 60 * 60
    service.get_bucket_name = mock.MagicMock(return_value="test-bucket")

    # Act
    result = service.create_signed_upload_url("test-object-key")

    # Assert
    mock_s3_client.generate_presigned_url.assert_called_once_with(
        ClientMethod="put_object",
        Params={"Bucket": service.get_bucket_name(), "Key": "test-object-key"},
        ExpiresIn=2 * 60 * 60,
    )
    assert result == "https://example.com/signed-upload-url"


@pytest.mark.integration
@mock.patch("aignostics.bucket._service.Service._get_s3_client")
def test_create_signed_download_url_expires_in_7_days(mock_get_s3_client: mock.MagicMock) -> None:
    """Test that create_signed_download_url calls generate_presigned_url with ExpiresIn of 7 days (604800 seconds)."""
    # Arrange
    mock_s3_client = mock.MagicMock()
    mock_s3_client.generate_presigned_url.return_value = "https://example.com/signed-download-url"
    mock_get_s3_client.return_value = mock_s3_client

    service = Service()
    service._settings = mock.MagicMock()
    service._settings.download_signed_url_expiration_seconds = 7 * 24 * 60 * 60  # 7 days in seconds
    service.get_bucket_name = mock.MagicMock(return_value="test-bucket")

    # Act
    result = service.create_signed_download_url("test-object-key")

    # Assert
    mock_s3_client.generate_presigned_url.assert_called_once_with(
        ClientMethod="get_object",
        Params={"Bucket": service.get_bucket_name(), "Key": "test-object-key"},
        ExpiresIn=604800,  # 7 days in seconds
    )
    assert result == "https://example.com/signed-download-url"


# ---------------------------------------------------------------------------
# find() — server-side prefix optimisation
# ---------------------------------------------------------------------------


@pytest.mark.unit
@mock.patch("aignostics.bucket._service.Service._get_s3_client")
def test_find_exact_key_passes_prefix_to_paginator(mock_get_s3_client: mock.MagicMock) -> None:
    """find() with a single exact key passes that key as the S3 Prefix parameter."""
    path_to_file = "path/to/file.txt"
    service, mock_paginator = _setup_find(
        mock_get_s3_client,
        [_make_page([path_to_file])],
    )

    result = service.find([path_to_file], what_is_key=True)

    mock_paginator.paginate.assert_called_once_with(Bucket="test-bucket", Prefix=path_to_file)
    assert result == [path_to_file]


@pytest.mark.unit
@mock.patch("aignostics.bucket._service.Service._get_s3_client")
def test_find_multiple_exact_keys_uses_common_prefix(mock_get_s3_client: mock.MagicMock) -> None:
    """find() with multiple exact keys derives their longest common prefix for S3."""
    path_to_a = "path/to/a.txt"
    path_to_b = "path/to/b.txt"
    service, mock_paginator = _setup_find(
        mock_get_s3_client,
        [_make_page([path_to_a, path_to_b])],
    )

    result = service.find([path_to_a, path_to_b], what_is_key=True)

    mock_paginator.paginate.assert_called_once_with(Bucket="test-bucket", Prefix="path/to/")
    assert set(result) == {path_to_a, path_to_b}


@pytest.mark.unit
@mock.patch("aignostics.bucket._service.Service._get_s3_client")
def test_find_exact_keys_no_common_prefix_scans_full_bucket(mock_get_s3_client: mock.MagicMock) -> None:
    """find() with keys that share no prefix performs a full-bucket scan (no Prefix kwarg)."""
    service, mock_paginator = _setup_find(
        mock_get_s3_client,
        [_make_page(["alpha/x", "beta/y"])],
    )

    service.find(["alpha/x", "beta/y"], what_is_key=True)

    call_kwargs = mock_paginator.paginate.call_args.kwargs
    assert "Prefix" not in call_kwargs
    assert call_kwargs["Bucket"] == "test-bucket"


@pytest.mark.unit
@mock.patch("aignostics.bucket._service.Service._get_s3_client")
def test_find_regex_with_literal_prefix(mock_get_s3_client: mock.MagicMock) -> None:
    """find() extracts the literal portion of a regex pattern and passes it as Prefix."""
    service, mock_paginator = _setup_find(
        mock_get_s3_client,
        [_make_page(["runner/test/abc/result.json"])],
    )

    result = service.find(["runner/test/abc/.*"])

    mock_paginator.paginate.assert_called_once_with(Bucket="test-bucket", Prefix="runner/test/abc/")
    assert result == ["runner/test/abc/result.json"]


@pytest.mark.unit
@mock.patch("aignostics.bucket._service.Service._get_s3_client")
def test_find_regex_starting_with_metachar_scans_full_bucket(mock_get_s3_client: mock.MagicMock) -> None:
    """find() with a regex starting with a metacharacter performs a full-bucket scan."""
    service, mock_paginator = _setup_find(
        mock_get_s3_client,
        [_make_page(["special/object.txt"])],
    )

    result = service.find([".*special.*"])

    call_kwargs = mock_paginator.paginate.call_args.kwargs
    assert "Prefix" not in call_kwargs
    assert result == ["special/object.txt"]


@pytest.mark.unit
@mock.patch("aignostics.bucket._service.Service._get_s3_client")
def test_find_multiple_regex_uses_common_literal_prefix(mock_get_s3_client: mock.MagicMock) -> None:
    """find() computes the common literal prefix across multiple regex patterns."""
    service, mock_paginator = _setup_find(
        mock_get_s3_client,
        [_make_page(["path/to/a_file.txt", "path/to/b_file.txt"])],
    )

    service.find(["path/to/a.*", "path/to/b.*"])

    mock_paginator.paginate.assert_called_once_with(Bucket="test-bucket", Prefix="path/to/")


@pytest.mark.unit
@mock.patch("aignostics.bucket._service.Service._get_s3_client")
def test_find_default_none_scans_full_bucket(mock_get_s3_client: mock.MagicMock) -> None:
    """find(None) defaults to '.*' which carries no useful prefix — full-bucket scan."""
    service, mock_paginator = _setup_find(
        mock_get_s3_client,
        [_make_page(["any/object.txt"])],
    )

    service.find(None)

    call_kwargs = mock_paginator.paginate.call_args.kwargs
    assert "Prefix" not in call_kwargs
    assert call_kwargs["Bucket"] == "test-bucket"


@pytest.mark.unit
@mock.patch("aignostics.bucket._service.Service._get_s3_client")
def test_find_returns_detailed_results_when_requested(mock_get_s3_client: mock.MagicMock) -> None:
    """find() with detail=True returns dicts containing key, size, size_human, etc."""
    path_to_file = "path/to/file.txt"
    service, _ = _setup_find(
        mock_get_s3_client,
        [_make_page([path_to_file])],
    )

    result = service.find([path_to_file], what_is_key=True, detail=True)

    assert len(result) == 1
    item = result[0]
    assert isinstance(item, dict)
    assert item["key"] == path_to_file
    assert item["size"] == 1024
    assert "size_human" in item
    assert "etag" in item
    assert "storage_class" in item


@pytest.mark.unit
@mock.patch("aignostics.bucket._service.Service._get_s3_client")
def test_find_filters_correctly_with_prefix_and_extra_objects(mock_get_s3_client: mock.MagicMock) -> None:
    """Client-side filtering still excludes non-matching keys returned under the S3 prefix."""
    path_to_file = "path/to/match.txt"
    service, _ = _setup_find(
        mock_get_s3_client,
        # The mock page returns two objects under the prefix — only one matches the requested key.
        [_make_page([path_to_file, "path/to/other.txt"])],
    )

    result = service.find([path_to_file], what_is_key=True)

    assert result == [path_to_file]
