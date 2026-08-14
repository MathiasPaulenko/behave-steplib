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
    "the API base url is {url}",
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
    "I set the API header {name} to {value}",
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
    "I send a {method} request with body to {url}",
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
    "the response body contains {text}",
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
    "the JSON path {path} equals {value}",
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
    api_assert_json_path_equals(_get_api(context), path.strip('"'), value.strip('"'))


@step(
    "the response header {name} is {value}",
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
    "I store the response body as {variable}",
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
    example="Then the response matches the table",
    tags=["tables", "kit"],
)
def step_response_matches_table(context: Any) -> None:
    """Compare the response JSON with a behave table.

    Uses ``behave-tables`` to convert ``context.table`` to dicts and
    ``behave-kit`` for soft assertions. Both require their respective extras.
    """
    from steplib.core.ecosystem import assert_soft, wrap_table

    api_ctx = _get_api(context)
    if api_ctx.last_response is None:
        raise AssertionError("No response available. Send a request first.")

    expected = wrap_table(context.table).as_dicts()
    actual = api_ctx.last_response.json()
    assert_soft(
        len(expected) == len(actual),
        f"Row count mismatch: expected {len(expected)} rows, got {len(actual)}",
    )
    for exp, act in zip(expected, actual, strict=False):
        assert_soft(exp == act, f"Row mismatch: expected {exp}, got {act}")


# --- Query parameters ---


@step(
    "I set the query parameter {name} to {value}",
    category="api",
    description="Set a default query parameter sent with every request.",
    example='Given I set the query parameter "page" to "1"',
    i18n={
        "es": "establezco el parámetro de consulta {name} a {value}",
        "pt": "defino o parâmetro de consulta {name} como {value}",
    },
)
def step_set_query_param(context: Any, name: str, value: str) -> None:
    """Set a query parameter."""
    api_set_query_param(_get_api(context), name.strip('"'), value.strip('"'))


@step(
    "I remove the query parameter {name}",
    category="api",
    description="Remove a previously set query parameter.",
    example='When I remove the query parameter "page"',
    i18n={
        "es": "elimino el parámetro de consulta {name}",
        "pt": "removo o parâmetro de consulta {name}",
    },
)
def step_remove_query_param(context: Any, name: str) -> None:
    """Remove a query parameter."""
    api_remove_query_param(_get_api(context), name.strip('"'))


# --- Authentication ---


@step(
    "I set basic authentication with username {user} and password {password}",
    category="api",
    description="Set basic auth credentials for subsequent requests.",
    example='Given I set basic authentication with username "admin" and password "secret"',
    i18n={
        "es": "establezco autenticación básica con usuario {user} y contraseña {password}",
        "pt": "defino autenticação básica com usuário {user} e senha {password}",
    },
)
def step_set_basic_auth(context: Any, user: str, password: str) -> None:
    """Set basic auth credentials."""
    api_set_basic_auth(_get_api(context), user.strip('"'), password.strip('"'))


@step(
    "I set the bearer token to {token}",
    category="api",
    description="Set a Bearer token in the Authorization header.",
    example='Given I set the bearer token to "eyJhbGciOi..."',
    i18n={
        "es": "establezco el token bearer a {token}",
        "pt": "defino o token bearer como {token}",
    },
)
def step_set_bearer_token(context: Any, token: str) -> None:
    """Set a bearer token."""
    api_set_bearer_token(_get_api(context), token.strip('"'))


# --- SSL and redirects ---


@step(
    "I disable SSL verification",
    category="api",
    description="Disable SSL certificate verification for subsequent requests.",
    example="Given I disable SSL verification",
    i18n={
        "es": "deshabilito la verificación SSL",
        "pt": "desativo a verificação SSL",
    },
)
def step_disable_ssl(context: Any) -> None:
    """Disable SSL verification."""
    api_set_ssl_verify(_get_api(context), False)


@step(
    "I enable SSL verification",
    category="api",
    description="Enable SSL certificate verification for subsequent requests.",
    example="Given I enable SSL verification",
    i18n={
        "es": "habilito la verificación SSL",
        "pt": "ativo a verificação SSL",
    },
)
def step_enable_ssl(context: Any) -> None:
    """Enable SSL verification."""
    api_set_ssl_verify(_get_api(context), True)


@step(
    "I disable redirects",
    category="api",
    description="Disable following redirects for subsequent requests.",
    example="Given I disable redirects",
    i18n={
        "es": "deshabilito las redirecciones",
        "pt": "desativo os redirecionamentos",
    },
)
def step_disable_redirects(context: Any) -> None:
    """Disable redirects."""
    api_set_allow_redirects(_get_api(context), False)


@step(
    "I enable redirects",
    category="api",
    description="Enable following redirects for subsequent requests.",
    example="Given I enable redirects",
    i18n={
        "es": "habilito las redirecciones",
        "pt": "ativo os redirecionamentos",
    },
)
def step_enable_redirects(context: Any) -> None:
    """Enable redirects."""
    api_set_allow_redirects(_get_api(context), True)


# --- Cookies ---


@step(
    "I save cookies from the response",
    category="api",
    description="Extract Set-Cookie headers from the last response and store them.",
    example="When I save cookies from the response",
    i18n={
        "es": "guardo las cookies de la respuesta",
        "pt": "salvo os cookies da resposta",
    },
)
def step_save_cookies(context: Any) -> None:
    """Save cookies from the response."""
    api_save_cookies(_get_api(context))


# --- Header management ---


@step(
    "I remove the header {name}",
    category="api",
    description="Remove a previously set default header.",
    example='When I remove the header "Authorization"',
    i18n={
        "es": "elimino el header {name}",
        "pt": "removo o header {name}",
    },
)
def step_remove_header(context: Any, name: str) -> None:
    """Remove a default header."""
    api_remove_header(_get_api(context), name.strip('"'))


# --- Request lifecycle ---


@step(
    "I clear the request data",
    category="api",
    description="Reset headers, params, auth, cookies, and last response.",
    example="When I clear the request data",
    i18n={
        "es": "limpio los datos de la petición",
        "pt": "limpo os dados da requisição",
    },
)
def step_clear_request_data(context: Any) -> None:
    """Clear request-specific data."""
    api_clear_request_data(_get_api(context))


# --- Extended assertions ---


@step(
    "the response status is one of {statuses}",
    category="api",
    description="Assert the response status is one of a comma-separated list.",
    example="Then the response status is one of 200, 201, 202",
    i18n={
        "es": "el estado de la respuesta es uno de {statuses}",
        "pt": "o status da resposta é um de {statuses}",
    },
)
def step_response_status_in(context: Any, statuses: str) -> None:
    """Assert response status is in a list."""
    try:
        codes = [int(s.strip()) for s in statuses.split(",")]
    except ValueError as exc:
        raise AssertionError(
            f"Invalid status code list '{statuses}': {exc}"
        ) from exc
    api_assert_status_in(_get_api(context), codes)


@step(
    "the response body does not contain {text}",
    category="api",
    description="Assert the response body does not contain a substring.",
    example='Then the response body does not contain "error"',
    i18n={
        "es": "el cuerpo de la respuesta no contiene {text}",
        "pt": "o corpo da resposta não contém {text}",
    },
)
def step_response_body_not_contains(context: Any, text: str) -> None:
    """Assert response body does not contain text."""
    api_assert_body_not_contains(_get_api(context), text.strip('"'))


@step(
    "the JSON path {path} exists",
    category="api",
    description="Assert that a JSON path exists in the response.",
    example='Then the JSON path "$.user.id" exists',
    i18n={
        "es": "el path JSON {path} existe",
        "pt": "o path JSON {path} existe",
    },
)
def step_json_path_exists(context: Any, path: str) -> None:
    """Assert JSON path exists."""
    api_assert_json_path_exists(_get_api(context), path.strip('"'))


@step(
    "the JSON path {path} has type {type}",
    category="api",
    description="Assert the value at a JSON path is of a specific type.",
    example='Then the JSON path "$.user.id" has type "int"',
    i18n={
        "es": "el path JSON {path} es de tipo {type}",
        "pt": "o path JSON {path} é do tipo {type}",
    },
)
def step_json_path_type(context: Any, path: str, type: str) -> None:
    """Assert JSON path value type."""
    api_assert_json_path_type(_get_api(context), path.strip('"'), type.strip('"'))


@step(
    "the response content type is {content_type}",
    category="api",
    description="Assert the Content-Type response header equals a value.",
    example='Then the response content type is "application/json"',
    i18n={
        "es": "el content type de la respuesta es {content_type}",
        "pt": "o content type da resposta é {content_type}",
    },
)
def step_response_content_type(context: Any, content_type: str) -> None:
    """Assert content type equals."""
    api_assert_content_type(_get_api(context), content_type.strip('"'))


@step(
    "the response content type contains {content_type}",
    category="api",
    description="Assert the Content-Type response header contains a substring.",
    example='Then the response content type contains "json"',
    i18n={
        "es": "el content type de la respuesta contiene {content_type}",
        "pt": "o content type da resposta contém {content_type}",
    },
)
def step_response_content_type_contains(context: Any, content_type: str) -> None:
    """Assert content type contains."""
    api_assert_content_type_contains(_get_api(context), content_type.strip('"'))


@step(
    "the response time is less than {seconds:d} seconds",
    category="api",
    description="Assert the response time is under a threshold.",
    example="Then the response time is less than 5 seconds",
    i18n={
        "es": "el tiempo de respuesta es menor a {seconds:d} segundos",
        "pt": "o tempo de resposta é menor que {seconds:d} segundos",
    },
)
def step_response_time_less_than(context: Any, seconds: int) -> None:
    """Assert response time is less than N seconds."""
    api_assert_response_time_less_than(_get_api(context), float(seconds))


@step(
    "the response time is greater than {seconds:d} seconds",
    category="api",
    description="Assert the response time exceeds a threshold.",
    example="Then the response time is greater than 1 seconds",
    i18n={
        "es": "el tiempo de respuesta es mayor a {seconds:d} segundos",
        "pt": "o tempo de resposta é maior que {seconds:d} segundos",
    },
)
def step_response_time_greater_than(context: Any, seconds: int) -> None:
    """Assert response time is greater than N seconds."""
    api_assert_response_time_greater_than(_get_api(context), float(seconds))


@step(
    "the response time is between {min:d} and {max:d} seconds",
    category="api",
    description="Assert the response time is within a range.",
    example="Then the response time is between 1 and 10 seconds",
    i18n={
        "es": "el tiempo de respuesta está entre {min:d} y {max:d} segundos",
        "pt": "o tempo de resposta está entre {min:d} e {max:d} segundos",
    },
)
def step_response_time_between(context: Any, min: int, max: int) -> None:
    """Assert response time is between min and max seconds."""
    api_assert_response_time_between(_get_api(context), float(min), float(max))


# --- Extended store operations ---


@step(
    "I store the JSON path {path} as {variable}",
    category="api",
    description="Store the value at a JSON path from the response as a variable.",
    example='Then I store the JSON path "$.user.id" as "user_id"',
    i18n={
        "es": "guardo el path JSON {path} como {variable}",
        "pt": "guardo o path JSON {path} como {variable}",
    },
)
def step_store_json_path(context: Any, path: str, variable: str) -> None:
    """Store a JSON path value as a variable."""
    api_store_json_path(_get_api(context), path.strip('"'), variable.strip('"'))


@step(
    "I store the response header {name} as {variable}",
    category="api",
    description="Store a response header value as a named variable.",
    example='Then I store the response header "Content-Type" as "content_type"',
    i18n={
        "es": "guardo el header de la respuesta {name} como {variable}",
        "pt": "guardo o header da resposta {name} como {variable}",
    },
)
def step_store_header(context: Any, name: str, variable: str) -> None:
    """Store a response header as a variable."""
    api_store_header(_get_api(context), name.strip('"'), variable.strip('"'))


@step(
    "I store the response status as {variable}",
    category="api",
    description="Store the last response status code as a named variable.",
    example='Then I store the response status as "status_code"',
    i18n={
        "es": "guardo el estado de la respuesta como {variable}",
        "pt": "guardo o status da resposta como {variable}",
    },
)
def step_store_status(context: Any, variable: str) -> None:
    """Store the response status as a variable."""
    api_store_status(_get_api(context), variable.strip('"'))


# --- Extended JSON Path assertions ---


@step(
    "the JSON path {path} contains {value}",
    category="api",
    description="Assert that a JSON path value contains a value (for lists or strings).",
    example='Then the JSON path "$.tags" contains "premium"',
    i18n={
        "es": "el path JSON {path} contiene {value}",
        "pt": "o path JSON {path} contém {value}",
    },
)
def step_json_path_contains(context: Any, path: str, value: str) -> None:
    """Assert JSON path contains value."""
    api_assert_json_path_contains(_get_api(context), path.strip('"'), value.strip('"'))


@step(
    "the JSON path {path} does not equal {value}",
    category="api",
    description="Assert that a JSON path value does not equal a value.",
    example='Then the JSON path "$.status" does not equal "error"',
    i18n={
        "es": "el path JSON {path} no es igual a {value}",
        "pt": "o path JSON {path} não é igual a {value}",
    },
)
def step_json_path_not_equals(context: Any, path: str, value: str) -> None:
    """Assert JSON path does not equal value."""
    api_assert_json_path_not_equals(_get_api(context), path.strip('"'), value.strip('"'))


@step(
    "the JSON path {path} is null",
    category="api",
    description="Assert that a JSON path value is null.",
    example='Then the JSON path "$.deleted_at" is null',
    i18n={
        "es": "el path JSON {path} es nulo",
        "pt": "o path JSON {path} é nulo",
    },
)
def step_json_path_is_null(context: Any, path: str) -> None:
    """Assert JSON path value is null."""
    api_assert_json_path_is_null(_get_api(context), path.strip('"'))


@step(
    "the JSON path {path} is not null",
    category="api",
    description="Assert that a JSON path value is not null.",
    example='Then the JSON path "$.user.id" is not null',
    i18n={
        "es": "el path JSON {path} no es nulo",
        "pt": "o path JSON {path} não é nulo",
    },
)
def step_json_path_is_not_null(context: Any, path: str) -> None:
    """Assert JSON path value is not null."""
    api_assert_json_path_is_not_null(_get_api(context), path.strip('"'))


@step(
    "the JSON path {path} has length {length:d}",
    category="api",
    description="Assert that a JSON path value (list or string) has a specific length.",
    example='Then the JSON path "$.items" has length 5',
    i18n={
        "es": "el path JSON {path} tiene longitud {length:d}",
        "pt": "o path JSON {path} tem comprimento {length:d}",
    },
)
def step_json_path_has_length(context: Any, path: str, length: int) -> None:
    """Assert JSON path value has a specific length."""
    api_assert_json_path_has_length(_get_api(context), path.strip('"'), length)


@step(
    "the JSON path {path} matches the pattern {pattern}",
    category="api",
    description="Assert that a JSON path string value matches a regex pattern.",
    example='Then the JSON path "$.email" matches the pattern "^[^@]+@[^@]+\\.[^@]+$"',
    i18n={
        "es": "el path JSON {path} coincide con el patrón {pattern}",
        "pt": "o path JSON {path} corresponde ao padrão {pattern}",
    },
)
def step_json_path_matches_regex(context: Any, path: str, pattern: str) -> None:
    """Assert JSON path value matches regex pattern."""
    api_assert_json_path_matches_regex(_get_api(context), path.strip('"'), pattern.strip('"'))


# --- Extended header assertions ---


@step(
    "the response header {name} contains {value}",
    category="api",
    description="Assert a response header contains a substring.",
    example='Then the response header "Content-Type" contains "json"',
    i18n={
        "es": "el header de la respuesta {name} contiene {value}",
        "pt": "o header da resposta {name} contém {value}",
    },
)
def step_response_header_contains(context: Any, name: str, value: str) -> None:
    """Assert response header contains substring."""
    api_assert_header_contains(_get_api(context), name.strip('"'), value.strip('"'))


@step(
    "the response header {name} is not {value}",
    category="api",
    description="Assert a response header does not equal a value.",
    example='Then the response header "Server" is not "Apache"',
    i18n={
        "es": "el header de la respuesta {name} no es {value}",
        "pt": "o header da resposta {name} não é {value}",
    },
)
def step_response_header_not_equals(context: Any, name: str, value: str) -> None:
    """Assert response header does not equal value."""
    api_assert_header_not_equals(_get_api(context), name.strip('"'), value.strip('"'))


@step(
    "the response has header {name}",
    category="api",
    description="Assert that a response header exists.",
    example='Then the response has header "X-Request-ID"',
    i18n={
        "es": "la respuesta tiene el header {name}",
        "pt": "a resposta tem o header {name}",
    },
)
def step_response_header_exists(context: Any, name: str) -> None:
    """Assert response header exists."""
    api_assert_header_exists(_get_api(context), name.strip('"'))


@step(
    "the response does not have header {name}",
    category="api",
    description="Assert that a response header does not exist.",
    example='Then the response does not have header "X-Debug"',
    i18n={
        "es": "la respuesta no tiene el header {name}",
        "pt": "a resposta não tem o header {name}",
    },
)
def step_response_header_not_exists(context: Any, name: str) -> None:
    """Assert response header does not exist."""
    api_assert_header_not_exists(_get_api(context), name.strip('"'))


# --- Send helpers ---


@step(
    "I send a {method} request with form data to {url}",
    category="api",
    description="Send an HTTP request with form-encoded data from the step table.",
    example='When I send a POST request to "/login" with form data',
    i18n={
        "es": "envío una petición {method} a {url} con datos de formulario",
        "pt": "envio uma requisição {method} para {url} com dados de formulário",
    },
)
def step_send_form_data(context: Any, method: str, url: str) -> None:
    """Send an HTTP request with form data from a behave table."""
    data: dict[str, str] = {}
    if hasattr(context, "table") and context.table is not None:
        for row in context.table:
            data[row["name"]] = row["value"]
    api_send_form(_get_api(context), method, url.strip('"'), data)


@step(
    "I send a {method} request with JSON body to {url}",
    category="api",
    description="Send an HTTP request with a JSON body from the step text.",
    example='When I send a POST request to "/users" with JSON body',
    i18n={
        "es": "envío una petición {method} a {url} con cuerpo JSON",
        "pt": "envio uma requisição {method} para {url} com corpo JSON",
    },
)
def step_send_json_body(context: Any, method: str, url: str) -> None:
    """Send an HTTP request with a JSON body from step text."""
    body = context.text or ""
    api_send_json(_get_api(context), method, url.strip('"'), body)


@step(
    "I send a {method} request with query parameters to {url}",
    category="api",
    description="Send an HTTP request with query parameters from the step table.",
    example='When I send a GET request to "/search" with query parameters',
    i18n={
        "es": "envío una petición {method} a {url} con parámetros de consulta",
        "pt": "envio uma requisição {method} para {url} com parâmetros de consulta",
    },
)
def step_send_with_params(context: Any, method: str, url: str) -> None:
    """Send an HTTP request with query params from a behave table."""
    params: dict[str, str] = {}
    if hasattr(context, "table") and context.table is not None:
        for row in context.table:
            params[row["name"]] = row["value"]
    api_send(_get_api(context), method=method, url=url.strip('"'), params=params)


@step(
    "I send a {method} request with headers to {url}",
    category="api",
    description="Send an HTTP request with extra headers from the step table.",
    example='When I send a GET request to "/secure" with headers',
    i18n={
        "es": "envío una petición {method} a {url} con headers",
        "pt": "envio uma requisição {method} para {url} com headers",
    },
)
def step_send_with_headers(context: Any, method: str, url: str) -> None:
    """Send an HTTP request with extra headers from a behave table."""
    headers: dict[str, str] = {}
    if hasattr(context, "table") and context.table is not None:
        for row in context.table:
            headers[row["name"]] = row["value"]
    api_send(_get_api(context), method=method, url=url.strip('"'), extra_headers=headers)


# --- Variable actions ---


@step(
    "I use the variable {variable} as the header {name}",
    category="api",
    description="Set a header from a previously stored variable.",
    example='Then I use the variable "token" as the header "Authorization"',
    i18n={
        "es": "uso la variable {variable} como el header {name}",
        "pt": "uso a variável {variable} como o header {name}",
    },
)
def step_use_variable_as_header(context: Any, variable: str, name: str) -> None:
    """Set a header from a stored variable."""
    api_use_variable_as_header(_get_api(context), name.strip('"'), variable.strip('"'))


@step(
    "I use the variable {variable} as the query parameter {name}",
    category="api",
    description="Set a query parameter from a previously stored variable.",
    example='Then I use the variable "page" as the query parameter "p"',
    i18n={
        "es": "uso la variable {variable} como el parámetro de consulta {name}",
        "pt": "uso a variável {variable} como o parâmetro de consulta {name}",
    },
)
def step_use_variable_as_param(context: Any, variable: str, name: str) -> None:
    """Set a query param from a stored variable."""
    api_use_variable_as_query_param(_get_api(context), name.strip('"'), variable.strip('"'))



@step(
    "I store the response time as {variable}",
    category="api",
    description="Store the last response time in milliseconds as a variable.",
    example='Then I store the response time as "elapsed"',
    i18n={
        "es": "guardo el tiempo de respuesta como {variable}",
        "pt": "guardo o tempo de resposta como {variable}",
    },
)
def step_store_response_time(context: Any, variable: str) -> None:
    """Store response time as a variable."""
    api_store_response_time(_get_api(context), variable.strip('"'))


# --- Proxy ---


@step(
    "I set the proxy to {url}",
    category="api",
    description="Set a proxy URL for both HTTP and HTTPS requests.",
    example='Given I set the proxy to "http://proxy.example.com:8080"',
    i18n={
        "es": "establezco el proxy a {url}",
        "pt": "defino o proxy como {url}",
    },
)
def step_set_proxy(context: Any, url: str) -> None:
    """Set the proxy URL."""
    api_set_proxy(_get_api(context), url.strip('"'))


# --- JSON Schema validation ---


@step(
    "the response matches the JSON schema",
    category="api",
    description="Validate the response body against a JSON Schema from the step text.",
    example="Then the response matches the JSON schema",
    i18n={
        "es": "la respuesta coincide con el esquema JSON",
        "pt": "a resposta corresponde ao esquema JSON",
    },
)
def step_response_matches_schema(context: Any) -> None:
    """Validate response against a JSON Schema from step text."""
    import json as _json

    schema_text = context.text or ""
    try:
        schema = _json.loads(schema_text)
    except _json.JSONDecodeError as exc:
        raise AssertionError(f"Invalid JSON schema in step text: {exc}") from exc
    api_assert_json_schema(_get_api(context), schema)


# --- Registration ---

_ALL_STEPS = [
    step_set_base_url,
    step_set_header,
    step_set_timeout,
    step_set_query_param,
    step_remove_query_param,
    step_set_basic_auth,
    step_set_bearer_token,
    step_disable_ssl,
    step_enable_ssl,
    step_disable_redirects,
    step_enable_redirects,
    step_save_cookies,
    step_remove_header,
    step_clear_request_data,
    step_set_proxy,
    step_send_request,
    step_send_request_with_body,
    step_send_form_data,
    step_send_json_body,
    step_send_with_params,
    step_send_with_headers,
    step_response_status,
    step_response_status_in,
    step_response_body_contains,
    step_response_body_not_contains,
    step_response_body_valid_json,
    step_json_path_equals,
    step_json_path_not_equals,
    step_json_path_exists,
    step_json_path_is_null,
    step_json_path_is_not_null,
    step_json_path_contains,
    step_json_path_has_length,
    step_json_path_matches_regex,
    step_json_path_type,
    step_response_header_equals,
    step_response_header_contains,
    step_response_header_not_equals,
    step_response_header_exists,
    step_response_header_not_exists,
    step_response_content_type,
    step_response_content_type_contains,
    step_response_time_less_than,
    step_response_time_greater_than,
    step_response_time_between,
    step_store_response_body,
    step_store_json_path,
    step_store_header,
    step_store_status,
    step_store_response_time,
    step_use_variable_as_header,
    step_use_variable_as_param,
    step_response_matches_table,
    step_response_matches_schema,
]


def register(registry: StepRegistry) -> None:
    """Register all API steps into the given registry."""
    for step_fn in _ALL_STEPS:
        registry.add(step_fn)
