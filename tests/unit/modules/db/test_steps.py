"""Tests for DB steps (using mock connection)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from steplib.core.state import SteplibState
from steplib.modules.db.context import DbContext
from steplib.modules.db.steps import (
    step_column_contains,
    step_column_equals,
    step_column_not_equals,
    step_execute_query,
    step_execute_query_with_params,
    step_query_row_count,
    step_set_db_connection,
)


class MockResult:
    """Mock SQLAlchemy result object."""

    def __init__(self, rows: list[dict[str, str]]) -> None:
        self._rows = rows

    def keys(self) -> list[str]:
        if not self._rows:
            return []
        return list(self._rows[0].keys())

    def fetchall(self) -> list[list[str]]:
        return [list(row.values()) for row in self._rows]


class MockConnection:
    """Mock SQLAlchemy connection."""

    def __init__(self, rows: list[dict[str, str]] | None = None) -> None:
        self._rows = rows or [{"id": "1", "name": "Ada"}]

    def execute(self, query: str) -> MockResult:
        return MockResult(self._rows)


def _make_context(rows: list[dict[str, str]] | None = None) -> SimpleNamespace:
    """Create a behave-like context with steplib state and DbContext."""
    context = SimpleNamespace()
    state = SteplibState(context, registry=None)  # type: ignore[arg-type]
    state.db = DbContext(connection=MockConnection(rows))  # type: ignore[attr-defined]
    context.steplib = state
    return context


def test_step_set_db_connection() -> None:
    """step_set_db_connection should set the connection string."""
    context = _make_context()
    step_set_db_connection(context, '"sqlite:///test.db"')
    assert context.steplib.db.connection_string == "sqlite:///test.db"  # type: ignore[attr-defined]


def test_step_execute_query() -> None:
    """step_execute_query should store the result in variables."""
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    result = context.steplib.db.variables["_last_result"]  # type: ignore[attr-defined]
    assert len(result) == 1
    assert result[0]["name"] == "Ada"


def test_step_query_row_count() -> None:
    """step_query_row_count should assert the row count."""
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    step_query_row_count(context, 1)


def test_step_query_row_count_mismatch() -> None:
    """step_query_row_count should raise on mismatch."""
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    with pytest.raises(AssertionError, match="Expected 5 rows"):
        step_query_row_count(context, 5)


def test_step_column_equals() -> None:
    """step_column_equals should assert a column value."""
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    step_column_equals(context, '"name"', '"Ada"')


def test_step_column_equals_mismatch() -> None:
    """step_column_equals should raise on mismatch."""
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    with pytest.raises(AssertionError, match="expected"):
        step_column_equals(context, '"name"', '"Bob"')


class TestBug37StepNormalization:
    """Regression tests for Bug 37: step_column_equals, step_column_contains,
    and step_column_not_equals must normalize boolean/None values using
    _normalize_value instead of str()."""

    def test_step_column_equals_boolean_true(self) -> None:
        context = _make_context(rows=[{"id": "1", "active": True}])
        step_execute_query(context, '"SELECT * FROM t"')
        step_column_equals(context, '"active"', '"true"')

    def test_step_column_equals_boolean_false(self) -> None:
        context = _make_context(rows=[{"id": "1", "active": False}])
        step_execute_query(context, '"SELECT * FROM t"')
        step_column_equals(context, '"active"', '"false"')

    def test_step_column_equals_none(self) -> None:
        context = _make_context(rows=[{"id": "1", "deleted_at": None}])
        step_execute_query(context, '"SELECT * FROM t"')
        step_column_equals(context, '"deleted_at"', '"null"')

    def test_step_column_not_equals_boolean(self) -> None:
        context = _make_context(rows=[{"id": "1", "active": True}])
        step_execute_query(context, '"SELECT * FROM t"')
        step_column_not_equals(context, '"active"', '"false"')

    def test_step_column_not_equals_none(self) -> None:
        context = _make_context(rows=[{"id": "1", "active": True}])
        step_execute_query(context, '"SELECT * FROM t"')
        step_column_not_equals(context, '"active"', '"null"')

    def test_step_column_contains_boolean(self) -> None:
        context = _make_context(rows=[{"id": "1", "active": True}])
        step_execute_query(context, '"SELECT * FROM t"')
        step_column_contains(context, '"active"', '"tru"')


class TestBug15ExecuteQueryWithParamsInvalidJson:
    """Regression tests for Bug 15: step_execute_query_with_params should
    raise AssertionError, not json.JSONDecodeError, when params is invalid JSON."""

    def test_invalid_params_raises_assertion_error(self) -> None:
        context = _make_context()
        with pytest.raises(AssertionError, match="Invalid JSON params"):
            step_execute_query_with_params(context, '"SELECT 1"', "'{invalid json}'")
