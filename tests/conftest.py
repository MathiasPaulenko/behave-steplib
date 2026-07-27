"""Shared pytest fixtures for the steplib test suite."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from steplib.core.registry import StepRegistry
from steplib.core.state import SteplibState
from steplib.modules.api.client import UrllibHTTPClient
from steplib.modules.api.context import ApiContext


@pytest.fixture()
def registry() -> StepRegistry:
    """Provide a clean registry per test (no behave registration)."""
    return StepRegistry(auto_register_behave=False)


@pytest.fixture()
def fake_context() -> SimpleNamespace:
    """Return a bare context with a steplib namespace."""
    ctx = SimpleNamespace()
    state = SteplibState(ctx, StepRegistry(auto_register_behave=False))
    ctx.steplib = state
    return ctx


@pytest.fixture()
def fake_api_context(fake_context: SimpleNamespace) -> SimpleNamespace:
    """Return a context with an ApiContext attached."""
    fake_context.steplib.api = ApiContext(client=UrllibHTTPClient())  # type: ignore[attr-defined]
    return fake_context
