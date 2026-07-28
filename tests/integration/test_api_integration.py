"""Integration tests for the API module using mocked urllib."""

from __future__ import annotations

import io
import urllib.error
from unittest.mock import MagicMock, patch

from steplib.modules.api.actions import (
    api_assert_body_contains,
    api_assert_json_path_equals,
    api_assert_json_valid,
    api_assert_status,
    api_send,
    api_set_base_url,
    api_set_header,
)
from steplib.modules.api.client import UrllibHTTPClient
from steplib.modules.api.context import ApiContext


def _mock_opener(body: bytes, status: int = 200, headers: dict[str, str] | None = None):
    """Create a mock opener for urllib.request.build_opener.

    The opener's ``open()`` returns a context manager whose ``__enter__``
    yields a mock response with the given body, status, and headers.
    """
    resp_headers = headers or {"Content-Type": "application/json"}
    mock_resp = MagicMock()
    mock_resp.read.return_value = body
    mock_resp.status = status
    mock_resp.headers = resp_headers
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_resp)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    mock_opener = MagicMock()
    mock_opener.open.return_value = mock_ctx
    return mock_opener


def test_get_request_with_urllib() -> None:
    """UrllibHTTPClient should send a GET request and return the response."""
    body = b'{"users": [{"name": "Ada"}]}'
    with patch("urllib.request.build_opener", return_value=_mock_opener(body)):
        ctx = ApiContext(client=UrllibHTTPClient())
        api_set_base_url(ctx, "https://api.example.com")
        response = api_send(ctx, "GET", "/users")

    assert response.status == 200
    api_assert_status(ctx, 200)
    api_assert_json_valid(ctx)
    api_assert_json_path_equals(ctx, "$.users[0].name", "Ada")


def test_post_request_with_body() -> None:
    """UrllibHTTPClient should send a POST request with a body."""
    body = b'{"id": 1, "name": "Ada"}'
    with patch("urllib.request.build_opener", return_value=_mock_opener(body, status=201)):
        ctx = ApiContext(client=UrllibHTTPClient())
        api_set_base_url(ctx, "https://api.example.com")
        response = api_send(ctx, "POST", "/users", body='{"name": "Ada"}')

    assert response.status == 201
    api_assert_status(ctx, 201)
    api_assert_body_contains(ctx, "Ada")


def test_request_with_default_headers() -> None:
    """Default headers should be sent with the request."""
    body = b'{"ok": true}'
    mock_opener = _mock_opener(body)
    with patch("urllib.request.build_opener", return_value=mock_opener):
        ctx = ApiContext(client=UrllibHTTPClient())
        api_set_base_url(ctx, "https://api.example.com")
        api_set_header(ctx, "Authorization", "Bearer token123")
        api_send(ctx, "GET", "/secure")

    # Verify opener.open was called with a request that has the header.
    assert mock_opener.open.called
    req = mock_opener.open.call_args[0][0]
    assert req.headers.get("Authorization") == "Bearer token123"


def test_404_response() -> None:
    """A 404 response should be handled via HTTPError."""
    body = b'{"error": "not found"}'
    error = urllib.error.HTTPError(
        url="https://api.example.com/missing",
        code=404,
        msg="Not Found",
        hdrs=None,
        fp=io.BytesIO(body),
    )
    mock_opener = MagicMock()
    mock_opener.open.side_effect = error
    with patch("urllib.request.build_opener", return_value=mock_opener):
        ctx = ApiContext(client=UrllibHTTPClient())
        api_set_base_url(ctx, "https://api.example.com")
        response = api_send(ctx, "GET", "/missing")

    assert response.status == 404
    api_assert_status(ctx, 404)
