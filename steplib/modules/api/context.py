"""ApiContext: per-scenario HTTP state for the API module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from steplib.modules.api.client import HTTPClient, Request, Response, UrllibHTTPClient


@dataclass
class ApiContext:
    """Holds all HTTP state for a scenario.

    Lives at ``context.steplib.api`` and is reset between scenarios.

    Attributes:
        client: The HTTP client implementation (defaults to ``UrllibHTTPClient``).
        base_url: The base URL for resolving relative URLs.
        default_headers: Headers sent with every request.
        query_params: Default query parameters sent with every request.
        auth: Optional ``(username, password)`` tuple for basic auth.
        cookies: Cookies sent with every request.
        timeout: Request timeout in seconds (``None`` = no timeout).
        allow_redirects: Whether to follow redirects (default ``True``).
        ssl_verify: Whether to verify SSL certificates (default ``True``).
        proxies: Proxy mappings (e.g. ``{"http": "http://proxy:8080"}``).
        last_request: The most recent ``Request`` sent.
        last_response: The most recent ``Response`` received.
        variables: User-defined variables stored by steps.
        backend: The backend name (e.g. ``"stdlib"``, ``"httpx"``).

    """

    client: HTTPClient | None = None
    base_url: str = ""
    default_headers: dict[str, str] = field(default_factory=dict)
    query_params: dict[str, str] = field(default_factory=dict)
    auth: tuple[str, str] | None = None
    cookies: dict[str, str] = field(default_factory=dict)
    timeout: float | None = None
    allow_redirects: bool = True
    ssl_verify: bool = True
    proxies: dict[str, str] = field(default_factory=dict)
    last_request: Request | None = None
    last_response: Response | None = None
    variables: dict[str, Any] = field(default_factory=dict)
    backend: str = "stdlib"

    def __post_init__(self) -> None:
        """Initialize a default client if none was provided."""
        if self.client is None:
            self.client = UrllibHTTPClient()

    def reset(self) -> None:
        """Reset per-scenario state, keeping the client and configuration."""
        self.default_headers = {}
        self.query_params = {}
        self.auth = None
        self.cookies = {}
        self.timeout = None
        self.allow_redirects = True
        self.ssl_verify = True
        self.proxies = {}
        self.last_request = None
        self.last_response = None
        self.variables = {}

    def cleanup(self) -> None:
        """Close any resources held by the client."""
        if self.client is not None and hasattr(self.client, "close"):
            close = getattr(self.client, "close", None)
            if callable(close):
                close()
