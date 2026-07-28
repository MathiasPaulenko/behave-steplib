"""Tests for ecosystem helpers (behave-kit, behave-tables, behave-data)."""

from __future__ import annotations

import sys
from collections.abc import Callable
from unittest.mock import patch

import pytest

from steplib.core.ecosystem import (
    assert_soft,
    check_behave_doctor_available,
    check_behave_model_available,
    load_test_data,
    wrap_table,
)
from steplib.core.exceptions import MissingDependencyError, StepContractError


def _block_import(module_name: str) -> Callable[..., object]:
    """Return a side-effect that raises ImportError for *module_name*."""

    def _raise(*_args: object, **_kwargs: object) -> object:
        raise ImportError(f"No module named '{module_name}'")

    return _raise


def test_assert_soft_missing_dependency() -> None:
    """assert_soft should raise MissingDependencyError if behave-kit is not installed."""
    with (
        patch("builtins.__import__", side_effect=_block_import("behave_kit")),
        pytest.raises(MissingDependencyError, match="kit"),
    ):
        assert_soft(True)


def test_assert_soft_with_message_missing_dependency() -> None:
    """assert_soft with a message should also raise MissingDependencyError."""
    with (
        patch("builtins.__import__", side_effect=_block_import("behave_kit")),
        pytest.raises(MissingDependencyError, match="kit"),
    ):
        assert_soft(False, "expected failure")


def test_wrap_table_missing_dependency() -> None:
    """wrap_table should raise MissingDependencyError if behave-tables is not installed."""
    with (
        patch("builtins.__import__", side_effect=_block_import("behave_tables")),
        pytest.raises(MissingDependencyError, match="tables"),
    ):
        wrap_table(None)


def test_check_behave_model_available() -> None:
    """check_behave_model_available should return a bool."""
    result = check_behave_model_available()
    assert isinstance(result, bool)


def test_check_behave_doctor_available() -> None:
    """check_behave_doctor_available should return a bool."""
    result = check_behave_doctor_available()
    assert isinstance(result, bool)


def test_load_test_data_missing_dependency() -> None:
    """load_test_data should raise MissingDependencyError if behave-data is not installed."""
    with (
        patch("builtins.__import__", side_effect=_block_import("behave_data")),
        pytest.raises(MissingDependencyError, match="data"),
    ):
        load_test_data("test.csv")


def test_load_test_data_no_load_function(monkeypatch: pytest.MonkeyPatch) -> None:
    """load_test_data should raise StepContractError if behave-data has no 'load' function."""
    import types

    fake_module = types.ModuleType("behave_data")
    monkeypatch.setitem(sys.modules, "behave_data", fake_module)
    with pytest.raises(StepContractError, match="load"):
        load_test_data("test.csv")


def test_assert_soft_with_message_calls_kit(monkeypatch: pytest.MonkeyPatch) -> None:
    """assert_soft should delegate to behave_kit.assert_soft with a message."""
    import types

    calls: list[tuple[bool, str]] = []

    def fake_assert_soft(condition: bool, message: str = "") -> None:
        calls.append((condition, message))

    fake_module = types.ModuleType("behave_kit")
    fake_module.assert_soft = fake_assert_soft  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "behave_kit", fake_module)

    assert_soft(True, "my message")
    assert calls == [(True, "my message")]


def test_assert_soft_without_message_calls_kit(monkeypatch: pytest.MonkeyPatch) -> None:
    """assert_soft should delegate to behave_kit.assert_soft without a message."""
    import types

    calls: list[tuple[bool, str]] = []

    def fake_assert_soft(condition: bool, message: str = "") -> None:
        calls.append((condition, message))

    fake_module = types.ModuleType("behave_kit")
    fake_module.assert_soft = fake_assert_soft  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "behave_kit", fake_module)

    assert_soft(False)
    assert calls == [(False, "")]


def test_wrap_table_calls_behave_tables(monkeypatch: pytest.MonkeyPatch) -> None:
    """wrap_table should delegate to behave_tables.wrap."""
    import types

    sentinel = object()
    fake_module = types.ModuleType("behave_tables")
    fake_module.wrap = lambda table: sentinel  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "behave_tables", fake_module)

    result = wrap_table("fake_table")
    assert result is sentinel


def test_load_test_data_calls_behave_data(monkeypatch: pytest.MonkeyPatch) -> None:
    """load_test_data should delegate to behave_data.load with kwargs."""
    import types

    calls: list[tuple[str, dict[str, object]]] = []

    def fake_load(source: str, **kwargs: object) -> str:
        calls.append((source, dict(kwargs)))
        return "loaded"

    fake_module = types.ModuleType("behave_data")
    fake_module.load = fake_load  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "behave_data", fake_module)

    result = load_test_data("data.json", encoding="utf-8")
    assert result == "loaded"
    assert calls == [("data.json", {"encoding": "utf-8"})]
