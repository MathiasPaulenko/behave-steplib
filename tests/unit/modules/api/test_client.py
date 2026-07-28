"""Tests for the API HTTP client implementations."""

from __future__ import annotations

import io
import urllib.error
import urllib.request

import pytest

from steplib.modules.api.client import NoRedirectHandler, UrllibHTTPClient


class TestNoRedirectHandler:
    """Tests for NoRedirectHandler."""

    def test_raises_http_error_with_real_status_code(self) -> None:
        """NoRedirectHandler should raise HTTPError with the actual redirect status code."""
        handler = NoRedirectHandler()
        headers = {"Location": "https://example.com/new"}
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            handler.redirect_request(
                req=urllib.request.Request("https://example.com/old"),
                fp=io.BytesIO(b""),
                code=301,
                msg="Moved Permanently",
                headers=headers,
                newurl="https://example.com/new",
            )
        assert exc_info.value.code == 301

    def test_raises_http_error_with_location_header(self) -> None:
        """NoRedirectHandler should preserve response headers including Location."""
        handler = NoRedirectHandler()
        headers = {"Location": "https://example.com/new"}
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            handler.redirect_request(
                req=urllib.request.Request("https://example.com/old"),
                fp=io.BytesIO(b""),
                code=302,
                msg="Found",
                headers=headers,
                newurl="https://example.com/new",
            )
        assert exc_info.value.headers.get("Location") == "https://example.com/new"

    def test_raises_http_error_with_correct_url(self) -> None:
        """NoRedirectHandler should set the redirect URL, not the Request object."""
        handler = NoRedirectHandler()
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            handler.redirect_request(
                req=urllib.request.Request("https://example.com/old"),
                fp=io.BytesIO(b""),
                code=307,
                msg="Temporary Redirect",
                headers={"Location": "https://example.com/new"},
                newurl="https://example.com/new",
            )
        assert exc_info.value.url == "https://example.com/new"


class TestUrllibHTTPClient:
    """Tests for UrllibHTTPClient."""

    def test_request_with_no_redirects_returns_redirect_status(self) -> None:
        """allow_redirects=False returns the real status and Location header."""
        from unittest.mock import MagicMock, patch

        client = UrllibHTTPClient()

        # Simulate a 301 redirect response
        mock_response = MagicMock()
        mock_response.status = 301
        mock_response.headers = {"Location": "https://example.com/new"}
        mock_response.read.return_value = b""
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        # The opener.open will raise HTTPError due to NoRedirectHandler
        http_error = urllib.error.HTTPError(
            "https://example.com/new",
            301,
            "Moved Permanently",
            {"Location": "https://example.com/new"},
            io.BytesIO(b""),
        )

        with patch.object(urllib.request, "build_opener") as mock_build:
            mock_opener = MagicMock()
            mock_opener.open.side_effect = http_error
            mock_build.return_value = mock_opener

            response = client.request(
                "GET",
                "https://example.com/old",
                allow_redirects=False,
            )

        assert response.status == 301
        assert response.headers.get("Location") == "https://example.com/new"


class TestRequestsHTTPClientMissingDependency:
    """Bug 22: RequestsHTTPClient should reference the 'requests' extra, not 'api'."""

    def test_missing_dependency_error_uses_requests_extra(self) -> None:
        """When requests is not installed, the error should say extra='requests'."""
        import builtins

        from steplib.core.exceptions import MissingDependencyError

        real_import = builtins.__import__

        def _block_requests(name: str, *args: object, **kwargs: object) -> object:
            if name == "requests":
                raise ImportError("No module named 'requests'")
            return real_import(name, *args, **kwargs)

        from steplib.modules.api.client import RequestsHTTPClient

        original_import = builtins.__import__
        builtins.__import__ = _block_requests  # type: ignore[assignment]
        try:
            with pytest.raises(MissingDependencyError) as exc_info:
                RequestsHTTPClient()
        finally:
            builtins.__import__ = original_import  # type: ignore[assignment]

        assert exc_info.value.extra == "requests"
        assert exc_info.value.package == "requests"


class TestHttpxHTTPClientProxyMountKeys:
    """Bug 23: HttpxHTTPClient proxy mount keys must include '://' suffix."""

    def test_proxy_mount_keys_include_scheme_suffix(self) -> None:
        """Mount keys for multiple proxies must use 'http://' and 'https://' format."""
        from unittest.mock import MagicMock, patch

        # Simulate httpx being available
        mock_httpx = MagicMock()
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.content = b"ok"
        mock_client.request.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_httpx.Client.return_value = mock_client
        mock_httpx.HTTPTransport = MagicMock()

        with patch.dict("sys.modules", {"httpx": mock_httpx}):
            from steplib.modules.api.client import HttpxHTTPClient

            client = HttpxHTTPClient()
            client.request(
                "GET",
                "https://example.com",
                proxies={"http": "http://proxy:8080", "https": "http://proxy:8080"},
            )

        # Verify Client was called with mounts having "://" suffix keys
        client_call_kwargs = mock_httpx.Client.call_args
        mounts = client_call_kwargs.kwargs.get("mounts", {})
        assert "http://" in mounts, f"Mount keys must include '://', got: {list(mounts.keys())}"
        assert "https://" in mounts, f"Mount keys must include '://', got: {list(mounts.keys())}"
        assert "http" not in mounts, "Bare 'http' key should not be present"
        assert "https" not in mounts, "Bare 'https' key should not be present"


class TestHttpxHTTPClientTimeout:
    """Bug 24: HttpxHTTPClient must pass timeout to httpx.Client() so None means no timeout."""

    def test_timeout_none_passed_to_client_constructor(self) -> None:
        """timeout=None should be passed to httpx.Client() so it means 'no timeout'."""
        from unittest.mock import MagicMock, patch

        mock_httpx = MagicMock()
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.content = b"ok"
        mock_client.request.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_httpx.Client.return_value = mock_client

        with patch.dict("sys.modules", {"httpx": mock_httpx}):
            from steplib.modules.api.client import HttpxHTTPClient

            client = HttpxHTTPClient()
            client.request("GET", "https://example.com", timeout=None)

        client_call_kwargs = mock_httpx.Client.call_args
        assert client_call_kwargs.kwargs.get("timeout") is None, (
            "timeout=None must be passed to httpx.Client() so it means 'no timeout', "
            "not httpx's default 5s"
        )

    def test_timeout_value_passed_to_client_constructor(self) -> None:
        """A specific timeout value should be passed to httpx.Client()."""
        from unittest.mock import MagicMock, patch

        mock_httpx = MagicMock()
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.content = b"ok"
        mock_client.request.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_httpx.Client.return_value = mock_client

        with patch.dict("sys.modules", {"httpx": mock_httpx}):
            from steplib.modules.api.client import HttpxHTTPClient

            client = HttpxHTTPClient()
            client.request("GET", "https://example.com", timeout=30.0)

        client_call_kwargs = mock_httpx.Client.call_args
        assert client_call_kwargs.kwargs.get("timeout") == 30.0, (
            "timeout=30.0 must be passed to httpx.Client() constructor"
        )

    def test_timeout_not_passed_to_request(self) -> None:
        """timeout should not be passed to client.request() since it's set at client level."""
        from unittest.mock import MagicMock, patch

        mock_httpx = MagicMock()
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.content = b"ok"
        mock_client.request.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_httpx.Client.return_value = mock_client

        with patch.dict("sys.modules", {"httpx": mock_httpx}):
            from steplib.modules.api.client import HttpxHTTPClient

            client = HttpxHTTPClient()
            client.request("GET", "https://example.com", timeout=10.0)

        request_call_kwargs = mock_client.request.call_args
        assert "timeout" not in request_call_kwargs.kwargs, (
            "timeout should not be passed to client.request() — it's set at the Client level"
        )


class TestBuildHeadersDict:
    """Tests for _build_headers_dict preserving multi-value headers."""

    def test_preserves_multiple_set_cookie(self) -> None:
        """Multiple Set-Cookie headers should be joined with newline."""
        from email.message import Message

        from steplib.modules.api.client import _build_headers_dict

        msg = Message()
        msg["Content-Type"] = "application/json"
        msg["Set-Cookie"] = "session=abc123; Path=/"
        msg["Set-Cookie"] = "csrf=xyz789; Path=/"
        result = _build_headers_dict(msg)
        assert result["Content-Type"] == "application/json"
        assert "session=abc123; Path=/" in result["Set-Cookie"]
        assert "csrf=xyz789; Path=/" in result["Set-Cookie"]
        assert "\n" in result["Set-Cookie"]

    def test_single_header_value_unchanged(self) -> None:
        """Single header values should not be modified."""
        from email.message import Message

        from steplib.modules.api.client import _build_headers_dict

        msg = Message()
        msg["Content-Type"] = "application/json"
        msg["Set-Cookie"] = "session=abc123; Path=/"
        result = _build_headers_dict(msg)
        assert result["Set-Cookie"] == "session=abc123; Path=/"
        assert "\n" not in result["Set-Cookie"]
