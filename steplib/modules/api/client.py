"""HTTP client abstraction: protocol, stdlib fallback, and lazy httpx/requests clients."""

from __future__ import annotations

import base64
import io
import json as _json
import ssl
import time
import urllib.error
import urllib.parse
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
        params: dict[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        allow_redirects: bool = True,
        verify: bool = True,
        proxies: dict[str, str] | None = None,
    ) -> Response:
        """Send an HTTP request and return the response.

        Args:
            method: The HTTP method (e.g. ``"GET"``).
            url: The target URL.
            headers: Optional request headers.
            body: Optional request body as bytes.
            timeout: Optional timeout in seconds.
            params: Optional query parameters.
            auth: Optional ``(username, password)`` tuple for basic auth.
            cookies: Optional cookies to send.
            allow_redirects: Whether to follow redirects (default ``True``).
            verify: Whether to verify SSL certificates (default ``True``).
            proxies: Optional proxy mappings.

        Returns:
            The ``Response`` object.

        """
        ...


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Redirect handler that raises HTTPError instead of following redirects."""

    def redirect_request(
        self,
        req: Any,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        """Reject all redirects by raising an HTTPError with the real status and headers."""
        raise urllib.error.HTTPError(
            newurl,
            code,
            msg,
            headers,
            io.BytesIO(b""),
        )


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
        params: dict[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        allow_redirects: bool = True,
        verify: bool = True,
        proxies: dict[str, str] | None = None,
    ) -> Response:
        """Send an HTTP request using urllib.

        Args:
            method: The HTTP method (e.g. ``"GET"``).
            url: The target URL.
            headers: Optional request headers.
            body: Optional request body as bytes.
            timeout: Optional timeout in seconds.
            params: Optional query parameters appended to the URL.
            auth: Optional ``(username, password)`` for basic auth.
            cookies: Optional cookies sent as a Cookie header.
            allow_redirects: Whether to follow redirects (default ``True``).
            verify: Whether to verify SSL certificates (default ``True``).
            proxies: Optional proxy mappings.

        Returns:
            The ``Response`` object.

        """
        req_headers = dict(headers or {})

        # Basic auth
        if auth is not None:
            credential = f"{auth[0]}:{auth[1]}"
            token = base64.b64encode(credential.encode()).decode()
            req_headers["Authorization"] = f"Basic {token}"

        # Cookies
        if cookies:
            req_headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())

        # Query params
        final_url = url
        if params:
            separator = "&" if "?" in url else "?"
            query = urllib.parse.urlencode(params)
            final_url = f"{url}{separator}{query}"

        req = urllib.request.Request(final_url, data=body, method=method, headers=req_headers)

        # SSL context
        ctx = None
        if not verify:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        # Proxy handlers
        handlers: list[urllib.request.BaseHandler] = []
        if proxies:
            proxy_support = urllib.request.ProxyHandler(proxies)
            handlers.append(proxy_support)
        if not allow_redirects:
            handlers.append(NoRedirectHandler())
        if handlers:
            opener = urllib.request.build_opener(*handlers)
        else:
            opener = urllib.request.build_opener()

        start = time.monotonic()
        try:
            with opener.open(req, timeout=timeout) as resp:
                resp_body = resp.read()
                resp_headers = _build_headers_dict(resp.headers)
                status = resp.status
        except urllib.error.HTTPError as exc:
            resp_body = exc.read() if hasattr(exc, "read") else b""
            resp_headers = _build_headers_dict(exc.headers) if exc.headers else {}
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
            import httpx
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
        params: dict[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        allow_redirects: bool = True,
        verify: bool = True,
        proxies: dict[str, str] | None = None,
    ) -> Response:
        """Send an HTTP request using httpx.

        Args:
            method: The HTTP method (e.g. ``"GET"``).
            url: The target URL.
            headers: Optional request headers.
            body: Optional request body as bytes.
            timeout: Optional timeout in seconds.
            params: Optional query parameters.
            auth: Optional ``(username, password)`` for basic auth.
            cookies: Optional cookies to send.
            allow_redirects: Whether to follow redirects (default ``True``).
            verify: Whether to verify SSL certificates (default ``True``).
            proxies: Optional proxy mappings.

        Returns:
            The ``Response`` object.

        """
        start = time.monotonic()
        client_kwargs: dict[str, Any] = {
            "verify": verify,
            "cookies": cookies,
            "timeout": timeout,
        }
        if proxies:
            # httpx 0.28+ uses `proxy` for a single proxy URL.
            # For multiple proxies, use mounts with HTTPTransport.
            # Mount keys must include the "://" suffix (e.g. "http://").
            if len(proxies) == 1:
                client_kwargs["proxy"] = next(iter(proxies.values()))
            else:
                mounts: dict[str, Any] = {}
                for scheme, proxy_url in proxies.items():
                    mounts[f"{scheme}://"] = self._httpx.HTTPTransport(proxy=proxy_url)
                client_kwargs["mounts"] = mounts
        with self._httpx.Client(**client_kwargs) as client:
            resp = client.request(
                method,
                url,
                headers=headers or {},
                content=body,
                params=params,
                auth=auth,
                follow_redirects=allow_redirects,
            )
            elapsed = (time.monotonic() - start) * 1000
            return Response(
                status=resp.status_code,
                headers=_build_headers_dict(resp.headers),
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
            import requests
        except ImportError as exc:
            raise MissingDependencyError("requests", "requests") from exc
        self._requests = requests

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
        timeout: float | None = None,
        params: dict[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        allow_redirects: bool = True,
        verify: bool = True,
        proxies: dict[str, str] | None = None,
    ) -> Response:
        """Send an HTTP request using requests.

        Args:
            method: The HTTP method (e.g. ``"GET"``).
            url: The target URL.
            headers: Optional request headers.
            body: Optional request body as bytes.
            timeout: Optional timeout in seconds.
            params: Optional query parameters.
            auth: Optional ``(username, password)`` for basic auth.
            cookies: Optional cookies to send.
            allow_redirects: Whether to follow redirects (default ``True``).
            verify: Whether to verify SSL certificates (default ``True``).
            proxies: Optional proxy mappings.

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
            params=params,
            auth=auth,
            cookies=cookies,
            allow_redirects=allow_redirects,
            verify=verify,
            proxies=proxies,
        )
        elapsed = (time.monotonic() - start) * 1000
        return Response(
            status=resp.status_code,
            headers=_build_headers_dict(resp.headers),
            body=resp.content,
            elapsed_ms=elapsed,
        )


def _build_headers_dict(headers_obj: Any) -> dict[str, str]:
    r"""Build a ``dict[str, str]`` from a headers object, preserving duplicates.

    Multiple values for the same header name (notably ``Set-Cookie``) are
    joined with ``\n`` so that callers can split them back apart.
    """
    result: dict[str, str] = {}
    for key in headers_obj:
        if key in result:
            continue
        get_all = getattr(headers_obj, "get_all", None)
        if get_all is not None:
            values = get_all(key)
        else:
            get_list = getattr(headers_obj, "get_list", None)
            values = get_list(key) if get_list is not None else [headers_obj[key]]
        if values:
            result[key] = "\n".join(values) if len(values) > 1 else values[0]
    return result


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
