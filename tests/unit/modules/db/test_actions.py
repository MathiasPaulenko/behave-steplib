"""Tests for DB actions (pure functions)."""

from __future__ import annotations

import pytest

from steplib.modules.db.actions import (
    db_assert_column_equals,
    db_assert_row_count,
    db_query,
    db_set_connection_string,
    db_store,
)
from steplib.modules.db.context import DbContext


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
        self._rows = rows or []
        self.executed: list[str] = []

    def execute(self, query: str) -> MockResult:
        self.executed.append(query)
        return MockResult(self._rows)


@pytest.fixture()
def db_ctx() -> DbContext:
    """Return a DbContext with a mock connection."""
    return DbContext(connection=MockConnection(rows=[{"id": "1", "name": "Ada"}]))


class TestDbSetConnectionString:
    """Tests for db_set_connection_string."""

    def test_set_connection_string(self, db_ctx: DbContext) -> None:
        """Setting connection string should update the context."""
        db_set_connection_string(db_ctx, "sqlite:///test.db")
        assert db_ctx.connection_string == "sqlite:///test.db"


class TestDbQuery:
    """Tests for db_query."""

    def test_query_returns_rows(self, db_ctx: DbContext) -> None:
        """Query should return rows as dicts."""
        rows = db_query(db_ctx, "SELECT * FROM users")
        assert len(rows) == 1
        assert rows[0]["name"] == "Ada"

    def test_query_no_connection_raises(self) -> None:
        """Query without a connection should raise."""
        ctx = DbContext(connection=None)
        with pytest.raises(RuntimeError, match="No database connection"):
            db_query(ctx, "SELECT 1")


class TestDbAssertRowCount:
    """Tests for db_assert_row_count."""

    def test_row_count_matches(self, db_ctx: DbContext) -> None:
        """Matching row count should not raise."""
        db_assert_row_count(db_ctx, "SELECT * FROM users", 1)

    def test_row_count_mismatch_raises(self, db_ctx: DbContext) -> None:
        """Mismatched row count should raise."""
        with pytest.raises(AssertionError, match="Expected 5 rows"):
            db_assert_row_count(db_ctx, "SELECT * FROM users", 5)


class TestDbAssertColumnEquals:
    """Tests for db_assert_column_equals."""

    def test_column_matches(self, db_ctx: DbContext) -> None:
        """Matching column value should not raise."""
        db_assert_column_equals(db_ctx, "SELECT * FROM users", "name", "Ada")

    def test_column_mismatch_raises(self, db_ctx: DbContext) -> None:
        """Mismatched column value should raise."""
        with pytest.raises(AssertionError, match="expected"):
            db_assert_column_equals(db_ctx, "SELECT * FROM users", "name", "Bob")

    def test_column_missing_raises(self, db_ctx: DbContext) -> None:
        """Missing column should raise."""
        with pytest.raises(AssertionError, match="not found"):
            db_assert_column_equals(db_ctx, "SELECT * FROM users", "missing", "value")

    def test_no_rows_raises(self) -> None:
        """No rows should raise."""
        ctx = DbContext(connection=MockConnection(rows=[]))
        with pytest.raises(AssertionError, match="no rows"):
            db_assert_column_equals(ctx, "SELECT * FROM users", "name", "Ada")


class TestDbStore:
    """Tests for db_store."""

    def test_store(self, db_ctx: DbContext) -> None:
        """Storing should save in variables."""
        db_store(db_ctx, "key", "value")
        assert db_ctx.variables["key"] == "value"


class TestDbContextLifecycle:
    """Tests for DbContext.reset and cleanup."""

    def test_reset_clears_variables(self) -> None:
        """reset() should clear variables."""
        ctx = DbContext()
        ctx.variables["key"] = "value"
        ctx.reset()
        assert ctx.variables == {}
