"""Tests for discovery (autoload, load, get_registry)."""

from __future__ import annotations

import sys
import types as mod_types
from types import SimpleNamespace

import pytest

from steplib.core.decorators import step
from steplib.core.discovery import _apply_filters, get_registry, load
from steplib.core.registry import StepRegistry
from steplib.core.state import SteplibState


def test_load_registers_module_steps() -> None:
    """load() should import a module and call its register() function."""

    @step("I do {thing}", category="test")
    def my_step(context, thing):  # type: ignore[no-untyped-def]
        pass

    fake_mod = mod_types.ModuleType("fake_test_module")

    def register(registry: StepRegistry) -> None:
        registry.add(my_step)

    fake_mod.register = register  # type: ignore[attr-defined]
    backup = sys.modules.get("fake_test_module")
    sys.modules["fake_test_module"] = fake_mod
    try:
        context = SimpleNamespace()
        state = load(context, "fake_test_module")
        assert isinstance(state, SteplibState)
        assert len(state.registry) == 1
        assert state.registry.steps[0].pattern == "I do {thing}"
    finally:
        if backup is not None:
            sys.modules["fake_test_module"] = backup
        else:
            sys.modules.pop("fake_test_module", None)


def test_load_missing_register_raises() -> None:
    """load() should raise if a module has no register() function."""
    fake_mod = mod_types.ModuleType("fake_no_register")
    sys.modules["fake_no_register"] = fake_mod
    try:
        context = SimpleNamespace()
        with pytest.raises(AttributeError, match="register"):
            load(context, "fake_no_register")
    finally:
        sys.modules.pop("fake_no_register", None)


def test_get_registry_returns_metadata_only() -> None:
    """get_registry() should return a registry without behave registration."""
    registry = get_registry()
    assert isinstance(registry, StepRegistry)
    # No crash; the registry may be empty if no plugins are installed.
    assert isinstance(len(registry), int)


def _build_test_registry() -> StepRegistry:
    """Build a registry with known steps for filter tests."""

    @step("I send a {method} request to {url}", category="api", backend="httpx")
    def step_send(context, method, url):  # type: ignore[no-untyped-def]
        pass

    @step("I send a {method} request to {url}", category="api", backend="requests")
    def step_send_requests(context, method, url):  # type: ignore[no-untyped-def]
        pass

    @step("I click {selector}", category="web", backend="selenium")
    def step_click(context, selector):  # type: ignore[no-untyped-def]
        pass

    reg = StepRegistry(auto_register_behave=False)
    reg.add(step_send)
    reg.add(step_send_requests)
    reg.add(step_click)
    return reg


def test_apply_filters_no_filters_is_noop() -> None:
    """_apply_filters with None for both should be a no-op."""
    reg = _build_test_registry()
    original_count = len(reg)
    _apply_filters(reg, categories=None, backends=None)
    assert len(reg) == original_count


def test_apply_filters_by_category() -> None:
    """_apply_filters should keep only steps in the given categories."""
    reg = _build_test_registry()
    _apply_filters(reg, categories=["api"], backends=None)
    assert len(reg) == 2
    for info in reg.steps:
        assert info.category == "api"


def test_apply_filters_by_backend() -> None:
    """_apply_filters should keep only steps matching the backend mapping."""
    reg = _build_test_registry()
    _apply_filters(reg, categories=None, backends={"api": "httpx"})
    # api/httpx kept, api/requests removed, web/selenium kept (no backend filter for web)
    assert len(reg) == 2
    api_steps = [s for s in reg.steps if s.category == "api"]
    assert len(api_steps) == 1
    assert api_steps[0].backend == "httpx"


def test_apply_filters_by_category_and_backend() -> None:
    """_apply_filters should combine category and backend filters."""
    reg = _build_test_registry()
    _apply_filters(reg, categories=["api"], backends={"api": "httpx"})
    assert len(reg) == 1
    assert reg.steps[0].category == "api"
    assert reg.steps[0].backend == "httpx"


def test_autoload_returns_state_with_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    """autoload should return a SteplibState with a registry attached."""
    from steplib.core.discovery import autoload

    # Avoid loading real entry points which would register with behave.
    monkeypatch.setattr("steplib.core.discovery._load_entry_points", lambda reg: None)
    context = SimpleNamespace()
    state = autoload(context)
    assert isinstance(state, SteplibState)
    assert isinstance(state.registry, StepRegistry)


def test_autoload_with_category_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    """autoload with categories filter should narrow the registry."""
    from steplib.core.discovery import autoload

    monkeypatch.setattr("steplib.core.discovery._load_entry_points", lambda reg: None)
    context = SimpleNamespace()
    state = autoload(context, categories=["api"])
    assert isinstance(state, SteplibState)
    # With no entry points loaded, registry should be empty.
    assert len(state.registry) == 0
