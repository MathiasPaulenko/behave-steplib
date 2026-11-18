"""Regression tests for DB module bugs found in the audit."""

from __future__ import annotations

from typing import Any

import pytest

from steplib.modules.db.client import DatabaseClient
from steplib.modules.db.context import DbContext


class _NonReturningResult:
    """Mimics a SQLAlchemy CursorResult for statements without rows."""

    returns_rows = False

    def keys(self) -> list[str]:
        raise RuntimeError("keys() must not be called without rows")

    def fetchall(self) -> list[Any]:
        raise RuntimeError("fetchall() must not be called without rows")

    def scalar(self) -> Any:
        raise RuntimeError("scalar() must not be called without rows")


class _ReturningResult:
    returns_rows = True

    def keys(self) -> list[str]:
        return ["a"]

    def fetchall(self) -> list[tuple[int]]:
        return [(1,)]

    def scalar(self) -> int:
        return 1


class _FakeConnection:
    def __init__(self, result: Any) -> None:
        self._result = result
        self.committed = 0
        self.closed = False

    def execute(self, clause: Any, params: Any = None) -> Any:
        return self._result

    def commit(self) -> None:
        self.committed += 1

    def close(self) -> None:
        self.closed = True


class _FakeEngine:
    def __init__(self) -> None:
        self.disposed = 0

    def dispose(self) -> None:
        self.disposed += 1


def _client_with(conn: _FakeConnection) -> DatabaseClient:
    """Build a DatabaseClient without touching SQLAlchemy."""
    client = DatabaseClient.__new__(DatabaseClient)
    client._text = lambda q: q
    client.engine = _FakeEngine()
    client.connection = conn
    client._tx = None
    return client


class TestNonReturningStatements:
    """INSERT/UPDATE/DDL statements return no rows; must not crash."""

    def test_execute_returns_empty_for_non_returning(self):
        conn = _FakeConnection(_NonReturningResult())
        client = _client_with(conn)
        assert client.execute("INSERT INTO t VALUES (1)") == []

    def test_execute_scalar_returns_none_for_non_returning(self):
        conn = _FakeConnection(_NonReturningResult())
        client = _client_with(conn)
        assert client.execute_scalar("DELETE FROM t") is None

    def test_execute_still_returns_rows_for_select(self):
        conn = _FakeConnection(_ReturningResult())
        client = _client_with(conn)
        assert client.execute("SELECT a FROM t") == [{"a": 1}]


class TestDbQueryFallback:
    """db_query handles raw-connection results without returns_rows."""

    def test_db_query_with_non_returning_result(self):
        from steplib.modules.db.actions import db_query

        db_ctx = DbContext(connection=_FakeConnection(_NonReturningResult()))
        assert db_query(db_ctx, "UPDATE t SET a = 1") == []

    def test_db_query_scalar_with_non_returning_result(self):
        from steplib.modules.db.actions import db_query_scalar

        db_ctx = DbContext(connection=_FakeConnection(_NonReturningResult()))
        assert db_query_scalar(db_ctx, "UPDATE t SET a = 1") is None


class TestClientCloseResilience:
    """A failing connection.close() must not skip engine.dispose()."""

    def test_close_continues_after_close_failure(self):
        conn = _FakeConnection(_ReturningResult())

        def boom() -> None:
            raise RuntimeError("close failed")

        conn.close = boom  # type: ignore[method-assign]
        client = _client_with(conn)

        with pytest.raises(RuntimeError, match="close failed"):
            client.close()

        assert client.engine.disposed == 1


class TestDbCleanupResilience:
    """A failing rollback must not skip connection/engine cleanup."""

    def test_cleanup_continues_after_rollback_failure(self):
        class BadTx:
            def rollback(self) -> None:
                raise RuntimeError("rollback failed")

        engine = _FakeEngine()
        conn = _FakeConnection(_ReturningResult())
        db_ctx = DbContext(
            engine=engine, connection=conn, transaction=BadTx()  # type: ignore[arg-type]
        )

        with pytest.raises(RuntimeError, match="rollback failed"):
            db_ctx.cleanup()

        assert conn.closed is True
        assert engine.disposed == 1

    def test_disconnect_continues_after_rollback_failure(self):
        from steplib.modules.db.actions import db_disconnect

        class BadTx:
            def rollback(self) -> None:
                raise RuntimeError("rollback failed")

        engine = _FakeEngine()
        conn = _FakeConnection(_ReturningResult())
        db_ctx = DbContext(
            engine=engine, connection=conn, transaction=BadTx()  # type: ignore[arg-type]
        )

        with pytest.raises(RuntimeError, match="rollback failed"):
            db_disconnect(db_ctx)

        assert conn.closed is True
        assert engine.disposed == 1
