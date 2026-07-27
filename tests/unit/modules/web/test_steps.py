"""Tests for Web steps (using mock driver)."""

from __future__ import annotations

from types import SimpleNamespace

from steplib.core.state import SteplibState
from steplib.modules.web.context import WebContext
from steplib.modules.web.steps import (
    step_element_present,
    step_navigate,
    step_page_contains,
    step_page_title,
    step_set_web_base_url,
    step_url_contains,
)


class MockDriver:
    """Mock browser driver for testing."""

    def __init__(self) -> None:
        self._url = "https://example.com/page"
        self._title = "Test Page"
        self._source = "<html><body>Hello World</body></html>"
        self.visited: list[str] = []

    def get(self, url: str) -> None:
        self.visited.append(url)
        self._url = url

    def find_element(self, by: str, value: str) -> object:
        return object()

    def find_elements(self, by: str, value: str) -> list[object]:
        return [object()]

    @property
    def current_url(self) -> str:
        return self._url

    @property
    def title(self) -> str:
        return self._title

    @property
    def page_source(self) -> str:
        return self._source

    def quit(self) -> None:
        pass


def _make_context() -> SimpleNamespace:
    """Create a behave-like context with steplib state and WebContext."""
    context = SimpleNamespace()
    state = SteplibState(context, registry=None)  # type: ignore[arg-type]
    state.web = WebContext(driver=MockDriver())  # type: ignore[attr-defined]
    context.steplib = state
    return context


def test_step_set_web_base_url() -> None:
    """step_set_web_base_url should set the base URL."""
    context = _make_context()
    step_set_web_base_url(context, '"https://example.com"')
    assert context.steplib.web.base_url == "https://example.com"  # type: ignore[attr-defined]


def test_step_navigate() -> None:
    """step_navigate should navigate to a URL."""
    context = _make_context()
    step_navigate(context, '"https://other.com"')
    assert context.steplib.web.driver.visited == ["https://other.com"]  # type: ignore[attr-defined]


def test_step_navigate_relative() -> None:
    """step_navigate should resolve relative URLs against the base URL."""
    context = _make_context()
    step_set_web_base_url(context, '"https://example.com"')
    step_navigate(context, '"/login"')
    assert context.steplib.web.driver.visited == ["https://example.com/login"]  # type: ignore[attr-defined]


def test_step_page_title() -> None:
    """step_page_title should assert the page title."""
    context = _make_context()
    step_page_title(context, '"Test Page"')


def test_step_url_contains() -> None:
    """step_url_contains should assert the URL contains a fragment."""
    context = _make_context()
    step_url_contains(context, '"example.com"')


def test_step_element_present() -> None:
    """step_element_present should assert an element is present."""
    context = _make_context()
    step_element_present(context, "id", '"login-button"')


def test_step_page_contains() -> None:
    """step_page_contains should assert the page contains text."""
    context = _make_context()
    step_page_contains(context, '"Hello"')
