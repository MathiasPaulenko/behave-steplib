"""Regression tests for SteplibState cleanup/reset resilience."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from steplib.core.registry import StepRegistry
from steplib.core.state import SteplibState


class _Recorder:
    """Fake module context recording reset/cleanup calls."""

    def __init__(self, fail: bool = False) -> None:
        self.reset_called = 0
        self.cleanup_called = 0
        self._fail = fail

    def reset(self) -> None:
        self.reset_called += 1
        if self._fail:
            raise RuntimeError("reset failed")

    def cleanup(self) -> None:
        self.cleanup_called += 1
        if self._fail:
            raise RuntimeError("cleanup failed")


def _state() -> SteplibState:
    return SteplibState(SimpleNamespace(), StepRegistry(auto_register_behave=False))


class TestCleanupResilience:
    """A failing module context must not block cleanup of the others."""

    def test_cleanup_runs_all_contexts_and_reraises_first_error(self):
        state = _state()
        failing = _Recorder(fail=True)
        ok = _Recorder()
        state.mod_a = failing  # type: ignore[attr-defined]
        state.mod_b = ok  # type: ignore[attr-defined]

        with pytest.raises(RuntimeError, match="cleanup failed"):
            state.cleanup()

        assert failing.cleanup_called == 1
        assert ok.cleanup_called == 1

    def test_cleanup_without_failures_runs_all(self):
        state = _state()
        ok1, ok2 = _Recorder(), _Recorder()
        state.mod_a = ok1  # type: ignore[attr-defined]
        state.mod_b = ok2  # type: ignore[attr-defined]

        state.cleanup()

        assert ok1.cleanup_called == 1
        assert ok2.cleanup_called == 1

    def test_reset_runs_all_contexts_and_reraises_first_error(self):
        state = _state()
        failing = _Recorder(fail=True)
        ok = _Recorder()
        state.mod_a = failing  # type: ignore[attr-defined]
        state.mod_b = ok  # type: ignore[attr-defined]

        with pytest.raises(RuntimeError, match="reset failed"):
            state.reset()

        assert failing.reset_called == 1
        assert ok.reset_called == 1
