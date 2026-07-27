"""API step definitions for behave.

These steps cover the MVP: configuration, requests, and assertions.
All steps delegate to pure action functions in ``actions.py``.
"""

from __future__ import annotations

from typing import Any

from steplib.core.decorators import step
from steplib.core.registry import StepRegistry
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
from steplib.modules.api.context import ApiContext


def _get_api(context: Any) -> ApiContext:
    """Get the ApiContext from context.steplib, creating it if needed."""
    steplib = getattr(context, "steplib", None)
    if steplib is None:
        raise RuntimeError(
            "context.steplib is not initialized. "
            "Call autoload(context) or load(context, ...) in before_all."
        )
    api = getattr(steplib, "api", None)
    if api is None:
        api = ApiContext()
        steplib.api = api
    return api


# --- Configuration steps ---

@step(
    'the API base url is {url}',
    category="api",
    description="Set the base URL for subsequent API requests.",
    example='Given the API base url is "https://api.example.com"',
    i18n={
        "es": "la url base de la API es {url}",
        "pt": "a url base da API é {url}",
    },
)
def step_set_base_url(context: Any, url: str) -> None:
    """Set the API base URL."""
    api_set_base_url(_get_api(context), url.strip('"'))


@step(
    'I set the API header {name} to {value}',
    category="api",
    description="Set a default header sent with every API request.",
    example='Given I set the API header "Authorization" to "Bearer token123"',
    i18n={
        "es": "establezco el header de la API {name} a {value}",
        "pt": "defino o header da API {name} como {value}",
    },
)
def step_set_header(context: Any, name: str, value: str) -> None:
    """Set a default API header."""
    api_set_header(_get_api(context), name.strip('"'), value.strip('"'))


@step(
    "I set the API timeout to {seconds:d} seconds",
    category="api",
    description="Set the request timeout in seconds.",
    example="Given I set the API timeout to 30 seconds",
    i18n={
        "es": "establezco el timeout de la API a {seconds:d} segundos",
        "pt": "defino o timeout da API para {seconds:d} segundos",
    },
)
def step_set_timeout(context: Any, seconds: int) -> None:
    """Set the API timeout."""
    api_set_timeout(_get_api(context), float(seconds))


# --- Request steps ---

@step(
    "I send a {method} request to {url}",
    category="api",
    description="Send an HTTP request and store the response.",
    example='When I send a GET request to "/users"',
    i18n={
        "es": "envío una petición {method} a {url}",
        "pt": "envio uma requisição {method} para {url}",
    },
)
def step_send_request(context: Any, method: str, url: str) -> None:
    """Send an HTTP request."""
    api_send(_get_api(context), method=method, url=url.strip('"'))


@step(
    "I send a {method} request to {url} with body",
    category="api",
    description="Send an HTTP request with a body from the step text.",
    example='When I send a POST request to "/users" with body',
    i18n={
        "es": "envío una petición {method} a {url} con cuerpo",
        "pt": "envio uma requisição {method} para {url} com corpo",
    },
)
def step_send_request_with_body(context: Any, method: str, url: str) -> None:
    """Send an HTTP request with a body from the step's text."""
    body = context.text or ""
    api_send(_get_api(context), method=method, url=url.strip('"'), body=body)


# --- Assertion steps ---

@step(
    "the response status is {status:d}",
    category="api",
    description="Assert the last response status code.",
    example="Then the response status is 200",
    i18n={
        "es": "el estado de la respuesta es {status:d}",
        "pt": "o status da resposta é {status:d}",
    },
)
def step_response_status(context: Any, status: int) -> None:
    """Assert response status code."""
    api_assert_status(_get_api(context), status)


@step(
    'the response body contains {text}',
    category="api",
    description="Assert the response body contains a substring.",
    example='Then the response body contains "success"',
    i18n={
        "es": "el cuerpo de la respuesta contiene {text}",
        "pt": "o corpo da resposta contém {text}",
    },
)
def step_response_body_contains(context: Any, text: str) -> None:
    """Assert response body contains text."""
    api_assert_body_contains(_get_api(context), text.strip('"'))


@step(
    "the response body is valid JSON",
    category="api",
    description="Assert the response body is valid JSON.",
    example="Then the response body is valid JSON",
    i18n={
        "es": "el cuerpo de la respuesta es JSON válido",
        "pt": "o corpo da resposta é JSON válido",
    },
)
def step_response_body_valid_json(context: Any) -> None:
    """Assert response body is valid JSON."""
    api_assert_json_valid(_get_api(context))


@step(
    'the JSON path {path} equals {value}',
    category="api",
    description="Assert a JSON path in the response equals a value.",
    example='Then the JSON path "$.name" equals "Ada"',
    i18n={
        "es": "el path JSON {path} es igual a {value}",
        "pt": "o path JSON {path} é igual a {value}",
    },
)
def step_json_path_equals(context: Any, path: str, value: str) -> None:
    """Assert JSON path equals value."""
    api_assert_json_path_equals(_get_api(context), path, value.strip('"'))


@step(
    'the response header {name} is {value}',
    category="api",
    description="Assert a response header equals a value.",
    example='Then the response header "Content-Type" is "application/json"',
    i18n={
        "es": "el header de la respuesta {name} es {value}",
        "pt": "o header da resposta {name} é {value}",
    },
)
def step_response_header_equals(context: Any, name: str, value: str) -> None:
    """Assert response header equals value."""
    api_assert_header_equals(_get_api(context), name.strip('"'), value.strip('"'))


@step(
    'I store the response body as {variable}',
    category="api",
    description="Store the response body as a named variable.",
    example='Then I store the response body as "user_response"',
    i18n={
        "es": "guardo el cuerpo de la respuesta como {variable}",
        "pt": "guardo o corpo da resposta como {variable}",
    },
)
def step_store_response_body(context: Any, variable: str) -> None:
    """Store the response body as a variable."""
    api_store_response_body(_get_api(context), variable.strip('"'))


@step(
    "the response matches the table",
    category="api",
    description="Compare the response JSON with a behave table (requires extras).",
    example='Then the response matches the table',
    tags=["tables", "kit"],
)
def step_response_matches_table(context: Any) -> None:
    """Compare the response JSON with a behave table.

    Uses ``behave-tables`` to convert ``context.table`` to dicts and
    ``behave-kit`` for soft assertions. Both require their respective extras.
    """
    from steplib.core.ecosystem import assert_soft, wrap_table  # noqa: PLC0415

    api_ctx = _get_api(context)
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")

    expected = wrap_table(context.table).as_dicts()
    actual = api_ctx.last_response.json()
    for exp, act in zip(expected, actual, strict=False):
        assert_soft(exp == act, f"Row mismatch: expected {exp}, got {act}")


# --- Registration ---

_ALL_STEPS = [
    step_set_base_url,
    step_set_header,
    step_set_timeout,
    step_send_request,
    step_send_request_with_body,
    step_response_status,
    step_response_body_contains,
    step_response_body_valid_json,
    step_json_path_equals,
    step_response_header_equals,
    step_store_response_body,
    step_response_matches_table,
]


def register(registry: StepRegistry) -> None:
    """Register all API steps into the given registry."""
    for step_fn in _ALL_STEPS:
        registry.add(step_fn)
