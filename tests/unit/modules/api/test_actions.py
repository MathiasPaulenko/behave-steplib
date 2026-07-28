"""Tests for API actions (pure functions)."""

from __future__ import annotations

import pytest

from steplib.modules.api.actions import (
    api_assert_body_contains,
    api_assert_body_not_contains,
    api_assert_content_type,
    api_assert_content_type_contains,
    api_assert_header_contains,
    api_assert_header_equals,
    api_assert_header_exists,
    api_assert_header_not_equals,
    api_assert_header_not_exists,
    api_assert_json_path_contains,
    api_assert_json_path_equals,
    api_assert_json_path_exists,
    api_assert_json_path_has_length,
    api_assert_json_path_is_not_null,
    api_assert_json_path_is_null,
    api_assert_json_path_matches_regex,
    api_assert_json_path_not_equals,
    api_assert_json_path_type,
    api_assert_json_schema,
    api_assert_json_valid,
    api_assert_response_time_between,
    api_assert_response_time_greater_than,
    api_assert_response_time_less_than,
    api_assert_status,
    api_assert_status_in,
    api_assert_variable_equals,
    api_clear_request_data,
    api_remove_header,
    api_remove_query_param,
    api_save_cookies,
    api_send,
    api_send_form,
    api_send_json,
    api_set_allow_redirects,
    api_set_base_url,
    api_set_basic_auth,
    api_set_bearer_token,
    api_set_header,
    api_set_proxy,
    api_set_query_param,
    api_set_ssl_verify,
    api_set_timeout,
    api_store_header,
    api_store_json_path,
    api_store_response_body,
    api_store_response_time,
    api_store_status,
    api_use_variable_as_header,
    api_use_variable_as_query_param,
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
        params: dict[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        allow_redirects: bool = True,
        verify: bool = True,
        proxies: dict[str, str] | None = None,
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
            status=200,
            headers={},
            body=b"not json",
            elapsed_ms=1.0,
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

    def test_json_path_boolean_true(self, api_ctx: ApiContext) -> None:
        """Boolean true should match string 'true' (not 'True')."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"active": true}',
            elapsed_ms=1.0,
        )
        api_assert_json_path_equals(api_ctx, "$.active", "true")

    def test_json_path_boolean_false(self, api_ctx: ApiContext) -> None:
        """Boolean false should match string 'false' (not 'False')."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"active": false}',
            elapsed_ms=1.0,
        )
        api_assert_json_path_equals(api_ctx, "$.active", "false")

    def test_json_path_null(self, api_ctx: ApiContext) -> None:
        """None should match string 'null' (not 'None')."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"data": null}',
            elapsed_ms=1.0,
        )
        api_assert_json_path_equals(api_ctx, "$.data", "null")


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


class TestApiAssertBodyNotContains:
    """Tests for api_assert_body_not_contains."""

    def test_body_not_contains_passes(self, api_ctx: ApiContext) -> None:
        """Not containing text should not raise."""
        api_send(api_ctx, "GET", "/users")
        api_assert_body_not_contains(api_ctx, "nonexistent")

    def test_body_contains_raises(self, api_ctx: ApiContext) -> None:
        """Containing text should raise."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="should not contain"):
            api_assert_body_not_contains(api_ctx, "Ada")


class TestApiAssertJsonPathExists:
    """Tests for api_assert_json_path_exists."""

    def test_path_exists(self, api_ctx: ApiContext) -> None:
        """Existing path should not raise."""
        api_send(api_ctx, "GET", "/users")
        api_assert_json_path_exists(api_ctx, "$.name")

    def test_path_not_exists_raises(self, api_ctx: ApiContext) -> None:
        """Non-existing path should raise."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="does not exist"):
            api_assert_json_path_exists(api_ctx, "$.nonexistent")


class TestApiAssertJsonPathType:
    """Tests for api_assert_json_path_type."""

    def test_type_matches(self, api_ctx: ApiContext) -> None:
        """Matching type should not raise."""
        api_send(api_ctx, "GET", "/users")
        api_assert_json_path_type(api_ctx, "$.name", "str")

    def test_type_mismatch_raises(self, api_ctx: ApiContext) -> None:
        """Mismatched type should raise."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="expected type"):
            api_assert_json_path_type(api_ctx, "$.name", "int")

    def test_unsupported_type_raises(self, api_ctx: ApiContext) -> None:
        """Unsupported type name should raise ValueError."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(ValueError, match="Unsupported type"):
            api_assert_json_path_type(api_ctx, "$.name", "bigint")


class TestApiAssertContentType:
    """Tests for api_assert_content_type and api_assert_content_type_contains."""

    def test_content_type_matches(self, api_ctx: ApiContext) -> None:
        """Matching content type should not raise."""
        api_send(api_ctx, "GET", "/users")
        api_assert_content_type(api_ctx, "application/json")

    def test_content_type_mismatch_raises(self, api_ctx: ApiContext) -> None:
        """Mismatched content type should raise."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="Expected Content-Type"):
            api_assert_content_type(api_ctx, "text/html")

    def test_content_type_contains_passes(self, api_ctx: ApiContext) -> None:
        """Containing substring should not raise."""
        api_send(api_ctx, "GET", "/users")
        api_assert_content_type_contains(api_ctx, "json")

    def test_content_type_contains_raises(self, api_ctx: ApiContext) -> None:
        """Not containing substring should raise."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="does not contain"):
            api_assert_content_type_contains(api_ctx, "xml")


class TestApiAssertStatusIn:
    """Tests for api_assert_status_in."""

    def test_status_in_list(self, api_ctx: ApiContext) -> None:
        """Status in list should not raise."""
        api_send(api_ctx, "GET", "/users")
        api_assert_status_in(api_ctx, [200, 201, 202])

    def test_status_not_in_list(self, api_ctx: ApiContext) -> None:
        """Status not in list should raise."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="one of"):
            api_assert_status_in(api_ctx, [404, 500])


class TestApiAssertResponseTime:
    """Tests for response time assertions."""

    def test_time_less_than_passes(self, api_ctx: ApiContext) -> None:
        """Fast response should not raise."""
        api_send(api_ctx, "GET", "/users")
        api_assert_response_time_less_than(api_ctx, 1.0)

    def test_time_less_than_raises(self, api_ctx: ApiContext) -> None:
        """Slow response should raise."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="not less than"):
            api_assert_response_time_less_than(api_ctx, 0.001)

    def test_time_greater_than_passes(self, api_ctx: ApiContext) -> None:
        """Slow enough response should not raise."""
        api_send(api_ctx, "GET", "/users")
        api_assert_response_time_greater_than(api_ctx, 0.001)

    def test_time_greater_than_raises(self, api_ctx: ApiContext) -> None:
        """Too fast response should raise."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="not greater than"):
            api_assert_response_time_greater_than(api_ctx, 1.0)

    def test_time_between_passes(self, api_ctx: ApiContext) -> None:
        """Response in range should not raise."""
        api_send(api_ctx, "GET", "/users")
        api_assert_response_time_between(api_ctx, 0.001, 1.0)

    def test_time_between_raises(self, api_ctx: ApiContext) -> None:
        """Response out of range should raise."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="not between"):
            api_assert_response_time_between(api_ctx, 10.0, 20.0)


class TestApiStoreJsonPath:
    """Tests for api_store_json_path."""

    def test_store_json_path(self, api_ctx: ApiContext) -> None:
        """Storing a JSON path value should save it in variables."""
        api_send(api_ctx, "GET", "/users")
        api_store_json_path(api_ctx, "$.name", "user_name")
        assert api_ctx.variables["user_name"] == "Ada"

    def test_store_no_response_raises(self, api_ctx: ApiContext) -> None:
        """Storing without a response should raise."""
        with pytest.raises(AssertionError, match="No response"):
            api_store_json_path(api_ctx, "$.name", "user_name")


class TestApiStoreHeader:
    """Tests for api_store_header."""

    def test_store_header(self, api_ctx: ApiContext) -> None:
        """Storing a header should save it in variables."""
        api_send(api_ctx, "GET", "/users")
        api_store_header(api_ctx, "Content-Type", "ct")
        assert api_ctx.variables["ct"] == "application/json"

    def test_store_missing_header_raises(self, api_ctx: ApiContext) -> None:
        """Storing a missing header should raise."""
        api_send(api_ctx, "GET", "/users")
        with pytest.raises(AssertionError, match="not found"):
            api_store_header(api_ctx, "X-Custom", "custom")


class TestApiStoreStatus:
    """Tests for api_store_status."""

    def test_store_status(self, api_ctx: ApiContext) -> None:
        """Storing the status should save it in variables."""
        api_send(api_ctx, "GET", "/users")
        api_store_status(api_ctx, "status")
        assert api_ctx.variables["status"] == 200


class TestApiSetQueryParam:
    """Tests for api_set_query_param and api_remove_query_param."""

    def test_set_query_param(self, api_ctx: ApiContext) -> None:
        """Setting a query param should update query_params."""
        api_set_query_param(api_ctx, "page", "1")
        assert api_ctx.query_params["page"] == "1"

    def test_remove_query_param(self, api_ctx: ApiContext) -> None:
        """Removing a query param should delete it."""
        api_set_query_param(api_ctx, "page", "1")
        api_remove_query_param(api_ctx, "page")
        assert "page" not in api_ctx.query_params

    def test_remove_nonexistent_param_raises(self, api_ctx: ApiContext) -> None:
        """Removing a non-existent param should raise KeyError."""
        with pytest.raises(KeyError, match="not found"):
            api_remove_query_param(api_ctx, "nonexistent")


class TestApiSetBasicAuth:
    """Tests for api_set_basic_auth."""

    def test_set_basic_auth(self, api_ctx: ApiContext) -> None:
        """Setting basic auth should store the tuple."""
        api_set_basic_auth(api_ctx, "admin", "secret")
        assert api_ctx.auth == ("admin", "secret")


class TestStepSetBasicAuthKeywordBug:
    """Regression test for Python keyword {pass} bug in step pattern.

    The step pattern previously used {pass} which is a Python reserved keyword.
    parse() returns it as ``{'pass': value}``, but no function can have a
    parameter named ``pass``. The fix changed the pattern to {password}.
    """

    def test_step_basic_auth_callable_with_parse_kwargs(self) -> None:
        """step_set_basic_auth must accept kwargs from parse without TypeError."""
        from types import SimpleNamespace

        from parse import parse as parse_pattern

        from steplib.core.state import SteplibState
        from steplib.modules.api.context import ApiContext
        from steplib.modules.api.steps import step_set_basic_auth

        context = SimpleNamespace()
        state = SteplibState(context, registry=None)  # type: ignore[arg-type]
        state.api = ApiContext()  # type: ignore[attr-defined]
        context.steplib = state

        pattern = "I set basic authentication with username {user} and password {password}"
        text = 'I set basic authentication with username "admin" and password "secret"'
        result = parse_pattern(pattern, text)
        assert result is not None
        step_set_basic_auth(context, **result.named)
        assert state.api.auth == ("admin", "secret")  # type: ignore[attr-defined]


class TestApiSetBearerToken:
    """Tests for api_set_bearer_token."""

    def test_set_bearer_token(self, api_ctx: ApiContext) -> None:
        """Setting a bearer token should add the Authorization header."""
        api_set_bearer_token(api_ctx, "abc123")
        assert api_ctx.default_headers["Authorization"] == "Bearer abc123"


class TestApiSetSslVerify:
    """Tests for api_set_ssl_verify."""

    def test_disable_ssl(self, api_ctx: ApiContext) -> None:
        """Disabling SSL should set ssl_verify to False."""
        api_set_ssl_verify(api_ctx, False)
        assert api_ctx.ssl_verify is False

    def test_enable_ssl(self, api_ctx: ApiContext) -> None:
        """Enabling SSL should set ssl_verify to True."""
        api_set_ssl_verify(api_ctx, True)
        assert api_ctx.ssl_verify is True


class TestApiSetAllowRedirects:
    """Tests for api_set_allow_redirects."""

    def test_disable_redirects(self, api_ctx: ApiContext) -> None:
        """Disabling redirects should set allow_redirects to False."""
        api_set_allow_redirects(api_ctx, False)
        assert api_ctx.allow_redirects is False

    def test_enable_redirects(self, api_ctx: ApiContext) -> None:
        """Enabling redirects should set allow_redirects to True."""
        api_set_allow_redirects(api_ctx, True)
        assert api_ctx.allow_redirects is True


class TestApiSaveCookies:
    """Tests for api_save_cookies."""

    def test_save_cookies(self, api_ctx: ApiContext) -> None:
        """Saving cookies should extract them from Set-Cookie headers."""
        api_ctx.client = MockHTTPClient()  # type: ignore[attr-defined]
        api_ctx.client.response = Response(  # type: ignore[attr-defined]
            status=200,
            headers={"Content-Type": "application/json", "Set-Cookie": "session=abc123; Path=/"},
            body=b'{"ok": true}',
            elapsed_ms=1.0,
        )
        api_send(api_ctx, "GET", "/users")
        api_save_cookies(api_ctx)
        assert api_ctx.cookies.get("session") == "abc123"

    def test_save_cookies_no_response_raises(self, api_ctx: ApiContext) -> None:
        """Saving cookies without a response should raise."""
        with pytest.raises(AssertionError, match="No response"):
            api_save_cookies(api_ctx)

    def test_save_multiple_cookies(self, api_ctx: ApiContext) -> None:
        """Saving cookies should handle multiple Set-Cookie headers."""
        api_ctx.client = MockHTTPClient()  # type: ignore[attr-defined]
        api_ctx.client.response = Response(  # type: ignore[attr-defined]
            status=200,
            headers={
                "Content-Type": "application/json",
                "Set-Cookie": "session=abc123; Path=/\ncsrf=xyz789; Path=/",
            },
            body=b'{"ok": true}',
            elapsed_ms=1.0,
        )
        api_send(api_ctx, "GET", "/users")
        api_save_cookies(api_ctx)
        assert api_ctx.cookies.get("session") == "abc123"
        assert api_ctx.cookies.get("csrf") == "xyz789"


class TestApiRemoveHeader:
    """Tests for api_remove_header."""

    def test_remove_header(self, api_ctx: ApiContext) -> None:
        """Removing a header should delete it."""
        api_set_header(api_ctx, "Authorization", "Bearer token")
        api_remove_header(api_ctx, "Authorization")
        assert "Authorization" not in api_ctx.default_headers

    def test_remove_nonexistent_header_raises(self, api_ctx: ApiContext) -> None:
        """Removing a non-existent header should raise KeyError."""
        with pytest.raises(KeyError, match="not found"):
            api_remove_header(api_ctx, "Nonexistent")

    def test_remove_header_case_insensitive(self, api_ctx: ApiContext) -> None:
        """Removing a header should work case-insensitively per RFC 7230."""
        api_set_header(api_ctx, "Content-Type", "application/json")
        api_remove_header(api_ctx, "content-type")
        assert "Content-Type" not in api_ctx.default_headers

    def test_remove_header_different_case(self, api_ctx: ApiContext) -> None:
        """Removing a header set with one case using a different case."""
        api_set_header(api_ctx, "X-Custom-Header", "value")
        api_remove_header(api_ctx, "x-custom-header")
        assert "X-Custom-Header" not in api_ctx.default_headers


class TestApiClearRequestData:
    """Tests for api_clear_request_data."""

    def test_clear_resets_request_data(self, api_ctx: ApiContext) -> None:
        """Clearing should reset headers, params, auth, cookies, and responses."""
        api_set_header(api_ctx, "Authorization", "Bearer token")
        api_set_query_param(api_ctx, "page", "1")
        api_set_basic_auth(api_ctx, "admin", "secret")
        api_ctx.cookies["session"] = "abc"
        api_send(api_ctx, "GET", "/users")

        api_clear_request_data(api_ctx)

        assert api_ctx.default_headers == {}
        assert api_ctx.query_params == {}
        assert api_ctx.auth is None
        assert api_ctx.cookies == {}
        assert api_ctx.last_request is None
        assert api_ctx.last_response is None

    def test_clear_preserves_base_config(self, api_ctx: ApiContext) -> None:
        """Clearing should preserve base_url, timeout, ssl_verify, etc."""
        api_set_base_url(api_ctx, "https://api.example.com")
        api_set_timeout(api_ctx, 30.0)
        api_set_ssl_verify(api_ctx, False)

        api_clear_request_data(api_ctx)

        assert api_ctx.base_url == "https://api.example.com"
        assert api_ctx.timeout == 30.0
        assert api_ctx.ssl_verify is False


# --- Tests for extended JSON Path assertions ---


class TestApiAssertJsonPathContains:
    """Tests for api_assert_json_path_contains."""

    def test_list_contains(self, api_ctx: ApiContext) -> None:
        """List contains the value."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"tags": ["a","b","c"]}',
            elapsed_ms=1.0,
        )
        api_assert_json_path_contains(api_ctx, "$.tags", "b")

    def test_list_not_contains_raises(self, api_ctx: ApiContext) -> None:
        """List does not contain the value."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"tags": ["a","b"]}',
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="does not contain"):
            api_assert_json_path_contains(api_ctx, "$.tags", "z")

    def test_string_contains(self, api_ctx: ApiContext) -> None:
        """String contains the substring."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"msg": "hello world"}',
            elapsed_ms=1.0,
        )
        api_assert_json_path_contains(api_ctx, "$.msg", "hello")

    def test_string_not_contains_raises(self, api_ctx: ApiContext) -> None:
        """String does not contain the substring."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"msg": "hello"}',
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="does not contain"):
            api_assert_json_path_contains(api_ctx, "$.msg", "world")

    def test_non_list_string_raises(self, api_ctx: ApiContext) -> None:
        """Non-list/string value raises."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"n": 42}',
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="not a list or string"):
            api_assert_json_path_contains(api_ctx, "$.n", "4")

    def test_no_response_raises(self, api_ctx: ApiContext) -> None:
        """No response raises."""
        with pytest.raises(AssertionError, match="No response"):
            api_assert_json_path_contains(api_ctx, "$.tags", "a")

    def test_list_contains_boolean_true(self, api_ctx: ApiContext) -> None:
        """List with boolean true should match string 'true'."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"flags": [true, false]}',
            elapsed_ms=1.0,
        )
        api_assert_json_path_contains(api_ctx, "$.flags", "true")

    def test_list_contains_boolean_false(self, api_ctx: ApiContext) -> None:
        """List with boolean false should match string 'false'."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"flags": [true, false]}',
            elapsed_ms=1.0,
        )
        api_assert_json_path_contains(api_ctx, "$.flags", "false")

    def test_list_contains_null(self, api_ctx: ApiContext) -> None:
        """List with None should match string 'null'."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"values": [null, "x"]}',
            elapsed_ms=1.0,
        )
        api_assert_json_path_contains(api_ctx, "$.values", "null")

    def test_list_not_contains_value_raises(self, api_ctx: ApiContext) -> None:
        """List without value should raise."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"items": ["a", "b"]}',
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="does not contain"):
            api_assert_json_path_contains(api_ctx, "$.items", "c")


class TestApiAssertJsonPathNotEquals:
    """Tests for api_assert_json_path_not_equals."""

    def test_not_equals_passes(self, api_ctx: ApiContext) -> None:
        """Different value passes."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"status": "ok"}',
            elapsed_ms=1.0,
        )
        api_assert_json_path_not_equals(api_ctx, "$.status", "error")

    def test_equals_raises(self, api_ctx: ApiContext) -> None:
        """Same value raises."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"status": "ok"}',
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="should not equal"):
            api_assert_json_path_not_equals(api_ctx, "$.status", "ok")

    def test_not_equals_boolean_true(self, api_ctx: ApiContext) -> None:
        """Boolean true should match string 'true' and raise."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"active": true}',
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="should not equal"):
            api_assert_json_path_not_equals(api_ctx, "$.active", "true")


class TestApiAssertJsonPathIsNull:
    """Tests for api_assert_json_path_is_null."""

    def test_is_null_passes(self, api_ctx: ApiContext) -> None:
        """Null value passes."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"deleted_at": null}',
            elapsed_ms=1.0,
        )
        api_assert_json_path_is_null(api_ctx, "$.deleted_at")

    def test_not_null_raises(self, api_ctx: ApiContext) -> None:
        """Non-null value raises."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"id": 1}',
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="expected null"):
            api_assert_json_path_is_null(api_ctx, "$.id")


class TestApiAssertJsonPathIsNotNull:
    """Tests for api_assert_json_path_is_not_null."""

    def test_not_null_passes(self, api_ctx: ApiContext) -> None:
        """Non-null value passes."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"id": 1}',
            elapsed_ms=1.0,
        )
        api_assert_json_path_is_not_null(api_ctx, "$.id")

    def test_null_raises(self, api_ctx: ApiContext) -> None:
        """Null value raises."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"x": null}',
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="expected non-null"):
            api_assert_json_path_is_not_null(api_ctx, "$.x")


class TestApiAssertJsonPathHasLength:
    """Tests for api_assert_json_path_has_length."""

    def test_list_length_matches(self, api_ctx: ApiContext) -> None:
        """List with correct length passes."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"items": [1, 2, 3]}',
            elapsed_ms=1.0,
        )
        api_assert_json_path_has_length(api_ctx, "$.items", 3)

    def test_list_length_mismatch_raises(self, api_ctx: ApiContext) -> None:
        """List with wrong length raises."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"items": [1, 2]}',
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="expected length 3"):
            api_assert_json_path_has_length(api_ctx, "$.items", 3)

    def test_string_length_matches(self, api_ctx: ApiContext) -> None:
        """String with correct length passes."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"name": "Ada"}',
            elapsed_ms=1.0,
        )
        api_assert_json_path_has_length(api_ctx, "$.name", 3)

    def test_no_length_raises(self, api_ctx: ApiContext) -> None:
        """Value without len() raises."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"n": 42}',
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="has no length"):
            api_assert_json_path_has_length(api_ctx, "$.n", 1)


class TestApiAssertJsonPathMatchesRegex:
    """Tests for api_assert_json_path_matches_regex."""

    def test_regex_matches(self, api_ctx: ApiContext) -> None:
        """Matching pattern passes."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"email": "user@test.com"}',
            elapsed_ms=1.0,
        )
        api_assert_json_path_matches_regex(api_ctx, "$.email", r"^[^@]+@[^@]+\.[^@]+$")

    def test_regex_no_match_raises(self, api_ctx: ApiContext) -> None:
        """Non-matching pattern raises."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"email": "notanemail"}',
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="does not match pattern"):
            api_assert_json_path_matches_regex(api_ctx, "$.email", r"^[^@]+@[^@]+$")

    def test_non_string_raises(self, api_ctx: ApiContext) -> None:
        """Non-string value raises."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"n": 42}',
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="not a string"):
            api_assert_json_path_matches_regex(api_ctx, "$.n", r"\d+")


# --- Tests for extended header assertions ---


class TestApiAssertHeaderContains:
    """Tests for api_assert_header_contains."""

    def test_contains_passes(self, api_ctx: ApiContext) -> None:
        """Header contains substring."""
        api_ctx.last_response = Response(
            status=200,
            headers={"Content-Type": "application/json; charset=utf-8"},
            body=b"",
            elapsed_ms=1.0,
        )
        api_assert_header_contains(api_ctx, "Content-Type", "json")

    def test_not_contains_raises(self, api_ctx: ApiContext) -> None:
        """Header does not contain substring."""
        api_ctx.last_response = Response(
            status=200,
            headers={"Content-Type": "text/html"},
            body=b"",
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="does not contain"):
            api_assert_header_contains(api_ctx, "Content-Type", "json")

    def test_missing_header_raises(self, api_ctx: ApiContext) -> None:
        """Missing header raises."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b"",
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="not found"):
            api_assert_header_contains(api_ctx, "X-Custom", "val")


class TestApiAssertHeaderNotEquals:
    """Tests for api_assert_header_not_equals."""

    def test_not_equals_passes(self, api_ctx: ApiContext) -> None:
        """Different value passes."""
        api_ctx.last_response = Response(
            status=200,
            headers={"Server": "nginx"},
            body=b"",
            elapsed_ms=1.0,
        )
        api_assert_header_not_equals(api_ctx, "Server", "Apache")

    def test_equals_raises(self, api_ctx: ApiContext) -> None:
        """Same value raises."""
        api_ctx.last_response = Response(
            status=200,
            headers={"Server": "nginx"},
            body=b"",
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="should not equal"):
            api_assert_header_not_equals(api_ctx, "Server", "nginx")


class TestApiAssertHeaderExists:
    """Tests for api_assert_header_exists."""

    def test_exists_passes(self, api_ctx: ApiContext) -> None:
        """Existing header passes."""
        api_ctx.last_response = Response(
            status=200,
            headers={"X-Request-ID": "abc123"},
            body=b"",
            elapsed_ms=1.0,
        )
        api_assert_header_exists(api_ctx, "X-Request-ID")

    def test_not_exists_raises(self, api_ctx: ApiContext) -> None:
        """Missing header raises."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b"",
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="not found"):
            api_assert_header_exists(api_ctx, "X-Request-ID")


class TestApiAssertHeaderNotExists:
    """Tests for api_assert_header_not_exists."""

    def test_not_exists_passes(self, api_ctx: ApiContext) -> None:
        """Missing header passes."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b"",
            elapsed_ms=1.0,
        )
        api_assert_header_not_exists(api_ctx, "X-Debug")

    def test_exists_raises(self, api_ctx: ApiContext) -> None:
        """Existing header raises."""
        api_ctx.last_response = Response(
            status=200,
            headers={"X-Debug": "true"},
            body=b"",
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="should not exist"):
            api_assert_header_not_exists(api_ctx, "X-Debug")


# --- Tests for send helpers ---


class TestApiSendForm:
    """Tests for api_send_form."""

    def test_send_form_sets_content_type(self, api_ctx: ApiContext) -> None:
        """Form send sets Content-Type header."""
        api_send_form(api_ctx, "POST", "/login", {"user": "admin", "pass": "123"})
        assert api_ctx.last_request is not None
        assert api_ctx.last_request.headers["Content-Type"] == "application/x-www-form-urlencoded"
        assert (
            b"user=admin" in api_ctx.last_request.body or b"pass=123" in api_ctx.last_request.body
        )


class TestApiSendJson:
    """Tests for api_send_json."""

    def test_send_json_dict_serializes(self, api_ctx: ApiContext) -> None:
        """JSON send with dict serializes to JSON."""
        api_send_json(api_ctx, "POST", "/users", {"name": "Ada", "age": 30})
        assert api_ctx.last_request is not None
        assert api_ctx.last_request.headers["Content-Type"] == "application/json"
        import json

        body = json.loads(api_ctx.last_request.body)
        assert body["name"] == "Ada"

    def test_send_json_string_passes_through(self, api_ctx: ApiContext) -> None:
        """JSON send with string passes through as-is."""
        api_send_json(api_ctx, "POST", "/users", '{"name": "Bob"}')
        assert api_ctx.last_request is not None
        assert api_ctx.last_request.headers["Content-Type"] == "application/json"


# --- Tests for variable actions ---


class TestApiUseVariableAsHeader:
    """Tests for api_use_variable_as_header."""

    def test_use_variable_as_header(self, api_ctx: ApiContext) -> None:
        """Variable value is set as header."""
        api_ctx.variables["token"] = "abc123"
        api_use_variable_as_header(api_ctx, "Authorization", "token")
        assert api_ctx.default_headers["Authorization"] == "abc123"

    def test_missing_variable_raises(self, api_ctx: ApiContext) -> None:
        """Missing variable raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            api_use_variable_as_header(api_ctx, "Authorization", "missing")

    def test_use_boolean_as_header(self, api_ctx: ApiContext) -> None:
        """Boolean variable is normalized to JSON representation."""
        api_ctx.variables["flag"] = True
        api_use_variable_as_header(api_ctx, "X-Flag", "flag")
        assert api_ctx.default_headers["X-Flag"] == "true"

    def test_use_none_as_header(self, api_ctx: ApiContext) -> None:
        """None variable is normalized to JSON representation."""
        api_ctx.variables["flag"] = None
        api_use_variable_as_header(api_ctx, "X-Flag", "flag")
        assert api_ctx.default_headers["X-Flag"] == "null"


class TestApiUseVariableAsQueryParam:
    """Tests for api_use_variable_as_query_param."""

    def test_use_variable_as_param(self, api_ctx: ApiContext) -> None:
        """Variable value is set as query param."""
        api_ctx.variables["page"] = 2
        api_use_variable_as_query_param(api_ctx, "p", "page")
        assert api_ctx.query_params["p"] == "2"

    def test_missing_variable_raises(self, api_ctx: ApiContext) -> None:
        """Missing variable raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            api_use_variable_as_query_param(api_ctx, "p", "missing")

    def test_use_boolean_as_param(self, api_ctx: ApiContext) -> None:
        """Boolean variable is normalized to JSON representation."""
        api_ctx.variables["active"] = True
        api_use_variable_as_query_param(api_ctx, "active", "active")
        assert api_ctx.query_params["active"] == "true"


class TestApiAssertVariableEquals:
    """Tests for api_assert_variable_equals."""

    def test_variable_equals_passes(self, api_ctx: ApiContext) -> None:
        """Matching variable value passes."""
        api_ctx.variables["user_id"] = 42
        api_assert_variable_equals(api_ctx, "user_id", "42")

    def test_variable_not_equals_raises(self, api_ctx: ApiContext) -> None:
        """Non-matching variable value raises."""
        api_ctx.variables["user_id"] = 42
        with pytest.raises(AssertionError, match="expected '99'"):
            api_assert_variable_equals(api_ctx, "user_id", "99")

    def test_missing_variable_raises(self, api_ctx: ApiContext) -> None:
        """Missing variable raises."""
        with pytest.raises(AssertionError, match="not found"):
            api_assert_variable_equals(api_ctx, "missing", "1")

    def test_boolean_true_equals(self, api_ctx: ApiContext) -> None:
        """Boolean True should match string 'true'."""
        api_ctx.variables["active"] = True
        api_assert_variable_equals(api_ctx, "active", "true")

    def test_boolean_false_equals(self, api_ctx: ApiContext) -> None:
        """Boolean False should match string 'false'."""
        api_ctx.variables["active"] = False
        api_assert_variable_equals(api_ctx, "active", "false")

    def test_none_equals(self, api_ctx: ApiContext) -> None:
        """None should match string 'null'."""
        api_ctx.variables["data"] = None
        api_assert_variable_equals(api_ctx, "data", "null")


class TestApiStoreResponseTime:
    """Tests for api_store_response_time."""

    def test_store_response_time(self, api_ctx: ApiContext) -> None:
        """Response time is stored."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b"",
            elapsed_ms=42.5,
        )
        api_store_response_time(api_ctx, "elapsed")
        assert api_ctx.variables["elapsed"] == 42.5

    def test_no_response_raises(self, api_ctx: ApiContext) -> None:
        """No response raises."""
        with pytest.raises(AssertionError, match="No response"):
            api_store_response_time(api_ctx, "elapsed")


# --- Tests for proxy ---


class TestApiSetProxy:
    """Tests for api_set_proxy."""

    def test_set_proxy(self, api_ctx: ApiContext) -> None:
        """Proxy URL is set for both http and https."""
        api_set_proxy(api_ctx, "http://proxy:8080")
        assert api_ctx.proxies["http"] == "http://proxy:8080"
        assert api_ctx.proxies["https"] == "http://proxy:8080"


# --- Tests for JSON Schema validation ---


class TestApiAssertJsonSchema:
    """Tests for api_assert_json_schema."""

    def test_valid_schema_passes(self, api_ctx: ApiContext) -> None:
        """Valid data passes schema validation."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"name": "Ada", "age": 30}',
            elapsed_ms=1.0,
        )
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0},
            },
            "required": ["name", "age"],
        }
        api_assert_json_schema(api_ctx, schema)

    def test_missing_required_raises(self, api_ctx: ApiContext) -> None:
        """Missing required field raises."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"name": "Ada"}',
            elapsed_ms=1.0,
        )
        schema = {
            "type": "object",
            "required": ["name", "age"],
        }
        with pytest.raises(AssertionError, match="missing required property 'age'"):
            api_assert_json_schema(api_ctx, schema)

    def test_wrong_type_raises(self, api_ctx: ApiContext) -> None:
        """Wrong type raises."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"name": 123}',
            elapsed_ms=1.0,
        )
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
            },
        }
        with pytest.raises(AssertionError, match="expected type 'string'"):
            api_assert_json_schema(api_ctx, schema)

    def test_array_items_validation(self, api_ctx: ApiContext) -> None:
        """Array items are validated."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"tags": ["a", "b", 3]}',
            elapsed_ms=1.0,
        )
        schema = {
            "type": "object",
            "properties": {
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
        }
        with pytest.raises(AssertionError, match="expected type 'string'"):
            api_assert_json_schema(api_ctx, schema)

    def test_enum_validation(self, api_ctx: ApiContext) -> None:
        """Enum constraint is validated."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"status": "unknown"}',
            elapsed_ms=1.0,
        )
        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["ok", "error"]},
            },
        }
        with pytest.raises(AssertionError, match="not in enum"):
            api_assert_json_schema(api_ctx, schema)

    def test_minimum_maximum_validation(self, api_ctx: ApiContext) -> None:
        """Minimum/maximum constraints are validated."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"age": -1}',
            elapsed_ms=1.0,
        )
        schema = {
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 0, "maximum": 120},
            },
        }
        with pytest.raises(AssertionError, match="less than minimum"):
            api_assert_json_schema(api_ctx, schema)

    def test_string_pattern_validation(self, api_ctx: ApiContext) -> None:
        """String pattern constraint is validated."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"code": "abc"}',
            elapsed_ms=1.0,
        )
        schema = {
            "type": "object",
            "properties": {
                "code": {"type": "string", "pattern": r"^\d+$"},
            },
        }
        with pytest.raises(AssertionError, match="does not match"):
            api_assert_json_schema(api_ctx, schema)

    def test_no_response_raises(self, api_ctx: ApiContext) -> None:
        """No response raises."""
        with pytest.raises(AssertionError, match="No response"):
            api_assert_json_schema(api_ctx, {"type": "object"})

    def test_bool_not_accepted_as_integer(self, api_ctx: ApiContext) -> None:
        """Boolean values must not pass integer type check (bool is int subclass)."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"active": true}',
            elapsed_ms=1.0,
        )
        schema = {
            "type": "object",
            "properties": {
                "active": {"type": "integer"},
            },
        }
        with pytest.raises(AssertionError, match=r"expected type 'integer'.*got 'bool'"):
            api_assert_json_schema(api_ctx, schema)

    def test_bool_not_accepted_as_number(self, api_ctx: ApiContext) -> None:
        """Boolean values must not pass number type check (bool is int subclass)."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"active": true}',
            elapsed_ms=1.0,
        )
        schema = {
            "type": "object",
            "properties": {
                "active": {"type": "number"},
            },
        }
        with pytest.raises(AssertionError, match=r"expected type 'number'.*got 'bool'"):
            api_assert_json_schema(api_ctx, schema)

    def test_bool_not_checked_against_minimum(self, api_ctx: ApiContext) -> None:
        """Boolean values must not be checked against minimum/maximum constraints."""
        api_ctx.last_response = Response(
            status=200,
            headers={},
            body=b'{"flag": true}',
            elapsed_ms=1.0,
        )
        schema = {
            "type": "object",
            "properties": {
                "flag": {"type": "boolean", "minimum": 0},
            },
        }
        # Should not raise - bool is valid boolean, minimum doesn't apply
        api_assert_json_schema(api_ctx, schema)


class TestApiAssertJsonPathTypeBoolInt:
    """Regression tests for bool/int confusion in api_assert_json_path_type."""

    def test_bool_not_accepted_as_int(self, api_ctx: ApiContext) -> None:
        """Boolean values must not pass int type check."""
        api_ctx.last_response = Response(
            status=200,
            headers={"Content-Type": "application/json"},
            body=b'{"flag": true}',
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match=r"expected type 'int'.*got 'bool'"):
            api_assert_json_path_type(api_ctx, "$.flag", "int")

    def test_bool_not_accepted_as_float(self, api_ctx: ApiContext) -> None:
        """Boolean values must not pass float type check."""
        api_ctx.last_response = Response(
            status=200,
            headers={"Content-Type": "application/json"},
            body=b'{"flag": true}',
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match=r"expected type 'float'.*got 'bool'"):
            api_assert_json_path_type(api_ctx, "$.flag", "float")


class TestApiHeaderCaseInsensitive:
    """Regression tests for case-insensitive HTTP header lookups (RFC 7230)."""

    def test_header_equals_case_insensitive(self, api_ctx: ApiContext) -> None:
        """Header lookup should be case-insensitive."""
        api_ctx.last_response = Response(
            status=200,
            headers={"content-type": "application/json"},
            body=b'{"ok": true}',
            elapsed_ms=1.0,
        )
        # Should not raise despite case mismatch
        api_assert_header_equals(api_ctx, "Content-Type", "application/json")
        api_assert_header_equals(api_ctx, "CONTENT-TYPE", "application/json")
        api_assert_header_equals(api_ctx, "content-type", "application/json")

    def test_header_contains_case_insensitive(self, api_ctx: ApiContext) -> None:
        """Header contains check should be case-insensitive."""
        api_ctx.last_response = Response(
            status=200,
            headers={"x-custom-header": "some-value"},
            body=b"{}",
            elapsed_ms=1.0,
        )
        api_assert_header_contains(api_ctx, "X-Custom-Header", "some")
        api_assert_header_contains(api_ctx, "X-CUSTOM-HEADER", "value")

    def test_header_not_equals_case_insensitive(self, api_ctx: ApiContext) -> None:
        """Header not-equals check should be case-insensitive."""
        api_ctx.last_response = Response(
            status=200,
            headers={"X-Total-Count": "42"},
            body=b"{}",
            elapsed_ms=1.0,
        )
        api_assert_header_not_equals(api_ctx, "x-total-count", "99")

    def test_header_exists_case_insensitive(self, api_ctx: ApiContext) -> None:
        """Header exists check should be case-insensitive."""
        api_ctx.last_response = Response(
            status=200,
            headers={"ETag": "abc123"},
            body=b"{}",
            elapsed_ms=1.0,
        )
        api_assert_header_exists(api_ctx, "etag")
        api_assert_header_exists(api_ctx, "ETAG")
        api_assert_header_exists(api_ctx, "ETag")

    def test_header_not_exists_case_insensitive(self, api_ctx: ApiContext) -> None:
        """Header not-exists check should be case-insensitive."""
        api_ctx.last_response = Response(
            status=200,
            headers={"ETag": "abc123"},
            body=b"{}",
            elapsed_ms=1.0,
        )
        with pytest.raises(AssertionError, match="should not exist"):
            api_assert_header_not_exists(api_ctx, "etag")

    def test_header_not_exists_passes_case_insensitive(self, api_ctx: ApiContext) -> None:
        """Header not-exists should pass when header is absent regardless of case."""
        api_ctx.last_response = Response(
            status=200,
            headers={"Content-Type": "application/json"},
            body=b"{}",
            elapsed_ms=1.0,
        )
        api_assert_header_not_exists(api_ctx, "X-Missing")

    def test_store_header_case_insensitive(self, api_ctx: ApiContext) -> None:
        """Storing a header value should work case-insensitively."""
        api_ctx.last_response = Response(
            status=200,
            headers={"X-Auth-Token": "secret123"},
            body=b"{}",
            elapsed_ms=1.0,
        )
        api_store_header(api_ctx, "x-auth-token", "token_var")
        assert api_ctx.variables["token_var"] == "secret123"

    def test_content_type_case_insensitive(self, api_ctx: ApiContext) -> None:
        """Content-Type assertion should work case-insensitively."""
        api_ctx.last_response = Response(
            status=200,
            headers={"content-type": "application/json; charset=utf-8"},
            body=b"{}",
            elapsed_ms=1.0,
        )
        api_assert_content_type_contains(api_ctx, "application/json")


class TestJsonPathMissingKeyRaisesAssertionError:
    """Regression: API functions using JsonPath must raise AssertionError for missing paths."""

    @pytest.fixture()
    def ctx_with_json(self, api_ctx: ApiContext) -> ApiContext:
        """Context with a JSON response containing nested data."""
        api_ctx.last_response = Response(
            status=200,
            headers={"Content-Type": "application/json"},
            body=b'{"name": "Ada", "age": 30, "items": [1, 2]}',
            elapsed_ms=1.0,
        )
        return api_ctx

    def test_json_path_equals_missing_raises_assertion(self, ctx_with_json: ApiContext) -> None:
        with pytest.raises(AssertionError, match="does not exist"):
            api_assert_json_path_equals(ctx_with_json, "$.nonexistent", "x")

    def test_json_path_type_missing_raises_assertion(self, ctx_with_json: ApiContext) -> None:
        with pytest.raises(AssertionError, match="does not exist"):
            api_assert_json_path_type(ctx_with_json, "$.nonexistent", "str")

    def test_json_path_exists_missing_raises_assertion(self, ctx_with_json: ApiContext) -> None:
        with pytest.raises(AssertionError, match="does not exist"):
            api_assert_json_path_exists(ctx_with_json, "$.nonexistent")

    def test_store_json_path_missing_raises_assertion(self, ctx_with_json: ApiContext) -> None:
        with pytest.raises(AssertionError, match="does not exist"):
            api_store_json_path(ctx_with_json, "$.nonexistent", "var")

    def test_json_path_contains_missing_raises_assertion(self, ctx_with_json: ApiContext) -> None:
        with pytest.raises(AssertionError, match="does not exist"):
            api_assert_json_path_contains(ctx_with_json, "$.nonexistent", "x")

    def test_json_path_not_equals_missing_raises_assertion(self, ctx_with_json: ApiContext) -> None:
        with pytest.raises(AssertionError, match="does not exist"):
            api_assert_json_path_not_equals(ctx_with_json, "$.nonexistent", "x")

    def test_json_path_is_null_missing_raises_assertion(self, ctx_with_json: ApiContext) -> None:
        with pytest.raises(AssertionError, match="does not exist"):
            api_assert_json_path_is_null(ctx_with_json, "$.nonexistent")

    def test_json_path_is_not_null_missing_raises_assertion(
        self, ctx_with_json: ApiContext,
    ) -> None:
        with pytest.raises(AssertionError, match="does not exist"):
            api_assert_json_path_is_not_null(ctx_with_json, "$.nonexistent")

    def test_json_path_has_length_missing_raises_assertion(self, ctx_with_json: ApiContext) -> None:
        with pytest.raises(AssertionError, match="does not exist"):
            api_assert_json_path_has_length(ctx_with_json, "$.nonexistent", 3)

    def test_json_path_matches_regex_missing_raises_assertion(
        self, ctx_with_json: ApiContext,
    ) -> None:
        with pytest.raises(AssertionError, match="does not exist"):
            api_assert_json_path_matches_regex(ctx_with_json, "$.nonexistent", ".*")


class TestInvalidJsonBodyRaisesAssertionError:
    """Regression: API functions should raise AssertionError for invalid JSON bodies."""

    @pytest.fixture()
    def ctx_with_invalid_json(self, api_ctx: ApiContext) -> ApiContext:
        """Context with a non-JSON response body."""
        api_ctx.last_response = Response(
            status=200,
            headers={"Content-Type": "text/plain"},
            body=b"not valid json {{{",
            elapsed_ms=1.0,
        )
        return api_ctx

    def test_assert_json_valid_invalid_body_raises_assertion(
        self, ctx_with_invalid_json: ApiContext,
    ) -> None:
        with pytest.raises(AssertionError, match="not valid JSON"):
            api_assert_json_valid(ctx_with_invalid_json)

    def test_json_path_equals_invalid_body_raises_assertion(
        self, ctx_with_invalid_json: ApiContext,
    ) -> None:
        with pytest.raises(AssertionError, match="not valid JSON"):
            api_assert_json_path_equals(ctx_with_invalid_json, "$.name", "x")

    def test_json_path_exists_invalid_body_raises_assertion(
        self, ctx_with_invalid_json: ApiContext,
    ) -> None:
        with pytest.raises(AssertionError, match="not valid JSON"):
            api_assert_json_path_exists(ctx_with_invalid_json, "$.name")

    def test_json_path_type_invalid_body_raises_assertion(
        self, ctx_with_invalid_json: ApiContext,
    ) -> None:
        with pytest.raises(AssertionError, match="not valid JSON"):
            api_assert_json_path_type(ctx_with_invalid_json, "$.name", "str")

    def test_store_json_path_invalid_body_raises_assertion(
        self, ctx_with_invalid_json: ApiContext,
    ) -> None:
        with pytest.raises(AssertionError, match="not valid JSON"):
            api_store_json_path(ctx_with_invalid_json, "$.name", "var")

    def test_json_path_contains_invalid_body_raises_assertion(
        self, ctx_with_invalid_json: ApiContext,
    ) -> None:
        with pytest.raises(AssertionError, match="not valid JSON"):
            api_assert_json_path_contains(ctx_with_invalid_json, "$.name", "x")

    def test_json_path_not_equals_invalid_body_raises_assertion(
        self, ctx_with_invalid_json: ApiContext,
    ) -> None:
        with pytest.raises(AssertionError, match="not valid JSON"):
            api_assert_json_path_not_equals(ctx_with_invalid_json, "$.name", "x")

    def test_json_path_is_null_invalid_body_raises_assertion(
        self, ctx_with_invalid_json: ApiContext,
    ) -> None:
        with pytest.raises(AssertionError, match="not valid JSON"):
            api_assert_json_path_is_null(ctx_with_invalid_json, "$.name")

    def test_json_path_is_not_null_invalid_body_raises_assertion(
        self, ctx_with_invalid_json: ApiContext,
    ) -> None:
        with pytest.raises(AssertionError, match="not valid JSON"):
            api_assert_json_path_is_not_null(ctx_with_invalid_json, "$.name")

    def test_json_path_has_length_invalid_body_raises_assertion(
        self, ctx_with_invalid_json: ApiContext,
    ) -> None:
        with pytest.raises(AssertionError, match="not valid JSON"):
            api_assert_json_path_has_length(ctx_with_invalid_json, "$.name", 3)

    def test_json_path_matches_regex_invalid_body_raises_assertion(
        self, ctx_with_invalid_json: ApiContext,
    ) -> None:
        with pytest.raises(AssertionError, match="not valid JSON"):
            api_assert_json_path_matches_regex(ctx_with_invalid_json, "$.name", ".*")

    def test_json_schema_invalid_body_raises_assertion(
        self, ctx_with_invalid_json: ApiContext,
    ) -> None:
        with pytest.raises(AssertionError, match="not valid JSON"):
            api_assert_json_schema(ctx_with_invalid_json, {"type": "object"})


class TestBug10StepResponseMatchesSchemaInvalidJson:
    """Regression tests for Bug 10: step_response_matches_schema should raise
    AssertionError, not json.JSONDecodeError, when schema text is invalid JSON."""

    def test_invalid_schema_text_raises_assertion_error(self) -> None:
        from types import SimpleNamespace

        from steplib.modules.api.steps import step_response_matches_schema

        ctx = SimpleNamespace()
        ctx.steplib = SimpleNamespace()
        ctx.text = "{invalid json"
        with pytest.raises(AssertionError, match="Invalid JSON schema in step text"):
            step_response_matches_schema(ctx)


class TestBug18InvalidRegexPattern:
    """Regression tests for Bug 18: api_assert_json_path_matches_regex should
    raise AssertionError, not re.error, when the regex pattern is invalid."""

    def test_invalid_regex_raises_assertion_error(self) -> None:
        from steplib.modules.api.actions import api_assert_json_path_matches_regex
        from steplib.modules.api.client import Response

        ctx = ApiContext()
        ctx.last_response = Response(status=200, headers={}, body=b'{"name": "test"}')
        with pytest.raises(AssertionError, match="Invalid regex pattern"):
            api_assert_json_path_matches_regex(ctx, "$.name", "[invalid(")


class TestBug19NonNumericStatusCodes:
    """Regression tests for Bug 19: step_response_status_in should raise
    AssertionError, not ValueError, when status codes are non-numeric."""

    def test_non_numeric_status_raises_assertion_error(self) -> None:
        from types import SimpleNamespace

        from steplib.modules.api.steps import step_response_status_in

        ctx = SimpleNamespace()
        ctx.steplib = SimpleNamespace()
        with pytest.raises(AssertionError, match="Invalid status code list"):
            step_response_status_in(ctx, "ok, 200")


class TestBug20InvalidSchemaPattern:
    """Regression tests for Bug 20: api_assert_json_schema should raise
    AssertionError, not re.error, when the schema contains an invalid regex
    pattern in the 'pattern' field."""

    def test_invalid_schema_pattern_raises_assertion_error(self) -> None:
        from steplib.modules.api.actions import api_assert_json_schema
        from steplib.modules.api.client import Response

        ctx = ApiContext()
        ctx.last_response = Response(
            status=200, headers={}, body=b'{"name": "test"}'
        )
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "pattern": "[invalid("}
            },
        }
        with pytest.raises(AssertionError, match="Invalid regex pattern"):
            api_assert_json_schema(ctx, schema)


class TestBug36ApiExpectedNormalization:
    """Regression tests for Bug 36: api_assert_json_path_equals,
    api_assert_json_path_not_equals, and api_assert_variable_equals should
    normalize the expected/value parameter using _normalize_json_value so
    that non-string inputs (bool, None) are compared using JSON-style
    lowercase representation."""

    def test_json_path_equals_expected_as_bool_true(self, api_ctx: ApiContext) -> None:
        api_ctx.last_response = Response(
            status=200, headers={}, body=b'{"active": true}', elapsed_ms=1.0
        )
        api_assert_json_path_equals(api_ctx, "$.active", True)  # type: ignore[arg-type]

    def test_json_path_equals_expected_as_bool_false(self, api_ctx: ApiContext) -> None:
        api_ctx.last_response = Response(
            status=200, headers={}, body=b'{"active": false}', elapsed_ms=1.0
        )
        api_assert_json_path_equals(api_ctx, "$.active", False)  # type: ignore[arg-type]

    def test_json_path_equals_expected_as_none(self, api_ctx: ApiContext) -> None:
        api_ctx.last_response = Response(
            status=200, headers={}, body=b'{"data": null}', elapsed_ms=1.0
        )
        api_assert_json_path_equals(api_ctx, "$.data", None)  # type: ignore[arg-type]

    def test_json_path_not_equals_expected_as_bool_false(self, api_ctx: ApiContext) -> None:
        api_ctx.last_response = Response(
            status=200, headers={}, body=b'{"active": true}', elapsed_ms=1.0
        )
        api_assert_json_path_not_equals(api_ctx, "$.active", False)  # type: ignore[arg-type]

    def test_variable_equals_expected_as_bool_true(self, api_ctx: ApiContext) -> None:
        api_ctx.variables["active"] = True
        api_assert_variable_equals(api_ctx, "active", True)  # type: ignore[arg-type]

    def test_variable_equals_expected_as_bool_false(self, api_ctx: ApiContext) -> None:
        api_ctx.variables["active"] = False
        api_assert_variable_equals(api_ctx, "active", False)  # type: ignore[arg-type]

    def test_variable_equals_expected_as_none(self, api_ctx: ApiContext) -> None:
        api_ctx.variables["data"] = None
        api_assert_variable_equals(api_ctx, "data", None)  # type: ignore[arg-type]
