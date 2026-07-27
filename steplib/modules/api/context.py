"""ApiContext: per-scenario HTTP state for the API module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from steplib.modules.api.client import HTTPClient, Request, Response, UrllibHTTPClient


@dataclass
class ApiContext:
    """Holds all HTTP state for a scenario.

    Lives at ``context.steplib.api`` and is reset between scenarios.
    """

    client: HTTPClient | None = None
    base_url: str = ""
    default_headers: dict[str, str] = field(default_factory=dict)
    timeout: float | None = None
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
        self.last_request = None
        self.last_response = None
        self.variables = {}

    def cleanup(self) -> None:
        """Close any resources held by the client."""
        if self.client is not None and hasattr(self.client, "close"):
            close = getattr(self.client, "close", None)
            if callable(close):
                close()
