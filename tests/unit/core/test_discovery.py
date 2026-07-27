"""Tests for discovery (autoload, load, get_registry)."""

from __future__ import annotations

import sys
import types as mod_types
from types import SimpleNamespace

import pytest

from steplib.core.decorators import step
from steplib.core.discovery import get_registry, load
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
