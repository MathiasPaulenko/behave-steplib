"""HTTP client abstraction: protocol, stdlib fallback, and lazy httpx/requests clients."""

from __future__ import annotations

import json as _json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Protocol

from steplib.core.exceptions import MissingDependencyError


@dataclass(frozen=True, slots=True)
class Request:
    """Immutable HTTP request representation.

    Attributes:
        method: The HTTP method (e.g. ``"GET"``, ``"POST"``).
        url: The resolved URL.
        headers: Request headers.
        body: Optional request body as bytes.

    """

    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes | None = None


@dataclass(frozen=True, slots=True)
class Response:
    """Immutable HTTP response representation.

    Attributes:
        status: The HTTP status code.
        headers: Response headers.
        body: The raw response body as bytes.
        elapsed_ms: The request duration in milliseconds.

    """

    status: int
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    elapsed_ms: float = 0.0

    @property
    def text(self) -> str:
        """Decode the body as UTF-8 text."""
        return self.body.decode("utf-8", errors="replace")

    def json(self) -> Any:
        """Parse the body as JSON.

        Returns:
            The parsed JSON data.

        Raises:
            json.JSONDecodeError: If the body is not valid JSON.

        """
        return _json.loads(self.text)


class HTTPClient(Protocol):
    """Protocol for HTTP client implementations."""

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
        timeout: float | None = None,
    ) -> Response:
        """Send an HTTP request and return the response.

        Args:
            method: The HTTP method (e.g. ``"GET"``).
            url: The target URL.
            headers: Optional request headers.
            body: Optional request body as bytes.
            timeout: Optional timeout in seconds.

        Returns:
            The ``Response`` object.

        """
        ...


class UrllibHTTPClient:
    """HTTP client using only the standard library (urllib)."""

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
        timeout: float | None = None,
    ) -> Response:
        """Send an HTTP request using urllib.

        Args:
            method: The HTTP method (e.g. ``"GET"``).
            url: The target URL.
            headers: Optional request headers.
            body: Optional request body as bytes.
            timeout: Optional timeout in seconds.

        Returns:
            The ``Response`` object.

        """
        req_headers = dict(headers or {})
        req = urllib.request.Request(url, data=body, method=method, headers=req_headers)
        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp_body = resp.read()
                resp_headers = dict(resp.headers)
                status = resp.status
        except urllib.error.HTTPError as exc:
            resp_body = exc.read() if hasattr(exc, "read") else b""
            resp_headers = dict(exc.headers) if exc.headers else {}
            status = exc.code
        elapsed = (time.monotonic() - start) * 1000
        return Response(
            status=status,
            headers=resp_headers,
            body=resp_body,
            elapsed_ms=elapsed,
        )


class HttpxHTTPClient:
    """HTTP client backed by httpx (requires the ``[api]`` extra)."""

    def __init__(self) -> None:
        """Initialize the client, importing httpx lazily.

        Raises:
            MissingDependencyError: If ``httpx`` is not installed.

        """
        try:
            import httpx  # noqa: PLC0415
        except ImportError as exc:
            raise MissingDependencyError("api", "httpx") from exc
        self._httpx = httpx

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
        timeout: float | None = None,
    ) -> Response:
        """Send an HTTP request using httpx.

        Args:
            method: The HTTP method (e.g. ``"GET"``).
            url: The target URL.
            headers: Optional request headers.
            body: Optional request body as bytes.
            timeout: Optional timeout in seconds.

        Returns:
            The ``Response`` object.

        """
        start = time.monotonic()
        with self._httpx.Client() as client:
            resp = client.request(
                method,
                url,
                headers=headers or {},
                content=body,
                timeout=timeout,
            )
            elapsed = (time.monotonic() - start) * 1000
            return Response(
                status=resp.status_code,
                headers=dict(resp.headers),
                body=resp.content,
                elapsed_ms=elapsed,
            )


class RequestsHTTPClient:
    """HTTP client backed by requests (requires the ``requests`` package)."""

    def __init__(self) -> None:
        """Initialize the client, importing requests lazily.

        Raises:
            MissingDependencyError: If ``requests`` is not installed.

        """
        try:
            import requests  # noqa: PLC0415
        except ImportError as exc:
            raise MissingDependencyError("api", "requests") from exc
        self._requests = requests

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
        timeout: float | None = None,
    ) -> Response:
        """Send an HTTP request using requests.

        Args:
            method: The HTTP method (e.g. ``"GET"``).
            url: The target URL.
            headers: Optional request headers.
            body: Optional request body as bytes.
            timeout: Optional timeout in seconds.

        Returns:
            The ``Response`` object.

        """
        start = time.monotonic()
        resp = self._requests.request(
            method,
            url,
            headers=headers or {},
            data=body,
            timeout=timeout,
        )
        elapsed = (time.monotonic() - start) * 1000
        return Response(
            status=resp.status_code,
            headers=dict(resp.headers),
            body=resp.content,
            elapsed_ms=elapsed,
        )


def get_client(backend: str = "stdlib") -> HTTPClient:
    """Return an HTTP client for the given backend.

    Args:
        backend: ``"stdlib"``, ``"httpx"``, or ``"requests"``.

    Returns:
        An ``HTTPClient`` instance for the requested backend.

    Raises:
        MissingDependencyError: If the backend's dependency is not installed.

    """
    if backend == "httpx":
        return HttpxHTTPClient()
    if backend == "requests":
        return RequestsHTTPClient()
    return UrllibHTTPClient()
