"""Tests for the @step decorator and StepInfo metadata."""

from __future__ import annotations

from steplib.core.decorators import get_step_infos, step
from steplib.core.metadata import StepInfo
from steplib.core.params import Param


def test_step_attaches_metadata() -> None:
    """@step should attach a StepInfo entry to the function."""

    @step("I do {thing}", category="test")
    def my_step(context, thing):  # type: ignore[no-untyped-def]
        pass

    infos = get_step_infos(my_step)
    assert len(infos) == 1
    info = infos[0]
    assert isinstance(info, StepInfo)
    assert info.pattern == "I do {thing}"
    assert info.category == "test"
    assert info.func is my_step


def test_step_stores_all_metadata() -> None:
    """@step should store every metadata field."""

    @step(
        "I send a {method} request to {url}",
        category="api",
        backend="httpx",
        description="Send an HTTP request.",
        parameters=[
            Param("method", type=str, required=True, default="GET"),
            Param("url", type=str, required=True),
        ],
        example='I send a GET request to "https://example.com"',
        tags=["api", "http"],
        version="1.0.0",
        i18n={"es": "envío una petición {method} a {url}"},
    )
    def step_send(context, method, url):  # type: ignore[no-untyped-def]
        pass

    info = get_step_infos(step_send)[0]
    assert info.backend == "httpx"
    assert info.description == "Send an HTTP request."
    assert info.example is not None
    assert "api" in info.tags
    assert info.version == "1.0.0"
    assert len(info.parameters) == 2
    assert info.parameters[0].name == "method"
    assert info.parameters[0].default == "GET"
    assert info.i18n == {"es": "envío una petición {method} a {url}"}


def test_step_uses_docstring_as_description() -> None:
    """When description is not provided, the docstring should be used."""

    @step("I wait {seconds:d} seconds", category="test")
    def step_wait(context, seconds):  # type: ignore[no-untyped-def]
        """Wait for the given number of seconds."""

    info = get_step_infos(step_wait)[0]
    assert info.description is not None
    assert "Wait for" in info.description


def test_stacked_decorators_produce_multiple_infos() -> None:
    """Stacked @step calls should each add a StepInfo entry."""

    @step("my name is {name}", category="example")
    @step("mi nombre es {name}", category="example")
    def step_my_name(context, name):  # type: ignore[no-untyped-def]
        pass

    infos = get_step_infos(step_my_name)
    assert len(infos) == 2
    patterns = {info.pattern for info in infos}
    assert "my name is {name}" in patterns
    assert "mi nombre es {name}" in patterns


def test_get_step_infos_on_plain_function() -> None:
    """get_step_infos should return an empty list for non-decorated functions."""

    def plain_fn() -> None:
        pass

    assert get_step_infos(plain_fn) == []
