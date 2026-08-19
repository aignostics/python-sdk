"""Applications resource module for the Aignostics platform.

This module provides classes for interacting with application resources in the Aignostics API.
It includes functionality for listing applications, managing application versions,
and retrieving application version release documents.
"""

import builtins
import typing as t
from datetime import datetime
from http import HTTPStatus
from io import BytesIO
from operator import itemgetter
from pathlib import Path
from urllib.parse import quote

import requests
import semver
from aignx.codegen.exceptions import NotFoundException, ServiceException
from aignx.codegen.models import ApplicationReadResponse as Application
from aignx.codegen.models import ApplicationReadShortResponse as ApplicationSummary
from aignx.codegen.models import ApplicationVersion as VersionTuple
from aignx.codegen.models import VersionDocumentResponse as VersionDocumentData
from aignx.codegen.models import VersionReadResponse as ApplicationVersion
from pydantic import BaseModel, ConfigDict
from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from aignostics.platform._api import (
    RETRYABLE_EXCEPTIONS,
    _AuthenticatedApi,
    _AuthenticatedResource,
    _log_retry_attempt,
)
from aignostics.platform._authentication import get_token
from aignostics.platform._operation_cache import cached_operation
from aignostics.platform._settings import settings
from aignostics.platform.resources.utils import paginate
from aignostics.utils import user_agent

_DOCUMENT_DOWNLOAD_CHUNK_SIZE = 1024 * 1024  # 1 MB


class Versions(_AuthenticatedResource):
    """Resource class for managing application versions.

    Provides operations to list and retrieve application versions.
    """

    def _get_application_version_validated(
        self, application_id: str, application_version: VersionTuple | str | None
    ) -> str:
        """Validate and extract the version string from a VersionTuple or str.

        Args:
            application_id (str): The ID of the application.
            application_version (VersionTuple | str | None): The version to validate.

        Returns:
            str: The validated version string.

        Raises:
            ValueError: If the version is not a valid semver string.
            NotFoundException: If the version is None and no versions are found for the application.
        """
        # Handle version resolution and validation first (not retried)
        if application_version is None:
            application_version = self.latest(application=application_id)
            if application_version is None:
                message = f"No versions found for application '{application_id}'."
                raise NotFoundException(message)
            application_version = application_version.number
        elif isinstance(application_version, VersionTuple):
            application_version = application_version.number
        elif application_version and not semver.Version.is_valid(application_version):
            message = f"Invalid version format: '{application_version}' not compliant with semantic versioning."
            raise ValueError(message)
        return application_version

    def list(self, application: Application | str, nocache: bool = False) -> builtins.list[VersionTuple]:
        """Find all versions for a specific application.

        Retries on network and server errors.

        Args:
            application (Application | str): The application to find versions for, either object or id
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.

        Returns:
            list[VersionTuple]: List of the available application versions.

        Raises:
            aignx.codegen.exceptions.ApiException: If the API request fails.
        """
        application_id = application.application_id if isinstance(application, Application) else application

        @cached_operation(ttl=settings().application_cache_ttl, token_provider=self._api.token_provider)
        def list_with_retry(app_id: str) -> Application:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().application_retry_attempts),
                wait=wait_exponential_jitter(
                    initial=settings().application_retry_wait_min, max=settings().application_retry_wait_max
                ),
                before_sleep=_log_retry_attempt,
                reraise=True,
            )(
                lambda: self._api.read_application_by_id_v1_applications_application_id_get(
                    application_id=app_id,
                    _request_timeout=settings().application_timeout,
                    _headers={"User-Agent": user_agent()},
                )
            )

        app = list_with_retry(application_id, nocache=nocache)  # type: ignore[call-arg]
        return app.versions if app.versions is not None else []

    def details(
        self, application_id: str, application_version: VersionTuple | str | None = None, nocache: bool = False
    ) -> ApplicationVersion:
        """Retrieves details for a specific application version.

        Retries on network and server errors.

        Args:
            application_id (str): The ID of the application.
            application_version (VersionTuple | str | None): The version of the application.
                If None, the latest version will be retrieved.
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.

        Returns:
            ApplicationVersion: The version details.

        Raises:
            ValueError: If the version is not valid semver.
            NotFoundException: If the application or version is not found.
            aignx.codegen.exceptions.ApiException: If the API request fails.
        """
        application_version = self._get_application_version_validated(application_id, application_version)

        # Make the API call with retry logic and caching
        @cached_operation(ttl=settings().application_version_cache_ttl, token_provider=self._api.token_provider)
        def details_with_retry(app_id: str, app_version: str) -> ApplicationVersion:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().application_version_retry_attempts),
                wait=wait_exponential_jitter(
                    initial=settings().application_version_retry_wait_min,
                    max=settings().application_version_retry_wait_max,
                ),
                before_sleep=_log_retry_attempt,
                reraise=True,
            )(
                lambda: self._api.application_version_details_v1_applications_application_id_versions_version_get(
                    application_id=app_id,
                    version=app_version,
                    _request_timeout=settings().application_version_timeout,
                    _headers={"User-Agent": user_agent()},
                )
            )

        return details_with_retry(application_id, application_version, nocache=nocache)  # type: ignore[call-arg]

    # TODO(Helmut): Refactor given new API capabilities
    def list_sorted(self, application: Application | str, nocache: bool = False) -> builtins.list[VersionTuple]:
        """Get application versions sorted by semver, descending.

        Args:
            application (Application | str): The application to find versions for, either object or id
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.

        Returns:
            list[VersionTuple]: List of version objects sorted by semantic versioning (latest first),
                or empty list if no versions are found
        """
        versions = builtins.list(self.list(application=application, nocache=nocache))

        # If no versions available
        if not versions:
            return []

        # Extract semantic versions using proper semver parsing
        versions_with_semver = []
        for v in versions:
            try:
                parsed_version = semver.Version.parse(v.number)
                versions_with_semver.append((v, parsed_version))
            except (ValueError, AttributeError):
                # If we can't parse the version or version attribute doesn't exist, skip it
                continue

        # Sort by semantic version (semver objects have built-in comparison)
        if versions_with_semver:
            versions_with_semver.sort(key=itemgetter(1), reverse=True)
            # Return just the version objects, not the tuples
            return [item[0] for item in versions_with_semver]

        # If we couldn't parse any versions, return all versions as is
        return versions

    def latest(self, application: Application | str, nocache: bool = False) -> VersionTuple | None:
        """Get latest version.

        Args:
            application (Application | str): The application to find versions for, either object or id
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.

        Returns:
            VersionTuple | None: The latest version, or None if no versions found.
        """
        sorted_versions = self.list_sorted(application=application, nocache=nocache)
        return sorted_versions[0] if sorted_versions else None

    def documents(self, application_id: str, application_version: VersionTuple | str | None) -> "Documents":
        """Returns a Documents resource bound to the given application version.

        Args:
            application_id (str): The ID of the application (e.g. "heta").
            application_version (VersionTuple | str | None): The application version, either as a
                VersionTuple, a semantic version string (e.g. "1.0.0"), or None to use the latest version.

        Returns:
            Documents: A Documents resource bound to the (application_id, version) pair.
        """
        application_version = self._get_application_version_validated(application_id, application_version)

        return Documents(self._api, application_id=application_id, application_version=application_version)


class ApplicationVersionDocument(BaseModel):
    """Public release document attached to an application version.

    The Aignostics public API exposes only documents with ``visibility=public`` and
    ``status=uploaded``. Internal-visibility documents are not surfaced.
    """

    id: str
    name: str
    mime_type: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(populate_by_name=True, validate_assignment=True)

    @classmethod
    def from_response(cls, data: VersionDocumentData) -> "ApplicationVersionDocument":
        """Build an ApplicationVersionDocument from the codegen response model.

        Args:
            data: The codegen ``VersionDocumentResponse`` returned by the API.

        Returns:
            ApplicationVersionDocument: Wrapped, SDK-friendly Pydantic model.
        """
        return cls(
            id=data.id,
            name=data.name,
            mime_type=data.mime_type,
            created_at=data.created_at,
            updated_at=data.updated_at,
        )


class Documents:
    """Resource class for retrieving release documents attached to an application version.

    Backed by ``GET /api/v1/applications/{application_id}/versions/{version}/documents``
    and the per-document ``/{name}``, ``/{name}/file``, and ``/{name}/content`` endpoints.

    The public API exposes only documents with ``visibility=public`` and
    ``status=uploaded``. Internal-visibility documents are not surfaced.

    Document downloads do not carry a CRC32C checksum (unlike run artifacts);
    integrity is bounded by HTTPS transport and the signed-URL lifetime.
    """

    def __init__(self, api: _AuthenticatedApi, application_id: str, application_version: str | VersionTuple) -> None:
        """Initializes the Documents resource bound to an application version.

        Args:
            api (_AuthenticatedApi): The configured API client.
            application_id (str): The ID of the application (e.g. "heta").
            application_version (str | VersionTuple): The semantic version number (e.g. "1.0.0") or a VersionTuple.
        """
        self._api = api
        self.application_id = application_id
        if isinstance(application_version, str):
            self.application_version = application_version
        else:
            self.application_version = application_version.number

    def list(self, nocache: bool = False) -> builtins.list[ApplicationVersionDocument]:
        """List metadata for all public, uploaded release documents for the bound version.

        Retries on network and server errors. Cached for the configured application-version TTL.

        Args:
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.

        Returns:
            list[ApplicationVersionDocument]: Metadata for each public, uploaded document.

        Raises:
            NotFoundException: When the application version does not exist or is not accessible.
            aignx.codegen.exceptions.ApiException: If the API request fails.
        """

        @cached_operation(ttl=settings().application_version_cache_ttl, token_provider=self._api.token_provider)
        def list_with_retry(application_id: str, application_version: str) -> builtins.list[VersionDocumentData]:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().application_version_retry_attempts),
                wait=wait_exponential_jitter(
                    initial=settings().application_version_retry_wait_min,
                    max=settings().application_version_retry_wait_max,
                ),
                before_sleep=_log_retry_attempt,
                reraise=True,
            )(
                lambda: self._api.list_version_documents(
                    application_id=application_id,
                    version=application_version,
                    _request_timeout=settings().application_version_timeout,
                    _headers={"User-Agent": user_agent()},
                )
            )

        documents = list_with_retry(self.application_id, self.application_version, nocache=nocache)  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]
        return [ApplicationVersionDocument.from_response(doc) for doc in (documents or [])]

    def details(self, document_name: str, nocache: bool = False) -> ApplicationVersionDocument:
        """Retrieve metadata for a single release document by name.

        Retries on network and server errors. Cached for the configured application-version TTL.

        Args:
            document_name (str): The document filename (e.g. "output_description.pdf").
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.

        Returns:
            ApplicationVersionDocument: The document metadata.

        Raises:
            NotFoundException: When the document does not exist, is not public, or is not uploaded.
            aignx.codegen.exceptions.ApiException: If the API request fails.
        """

        @cached_operation(ttl=settings().application_version_cache_ttl, token_provider=self._api.token_provider)
        def details_with_retry(
            application_id: str, application_version: str, document_name: str
        ) -> VersionDocumentData:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().application_version_retry_attempts),
                wait=wait_exponential_jitter(
                    initial=settings().application_version_retry_wait_min,
                    max=settings().application_version_retry_wait_max,
                ),
                before_sleep=_log_retry_attempt,
                reraise=True,
            )(
                lambda: self._api.get_version_document(
                    application_id=application_id,
                    version=application_version,
                    name=document_name,
                    _request_timeout=settings().application_version_timeout,
                    _headers={"User-Agent": user_agent()},
                )
            )

        # The cached_operation decorator injects a `nocache` keyword that pyright/mypy can't see.
        data = details_with_retry(self.application_id, self.application_version, document_name, nocache=nocache)  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]
        return ApplicationVersionDocument.from_response(data)

    def download_to_path(self, document_name: str, destination: Path | str) -> Path:
        """Download a release document file to a local path.

        Calls ``GET /api/v1/applications/{application_id}/versions/{version}/documents/{name}/file``,
        which returns a ``307`` redirect to a short-lived GCS signed URL serving the file
        with ``Content-Disposition: attachment; filename="{name}"``. ``requests`` follows
        the redirect automatically and strips the bearer ``Authorization`` header on the
        cross-host hop, so the credential is not forwarded to GCS.

        If ``destination`` is a directory, the file is written as
        ``{destination}/{document_name}``; the requested document name is the canonical
        filename and is used regardless of any ``Content-Disposition`` served by the
        storage backend. Parent directories are created if they do not yet exist.

        Args:
            document_name (str): The document filename.
            destination (Path | str): Target directory to write into.

        Returns:
            Path: The absolute path to the written file.

        Raises:
            NotFoundException: When the document does not exist, is not public, or is not uploaded.
            ServiceException: 5xx errors, request timeouts, or connection errors after retries.
            requests.HTTPError: For other 4xx errors or signed-URL download failures.
        """
        destination_path = self._resolve_destination_path(destination, document_name)
        endpoint_url, token_provider, ssl_verify, proxy = self._prepare_document_request(
            document_name=document_name, suffix="file"
        )

        def _stream_to_disk() -> None:
            with destination_path.open("wb") as out_file:
                self._stream_document(
                    url=endpoint_url,
                    write_chunk=out_file.write,
                    document_name=document_name,
                    token_provider=token_provider,
                    ssl_verify=ssl_verify,
                    proxy=proxy,
                )

        Retrying(
            retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
            stop=stop_after_attempt(settings().application_version_retry_attempts),
            wait=wait_exponential_jitter(
                initial=settings().application_version_retry_wait_min,
                max=settings().application_version_retry_wait_max,
            ),
            before_sleep=_log_retry_attempt,
            reraise=True,
        )(_stream_to_disk)
        return destination_path

    @staticmethod
    def _resolve_destination_path(destination: Path | str, document_name: str) -> Path:
        """Resolve the on-disk path to write a document to and ensure its parent exists.

        Returns:
            Path: The absolute, parent-created destination path.

        Raises:
            ValueError: If the destination is an existing file or a non-existent path
                with an existing parent that is a file.
        """
        destination_path = Path(destination)
        if destination_path.is_file() or (destination_path.exists() and not destination_path.is_dir()):
            msg = f"Destination '{destination}' is an existing file. Please provide a directory or a non-existent path."
            raise ValueError(msg)

        destination_path /= document_name
        destination_path = destination_path.resolve()
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        return destination_path

    @staticmethod
    def _build_document_endpoint_url(
        host: str, application_id: str, version: str, document_name: str, suffix: str
    ) -> str:
        """Build a per-document endpoint URL with each path segment encoded individually.

        Per-segment encoding ensures reserved characters (spaces, '#', '?', '/', ...) inside
        a document name cannot inject extra path segments or query strings into the URL.

        Args:
            host: API host (without trailing slash).
            application_id: Application ID.
            version: Application version (semver string).
            document_name: Document filename.
            suffix: Endpoint variant — ``"file"`` for browser-attachment downloads or
                ``"content"`` for programmatic raw-content streaming.

        Returns:
            str: The fully-qualified ``/api/v1/applications/.../documents/.../{suffix}`` URL.
        """
        encoded_application_id = quote(application_id, safe="")
        encoded_version = quote(version, safe="")
        encoded_document_name = quote(document_name, safe="")
        return (
            f"{host}/api/v1/applications/{encoded_application_id}"
            f"/versions/{encoded_version}/documents/{encoded_document_name}/{suffix}"
        )

    def _prepare_document_request(
        self, document_name: str, suffix: str
    ) -> tuple[str, t.Callable[[], str], bool | str, str | None]:
        """Resolve the endpoint URL and the codegen client's transport settings for a document.

        Honors the codegen client's ``token_provider`` when set: ``Client.get_api_client()``
        wires it up with ``use_cache=cache_token``, so a user who instantiates
        ``Client(cache_token=False)`` does not want us to read/write the token cache.
        Falls back to ``get_token()`` only when the configuration was built outside of
        ``Client`` (e.g. unit tests with bare ``PublicApi``).

        Returns:
            tuple of (endpoint_url, token_provider, ssl_verify, proxy).
        """
        configuration = self._api.api_client.configuration
        endpoint_url = self._build_document_endpoint_url(
            host=configuration.host.rstrip("/"),
            application_id=self.application_id,
            version=self.application_version,
            document_name=document_name,
            suffix=suffix,
        )
        ssl_ca_cert = getattr(configuration, "ssl_ca_cert", None)
        verify_ssl = getattr(configuration, "verify_ssl", True)
        ssl_verify: bool | str = ssl_ca_cert or verify_ssl
        token_provider = getattr(configuration, "token_provider", None) or get_token
        proxy = getattr(configuration, "proxy", None)
        return endpoint_url, token_provider, ssl_verify, proxy

    # Private helper; splitting params would require a thin DTO.
    def _stream_document(  # noqa: PLR0913, PLR0917
        self,
        url: str,
        write_chunk: t.Callable[[bytes], object],
        document_name: str,
        token_provider: t.Callable[[], str],
        ssl_verify: bool | str,
        proxy: str | None,
    ) -> None:
        """Stream a single document download into a caller-provided sink.

        ``write_chunk`` is invoked for each non-empty body chunk; the caller decides
        where the bytes go (file on disk, in-memory buffer, ...). Return type is
        ``object`` so both ``BinaryIO.write`` and ``BytesIO.write`` (which return
        the number of bytes written) are accepted without a cast.

        Raises:
            NotFoundException: When the platform returns 404 for the document.
            ServiceException: For 5xx responses, request timeouts, or connection errors.
        """
        try:
            with requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {token_provider()}",
                    "User-Agent": user_agent(),
                },
                allow_redirects=True,
                timeout=settings().application_version_timeout,
                proxies={"http": proxy, "https": proxy} if proxy else None,
                verify=ssl_verify,
                stream=True,
            ) as response:
                if response.status_code == HTTPStatus.NOT_FOUND:
                    raise NotFoundException(
                        status=HTTPStatus.NOT_FOUND.value,
                        reason=(
                            f"Document '{document_name}' not found for application "
                            f"'{self.application_id}' version '{self.application_version}'"
                        ),
                    )
                if response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
                    raise ServiceException(status=response.status_code, reason=response.reason)
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=_DOCUMENT_DOWNLOAD_CHUNK_SIZE):
                    if chunk:
                        write_chunk(chunk)
        except requests.Timeout as e:
            raise ServiceException(status=HTTPStatus.SERVICE_UNAVAILABLE.value, reason="Request timed out") from e
        except requests.ConnectionError as e:
            raise ServiceException(status=HTTPStatus.SERVICE_UNAVAILABLE.value, reason="Connection failed") from e
        except requests.RequestException as e:
            raise ServiceException(status=HTTPStatus.SERVICE_UNAVAILABLE.value, reason="Request failed") from e

    def read_content(self, document_name: str) -> bytes:
        """Fetch a release document's raw content into memory.

        Calls ``GET /api/v1/applications/{application_id}/versions/{version}/documents/{name}/content``,
        which returns a ``307`` redirect to a short-lived GCS signed URL. Unlike ``/file``,
        no ``Content-Disposition`` override is set — GCS serves the object body with its
        stored ``Content-Type`` and ``Cache-Control: no-store``.

        Use this for small documents (JSON manifests, license text, etc.) where holding
        the bytes in memory is appropriate. For large files, prefer ``download_to_path``,
        which streams directly to disk.

        Document downloads do not carry a CRC32C checksum (unlike run artifacts);
        integrity is bounded by HTTPS transport and the signed-URL lifetime.

        Args:
            document_name (str): The document filename.

        Returns:
            bytes: The raw document content.

        Raises:
            NotFoundException: When the document does not exist, is not public, or is not uploaded.
            ServiceException: 5xx errors, request timeouts, or connection errors after retries.
            requests.HTTPError: For other 4xx errors or signed-URL download failures.
        """
        endpoint_url, token_provider, ssl_verify, proxy = self._prepare_document_request(
            document_name=document_name, suffix="content"
        )

        def _stream_to_buffer() -> bytes:
            buffer = BytesIO()
            self._stream_document(
                url=endpoint_url,
                write_chunk=buffer.write,
                document_name=document_name,
                token_provider=token_provider,
                ssl_verify=ssl_verify,
                proxy=proxy,
            )
            return buffer.getvalue()

        return Retrying(
            retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
            stop=stop_after_attempt(settings().application_version_retry_attempts),
            wait=wait_exponential_jitter(
                initial=settings().application_version_retry_wait_min,
                max=settings().application_version_retry_wait_max,
            ),
            before_sleep=_log_retry_attempt,
            reraise=True,
        )(_stream_to_buffer)


class Applications(_AuthenticatedResource):
    """Resource class for managing applications.

    Provides operations to list applications and access version resources.
    """

    def __init__(self, api: _AuthenticatedApi) -> None:
        """Initializes the Applications resource with the API platform.

        Args:
            api (_AuthenticatedApi): The configured API platform.
        """
        super().__init__(api)
        self.versions: Versions = Versions(self._api)

    def details(self, application_id: str, nocache: bool = False) -> Application:
        """Find application by id.

        Retries on network and server errors.

        Args:
            application_id (str): The ID of the application.
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.

        Returns:
            Application: The application object

        Raises:
            NotFoundException: If the application with the given ID is not found.
            aignx.codegen.exceptions.ApiException: If the API call fails.
        """

        @cached_operation(ttl=settings().application_cache_ttl, token_provider=self._api.token_provider)
        def details_with_retry(application_id: str) -> Application:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().application_retry_attempts),
                wait=wait_exponential_jitter(
                    initial=settings().application_retry_wait_min, max=settings().application_retry_wait_max
                ),
                before_sleep=_log_retry_attempt,
                reraise=True,
            )(
                lambda: self._api.read_application_by_id_v1_applications_application_id_get(
                    application_id=application_id,
                    _request_timeout=settings().application_timeout,
                    _headers={"User-Agent": user_agent()},
                )
            )

        return details_with_retry(application_id, nocache=nocache)  # type: ignore[call-arg]

    def list(self, nocache: bool = False) -> t.Iterator[ApplicationSummary]:
        """Find all available applications.

        Retries on network and server errors for each page.

        Args:
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.

        Returns:
            Iterator[ApplicationSummary]: An iterator over the available applications.

        Raises:
            aignx.codegen.exceptions.ApiException: If the API request fails.
        """

        # Create a wrapper function that applies retry logic and caching to each API call
        # Caching at this level ensures having a fresh iterator on cache hits
        @cached_operation(ttl=settings().application_cache_ttl, token_provider=self._api.token_provider)
        def list_with_retry(**kwargs: object) -> builtins.list[ApplicationSummary]:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().application_retry_attempts),
                wait=wait_exponential_jitter(
                    initial=settings().application_retry_wait_min, max=settings().application_retry_wait_max
                ),
                before_sleep=_log_retry_attempt,
                reraise=True,
            )(
                lambda: self._api.list_applications_v1_applications_get(
                    _request_timeout=settings().application_timeout,
                    _headers={"User-Agent": user_agent()},
                    **kwargs,  # pyright: ignore[reportArgumentType]
                )
            )

        return paginate(
            lambda **kwargs: list_with_retry(
                nocache=nocache,
                **kwargs,
            )
        )
