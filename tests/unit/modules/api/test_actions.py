"""Tests for API actions (pure functions)."""

from __future__ import annotations

import pytest

from steplib.modules.api.actions import (
    api_assert_body_contains,
    api_assert_header_equals,
    api_assert_json_path_equals,
    api_assert_json_valid,
    api_assert_status,
    api_send,
    api_set_base_url,
    api_set_header,
    api_set_timeout,
    api_store_response_body,
)
from steplib.modules.api.client import Response
from steplib.modules.api.context import ApiContext


@pytest.fixture()
def api_ctx() -> ApiContext:
    """Return a fresh ApiContext with a mock client."""
    return ApiContext(client=MockHTTPClient())


class MockHTTPClient:
    """Mock HTTP client that returns predefined responses."""

    def __init__(self) -> None:
        self.requests: list[tuple[str, str, dict[str, str], bytes | None]] = []
        self.response = Response(
            status=200,
            headers={"Content-Type": "application/json"},
            body=b'{"name": "Ada", "age": 30}',
            elapsed_ms=5.0,
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
        timeout: float | None = None,
    ) -> Response:
        self.requests.append((method, url, headers or {}, body))
        return self.response


class TestApiSetBaseUrl:
    """Tests for api_set_base_url."""

    def test_set_base_url(self, api_ctx: ApiContext) -> None:
        """Setting base URL should update the context."""
        api_set_base_url(api_ctx, "https://api.example.com")
        assert api_ctx.base_url == "https://api.example.com"


class TestApiSetHeader:
    """Tests for api_set_header."""

    def test_set_header(self, api_ctx: ApiContext) -> None:
        """Setting a header should update default_headers."""
        api_set_header(api_ctx, "Authorization", "Bearer token")
        assert api_ctx.default_headers["Authorization"] == "Bearer token"


class TestApiSetTimeout:
    """Tests for api_set_timeout."""

    def test_set_timeout(self, api_ctx: ApiContext) -> None:
        """Setting timeout should update the context."""
        api_set_timeout(api_ctx, 30.0)
        assert api_ctx.timeout == 30.0


class TestApiSend:
    """Tests for api_send."""

    def test_send_stores_request_and_response(self, api_ctx: ApiContext) -> None:
        """api_send should store the request and response."""
        api_set_base_url(api_ctx, "https://api.example.com")
        response = api_send(api_ctx, "GET", "/users")
        assert response.status == 200
        assert api_ctx.last_request is not None
        assert api_ctx.last_request.method == "GET"
        assert api_ctx.last_request.url == "https://api.example.com/users"
        assert api_ctx.last_response is not None
        assert api_ctx.last_response.status == 200

    def test_send_with_body(self, api_ctx: ApiContext) -> None:
        """api_send should encode string body to bytes."""
        api_send(api_ctx, "POST", "/users", body='{"name": "Ada"}')
        assert api_ctx.last_request is not None
        assert api_ctx.last_request.body == b'{"name": "Ada"}'

    def test_send_no_client_raises(self) -> None:
        """api_send without a client should raise RuntimeError."""
        ctx = ApiContext()
        ctx.client = None  # Bypass __post_init__ default
        with pytest.raises(RuntimeError, match="No HTTP client"):
            api_send(ctx, "GET", "/users")


class TestApiAssertStatus:
    """Tests for api_assert_status."""

    def test_status_matches(self, api_ctx: ApiContext) -> None:
        """Matching status should not raise."""
        api_send(api_ctx, "GET", "/users")
        api_assert_status(api_ctx, 200)

    def test_status_mismatch_raises(self, api_ctx: ApiContext) -> None:
        """Mismatched status should raise AssertionError."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="Expected status 404"):
            api_assert_status(api_ctx, 404)

    def test_no_response_raises(self, api_ctx: ApiContext) -> None:
        """Asserting status without a response should raise."""
        with pytest.raises(AssertionError, match="No response"):
            api_assert_status(api_ctx, 200)


class TestApiAssertBodyContains:
    """Tests for api_assert_body_contains."""

    def test_body_contains(self, api_ctx: ApiContext) -> None:
        """Containing text should not raise."""
        api_send(api_ctx, "GET", "/users")
        api_assert_body_contains(api_ctx, "Ada")

    def test_body_not_contains_raises(self, api_ctx: ApiContext) -> None:
        """Not containing text should raise."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="does not contain"):
            api_assert_body_contains(api_ctx, "nonexistent")


class TestApiAssertJsonValid:
    """Tests for api_assert_json_valid."""

    def test_valid_json(self, api_ctx: ApiContext) -> None:
        """Valid JSON should not raise."""
        api_send(api_ctx, "GET", "/users")
        api_assert_json_valid(api_ctx)

    def test_invalid_json_raises(self, api_ctx: ApiContext) -> None:
        """Invalid JSON should raise."""
        api_ctx.client = MockHTTPClient()  # type: ignore[attr-defined]
        api_ctx.client.response = Response(  # type: ignore[attr-defined]
            status=200, headers={}, body=b"not json", elapsed_ms=1.0,
        )
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="not valid JSON"):
            api_assert_json_valid(api_ctx)


class TestApiAssertJsonPath:
    """Tests for api_assert_json_path_equals."""

    def test_json_path_matches(self, api_ctx: ApiContext) -> None:
        """Matching JSON path should not raise."""
        api_send(api_ctx, "GET", "/users")
        api_assert_json_path_equals(api_ctx, "$.name", "Ada")

    def test_json_path_mismatch_raises(self, api_ctx: ApiContext) -> None:
        """Mismatched JSON path should raise."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="JSON path"):
            api_assert_json_path_equals(api_ctx, "$.name", "Bob")


class TestApiAssertHeader:
    """Tests for api_assert_header_equals."""

    def test_header_matches(self, api_ctx: ApiContext) -> None:
        """Matching header should not raise."""
        api_send(api_ctx, "GET", "/users")
        api_assert_header_equals(api_ctx, "Content-Type", "application/json")

    def test_header_missing_raises(self, api_ctx: ApiContext) -> None:
        """Missing header should raise."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="not found"):
            api_assert_header_equals(api_ctx, "X-Custom", "value")

    def test_header_mismatch_raises(self, api_ctx: ApiContext) -> None:
        """Mismatched header should raise."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="expected"):
            api_assert_header_equals(api_ctx, "Content-Type", "text/html")


class TestApiStoreResponseBody:
    """Tests for api_store_response_body."""

    def test_store_body(self, api_ctx: ApiContext) -> None:
        """Storing the response body should save it in variables."""
        api_send(api_ctx, "GET", "/users")
        api_store_response_body(api_ctx, "response")
        assert "response" in api_ctx.variables
        assert "Ada" in api_ctx.variables["response"]

    def test_store_no_response_raises(self, api_ctx: ApiContext) -> None:
        """Storing without a response should raise."""
        with pytest.raises(AssertionError, match="No response"):
            api_store_response_body(api_ctx, "response")
