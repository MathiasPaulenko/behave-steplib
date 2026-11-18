"""Regression tests for API module bugs found in the audit."""

from __future__ import annotations

import urllib.request
from typing import Any

import pytest

from steplib.modules.api.actions import (
    api_assert_json_schema,
    api_send,
    api_send_json,
)
from steplib.modules.api.client import Response, UrllibHTTPClient
from steplib.modules.api.context import ApiContext
from steplib.modules.api.transforms import Url


class _FakeResponse:
    def __init__(self) -> None:
        self.status = 200
        self.headers: dict[str, str] = {}
        self._body = b"{}"

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *args: Any) -> None:
        return None


class TestUrllibSslVerify:
    """verify=False must reach the urllib opener via an HTTPSHandler."""

    def test_verify_false_installs_https_handler(self, monkeypatch):
        captured: dict[str, Any] = {}

        def fake_build_opener(*handlers: Any) -> Any:
            captured["handlers"] = handlers

            class _Opener:
                def open(self, req: Any, timeout: Any = None) -> _FakeResponse:
                    return _FakeResponse()

            return _Opener()

        monkeypatch.setattr(urllib.request, "build_opener", fake_build_opener)
        client = UrllibHTTPClient()
        client.request("GET", "https://example.test", verify=False)

        https_handlers = [
            h for h in captured["handlers"]
            if isinstance(h, urllib.request.HTTPSHandler)
        ]
        assert https_handlers, "verify=False must add an HTTPSHandler"
        context = https_handlers[0]._context
        assert context.check_hostname is False
        assert context.verify_mode == __import__("ssl").CERT_NONE

    def test_verify_true_adds_no_custom_handler(self, monkeypatch):
        captured: dict[str, Any] = {}

        def fake_build_opener(*handlers: Any) -> Any:
            captured["handlers"] = handlers

            class _Opener:
                def open(self, req: Any, timeout: Any = None) -> _FakeResponse:
                    return _FakeResponse()

            return _Opener()

        monkeypatch.setattr(urllib.request, "build_opener", fake_build_opener)
        UrllibHTTPClient().request("GET", "https://example.test", verify=True)
        assert not any(
            isinstance(h, urllib.request.HTTPSHandler)
            for h in captured["handlers"]
        )


class TestApiSendState:
    """A failed request must not leave a stale last_response."""

    def test_failed_request_clears_last_response(self):
        class Boom:
            def request(self, **kwargs: Any) -> Response:
                raise ConnectionError("down")

        api_ctx = ApiContext(client=Boom())
        api_ctx.last_response = Response(status=200, body=b"{}")

        with pytest.raises(ConnectionError):
            api_send(api_ctx, "GET", "http://example.test")

        assert api_ctx.last_response is None


class _CapturingClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> Response:
        self.calls.append({"method": method, "url": url, **kwargs})
        return Response(status=200, body=b"{}")


class TestApiSendJson:
    """api_send_json must serialize lists as JSON, not Python repr."""

    def test_list_body_is_json_serialized(self):
        client = _CapturingClient()
        api_ctx = ApiContext(client=client)
        api_send_json(api_ctx, "POST", "http://example.test", [1, 2])  # type: ignore[arg-type]
        assert client.calls[0]["body"] == b"[1, 2]"


class TestUrlResolution:
    """Absolute URLs are detected case-insensitively."""

    def test_uppercase_scheme_is_absolute(self):
        assert Url("HTTP://EXAMPLE.TEST/x", "https://base.test").value == "HTTP://EXAMPLE.TEST/x"

    def test_mixed_case_scheme_is_absolute(self):
        assert Url("Https://EXAMPLE.TEST", "https://base.test").value == "Https://EXAMPLE.TEST"

    def test_relative_url_still_resolves(self):
        assert Url("/path", "https://base.test").value == "https://base.test/path"


class TestJsonSchemaValidation:
    """The subset validator must handle valid JSON Schema type lists."""

    def _ctx_with(self, body: bytes) -> ApiContext:
        api_ctx = ApiContext(client=_CapturingClient())
        api_ctx.last_response = Response(status=200, body=body)
        return api_ctx

    def test_type_as_list_is_supported(self):
        api_ctx = self._ctx_with(b'{"a": null}')
        api_assert_json_schema(
            api_ctx,
            {"type": "object", "properties": {"a": {"type": ["string", "null"]}}},
        )

    def test_type_as_list_reports_mismatch(self):
        api_ctx = self._ctx_with(b'{"a": 5}')
        with pytest.raises(AssertionError, match="expected type"):
            api_assert_json_schema(
                api_ctx,
                {"type": "object", "properties": {"a": {"type": ["string", "null"]}}},
            )

    def test_unknown_type_is_an_error_not_a_silent_pass(self):
        api_ctx = self._ctx_with(b'{"a": 5}')
        with pytest.raises(AssertionError, match="unknown"):
            api_assert_json_schema(
                api_ctx,
                {"type": "object", "properties": {"a": {"type": "stringg"}}},
            )


class TestSchemaStepTypeValidation:
    """The schema step must reject a non-object JSON schema."""

    def test_non_object_schema_raises_assertion_error(self):
        from types import SimpleNamespace

        from steplib.modules.api.steps import step_response_matches_schema

        context = SimpleNamespace(
            steplib=SimpleNamespace(api=ApiContext(client=_CapturingClient())),
            text='["not", "an", "object"]',
        )

        with pytest.raises(AssertionError, match="schema must be an object"):
            step_response_matches_schema(context)
