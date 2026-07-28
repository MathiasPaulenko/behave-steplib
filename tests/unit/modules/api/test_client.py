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
