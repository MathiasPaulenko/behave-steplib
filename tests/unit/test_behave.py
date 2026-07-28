"""Tests for steplib.behave integration helpers."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from steplib.behave import after_scenario, autoload, before_all, load
from steplib.core.registry import StepRegistry
from steplib.core.state import SteplibState


def _make_state(context: SimpleNamespace) -> SteplibState:
    """Build a SteplibState with a non-behave-registering registry."""
    return SteplibState(context, StepRegistry(auto_register_behave=False))


def test_autoload_returns_state() -> None:
    """autoload() should delegate to discovery.autoload and return a SteplibState."""
    context = SimpleNamespace()
    expected = _make_state(context)
    with patch("steplib.behave._autoload", return_value=expected) as mock_fn:
        result = autoload(context)
    assert result is expected
    mock_fn.assert_called_once_with(context, categories=None, backends=None)


def test_autoload_passes_filters() -> None:
    """autoload() should forward categories and backends to discovery.autoload."""
    context = SimpleNamespace()
    expected = _make_state(context)
    with patch("steplib.behave._autoload", return_value=expected) as mock_fn:
        result = autoload(context, categories=["api"], backends={"api": "httpx"})
    assert result is expected
    mock_fn.assert_called_once_with(context, categories=["api"], backends={"api": "httpx"})


def test_load_delegates_to_discovery() -> None:
    """load() should delegate to discovery.load with the given modules."""
    context = SimpleNamespace()
    expected = _make_state(context)
    with patch("steplib.behave._load", return_value=expected) as mock_fn:
        result = load(context, "steplib.modules.api.steps")
    assert result is expected
    mock_fn.assert_called_once_with(context, "steplib.modules.api.steps")


def test_before_all_attaches_state() -> None:
    """before_all() should autoload and attach state to context."""
    context = SimpleNamespace()
    expected = _make_state(context)
    with patch("steplib.behave._autoload", return_value=expected):
        result = before_all(context)
    assert context.steplib is expected
    assert result is expected


def test_after_scenario_cleans_up_state() -> None:
    """after_scenario() should call cleanup() on context.steplib."""
    context = SimpleNamespace()
    state = _make_state(context)
    context.steplib = state

    cleaned = {"called": False}

    class FakeModuleContext:
        def cleanup(self) -> None:
            cleaned["called"] = True

    state.fake = FakeModuleContext()  # type: ignore[attr-defined]
    after_scenario(context, scenario=None)
    assert cleaned["called"]


def test_after_scenario_without_steplib_is_noop() -> None:
    """after_scenario() should not raise if context has no steplib."""
    context = SimpleNamespace()
    after_scenario(context, scenario=None)


def test_after_scenario_with_state_without_cleanup_is_noop() -> None:
    """after_scenario() should not raise if steplib state has no cleanup-able attrs."""
    context = SimpleNamespace()
    state = _make_state(context)
    context.steplib = state
    after_scenario(context, scenario=None)
