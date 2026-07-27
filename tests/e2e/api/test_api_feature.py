"""E2E test: simulate a behave scenario by calling step functions directly.

This tests the full flow: step function → action → HTTP client → assertion,
using a mock HTTP client to avoid real network calls.
"""

from __future__ import annotations

from types import SimpleNamespace

from steplib.core.state import SteplibState
from steplib.modules.api.client import Response
from steplib.modules.api.context import ApiContext
from steplib.modules.api.steps import (
    step_json_path_equals,
    step_response_body_contains,
    step_response_body_valid_json,
    step_response_header_equals,
    step_response_status,
    step_send_request,
    step_set_base_url,
    step_set_header,
)


class MockHTTPClient:
    """Mock HTTP client that returns a configurable response."""

    def __init__(self, response: Response | None = None) -> None:
        self.response = response or Response(
            status=200,
            headers={"Content-Type": "application/json"},
            body=b'{"users": [{"name": "Ada"}]}',
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
        return self.response


def _make_context(response: Response | None = None) -> SimpleNamespace:
    """Create a behave-like context with steplib state and ApiContext."""
    context = SimpleNamespace()
    state = SteplibState(context, registry=None)  # type: ignore[arg-type]
    state.api = ApiContext(client=MockHTTPClient(response))  # type: ignore[attr-defined]
    context.steplib = state
    return context


def test_full_api_scenario() -> None:
    """Run a complete API scenario: set base URL, send request, assert response."""
    context = _make_context()

    # Given the API base url is "https://api.example.com"
    step_set_base_url(context, '"https://api.example.com"')

    # When I send a GET request to "/users"
    step_send_request(context, "GET", '"/users"')

    # Then the response status is 200
    step_response_status(context, 200)

    # And the response body is valid JSON
    step_response_body_valid_json(context)

    # And the JSON path "$.users[0].name" equals "Ada"
    step_json_path_equals(context, "$.users[0].name", '"Ada"')


def test_api_scenario_with_headers() -> None:
    """Run a scenario with custom headers."""
    response = Response(
        status=200,
        headers={"X-Custom-Header": "yes"},
        body=b'{"ok": true}',
        elapsed_ms=3.0,
    )
    context = _make_context(response)

    step_set_base_url(context, '"https://api.example.com"')
    step_set_header(context, '"Authorization"', '"Bearer token"')
    step_send_request(context, "GET", '"/secure"')
    step_response_status(context, 200)
    step_response_header_equals(context, '"X-Custom-Header"', '"yes"')


def test_api_scenario_404() -> None:
    """Run a scenario with a 404 response."""
    response = Response(
        status=404,
        headers={},
        body=b'{"error": "not found"}',
        elapsed_ms=2.0,
    )
    context = _make_context(response)

    step_set_base_url(context, '"https://api.example.com"')
    step_send_request(context, "GET", '"/missing"')
    step_response_status(context, 404)
    step_response_body_contains(context, '"not found"')
