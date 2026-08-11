"""Tests for StepRegistry."""

from __future__ import annotations

import pytest

from steplib.core.decorators import step
from steplib.core.exceptions import DuplicateStepError, StepContractError
from steplib.core.registry import StepRegistry


def test_registry_add_and_filter() -> None:
    """add() should store steps and filter() should return matching entries."""

    @step("I send a {method} request to {url}", category="api", backend="httpx")
    def step_send(context, method, url):  # type: ignore[no-untyped-def]
        pass

    @step("I click {selector}", category="web", backend="selenium")
    def step_click(context, selector):  # type: ignore[no-untyped-def]
        pass

    registry = StepRegistry(auto_register_behave=False)
    registry.add(step_send)
    registry.add(step_click)

    assert len(registry) == 2

    api_steps = registry.filter(category="api")
    assert len(api_steps) == 1
    assert api_steps[0].pattern == "I send a {method} request to {url}"

    httpx_steps = registry.filter(backend="httpx")
    assert len(httpx_steps) == 1

    web_steps = registry.filter(category="web")
    assert len(web_steps) == 1
    assert web_steps[0].backend == "selenium"


def test_registry_filter_by_tag() -> None:
    """filter(tag=...) should return only steps with that tag."""

    @step("step one", category="test", tags=["smoke"])
    def step_one(context):  # type: ignore[no-untyped-def]
        pass

    @step("step two", category="test", tags=["regression"])
    def step_two(context):  # type: ignore[no-untyped-def]
        pass

    registry = StepRegistry(auto_register_behave=False)
    registry.add(step_one)
    registry.add(step_two)

    smoke = registry.filter(tag="smoke")
    assert len(smoke) == 1
    assert smoke[0].pattern == "step one"


def test_registry_get_by_pattern() -> None:
    """get() should return the StepInfo for a given pattern."""

    @step("I do {thing}", category="test", backend="httpx")
    def my_step(context, thing):  # type: ignore[no-untyped-def]
        pass

    registry = StepRegistry(auto_register_behave=False)
    registry.add(my_step)

    info = registry.get("I do {thing}", backend="httpx")
    assert info is not None
    assert info.pattern == "I do {thing}"

    assert registry.get("nonexistent") is None


def test_registry_available_backends() -> None:
    """available_backends() should return all backends for a category."""

    @step("step a", category="api", backend="httpx")
    def step_a(context):  # type: ignore[no-untyped-def]
        pass

    @step("step b", category="api", backend="requests")
    def step_b(context):  # type: ignore[no-untyped-def]
        pass

    registry = StepRegistry(auto_register_behave=False)
    registry.add(step_a)
    registry.add(step_b)

    backends = registry.available_backends(category="api")
    assert backends == {"httpx", "requests"}


def test_registry_duplicate_pattern_raises() -> None:
    """Duplicate patterns with the same backend should raise."""

    @step("I do {thing}", category="test", backend="httpx")
    def step_one(context, thing):  # type: ignore[no-untyped-def]
        pass

    @step("I do {thing}", category="test", backend="httpx")
    def step_two(context, thing):  # type: ignore[no-untyped-def]
        pass

    registry = StepRegistry(auto_register_behave=False)
    registry.add(step_one)
    with pytest.raises(DuplicateStepError):
        registry.add(step_two)


def test_registry_add_non_step_raises() -> None:
    """add() on a non-decorated function should raise StepContractError."""

    def plain_fn() -> None:
        pass

    registry = StepRegistry(auto_register_behave=False)
    with pytest.raises(StepContractError):
        registry.add(plain_fn)


def test_registry_i18n_expands_patterns() -> None:
    """A step with i18n should register all translated patterns."""

    @step(
        "I send a {method} request to {url}",
        category="api",
        backend="httpx",
        i18n={
            "es": "envío una petición {method} a {url}",
            "pt": "envio uma requisição {method} para {url}",
        },
    )
    def step_send(context, method, url):  # type: ignore[no-untyped-def]
        pass

    registry = StepRegistry(auto_register_behave=False)
    registry.add(step_send)

    # The base pattern and both translations should be findable.
    assert registry.get("I send a {method} request to {url}", backend="httpx") is not None
    assert registry.get("envío una petición {method} a {url}", backend="httpx") is not None
    assert registry.get("envio uma requisição {method} para {url}", backend="httpx") is not None

    # But only one StepInfo is stored (i18n expands patterns, not steps).
    assert len(registry) == 1


def test_registry_replace_steps() -> None:
    """replace_steps() should rebuild the registry with only the kept steps."""

    @step("step a", category="api", backend="httpx")
    def step_a(context):  # type: ignore[no-untyped-def]
        pass

    @step("step b", category="web", backend="selenium")
    def step_b(context):  # type: ignore[no-untyped-def]
        pass

    registry = StepRegistry(auto_register_behave=False)
    registry.add(step_a)
    registry.add(step_b)
    assert len(registry) == 2

    # Keep only the api step.
    api_steps = registry.filter(category="api")
    registry.replace_steps(api_steps)

    assert len(registry) == 1
    assert registry.get("step a", backend="httpx") is not None
    assert registry.get("step b", backend="selenium") is None


def test_registry_iter() -> None:
    """__iter__ should yield all registered StepInfo entries."""

    @step("step one", category="test")
    def step_one(context):  # type: ignore[no-untyped-def]
        pass

    @step("step two", category="test")
    def step_two(context):  # type: ignore[no-untyped-def]
        pass

    registry = StepRegistry(auto_register_behave=False)
    registry.add(step_one)
    registry.add(step_two)

    patterns = [info.pattern for info in registry]
    assert patterns == ["step one", "step two"]


def test_registry_search_partial_pattern() -> None:
    """search() should match steps by case-insensitive substring."""

    @step("I send a {method} request to {url}", category="api", backend="httpx")
    def step_send(context, method, url):  # type: ignore[no-untyped-def]
        pass

    @step("I click {selector}", category="web", backend="selenium")
    def step_click(context, selector):  # type: ignore[no-untyped-def]
        pass

    registry = StepRegistry(auto_register_behave=False)
    registry.add(step_send)
    registry.add(step_click)

    results = registry.search(pattern="send a")
    assert len(results) == 1
    assert results[0].pattern == "I send a {method} request to {url}"

    results_ci = registry.search(pattern="SEND")
    assert len(results_ci) == 1
    assert results_ci[0].pattern == "I send a {method} request to {url}"

    results_none = registry.search(pattern="nonexistent")
    assert len(results_none) == 0


def test_registry_search_with_filters() -> None:
    """search() should AND-combine pattern substring with category/backend/tag."""

    @step(
        "I send a {method} request to {url}",
        category="api",
        backend="httpx",
        tags=["smoke"],
    )
    def step_send(context, method, url):  # type: ignore[no-untyped-def]
        pass

    @step("I click {selector}", category="web", backend="selenium")
    def step_click(context, selector):  # type: ignore[no-untyped-def]
        pass

    registry = StepRegistry(auto_register_behave=False)
    registry.add(step_send)
    registry.add(step_click)

    assert len(registry.search(pattern="send", category="api")) == 1
    assert len(registry.search(pattern="send", category="web")) == 0
    assert len(registry.search(pattern="send", backend="httpx")) == 1
    assert len(registry.search(pattern="send", tag="smoke")) == 1
    assert len(registry.search(tag="smoke")) == 1
    assert len(registry.search(category="api")) == 1
    assert len(registry.search()) == 2
