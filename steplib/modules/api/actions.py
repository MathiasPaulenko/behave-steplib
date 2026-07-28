"""Pure action functions for the API module.

These functions contain the actual logic and are called by step definitions.
They operate on ``ApiContext`` and are fully testable without behave.
"""

from __future__ import annotations

from typing import Any

from steplib.modules.api.client import Request, Response
from steplib.modules.api.context import ApiContext
from steplib.modules.api.transforms import JsonPath, Url, parse_json


def _parse_response_json(api_ctx: ApiContext) -> Any:
    """Parse the last response body as JSON, raising AssertionError on failure.

    Raises:
        AssertionError: If the response body is not valid JSON.

    """
    try:
        return parse_json(api_ctx.last_response.text)  # type: ignore[union-attr]
    except Exception as exc:
        raise AssertionError(f"Response body is not valid JSON: {exc}") from exc


def _get_header_ci(headers: dict[str, str], name: str) -> str | None:
    """Case-insensitive header lookup.

    HTTP header names are case-insensitive per RFC 7230.
    """
    lower_name = name.lower()
    for key, value in headers.items():
        if key.lower() == lower_name:
            return value
    return None


def _header_exists_ci(headers: dict[str, str], name: str) -> bool:
    """Case-insensitive header existence check.

    HTTP header names are case-insensitive per RFC 7230.
    """
    lower_name = name.lower()
    return any(key.lower() == lower_name for key in headers)


def _normalize_json_value(value: Any) -> str:
    """Normalize a value to its JSON string representation for comparison.

    Python's ``str(True)`` returns ``"True"``, but JSON uses lowercase
    ``"true"``.  This helper ensures booleans and ``None`` are compared
    using their JSON representation so that user-provided string values
    like ``"true"`` or ``"false"`` match correctly.
    """
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    return str(value)


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
    *,
    params: dict[str, str] | None = None,
    extra_headers: dict[str, str] | None = None,
) -> Response:
    """Send an HTTP request and store the response in ``api_ctx``.

    Args:
        api_ctx: The API context to operate on.
        method: HTTP method (e.g. ``"GET"``, ``"POST"``).
        url: URL (relative URLs are resolved against ``base_url``).
        body: Optional request body as string or bytes.
        params: Optional per-request query params (overrides context defaults).
        extra_headers: Optional per-request headers merged with defaults.

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
    if extra_headers:
        headers.update(extra_headers)

    req = Request(
        method=method.upper(),
        url=resolved_url,
        headers=headers,
        body=body_bytes,
    )
    api_ctx.last_request = req

    request_params = params if params is not None else (api_ctx.query_params or None)

    response = api_ctx.client.request(
        method=req.method,
        url=req.url,
        headers=req.headers,
        body=req.body,
        timeout=api_ctx.timeout,
        params=request_params,
        auth=api_ctx.auth,
        cookies=api_ctx.cookies or None,
        allow_redirects=api_ctx.allow_redirects,
        verify=api_ctx.ssl_verify,
        proxies=api_ctx.proxies or None,
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
        raise AssertionError(f"Expected status {expected}, got {actual}.")


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
            f"Response body does not contain '{text}'. Body: {api_ctx.last_response.text[:200]}"
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
    _parse_response_json(api_ctx)


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
    data = _parse_response_json(api_ctx)
    try:
        actual = JsonPath(path).evaluate(data)
    except KeyError as exc:
        raise AssertionError(f"JSON path '{path}' does not exist: {exc}.") from exc
    if _normalize_json_value(actual) != _normalize_json_value(expected):
        raise AssertionError(f"JSON path '{path}': expected '{expected}', got '{actual}'.")


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
    actual = _get_header_ci(api_ctx.last_response.headers, name)
    if actual is None:
        raise AssertionError(f"Response header '{name}' not found.")
    if actual != expected:
        raise AssertionError(f"Response header '{name}': expected '{expected}', got '{actual}'.")


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


# --- Query parameters ---


def api_set_query_param(api_ctx: ApiContext, name: str, value: str) -> None:
    """Set a default query parameter sent with every request.

    Args:
        api_ctx: The API context to operate on.
        name: The query parameter name.
        value: The query parameter value.

    """
    api_ctx.query_params[name] = value


def api_remove_query_param(api_ctx: ApiContext, name: str) -> None:
    """Remove a query parameter from the default params.

    Args:
        api_ctx: The API context to operate on.
        name: The query parameter name to remove.

    Raises:
        KeyError: If the parameter does not exist.

    """
    if name not in api_ctx.query_params:
        raise KeyError(f"Query parameter '{name}' not found.")
    del api_ctx.query_params[name]


# --- Authentication ---


def api_set_basic_auth(api_ctx: ApiContext, username: str, password: str) -> None:
    """Set basic authentication credentials for subsequent requests.

    Args:
        api_ctx: The API context to operate on.
        username: The username for basic auth.
        password: The password for basic auth.

    """
    api_ctx.auth = (username, password)


def api_set_bearer_token(api_ctx: ApiContext, token: str) -> None:
    """Set a Bearer token in the Authorization header.

    Args:
        api_ctx: The API context to operate on.
        token: The bearer token value.

    """
    api_ctx.default_headers["Authorization"] = f"Bearer {token}"


# --- SSL and redirects ---


def api_set_ssl_verify(api_ctx: ApiContext, verify: bool) -> None:
    """Enable or disable SSL certificate verification.

    Args:
        api_ctx: The API context to operate on.
        verify: Whether to verify SSL certificates.

    """
    api_ctx.ssl_verify = verify


def api_set_allow_redirects(api_ctx: ApiContext, allow: bool) -> None:
    """Enable or disable following redirects.

    Args:
        api_ctx: The API context to operate on.
        allow: Whether to follow redirects.

    """
    api_ctx.allow_redirects = allow


# --- Cookies ---


def api_save_cookies(api_ctx: ApiContext) -> None:
    """Extract cookies from the last response and store them in the context.

    Args:
        api_ctx: The API context to operate on.

    Raises:
        AssertionError: If no response exists.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    for name, value in api_ctx.last_response.headers.items():
        if name.lower() == "set-cookie":
            for cookie_value in value.split("\n"):
                parts = cookie_value.split(";")[0].split("=", 1)
                if len(parts) == 2:
                    api_ctx.cookies[parts[0].strip()] = parts[1].strip()


# --- Header management ---


def api_remove_header(api_ctx: ApiContext, name: str) -> None:
    """Remove a default header from the context.

    Header lookup is case-insensitive per RFC 7230.

    Args:
        api_ctx: The API context to operate on.
        name: The header name to remove.

    Raises:
        KeyError: If the header does not exist.

    """
    lower_name = name.lower()
    for key in api_ctx.default_headers:
        if key.lower() == lower_name:
            del api_ctx.default_headers[key]
            return
    raise KeyError(f"Header '{name}' not found.")


# --- Request lifecycle ---


def api_clear_request_data(api_ctx: ApiContext) -> None:
    """Reset request-specific data: headers, params, auth, cookies, body.

    Keeps base_url, timeout, ssl_verify, allow_redirects, and proxies.

    Args:
        api_ctx: The API context to operate on.

    """
    api_ctx.default_headers.clear()
    api_ctx.query_params.clear()
    api_ctx.auth = None
    api_ctx.cookies.clear()
    api_ctx.last_request = None
    api_ctx.last_response = None


# --- Extended assertions ---


def api_assert_status_in(api_ctx: ApiContext, expected: list[int]) -> None:
    """Assert that the last response status is one of the expected values.

    Args:
        api_ctx: The API context to operate on.
        expected: A list of acceptable status codes.

    Raises:
        AssertionError: If no response exists or the status is not in the list.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    actual = api_ctx.last_response.status
    if actual not in expected:
        raise AssertionError(f"Expected status to be one of {expected}, got {actual}.")


def api_assert_body_not_contains(api_ctx: ApiContext, text: str) -> None:
    """Assert that the last response body does NOT contain *text*.

    Args:
        api_ctx: The API context to operate on.
        text: The substring that should not be present.

    Raises:
        AssertionError: If no response exists or the body contains *text*.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    if text in api_ctx.last_response.text:
        raise AssertionError(
            f"Response body should not contain '{text}'. Body: {api_ctx.last_response.text[:200]}"
        )


def api_assert_json_path_exists(api_ctx: ApiContext, path: str) -> None:
    """Assert that a JSON path exists in the last response.

    Args:
        api_ctx: The API context to operate on.
        path: A JSONPath expression starting with ``$``.

    Raises:
        AssertionError: If no response exists or the path does not exist.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    data = _parse_response_json(api_ctx)
    try:
        JsonPath(path).evaluate(data)
    except KeyError as exc:
        raise AssertionError(f"JSON path '{path}' does not exist: {exc}.") from exc


def api_assert_json_path_type(api_ctx: ApiContext, path: str, expected_type: str) -> None:
    """Assert that the value at a JSON path is of a specific type.

    Args:
        api_ctx: The API context to operate on.
        path: A JSONPath expression starting with ``$``.
        expected_type: One of ``"str"``, ``"int"``, ``"float"``, ``"bool"``,
            ``"list"``, ``"dict"``, ``"NoneType"``.

    Raises:
        AssertionError: If no response exists or the type does not match.
        ValueError: If *expected_type* is not a recognized type name.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    type_map = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
        "NoneType": type(None),
    }
    if expected_type not in type_map:
        raise ValueError(f"Unsupported type '{expected_type}'. Valid types: {sorted(type_map)}")
    data = _parse_response_json(api_ctx)
    try:
        actual = JsonPath(path).evaluate(data)
    except KeyError as exc:
        raise AssertionError(f"JSON path '{path}' does not exist: {exc}.") from exc
    # In Python, bool is a subclass of int, so we must explicitly
    # exclude bool when checking for int or float types.
    if expected_type in ("int", "float") and isinstance(actual, bool):
        raise AssertionError(f"JSON path '{path}': expected type '{expected_type}', got 'bool'.")
    if not isinstance(actual, type_map[expected_type]):
        raise AssertionError(
            f"JSON path '{path}': expected type '{expected_type}', got '{type(actual).__name__}'."
        )


def api_assert_content_type(api_ctx: ApiContext, expected: str) -> None:
    """Assert that the Content-Type response header equals *expected*.

    Args:
        api_ctx: The API context to operate on.
        expected: The expected content type value.

    Raises:
        AssertionError: If no response exists or the content type does not match.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    actual = _get_header_ci(api_ctx.last_response.headers, "Content-Type") or ""
    if actual != expected:
        raise AssertionError(f"Expected Content-Type '{expected}', got '{actual}'.")


def api_assert_content_type_contains(api_ctx: ApiContext, substring: str) -> None:
    """Assert that the Content-Type response header contains *substring*.

    Args:
        api_ctx: The API context to operate on.
        substring: The substring to search for in the Content-Type header.

    Raises:
        AssertionError: If no response exists or the content type does not contain the substring.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    actual = _get_header_ci(api_ctx.last_response.headers, "Content-Type") or ""
    if substring not in actual:
        raise AssertionError(f"Content-Type '{actual}' does not contain '{substring}'.")


def api_assert_response_time_less_than(api_ctx: ApiContext, seconds: float) -> None:
    """Assert that the last response took less than *seconds* seconds.

    Args:
        api_ctx: The API context to operate on.
        seconds: The maximum acceptable response time in seconds.

    Raises:
        AssertionError: If no response exists or the response was too slow.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    elapsed_s = api_ctx.last_response.elapsed_ms / 1000.0
    if elapsed_s >= seconds:
        raise AssertionError(f"Response time {elapsed_s:.3f}s is not less than {seconds}s.")


def api_assert_response_time_greater_than(api_ctx: ApiContext, seconds: float) -> None:
    """Assert that the last response took more than *seconds* seconds.

    Args:
        api_ctx: The API context to operate on.
        seconds: The minimum acceptable response time in seconds.

    Raises:
        AssertionError: If no response exists or the response was too fast.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    elapsed_s = api_ctx.last_response.elapsed_ms / 1000.0
    if elapsed_s <= seconds:
        raise AssertionError(f"Response time {elapsed_s:.3f}s is not greater than {seconds}s.")


def api_assert_response_time_between(api_ctx: ApiContext, min_s: float, max_s: float) -> None:
    """Assert that the last response time is between *min_s* and *max_s* seconds.

    Args:
        api_ctx: The API context to operate on.
        min_s: The minimum acceptable response time in seconds.
        max_s: The maximum acceptable response time in seconds.

    Raises:
        AssertionError: If no response exists or the response time is out of range.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    elapsed_s = api_ctx.last_response.elapsed_ms / 1000.0
    if not (min_s <= elapsed_s <= max_s):
        raise AssertionError(
            f"Response time {elapsed_s:.3f}s is not between {min_s}s and {max_s}s."
        )


# --- Extended store operations ---


def api_store_json_path(api_ctx: ApiContext, path: str, variable: str) -> None:
    """Store the value at a JSON path from the last response as *variable*.

    Args:
        api_ctx: The API context to operate on.
        path: A JSONPath expression starting with ``$``.
        variable: The variable name to store the value under.

    Raises:
        AssertionError: If no response exists.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    data = _parse_response_json(api_ctx)
    try:
        api_ctx.variables[variable] = JsonPath(path).evaluate(data)
    except KeyError as exc:
        raise AssertionError(f"JSON path '{path}' does not exist: {exc}.") from exc


def api_store_header(api_ctx: ApiContext, name: str, variable: str) -> None:
    """Store a response header value as *variable*.

    Args:
        api_ctx: The API context to operate on.
        name: The header name.
        variable: The variable name to store the header value under.

    Raises:
        AssertionError: If no response exists or the header is missing.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    value = _get_header_ci(api_ctx.last_response.headers, name)
    if value is None:
        raise AssertionError(f"Response header '{name}' not found.")
    api_ctx.variables[variable] = value


def api_store_status(api_ctx: ApiContext, variable: str) -> None:
    """Store the last response status code as *variable*.

    Args:
        api_ctx: The API context to operate on.
        variable: The variable name to store the status code under.

    Raises:
        AssertionError: If no response exists.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    api_ctx.variables[variable] = api_ctx.last_response.status


# --- Extended JSON Path assertions ---


def api_assert_json_path_contains(api_ctx: ApiContext, path: str, value: str) -> None:
    """Assert that a JSON path value contains *value* (for lists or strings).

    Args:
        api_ctx: The API context to operate on.
        path: A JSONPath expression starting with ``$``.
        value: The value that should be contained.

    Raises:
        AssertionError: If no response exists or the value is not contained.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    data = _parse_response_json(api_ctx)
    try:
        actual = JsonPath(path).evaluate(data)
    except KeyError as exc:
        raise AssertionError(f"JSON path '{path}' does not exist: {exc}.") from exc
    if isinstance(actual, list):
        normalized_value = _normalize_json_value(value)
        if normalized_value not in [_normalize_json_value(v) for v in actual]:
            raise AssertionError(
                f"JSON path '{path}': list does not contain '{value}'. Items: {actual}"
            )
    elif isinstance(actual, str):
        if value not in actual:
            raise AssertionError(
                f"JSON path '{path}': string does not contain '{value}'. Value: {actual}"
            )
    else:
        raise AssertionError(
            f"JSON path '{path}': value of type '{type(actual).__name__}' "
            f"is not a list or string, cannot check contains."
        )


def api_assert_json_path_not_equals(api_ctx: ApiContext, path: str, value: str) -> None:
    """Assert that a JSON path value does NOT equal *value*.

    Args:
        api_ctx: The API context to operate on.
        path: A JSONPath expression starting with ``$``.
        value: The value that should not match.

    Raises:
        AssertionError: If no response exists or the value matches.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    data = _parse_response_json(api_ctx)
    try:
        actual = JsonPath(path).evaluate(data)
    except KeyError as exc:
        raise AssertionError(f"JSON path '{path}' does not exist: {exc}.") from exc
    if _normalize_json_value(actual) == _normalize_json_value(value):
        raise AssertionError(f"JSON path '{path}': value should not equal '{value}'.")


def api_assert_json_path_is_null(api_ctx: ApiContext, path: str) -> None:
    """Assert that a JSON path value is null.

    Args:
        api_ctx: The API context to operate on.
        path: A JSONPath expression starting with ``$``.

    Raises:
        AssertionError: If no response exists or the value is not null.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    data = _parse_response_json(api_ctx)
    try:
        actual = JsonPath(path).evaluate(data)
    except KeyError as exc:
        raise AssertionError(f"JSON path '{path}' does not exist: {exc}.") from exc
    if actual is not None:
        raise AssertionError(f"JSON path '{path}': expected null, got '{actual}'.")


def api_assert_json_path_is_not_null(api_ctx: ApiContext, path: str) -> None:
    """Assert that a JSON path value is not null.

    Args:
        api_ctx: The API context to operate on.
        path: A JSONPath expression starting with ``$``.

    Raises:
        AssertionError: If no response exists or the value is null.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    data = _parse_response_json(api_ctx)
    try:
        actual = JsonPath(path).evaluate(data)
    except KeyError as exc:
        raise AssertionError(f"JSON path '{path}' does not exist: {exc}.") from exc
    if actual is None:
        raise AssertionError(f"JSON path '{path}': expected non-null value.")


def api_assert_json_path_has_length(api_ctx: ApiContext, path: str, expected: int) -> None:
    """Assert that a JSON path value has a specific length.

    Args:
        api_ctx: The API context to operate on.
        path: A JSONPath expression starting with ``$``.
        expected: The expected length.

    Raises:
        AssertionError: If no response exists or the length does not match.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    data = _parse_response_json(api_ctx)
    try:
        actual = JsonPath(path).evaluate(data)
    except KeyError as exc:
        raise AssertionError(f"JSON path '{path}' does not exist: {exc}.") from exc
    try:
        actual_len = len(actual)
    except TypeError as exc:
        raise AssertionError(
            f"JSON path '{path}': value of type '{type(actual).__name__}' has no length."
        ) from exc
    if actual_len != expected:
        raise AssertionError(f"JSON path '{path}': expected length {expected}, got {actual_len}.")


def api_assert_json_path_matches_regex(api_ctx: ApiContext, path: str, pattern: str) -> None:
    """Assert that a JSON path string value matches a regex pattern.

    Args:
        api_ctx: The API context to operate on.
        path: A JSONPath expression starting with ``$``.
        pattern: A regular expression pattern to match.

    Raises:
        AssertionError: If no response exists or the value does not match.

    """
    import re

    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    data = _parse_response_json(api_ctx)
    try:
        actual = JsonPath(path).evaluate(data)
    except KeyError as exc:
        raise AssertionError(f"JSON path '{path}' does not exist: {exc}.") from exc
    if not isinstance(actual, str):
        raise AssertionError(
            f"JSON path '{path}': value of type '{type(actual).__name__}' "
            f"is not a string, cannot match regex."
        )
    try:
        if not re.search(pattern, actual):
            raise AssertionError(
                f"JSON path '{path}': value '{actual}' does not match pattern '{pattern}'."
            )
    except re.error as exc:
        raise AssertionError(f"Invalid regex pattern '{pattern}': {exc}") from exc


# --- Extended header assertions ---


def api_assert_header_contains(api_ctx: ApiContext, name: str, substring: str) -> None:
    """Assert that a response header contains *substring*.

    Args:
        api_ctx: The API context to operate on.
        name: The header name.
        substring: The substring to search for.

    Raises:
        AssertionError: If no response exists, the header is missing, or
            the value does not contain the substring.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    actual = _get_header_ci(api_ctx.last_response.headers, name)
    if actual is None:
        raise AssertionError(f"Response header '{name}' not found.")
    if substring not in actual:
        raise AssertionError(
            f"Response header '{name}': '{actual}' does not contain '{substring}'."
        )


def api_assert_header_not_equals(api_ctx: ApiContext, name: str, value: str) -> None:
    """Assert that a response header does NOT equal *value*.

    Args:
        api_ctx: The API context to operate on.
        name: The header name.
        value: The value that should not match.

    Raises:
        AssertionError: If no response exists, the header is missing, or
            the value matches.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    actual = _get_header_ci(api_ctx.last_response.headers, name)
    if actual is None:
        raise AssertionError(f"Response header '{name}' not found.")
    if actual == value:
        raise AssertionError(f"Response header '{name}': value should not equal '{value}'.")


def api_assert_header_exists(api_ctx: ApiContext, name: str) -> None:
    """Assert that a response header exists.

    Args:
        api_ctx: The API context to operate on.
        name: The header name.

    Raises:
        AssertionError: If no response exists or the header is missing.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    if not _header_exists_ci(api_ctx.last_response.headers, name):
        raise AssertionError(f"Response header '{name}' not found.")


def api_assert_header_not_exists(api_ctx: ApiContext, name: str) -> None:
    """Assert that a response header does NOT exist.

    Args:
        api_ctx: The API context to operate on.
        name: The header name.

    Raises:
        AssertionError: If no response exists or the header is present.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    existing = _get_header_ci(api_ctx.last_response.headers, name)
    if existing is not None:
        raise AssertionError(f"Response header '{name}' should not exist, got '{existing}'.")


# --- Send helpers ---


def api_send_form(
    api_ctx: ApiContext,
    method: str,
    url: str,
    data: dict[str, str],
) -> Response:
    """Send an HTTP request with form-encoded data.

    Sets ``Content-Type: application/x-www-form-urlencoded`` and encodes
    *data* as the request body.

    Args:
        api_ctx: The API context to operate on.
        method: HTTP method (typically ``"POST"`` or ``"PUT"``).
        url: Target URL.
        data: Form fields as a dict.

    Returns:
        The ``Response`` object.

    """
    import urllib.parse as _urlparse

    body = _urlparse.urlencode(data)
    return api_send(
        api_ctx,
        method,
        url,
        body=body,
        extra_headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def api_send_json(
    api_ctx: ApiContext,
    method: str,
    url: str,
    data: str | dict[str, Any],
) -> Response:
    """Send an HTTP request with a JSON body.

    Sets ``Content-Type: application/json``. If *data* is a dict, it is
    serialized to JSON. If it is a string, it is sent as-is.

    Args:
        api_ctx: The API context to operate on.
        method: HTTP method.
        url: Target URL.
        data: JSON body as a dict or pre-serialized string.

    Returns:
        The ``Response`` object.

    """
    import json as _json

    body = _json.dumps(data) if isinstance(data, dict) else data
    return api_send(
        api_ctx,
        method,
        url,
        body=body,
        extra_headers={"Content-Type": "application/json"},
    )


# --- Variable actions ---


def api_use_variable_as_header(api_ctx: ApiContext, name: str, variable: str) -> None:
    """Set a header from a stored variable.

    Args:
        api_ctx: The API context to operate on.
        name: The header name to set.
        variable: The variable name to read the value from.

    Raises:
        KeyError: If the variable does not exist.

    """
    if variable not in api_ctx.variables:
        raise KeyError(f"Variable '{variable}' not found.")
    api_ctx.default_headers[name] = _normalize_json_value(api_ctx.variables[variable])


def api_use_variable_as_query_param(api_ctx: ApiContext, name: str, variable: str) -> None:
    """Set a query parameter from a stored variable.

    Args:
        api_ctx: The API context to operate on.
        name: The query parameter name to set.
        variable: The variable name to read the value from.

    Raises:
        KeyError: If the variable does not exist.

    """
    if variable not in api_ctx.variables:
        raise KeyError(f"Variable '{variable}' not found.")
    api_ctx.query_params[name] = _normalize_json_value(api_ctx.variables[variable])


def api_assert_variable_equals(api_ctx: ApiContext, variable: str, expected: str) -> None:
    """Assert that a stored variable equals *expected* (compared as string).

    Args:
        api_ctx: The API context to operate on.
        variable: The variable name.
        expected: The expected value.

    Raises:
        AssertionError: If the variable does not exist or the value does not match.

    """
    if variable not in api_ctx.variables:
        raise AssertionError(f"Variable '{variable}' not found.")
    actual = _normalize_json_value(api_ctx.variables[variable])
    if actual != _normalize_json_value(expected):
        raise AssertionError(f"Variable '{variable}': expected '{expected}', got '{actual}'.")


def api_store_response_time(api_ctx: ApiContext, variable: str) -> None:
    """Store the last response time in milliseconds as *variable*.

    Args:
        api_ctx: The API context to operate on.
        variable: The variable name to store the elapsed time under.

    Raises:
        AssertionError: If no response exists.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    api_ctx.variables[variable] = api_ctx.last_response.elapsed_ms


# --- Proxy ---


def api_set_proxy(api_ctx: ApiContext, url: str) -> None:
    """Set a proxy URL for both HTTP and HTTPS requests.

    Args:
        api_ctx: The API context to operate on.
        url: The proxy URL (e.g. ``"http://proxy:8080"``).

    """
    api_ctx.proxies = {"http": url, "https": url}


# --- JSON Schema validation ---


def api_assert_json_schema(api_ctx: ApiContext, schema: dict[str, Any]) -> None:
    """Validate the last response body against a JSON Schema (draft-07 subset).

    Supports: type, properties, required, items, enum, minimum, maximum,
    minLength, maxLength, pattern.

    Args:
        api_ctx: The API context to operate on.
        schema: The JSON Schema dictionary.

    Raises:
        AssertionError: If no response exists or validation fails.

    """
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")
    data = _parse_response_json(api_ctx)
    errors = _validate_schema(data, schema, "$")
    if errors:
        raise AssertionError("JSON schema validation failed:\n  " + "\n  ".join(errors))


def _validate_schema(
    data: Any,
    schema: dict[str, Any],
    path: str,
) -> list[str]:
    """Validate *data* against *schema* and return a list of error messages."""
    import re

    errors: list[str] = []

    # type
    expected_type = schema.get("type")
    if expected_type:
        type_checks: dict[str, tuple[type[Any], ...]] = {
            "string": (str,),
            "number": (int, float),
            "integer": (int,),
            "boolean": (bool,),
            "object": (dict,),
            "array": (list,),
            "null": (type(None),),
        }
        if expected_type in type_checks:
            # In Python, bool is a subclass of int, so we must explicitly
            # exclude bool when checking for integer or number types.
            if expected_type in ("integer", "number") and isinstance(data, bool):
                errors.append(f"{path}: expected type '{expected_type}', got 'bool'")
                return errors
            if not isinstance(data, type_checks[expected_type]):
                errors.append(
                    f"{path}: expected type '{expected_type}', got '{type(data).__name__}'"
                )
                return errors

    # enum
    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: value '{data}' is not in enum {schema['enum']}")

    # minimum / maximum (for numbers, excluding bool which is int subclass)
    if isinstance(data, (int, float)) and not isinstance(data, bool):
        if "minimum" in schema and data < schema["minimum"]:
            errors.append(f"{path}: value {data} is less than minimum {schema['minimum']}")
        if "maximum" in schema and data > schema["maximum"]:
            errors.append(f"{path}: value {data} is greater than maximum {schema['maximum']}")

    # minLength / maxLength (for strings)
    if isinstance(data, str):
        if "minLength" in schema and len(data) < schema["minLength"]:
            errors.append(
                f"{path}: string length {len(data)} is less than minLength {schema['minLength']}"
            )
        if "maxLength" in schema and len(data) > schema["maxLength"]:
            errors.append(
                f"{path}: string length {len(data)} is greater than maxLength {schema['maxLength']}"
            )
        if "pattern" in schema:
            try:
                if not re.search(schema["pattern"], data):
                    errors.append(
                        f"{path}: string '{data}' does not match pattern '{schema['pattern']}'"
                    )
            except re.error as exc:
                raise AssertionError(
                    f"Invalid regex pattern '{schema['pattern']}' in schema: {exc}"
                ) from exc

    # properties (for objects)
    if isinstance(data, dict) and "properties" in schema:
        for key, sub_schema in schema["properties"].items():
            if key in data:
                errors.extend(_validate_schema(data[key], sub_schema, f"{path}.{key}"))

    # required (for objects)
    if isinstance(data, dict) and "required" in schema:
        for req_key in schema["required"]:
            if req_key not in data:
                errors.append(f"{path}: missing required property '{req_key}'")

    # items (for arrays)
    if isinstance(data, list) and "items" in schema:
        for i, item in enumerate(data):
            errors.extend(_validate_schema(item, schema["items"], f"{path}[{i}]"))

    return errors
