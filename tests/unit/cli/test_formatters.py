"""Tests for CLI output formatters."""

from __future__ import annotations

import json

from steplib.core.decorators import step
from steplib.core.metadata import StepInfo
from steplib.core.params import Param
from steplib.core.registry import StepRegistry


def _make_step_infos() -> list[StepInfo]:
    """Build a list of StepInfo entries for testing formatters."""

    @step(
        "I send a {method} request to {url}",
        category="api",
        backend="httpx",
        description="Send an HTTP request.",
        tags=["smoke"],
        version="1.0.0",
        example='Given I send a "GET" request to "https://example.com"',
        parameters=[
            Param(name="method", type=str, required=True, description="HTTP method"),
            Param(name="url", type=str, required=True),
        ],
        i18n={"es": "envío una petición {method} a {url}"},
        requires=["steplib.api.client"],
    )
    def step_send(context, method, url):  # type: ignore[no-untyped-def]
        pass

    @step("I click {selector}", category="web", backend="selenium")
    def step_click(context, selector):  # type: ignore[no-untyped-def]
        pass

    reg = StepRegistry(auto_register_behave=False)
    reg.add(step_send)
    reg.add(step_click)
    return reg.steps


def test_format_step_table_empty() -> None:
    """format_step_table should return 'No steps found.' for empty list."""
    from steplib.cli.formatters import format_step_table

    result = format_step_table([])
    assert result == "No steps found."


def test_format_step_table_with_steps() -> None:
    """format_step_table should produce a table with headers and rows."""
    from steplib.cli.formatters import format_step_table

    infos = _make_step_infos()
    result = format_step_table(infos)
    assert "PATTERN" in result
    assert "CATEGORY" in result
    assert "BACKEND" in result
    assert "DESCRIPTION" in result
    assert "I send a {method} request to {url}" in result
    assert "I click {selector}" in result


def test_format_step_detail_full() -> None:
    """format_step_detail should render all metadata fields."""
    from steplib.cli.formatters import format_step_detail

    infos = _make_step_infos()
    info = infos[0]
    result = format_step_detail(info)
    assert "Pattern:" in result
    assert "I send a {method} request to {url}" in result
    assert "Category:" in result
    assert "api" in result
    assert "Backend:" in result
    assert "httpx" in result
    assert "Module:" in result
    assert "Function:" in result
    assert "Description:" in result
    assert "Send an HTTP request." in result
    assert "Example:" in result
    assert "Tags:" in result
    assert "smoke" in result
    assert "Version:" in result
    assert "1.0.0" in result
    assert "Parameters:" in result
    assert "method" in result
    assert "Translations:" in result
    assert "[es]" in result
    assert "Requires:" in result


def test_format_step_detail_minimal() -> None:
    """format_step_detail should handle a step with minimal metadata."""
    from steplib.cli.formatters import format_step_detail

    @step("I do {thing}", category="test")
    def step_minimal(context, thing):  # type: ignore[no-untyped-def]
        pass

    reg = StepRegistry(auto_register_behave=False)
    reg.add(step_minimal)
    result = format_step_detail(reg.steps[0])
    assert "Pattern:" in result
    assert "I do {thing}" in result
    assert "Category:" in result
    assert "test" in result
    assert "Backend:" in result
    # No description, example, tags, version, parameters, i18n, requires
    assert "Description:" not in result
    assert "Example:" not in result
    assert "Tags:" not in result
    assert "Version:" not in result
    assert "Parameters:" not in result
    assert "Translations:" not in result
    assert "Requires:" not in result


def test_format_step_json() -> None:
    """format_step_json should produce valid JSON with expected fields."""
    from steplib.cli.formatters import format_step_json

    infos = _make_step_infos()
    result = format_step_json(infos)
    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["pattern"] == "I send a {method} request to {url}"
    assert data[0]["category"] == "api"
    assert data[0]["backend"] == "httpx"
    assert data[0]["description"] == "Send an HTTP request."
    assert data[0]["tags"] == ["smoke"]
    assert data[0]["version"] == "1.0.0"
    assert data[0]["i18n"] == {"es": "envío una petición {method} a {url}"}


def test_format_step_detail_json() -> None:
    """format_step_detail_json should produce valid JSON with all fields."""
    from steplib.cli.formatters import format_step_detail_json

    infos = _make_step_infos()
    info = infos[0]
    result = format_step_detail_json(info)
    data = json.loads(result)
    assert data["pattern"] == "I send a {method} request to {url}"
    assert data["category"] == "api"
    assert data["backend"] == "httpx"
    assert data["description"] == "Send an HTTP request."
    assert data["example"] is not None
    assert data["tags"] == ["smoke"]
    assert data["version"] == "1.0.0"
    assert data["requires"] == ["steplib.api.client"]
    assert isinstance(data["parameters"], list)
    assert len(data["parameters"]) == 2
    assert data["parameters"][0]["name"] == "method"
    assert data["parameters"][0]["required"] is True


def test_format_step_detail_json_minimal() -> None:
    """format_step_detail_json should handle minimal metadata."""
    from steplib.cli.formatters import format_step_detail_json

    @step("I do {thing}", category="test")
    def step_minimal(context, thing):  # type: ignore[no-untyped-def]
        pass

    reg = StepRegistry(auto_register_behave=False)
    reg.add(step_minimal)
    data = json.loads(format_step_detail_json(reg.steps[0]))
    assert data["pattern"] == "I do {thing}"
    assert data["category"] == "test"
    assert data["backend"] is None
    assert data["description"] is None
    assert data["example"] is None
    assert data["tags"] == []
    assert data["version"] is None
    assert data["deprecated"] is False
    assert data["requires"] == []
    assert data["parameters"] == []
    assert data["i18n"] == {}


def test_format_step_detail_deprecated() -> None:
    """format_step_detail should show deprecation info."""
    from steplib.cli.formatters import format_step_detail

    @step(
        "I use old {thing}",
        category="test",
        deprecated="Use 'I do {thing}' instead.",
    )
    def step_deprecated(context, thing):  # type: ignore[no-untyped-def]
        pass

    reg = StepRegistry(auto_register_behave=False)
    reg.add(step_deprecated)
    result = format_step_detail(reg.steps[0])
    assert "Deprecated:" in result
    assert "Use 'I do {thing}' instead." in result
