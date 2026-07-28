"""Tests for ApiContext and DbContext reset/cleanup methods."""

from __future__ import annotations

from steplib.modules.api.client import UrllibHTTPClient
from steplib.modules.api.context import ApiContext
from steplib.modules.db.context import DbContext


class TestApiContextReset:
    """Tests for ApiContext.reset()."""

    def test_reset_clears_default_headers(self) -> None:
        ctx = ApiContext()
        ctx.default_headers["Authorization"] = "Bearer token"
        ctx.reset()
        assert ctx.default_headers == {}

    def test_reset_clears_query_params(self) -> None:
        ctx = ApiContext()
        ctx.query_params["page"] = "1"
        ctx.reset()
        assert ctx.query_params == {}

    def test_reset_clears_auth(self) -> None:
        ctx = ApiContext()
        ctx.auth = ("user", "pass")
        ctx.reset()
        assert ctx.auth is None

    def test_reset_clears_cookies(self) -> None:
        ctx = ApiContext()
        ctx.cookies["session"] = "abc123"
        ctx.reset()
        assert ctx.cookies == {}

    def test_reset_clears_timeout(self) -> None:
        ctx = ApiContext()
        ctx.timeout = 30.0
        ctx.reset()
        assert ctx.timeout is None

    def test_reset_restores_allow_redirects(self) -> None:
        ctx = ApiContext()
        ctx.allow_redirects = False
        ctx.reset()
        assert ctx.allow_redirects is True

    def test_reset_restores_ssl_verify(self) -> None:
        ctx = ApiContext()
        ctx.ssl_verify = False
        ctx.reset()
        assert ctx.ssl_verify is True

    def test_reset_clears_proxies(self) -> None:
        ctx = ApiContext()
        ctx.proxies["http"] = "http://proxy:8080"
        ctx.reset()
        assert ctx.proxies == {}

    def test_reset_clears_last_request_and_response(self) -> None:
        ctx = ApiContext()
        ctx.last_request = ctx.last_response = object()  # type: ignore[assignment]
        ctx.reset()
        assert ctx.last_request is None
        assert ctx.last_response is None

    def test_reset_clears_variables(self) -> None:
        ctx = ApiContext()
        ctx.variables["key"] = "value"
        ctx.reset()
        assert ctx.variables == {}

    def test_reset_preserves_client_and_base_url(self) -> None:
        client = UrllibHTTPClient()
        ctx = ApiContext(client=client, base_url="https://api.example.com")
        ctx.reset()
        assert ctx.client is client
        assert ctx.base_url == "https://api.example.com"


class TestApiContextCleanup:
    """Tests for ApiContext.cleanup()."""

    def test_cleanup_calls_client_close(self) -> None:
        class MockClient:
            closed = False

            def close(self) -> None:
                self.closed = True

        client = MockClient()
        ctx = ApiContext(client=client)  # type: ignore[arg-type]
        ctx.cleanup()
        assert client.closed is True

    def test_cleanup_with_no_close_method_is_noop(self) -> None:
        class NoCloseClient:
            pass

        ctx = ApiContext(client=NoCloseClient())  # type: ignore[arg-type]
        ctx.cleanup()  # should not raise

    def test_cleanup_with_none_client_is_noop(self) -> None:
        ctx = ApiContext()
        ctx.client = None
        ctx.cleanup()  # should not raise


class TestDbContextCleanup:
    """Tests for DbContext.cleanup()."""

    def test_cleanup_rolls_back_transaction(self) -> None:
        class MockTransaction:
            rolled_back = False

            def rollback(self) -> None:
                self.rolled_back = True

        txn = MockTransaction()
        ctx = DbContext(transaction=txn)  # type: ignore[arg-type]
        ctx.cleanup()
        assert txn.rolled_back is True
        assert ctx.transaction is None

    def test_cleanup_closes_connection(self) -> None:
        class MockConnection:
            closed = False

            def close(self) -> None:
                self.closed = True

        conn = MockConnection()
        ctx = DbContext(connection=conn)  # type: ignore[arg-type]
        ctx.cleanup()
        assert conn.closed is True
        assert ctx.connection is None

    def test_cleanup_disposes_engine(self) -> None:
        class MockEngine:
            disposed = False

            def dispose(self) -> None:
                self.disposed = True

        engine = MockEngine()
        ctx = DbContext(engine=engine)  # type: ignore[arg-type]
        ctx.cleanup()
        assert engine.disposed is True
        assert ctx.engine is None

    def test_cleanup_with_no_resources_is_noop(self) -> None:
        ctx = DbContext()
        ctx.cleanup()  # should not raise
        assert ctx.engine is None
        assert ctx.connection is None
        assert ctx.transaction is None
