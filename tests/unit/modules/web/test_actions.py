"""Tests for Web actions (pure functions)."""

from __future__ import annotations

import pytest

from steplib.modules.web.actions import (
    web_assert_element_present,
    web_assert_page_contains,
    web_assert_title,
    web_assert_url_contains,
    web_navigate,
    web_set_base_url,
    web_store,
)
from steplib.modules.web.context import WebContext


class MockDriver:
    """Mock browser driver for testing."""

    def __init__(
        self,
        title: str = "Test Page",
        url: str = "https://example.com/page",
        source: str = "<html><body>Hello World</body></html>",
        elements: list[object] | None = None,
    ) -> None:
        self._title = title
        self._url = url
        self._source = source
        self._elements = elements if elements is not None else [object()]
        self.visited: list[str] = []

    def get(self, url: str) -> None:
        self.visited.append(url)
        self._url = url

    def find_element(self, by: str, value: str) -> object:
        if not self._elements:
            raise ValueError("No elements")
        return self._elements[0]

    def find_elements(self, by: str, value: str) -> list[object]:
        return self._elements

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


@pytest.fixture()
def web_ctx() -> WebContext:
    """Return a WebContext with a mock driver."""
    ctx = WebContext(driver=MockDriver())
    return ctx


class TestWebSetBaseUrl:
    """Tests for web_set_base_url."""

    def test_set_base_url(self, web_ctx: WebContext) -> None:
        """Setting base URL should update the context."""
        web_set_base_url(web_ctx, "https://example.com")
        assert web_ctx.base_url == "https://example.com"


class TestWebNavigate:
    """Tests for web_navigate."""

    def test_navigate_absolute(self, web_ctx: WebContext) -> None:
        """Absolute URLs should be navigated to directly."""
        web_navigate(web_ctx, "https://other.com/page")
        assert web_ctx.driver.visited == ["https://other.com/page"]  # type: ignore[attr-defined]

    def test_navigate_relative_with_base(self, web_ctx: WebContext) -> None:
        """Relative URLs should be resolved against the base URL."""
        web_set_base_url(web_ctx, "https://example.com")
        web_navigate(web_ctx, "/login")
        assert web_ctx.driver.visited == ["https://example.com/login"]  # type: ignore[attr-defined]

    def test_navigate_no_driver_raises(self) -> None:
        """Navigating without a driver should raise."""
        ctx = WebContext(driver=None)
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_navigate(ctx, "https://example.com")


class TestWebAssertTitle:
    """Tests for web_assert_title."""

    def test_title_matches(self, web_ctx: WebContext) -> None:
        """Matching title should not raise."""
        web_assert_title(web_ctx, "Test Page")

    def test_title_mismatch_raises(self, web_ctx: WebContext) -> None:
        """Mismatched title should raise."""
        with pytest.raises(AssertionError, match="Expected title"):
            web_assert_title(web_ctx, "Wrong Title")


class TestWebAssertUrlContains:
    """Tests for web_assert_url_contains."""

    def test_url_contains(self, web_ctx: WebContext) -> None:
        """Containing fragment should not raise."""
        web_assert_url_contains(web_ctx, "example.com")

    def test_url_not_contains_raises(self, web_ctx: WebContext) -> None:
        """Not containing fragment should raise."""
        with pytest.raises(AssertionError, match="does not contain"):
            web_assert_url_contains(web_ctx, "nonexistent")


class TestWebAssertElementPresent:
    """Tests for web_assert_element_present."""

    def test_element_present(self, web_ctx: WebContext) -> None:
        """Present element should not raise."""
        web_assert_element_present(web_ctx, "id", "login-button")

    def test_element_absent_raises(self) -> None:
        """Absent element should raise."""
        ctx = WebContext(driver=MockDriver(elements=[]))
        with pytest.raises(AssertionError, match="not found"):
            web_assert_element_present(ctx, "id", "missing")


class TestWebAssertPageContains:
    """Tests for web_assert_page_contains."""

    def test_page_contains(self, web_ctx: WebContext) -> None:
        """Containing text should not raise."""
        web_assert_page_contains(web_ctx, "Hello")

    def test_page_not_contains_raises(self, web_ctx: WebContext) -> None:
        """Not containing text should raise."""
        with pytest.raises(AssertionError, match="does not contain"):
            web_assert_page_contains(web_ctx, "nonexistent")


class TestWebStore:
    """Tests for web_store."""

    def test_store(self, web_ctx: WebContext) -> None:
        """Storing should save in variables."""
        web_store(web_ctx, "key", "value")
        assert web_ctx.variables["key"] == "value"


class TestWebContextLifecycle:
    """Tests for WebContext.reset and cleanup."""

    def test_reset_clears_variables(self) -> None:
        """reset() should clear variables."""
        ctx = WebContext()
        ctx.variables["key"] = "value"
        ctx.reset()
        assert ctx.variables == {}

    def test_cleanup_quits_driver(self) -> None:
        """cleanup() should quit the driver."""
        driver = MockDriver()
        ctx = WebContext(driver=driver)
        ctx.cleanup()
        assert ctx.driver is None
