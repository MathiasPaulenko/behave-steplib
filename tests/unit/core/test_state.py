"""Tests for SteplibState."""

from __future__ import annotations

from types import SimpleNamespace

from steplib.core.registry import StepRegistry
from steplib.core.state import SteplibState


class FakeModuleState:
    """Fake module state for testing reset/cleanup."""

    def __init__(self) -> None:
        self.reset_called = False
        self.cleanup_called = False

    def reset(self) -> None:
        self.reset_called = True

    def cleanup(self) -> None:
        self.cleanup_called = True


def test_state_holds_context_and_registry() -> None:
    """SteplibState should expose context and registry."""
    context = SimpleNamespace()
    registry = StepRegistry(auto_register_behave=False)
    state = SteplibState(context, registry)

    assert state.context is context
    assert state.registry is registry


def test_state_reset_calls_module_reset() -> None:
    """reset() should call reset() on all module-level attributes."""
    context = SimpleNamespace()
    registry = StepRegistry(auto_register_behave=False)
    state = SteplibState(context, registry)

    api_state = FakeModuleState()
    state.api = api_state  # type: ignore[attr-defined]

    state.reset()
    assert api_state.reset_called is True
    assert api_state.cleanup_called is False


def test_state_cleanup_calls_module_cleanup() -> None:
    """cleanup() should call cleanup() on all module-level attributes."""
    context = SimpleNamespace()
    registry = StepRegistry(auto_register_behave=False)
    state = SteplibState(context, registry)

    api_state = FakeModuleState()
    state.api = api_state  # type: ignore[attr-defined]

    state.cleanup()
    assert api_state.cleanup_called is True
    assert api_state.reset_called is False


def test_state_reset_skips_underscore_attrs() -> None:
    """reset() should not touch private (underscore) attributes."""
    context = SimpleNamespace()
    registry = StepRegistry(auto_register_behave=False)
    state = SteplibState(context, registry)

    state._private = FakeModuleState()  # type: ignore[attr-defined]
    state.reset()
    assert state._private.reset_called is False  # type: ignore[attr-defined]
