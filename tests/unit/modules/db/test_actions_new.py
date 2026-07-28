"""Tests for new DB actions (pure functions)."""

from __future__ import annotations

from typing import Any

import pytest

from steplib.modules.db.actions import (
    db_assert_column_contains,
    db_assert_column_is_not_null,
    db_assert_column_is_null,
    db_assert_column_not_equals,
    db_assert_row_count_greater_than,
    db_assert_row_count_less_than,
    db_assert_scalar_equals,
    db_assert_table_exists,
    db_assert_table_row_count,
    db_begin_transaction,
    db_commit,
    db_disconnect,
    db_query_scalar,
    db_query_with_params,
    db_rollback,
    db_store_column_value,
    db_store_row_count,
    db_store_scalar,
)
from steplib.modules.db.context import DbContext


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
    """Mock SQLAlchemy connection with params and scalar support."""

    def __init__(
        self,
        rows: list[dict[str, Any]] | None = None,
        scalar_value: Any = 42,
    ) -> None:
        self._rows = rows or []
        self._scalar_value = scalar_value
        self.executed: list[tuple[str, dict[str, Any] | None]] = []
        self._transaction: MockTransaction | None = None
        self.closed = False

    def execute(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> MockResult:
        self.executed.append((query, params))
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


@pytest.fixture()
def db_ctx() -> DbContext:
    """Return a DbContext with a mock connection."""
    return DbContext(
        connection=MockConnection(rows=[{"id": 1, "name": "Ada", "email": "ada@example.com"}]),
        engine=MockEngine(),
    )


@pytest.fixture()
def no_conn_ctx() -> DbContext:
    """Return a DbContext with no connection."""
    return DbContext(connection=None)


# --- Query with params ---


class TestDbQueryWithParams:
    def test_query_with_params_returns_rows(self, db_ctx: DbContext) -> None:
        rows = db_query_with_params(db_ctx, "SELECT * FROM users WHERE id = :id", {"id": 1})
        assert len(rows) == 1
        assert rows[0]["name"] == "Ada"

    def test_query_with_params_no_connection_raises(self, no_conn_ctx: DbContext) -> None:
        with pytest.raises(RuntimeError, match="No database connection"):
            db_query_with_params(no_conn_ctx, "SELECT 1", {})


# --- Scalar ---


class MockConnectionNoScalar:
    """Mock connection without execute_scalar, to test fallback path."""

    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self._rows = rows or []

    def execute(self, query: str, params: dict[str, Any] | None = None) -> MockResult:
        return MockResult(self._rows)


class TestDbQueryScalar:
    def test_scalar_via_execute_scalar(self) -> None:
        ctx = DbContext(connection=MockConnection(scalar_value=99))
        result = db_query_scalar(ctx, "SELECT COUNT(*) FROM users")
        assert result == 99

    def test_scalar_via_execute_fallback(self) -> None:
        ctx = DbContext(
            connection=MockConnectionNoScalar(rows=[{"cnt": 7}]),
        )
        result = db_query_scalar(ctx, "SELECT COUNT(*) FROM users")
        assert result == 7

    def test_scalar_no_connection_raises(self, no_conn_ctx: DbContext) -> None:
        with pytest.raises(RuntimeError, match="No database connection"):
            db_query_scalar(no_conn_ctx, "SELECT 1")


class TestDbAssertScalarEquals:
    def test_scalar_equals_matches(self) -> None:
        ctx = DbContext(connection=MockConnection(scalar_value=42))
        db_assert_scalar_equals(ctx, "SELECT COUNT(*)", "42")

    def test_scalar_equals_mismatch_raises(self) -> None:
        ctx = DbContext(connection=MockConnection(scalar_value=42))
        with pytest.raises(AssertionError, match="Scalar"):
            db_assert_scalar_equals(ctx, "SELECT COUNT(*)", "99")


# --- Extended assertions ---


class TestDbAssertRowCountGreaterThan:
    def test_count_greater_passes(self, db_ctx: DbContext) -> None:
        db_assert_row_count_greater_than(db_ctx, "SELECT * FROM users", 0)

    def test_count_greater_fails(self, db_ctx: DbContext) -> None:
        with pytest.raises(AssertionError, match="Expected more than"):
            db_assert_row_count_greater_than(db_ctx, "SELECT * FROM users", 1)


class TestDbAssertRowCountLessThan:
    def test_count_less_passes(self, db_ctx: DbContext) -> None:
        db_assert_row_count_less_than(db_ctx, "SELECT * FROM users", 10)

    def test_count_less_fails(self, db_ctx: DbContext) -> None:
        with pytest.raises(AssertionError, match="Expected fewer than"):
            db_assert_row_count_less_than(db_ctx, "SELECT * FROM users", 1)


class TestDbAssertColumnContains:
    def test_contains_passes(self, db_ctx: DbContext) -> None:
        db_assert_column_contains(db_ctx, "SELECT * FROM users", "email", "@")

    def test_contains_fails(self, db_ctx: DbContext) -> None:
        with pytest.raises(AssertionError, match="expected to contain"):
            db_assert_column_contains(db_ctx, "SELECT * FROM users", "email", "xyz")

    def test_no_rows_raises(self) -> None:
        ctx = DbContext(connection=MockConnection(rows=[]))
        with pytest.raises(AssertionError, match="no rows"):
            db_assert_column_contains(ctx, "SELECT 1", "col", "x")


class TestDbAssertColumnNotEquals:
    def test_not_equals_passes(self, db_ctx: DbContext) -> None:
        db_assert_column_not_equals(db_ctx, "SELECT * FROM users", "name", "Bob")

    def test_not_equals_fails(self, db_ctx: DbContext) -> None:
        with pytest.raises(AssertionError, match="should not equal"):
            db_assert_column_not_equals(db_ctx, "SELECT * FROM users", "name", "Ada")


class TestDbAssertColumnIsNull:
    def test_is_null_passes(self) -> None:
        ctx = DbContext(connection=MockConnection(rows=[{"x": None}]))
        db_assert_column_is_null(ctx, "SELECT x", "x")

    def test_is_null_fails(self, db_ctx: DbContext) -> None:
        with pytest.raises(AssertionError, match="expected NULL"):
            db_assert_column_is_null(db_ctx, "SELECT * FROM users", "name")


class TestDbAssertColumnIsNotNull:
    def test_is_not_null_passes(self, db_ctx: DbContext) -> None:
        db_assert_column_is_not_null(db_ctx, "SELECT * FROM users", "name")

    def test_is_not_null_fails(self) -> None:
        ctx = DbContext(connection=MockConnection(rows=[{"x": None}]))
        with pytest.raises(AssertionError, match="expected NOT NULL"):
            db_assert_column_is_not_null(ctx, "SELECT x", "x")


# --- Store / Extract ---


class TestDbStoreColumnValue:
    def test_store_column(self, db_ctx: DbContext) -> None:
        db_store_column_value(db_ctx, "SELECT * FROM users", "name", "var")
        assert db_ctx.variables["var"] == "Ada"

    def test_store_column_no_rows_raises(self) -> None:
        ctx = DbContext(connection=MockConnection(rows=[]))
        with pytest.raises(AssertionError, match="no rows"):
            db_store_column_value(ctx, "SELECT 1", "col", "var")


class TestDbStoreRowCount:
    def test_store_row_count(self, db_ctx: DbContext) -> None:
        db_store_row_count(db_ctx, "SELECT * FROM users", "count")
        assert db_ctx.variables["count"] == 1


class TestDbStoreScalar:
    def test_store_scalar(self) -> None:
        ctx = DbContext(connection=MockConnection(scalar_value=77))
        db_store_scalar(ctx, "SELECT COUNT(*)", "total")
        assert ctx.variables["total"] == 77


# --- Transactional ---


class TestDbBeginTransaction:
    def test_begin_transaction(self, db_ctx: DbContext) -> None:
        db_begin_transaction(db_ctx)
        assert db_ctx.transaction is not None

    def test_begin_no_connection_raises(self, no_conn_ctx: DbContext) -> None:
        with pytest.raises(RuntimeError, match="No database connection"):
            db_begin_transaction(no_conn_ctx)


class TestDbRollback:
    def test_rollback(self, db_ctx: DbContext) -> None:
        db_begin_transaction(db_ctx)
        db_rollback(db_ctx)
        assert db_ctx.transaction is None
        assert db_ctx.connection._transaction.rolled_back is True  # type: ignore[union-attr]

    def test_rollback_no_transaction_raises(self, db_ctx: DbContext) -> None:
        with pytest.raises(RuntimeError, match="No active transaction"):
            db_rollback(db_ctx)


class TestDbCommit:
    def test_commit(self, db_ctx: DbContext) -> None:
        db_begin_transaction(db_ctx)
        db_commit(db_ctx)
        assert db_ctx.transaction is None
        assert db_ctx.connection._transaction.committed is True  # type: ignore[union-attr]

    def test_commit_no_transaction_raises(self, db_ctx: DbContext) -> None:
        with pytest.raises(RuntimeError, match="No active transaction"):
            db_commit(db_ctx)


# --- Disconnect ---


class TestDbDisconnect:
    def test_disconnect_closes_connection(self) -> None:
        conn = MockConnection()
        engine = MockEngine()
        ctx = DbContext(connection=conn, engine=engine)
        db_disconnect(ctx)
        assert ctx.connection is None
        assert ctx.engine is None
        assert conn.closed is True
        assert engine.disposed is True

    def test_disconnect_with_transaction_rolls_back(self) -> None:
        conn = MockConnection()
        ctx = DbContext(connection=conn)
        db_begin_transaction(ctx)
        db_disconnect(ctx)
        assert ctx.transaction is None
        assert conn._transaction.rolled_back is True  # type: ignore[union-attr]


# --- Table assertions ---


class TestDbAssertTableRowCount:
    def test_table_row_count_matches(self) -> None:
        ctx = DbContext(
            connection=MockConnection(rows=[{"cnt": 5}]),
        )
        db_assert_table_row_count(ctx, "users", 5)

    def test_table_row_count_mismatch_raises(self) -> None:
        ctx = DbContext(
            connection=MockConnection(rows=[{"cnt": 5}]),
        )
        with pytest.raises(AssertionError, match="expected 10 rows"):
            db_assert_table_row_count(ctx, "users", 10)


# --- Table existence ---


class TestDbAssertTableExists:
    """Tests for db_assert_table_exists."""

    def test_table_exists_sqlite(self) -> None:
        """Table exists via sqlite_master query."""
        ctx = DbContext(
            connection=MockConnection(rows=[{"name": "users"}]),
            connection_string="sqlite:///test.db",
        )
        db_assert_table_exists(ctx, "users")

    def test_table_exists_non_sqlite(self) -> None:
        """Table exists via information_schema query."""
        ctx = DbContext(
            connection=MockConnection(rows=[{"table_name": "users"}]),
            connection_string="postgresql:///test",
        )
        db_assert_table_exists(ctx, "users")

    def test_table_not_found_raises(self) -> None:
        """Table not found raises AssertionError."""

        class FailingConnection(MockConnection):
            """Mock that raises for SELECT 1 FROM ... queries."""

            def execute(
                self,
                query: str,
                params: dict[str, Any] | None = None,
            ) -> MockResult:
                if "SELECT 1 FROM" in query:
                    raise RuntimeError("no such table")
                return super().execute(query, params)

        ctx = DbContext(
            connection=FailingConnection(rows=[]),
            connection_string="sqlite:///test.db",
        )
        with pytest.raises(AssertionError, match="Table 'users' does not exist"):
            db_assert_table_exists(ctx, "users")

    def test_table_exists_no_connection_raises(self) -> None:
        """No connection raises RuntimeError, not misleading AssertionError."""
        ctx = DbContext(
            connection=None,
            connection_string="sqlite:///test.db",
        )
        with pytest.raises(RuntimeError, match="No database connection configured"):
            db_assert_table_exists(ctx, "users")

    def test_table_exists_fallback_success(self) -> None:
        """Fallback SELECT works when metadata query returns no rows."""
        ctx = DbContext(
            connection=MockConnection(rows=[]),
            connection_string="sqlite:///test.db",
        )
        # MockConnection returns empty rows for the metadata query,
        # then the fallback SELECT 1 FROM users LIMIT 1 also returns
        # empty rows (no exception), so table is considered to exist.
        db_assert_table_exists(ctx, "users")


class TestSqlIdentifierValidation:
    """Regression tests for SQL identifier validation."""

    def test_table_exists_rejects_semicolon_injection(self) -> None:
        """Table name with semicolon is rejected (SQL injection attempt)."""
        ctx = DbContext(
            connection=MockConnection(rows=[]),
            connection_string="sqlite:///test.db",
        )
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            db_assert_table_exists(ctx, "users; DROP TABLE users;--")

    def test_table_exists_rejects_quote_injection(self) -> None:
        """Table name with quotes is rejected (SQL injection attempt)."""
        ctx = DbContext(
            connection=MockConnection(rows=[]),
            connection_string="sqlite:///test.db",
        )
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            db_assert_table_exists(ctx, "users' OR '1'='1")

    def test_table_exists_rejects_empty_name(self) -> None:
        """Empty table name is rejected."""
        ctx = DbContext(
            connection=MockConnection(rows=[]),
            connection_string="sqlite:///test.db",
        )
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            db_assert_table_exists(ctx, "")

    def test_table_exists_accepts_schema_qualified(self) -> None:
        """Schema-qualified table names are accepted."""
        ctx = DbContext(
            connection=MockConnection(rows=[]),
            connection_string="sqlite:///test.db",
        )
        # Should not raise ValueError - schema.public.users is valid
        db_assert_table_exists(ctx, "public.users")

    def test_table_row_count_rejects_injection(self) -> None:
        """Table row count with injection attempt is rejected."""
        ctx = DbContext(
            connection=MockConnection(rows=[{"cnt": 5}]),
            connection_string="sqlite:///test.db",
        )
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            db_assert_table_row_count(ctx, "users; DROP TABLE users", 5)
