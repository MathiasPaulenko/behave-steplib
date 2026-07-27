"""Pure action functions for the API module.

These functions contain the actual logic and are called by step definitions.
They operate on ``ApiContext`` and are fully testable without behave.
"""

from __future__ import annotations

from typing import Any

from steplib.modules.api.client import Request, Response
from steplib.modules.api.context import ApiContext
from steplib.modules.api.transforms import JsonPath, Url, parse_json


def api_set_base_url(api_ctx: ApiContext, url: str) -> None:
    """Set the base URL for subsequent requests."""
    api_ctx.base_url = url


def api_set_header(api_ctx: ApiContext, name: str, value: str) -> None:
    """Set a default header that will be sent with every request."""
    api_ctx.default_headers[name] = value


def api_set_timeout(api_ctx: ApiContext, seconds: float) -> None:
    """Set the request timeout in seconds."""
    api_ctx.timeout = seconds


def api_send(
    api_ctx: ApiContext,
    method: str,
    url: str,
    body: str | bytes | None = None,
) -> Response:
    """Send an HTTP request and store the response in ``api_ctx``.

    Args:
        api_ctx: The API context to operate on.
        method: HTTP method (e.g. ``"GET"``, ``"POST"``).
        url: URL (relative URLs are resolved against ``base_url``).
        body: Optional request body as string or bytes.

    Returns:
        The ``Response`` object.

    Raises:
        RuntimeError: If no HTTP client is configured.

    """
    if api_ctx.client is None:
        raise RuntimeError("No HTTP client configured in ApiContext.")

    resolved_url = str(Url(url, base_url=api_ctx.base_url))
    body_bytes: bytes | None = None
    if body is not None:
        body_bytes = body.encode("utf-8") if isinstance(body, str) else body

    headers = dict(api_ctx.default_headers)

    req = Request(
        method=method.upper(),
        url=resolved_url,
        headers=headers,
        body=body_bytes,
    )
    api_ctx.last_request = req

    response = api_ctx.client.request(
        method=req.method,
        url=req.url,
        headers=req.headers,
        body=req.body,
        timeout=api_ctx.timeout,
    )
    api_ctx.last_response = response
    return response


def api_assert_status(api_ctx: ApiContext, expected: int) -> None:
    """Assert that the last response status matches *expected*.

    Raises:
        AssertionError: If the status does not match or no response exists.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    actual = api_ctx.last_response.status
    if actual != expected:
        raise AssertionError(
            f"Expected status {expected}, got {actual}."
        )


def api_assert_body_contains(api_ctx: ApiContext, text: str) -> None:
    """Assert that the last response body contains *text*.

    Args:
        api_ctx: The API context to operate on.
        text: The substring to search for.

    Raises:
        AssertionError: If no response exists or the body does not contain *text*.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    if text not in api_ctx.last_response.text:
        raise AssertionError(
            f"Response body does not contain '{text}'. "
            f"Body: {api_ctx.last_response.text[:200]}"
        )


def api_assert_json_valid(api_ctx: ApiContext) -> None:
    """Assert that the last response body is valid JSON.

    Args:
        api_ctx: The API context to operate on.

    Raises:
        AssertionError: If no response exists or the body is not valid JSON.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    try:
        parse_json(api_ctx.last_response.text)
    except Exception as exc:
        raise AssertionError(f"Response body is not valid JSON: {exc}") from exc


def api_assert_json_path_equals(api_ctx: ApiContext, path: str, expected: str) -> None:
    """Assert that a JSON path in the last response equals *expected*.

    Args:
        api_ctx: The API context to operate on.
        path: A JSONPath expression starting with ``$``.
        expected: The expected value (compared as string).

    Raises:
        AssertionError: If no response exists or the value does not match.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    data = parse_json(api_ctx.last_response.text)
    actual = JsonPath(path).evaluate(data)
    if str(actual) != str(expected):
        raise AssertionError(
            f"JSON path '{path}': expected '{expected}', got '{actual}'."
        )


def api_assert_header_equals(api_ctx: ApiContext, name: str, expected: str) -> None:
    """Assert that a response header equals *expected*.

    Args:
        api_ctx: The API context to operate on.
        name: The header name.
        expected: The expected header value.

    Raises:
        AssertionError: If no response exists, the header is missing, or the
            value does not match.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    actual = api_ctx.last_response.headers.get(name)
    if actual is None:
        raise AssertionError(f"Response header '{name}' not found.")
    if actual != expected:
        raise AssertionError(
            f"Response header '{name}': expected '{expected}', got '{actual}'."
        )


def api_store(api_ctx: ApiContext, variable: str, value: Any) -> None:
    """Store a *value* under *variable* name in the API context.

    Args:
        api_ctx: The API context to operate on.
        variable: The variable name.
        value: The value to store.

    """
    api_ctx.variables[variable] = value


def api_store_response_body(api_ctx: ApiContext, variable: str) -> None:
    """Store the last response body as *variable*.

    Args:
        api_ctx: The API context to operate on.
        variable: The variable name to store the body under.

    Raises:
        AssertionError: If no response exists.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    api_ctx.variables[variable] = api_ctx.last_response.text
