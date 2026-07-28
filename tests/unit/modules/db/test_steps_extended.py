"""Extended tests for DB step functions (thin wrappers around actions)."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from steplib.core.state import SteplibState
from steplib.modules.db.context import DbContext
from steplib.modules.db.steps import (
    step_begin_transaction,
    step_column_contains,
    step_column_is_not_null,
    step_column_is_null,
    step_column_not_equals,
    step_commit_transaction,
    step_db_connect,
    step_db_disconnect,
    step_execute_query,
    step_execute_query_with_params,
    step_query_row_count_greater_than,
    step_query_row_count_less_than,
    step_rollback_transaction,
    step_scalar_equals,
    step_store_column_value,
    step_store_row_count,
    step_store_scalar,
    step_table_exists,
    step_table_row_count,
)


class MockResult:
    """Mock SQLAlchemy result object."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def keys(self) -> list[str]:
        if not self._rows:
            return []
        return list(self._rows[0].keys())

    def fetchall(self) -> list[list[Any]]:
        return [list(row.values()) for row in self._rows]

    def scalar(self) -> Any:
        if not self._rows:
            return None
        return next(iter(self._rows[0].values()))


class MockTransaction:
    """Mock SQLAlchemy transaction."""

    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


class MockConnection:
    """Mock SQLAlchemy connection."""

    def __init__(
        self,
        rows: list[dict[str, Any]] | None = None,
        scalar_value: Any = 42,
    ) -> None:
        self._rows = rows or [{"id": 1, "name": "Ada", "email": "ada@example.com"}]
        self._scalar_value = scalar_value
        self._transaction: MockTransaction | None = None
        self.closed = False

    def execute(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> MockResult:
        return MockResult(self._rows)

    def execute_scalar(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        return self._scalar_value

    def begin(self) -> MockTransaction:
        self._transaction = MockTransaction()
        return self._transaction

    def close(self) -> None:
        self.closed = True


class MockEngine:
    """Mock SQLAlchemy engine."""

    def __init__(self) -> None:
        self.disposed = False

    def dispose(self) -> None:
        self.disposed = True


def _make_context(
    rows: list[dict[str, Any]] | None = None,
    scalar_value: Any = 42,
) -> SimpleNamespace:
    """Create a behave-like context with steplib state and DbContext."""
    context = SimpleNamespace()
    state = SteplibState(context, registry=None)  # type: ignore[arg-type]
    state.db = DbContext(  # type: ignore[attr-defined]
        connection=MockConnection(rows=rows, scalar_value=scalar_value),
        engine=MockEngine(),
    )
    context.steplib = state
    return context


def _make_context_no_conn() -> SimpleNamespace:
    """Create a context with no DB connection."""
    context = SimpleNamespace()
    state = SteplibState(context, registry=None)  # type: ignore[arg-type]
    state.db = DbContext(connection=None)  # type: ignore[attr-defined]
    context.steplib = state
    return context


# --- Connection management ---


def test_step_db_connect() -> None:
    context = _make_context_no_conn()
    context.steplib.db.connection_string = "sqlite:///test.db"  # type: ignore[attr-defined]
    # step_db_connect calls db_connect which uses the client module
    # We can't fully test it without mocking sqlalchemy, but we can verify it raises
    # when no connection string is set
    context2 = _make_context_no_conn()
    with pytest.raises(RuntimeError, match="No connection string"):
        step_db_connect(context2)


def test_step_db_disconnect() -> None:
    context = _make_context()
    step_db_disconnect(context)
    assert context.steplib.db.connection is None  # type: ignore[attr-defined]
    assert context.steplib.db.engine is None  # type: ignore[attr-defined]


# --- Extended assertions ---


def test_step_query_row_count_greater_than() -> None:
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    step_query_row_count_greater_than(context, 0)


def test_step_query_row_count_greater_than_raises() -> None:
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    with pytest.raises(AssertionError, match="Expected more than"):
        step_query_row_count_greater_than(context, 1)


def test_step_query_row_count_less_than() -> None:
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    step_query_row_count_less_than(context, 10)


def test_step_query_row_count_less_than_raises() -> None:
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    with pytest.raises(AssertionError, match="Expected fewer than"):
        step_query_row_count_less_than(context, 1)


def test_step_column_contains() -> None:
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    step_column_contains(context, '"email"', '"@"')


def test_step_column_contains_raises() -> None:
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    with pytest.raises(AssertionError, match="expected to contain"):
        step_column_contains(context, '"email"', '"xyz"')


def test_step_column_not_equals() -> None:
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    step_column_not_equals(context, '"name"', '"Bob"')


def test_step_column_not_equals_raises() -> None:
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    with pytest.raises(AssertionError, match="should not equal"):
        step_column_not_equals(context, '"name"', '"Ada"')


def test_step_column_is_null() -> None:
    context = _make_context(rows=[{"x": None}])
    step_execute_query(context, '"SELECT x"')
    step_column_is_null(context, '"x"')


def test_step_column_is_null_raises() -> None:
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    with pytest.raises(AssertionError, match="expected NULL"):
        step_column_is_null(context, '"name"')


def test_step_column_is_not_null() -> None:
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    step_column_is_not_null(context, '"name"')


def test_step_column_is_not_null_raises() -> None:
    context = _make_context(rows=[{"x": None}])
    step_execute_query(context, '"SELECT x"')
    with pytest.raises(AssertionError, match="expected NOT NULL"):
        step_column_is_not_null(context, '"x"')


def test_step_scalar_equals() -> None:
    context = _make_context(scalar_value=42)
    step_scalar_equals(context, '"SELECT COUNT(*)"', '"42"')


def test_step_scalar_equals_raises() -> None:
    context = _make_context(scalar_value=42)
    with pytest.raises(AssertionError, match="Scalar"):
        step_scalar_equals(context, '"SELECT COUNT(*)"', '"99"')


# --- Store / Extract ---


def test_step_store_column_value() -> None:
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    step_store_column_value(context, '"name"', '"var"')
    assert context.steplib.db.variables["var"] == "Ada"  # type: ignore[attr-defined]


def test_step_store_row_count() -> None:
    context = _make_context()
    step_execute_query(context, '"SELECT * FROM users"')
    step_store_row_count(context, '"count"')
    assert context.steplib.db.variables["count"] == 1  # type: ignore[attr-defined]


def test_step_store_scalar() -> None:
    context = _make_context(scalar_value=77)
    step_store_scalar(context, '"SELECT COUNT(*)"', '"total"')
    assert context.steplib.db.variables["total"] == 77  # type: ignore[attr-defined]


# --- Transactional ---


def test_step_begin_transaction() -> None:
    context = _make_context()
    step_begin_transaction(context)
    assert context.steplib.db.transaction is not None  # type: ignore[attr-defined]


def test_step_rollback_transaction() -> None:
    context = _make_context()
    step_begin_transaction(context)
    step_rollback_transaction(context)
    assert context.steplib.db.transaction is None  # type: ignore[attr-defined]


def test_step_rollback_transaction_raises() -> None:
    context = _make_context()
    with pytest.raises(RuntimeError, match="No active transaction"):
        step_rollback_transaction(context)


def test_step_commit_transaction() -> None:
    context = _make_context()
    step_begin_transaction(context)
    step_commit_transaction(context)
    assert context.steplib.db.transaction is None  # type: ignore[attr-defined]


def test_step_commit_transaction_raises() -> None:
    context = _make_context()
    with pytest.raises(RuntimeError, match="No active transaction"):
        step_commit_transaction(context)


# --- Table assertions ---


def test_step_table_exists() -> None:
    context = _make_context(rows=[{"name": "users"}])
    context.steplib.db.connection_string = "sqlite:///test.db"  # type: ignore[attr-defined]
    step_table_exists(context, '"users"')


def test_step_table_row_count() -> None:
    context = _make_context(rows=[{"cnt": 5}])
    context.steplib.db.connection_string = "sqlite:///test.db"  # type: ignore[attr-defined]
    step_table_row_count(context, '"users"', 5)


def test_step_table_row_count_raises() -> None:
    context = _make_context(rows=[{"cnt": 5}])
    context.steplib.db.connection_string = "sqlite:///test.db"  # type: ignore[attr-defined]
    with pytest.raises(AssertionError, match="expected 10 rows"):
        step_table_row_count(context, '"users"', 10)


# --- Query with params ---


def test_step_execute_query_with_params() -> None:
    context = _make_context()
    step_execute_query_with_params(
        context,
        '"SELECT * FROM users WHERE id = :id"',
        '\'{"id": 1}\'',
    )
    result = context.steplib.db.variables["_last_result"]  # type: ignore[attr-defined]
    assert len(result) == 1
    assert result[0]["name"] == "Ada"
