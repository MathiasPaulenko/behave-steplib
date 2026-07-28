"""Tests for new Web actions (pure functions)."""

from __future__ import annotations

import os
import tempfile

import pytest

from steplib.modules.web.actions import (
    web_assert_cookie_exists,
    web_assert_element_attribute,
    web_assert_element_enabled,
    web_assert_element_not_present,
    web_assert_element_text_equals,
    web_assert_element_visible,
    web_assert_page_not_contains,
    web_clear_input,
    web_click,
    web_delete_cookie,
    web_navigate_back,
    web_navigate_forward,
    web_refresh_page,
    web_select_option,
    web_set_implicit_wait,
    web_set_page_load_timeout,
    web_set_window_size,
    web_store_cookie,
    web_store_current_url,
    web_store_element_attribute,
    web_store_element_text,
    web_switch_to_default,
    web_switch_to_frame,
    web_take_screenshot,
    web_type_text,
    web_wait_for_element,
    web_wait_for_element_visible,
    web_wait_for_text,
)
from steplib.modules.web.context import WebContext


class MockDriver:
    """Mock browser driver for testing new web actions."""

    def __init__(
        self,
        title: str = "Test Page",
        url: str = "https://example.com/page",
        source: str = "<html><body>Hello World</body></html>",
        elements: list[object] | None = None,
        visible: bool = True,
        enabled: bool = True,
        element_text: str = "Hello",
        element_attrs: dict[str, str] | None = None,
        cookies: dict[str, dict[str, str]] | None = None,
    ) -> None:
        self._title = title
        self._url = url
        self._source = source
        self._elements = elements if elements is not None else [object()]
        self._visible = visible
        self._enabled = enabled
        self._element_text = element_text
        self._element_attrs = element_attrs or {"href": "https://link.com"}
        self._cookies = cookies or {"session": {"value": "abc123"}}
        self.clicked: list[tuple[str, str]] = []
        self.typed: list[tuple[str, str, str]] = []
        self.cleared: list[tuple[str, str]] = []
        self.selected: list[tuple[str, str, str]] = []
        self.refreshed = False
        self.back_called = False
        self.forward_called = False
        self.frame_switched: list[tuple[str, str]] = []
        self.default_switched = False
        self.deleted_cookies: list[str] = []
        self.screenshots: list[str] = []
        self.window_size: tuple[int, int] | None = None

    def get(self, url: str) -> None:
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

    # New methods
    def click(self, by: str, value: str) -> None:
        self.clicked.append((by, value))

    def type_text(self, by: str, value: str, text: str) -> None:
        self.typed.append((by, value, text))

    def clear_input(self, by: str, value: str) -> None:
        self.cleared.append((by, value))

    def select_option(self, by: str, value: str, option: str) -> None:
        self.selected.append((by, value, option))

    def is_element_visible(self, by: str, value: str) -> bool:
        return self._visible and bool(self._elements)

    def is_element_enabled(self, by: str, value: str) -> bool:
        return self._enabled

    def get_element_text(self, by: str, value: str) -> str:
        return self._element_text

    def get_element_attribute(self, by: str, value: str, attr: str) -> str:
        return self._element_attrs.get(attr, "")

    def refresh(self) -> None:
        self.refreshed = True

    def back(self) -> None:
        self.back_called = True

    def forward(self) -> None:
        self.forward_called = True

    def switch_to_frame(self, by: str, value: str) -> None:
        self.frame_switched.append((by, value))

    def switch_to_default(self) -> None:
        self.default_switched = True

    def get_cookie(self, name: str) -> dict[str, str] | None:
        return self._cookies.get(name)

    def delete_cookie(self, name: str) -> None:
        self.deleted_cookies.append(name)
        self._cookies.pop(name, None)

    def set_window_size(self, width: int, height: int) -> None:
        self.window_size = (width, height)

    def take_screenshot(self, path: str) -> None:
        self.screenshots.append(path)
        # Create the file so os.path.exists works
        with open(path, "w") as f:
            f.write("mock")


@pytest.fixture()
def web_ctx() -> WebContext:
    """Return a WebContext with a mock driver."""
    return WebContext(driver=MockDriver())


@pytest.fixture()
def no_driver_ctx() -> WebContext:
    """Return a WebContext with no driver."""
    return WebContext(driver=None)


# --- Interactions ---


class TestWebClick:
    def test_click_calls_driver(self, web_ctx: WebContext) -> None:
        web_click(web_ctx, "id", "btn")
        assert web_ctx.driver.clicked == [("id", "btn")]  # type: ignore[attr-defined]

    def test_click_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_click(no_driver_ctx, "id", "btn")


class TestWebTypeText:
    def test_type_calls_driver(self, web_ctx: WebContext) -> None:
        web_type_text(web_ctx, "id", "input", "hello")
        assert web_ctx.driver.typed == [("id", "input", "hello")]  # type: ignore[attr-defined]

    def test_type_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_type_text(no_driver_ctx, "id", "input", "hello")


class TestWebClearInput:
    def test_clear_calls_driver(self, web_ctx: WebContext) -> None:
        web_clear_input(web_ctx, "id", "input")
        assert web_ctx.driver.cleared == [("id", "input")]  # type: ignore[attr-defined]

    def test_clear_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_clear_input(no_driver_ctx, "id", "input")


class TestWebSelectOption:
    def test_select_calls_driver(self, web_ctx: WebContext) -> None:
        web_select_option(web_ctx, "id", "sel", "Option1")
        assert web_ctx.driver.selected == [("id", "sel", "Option1")]  # type: ignore[attr-defined]

    def test_select_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_select_option(no_driver_ctx, "id", "sel", "Option1")


# --- Waits ---


class TestWebWaitForElement:
    def test_wait_element_present(self, web_ctx: WebContext) -> None:
        web_wait_for_element(web_ctx, "id", "el", timeout=1.0)

    def test_wait_element_absent_raises(self) -> None:
        ctx = WebContext(driver=MockDriver(elements=[]))
        with pytest.raises(AssertionError, match="not found within"):
            web_wait_for_element(ctx, "id", "missing", timeout=0.3)

    def test_wait_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_wait_for_element(no_driver_ctx, "id", "el")


class TestWebWaitForElementVisible:
    def test_wait_visible(self, web_ctx: WebContext) -> None:
        web_wait_for_element_visible(web_ctx, "id", "el", timeout=1.0)

    def test_wait_not_visible_raises(self) -> None:
        ctx = WebContext(driver=MockDriver(visible=False))
        with pytest.raises(AssertionError, match="not visible within"):
            web_wait_for_element_visible(ctx, "id", "el", timeout=0.3)

    def test_wait_visible_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_wait_for_element_visible(no_driver_ctx, "id", "el")


class TestWebWaitForText:
    def test_wait_text_present(self, web_ctx: WebContext) -> None:
        web_wait_for_text(web_ctx, "Hello", timeout=1.0)

    def test_wait_text_absent_raises(self) -> None:
        ctx = WebContext(driver=MockDriver(source="<html></html>"))
        with pytest.raises(AssertionError, match="not found in page"):
            web_wait_for_text(ctx, "missing", timeout=0.3)

    def test_wait_text_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_wait_for_text(no_driver_ctx, "Hello")


# --- Extended assertions ---


class TestWebAssertElementNotPresent:
    def test_not_present_passes(self) -> None:
        ctx = WebContext(driver=MockDriver(elements=[]))
        web_assert_element_not_present(ctx, "id", "missing")

    def test_present_raises(self, web_ctx: WebContext) -> None:
        with pytest.raises(AssertionError, match="should not be present"):
            web_assert_element_not_present(web_ctx, "id", "el")

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_assert_element_not_present(no_driver_ctx, "id", "el")


class TestWebAssertElementVisible:
    def test_visible_passes(self, web_ctx: WebContext) -> None:
        web_assert_element_visible(web_ctx, "id", "el")

    def test_not_visible_raises(self) -> None:
        ctx = WebContext(driver=MockDriver(visible=False))
        with pytest.raises(AssertionError, match="is not visible"):
            web_assert_element_visible(ctx, "id", "el")

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_assert_element_visible(no_driver_ctx, "id", "el")


class TestWebAssertElementEnabled:
    def test_enabled_passes(self, web_ctx: WebContext) -> None:
        web_assert_element_enabled(web_ctx, "id", "el")

    def test_not_enabled_raises(self) -> None:
        ctx = WebContext(driver=MockDriver(enabled=False))
        with pytest.raises(AssertionError, match="is not enabled"):
            web_assert_element_enabled(ctx, "id", "el")

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_assert_element_enabled(no_driver_ctx, "id", "el")


class TestWebAssertElementTextEquals:
    def test_text_matches(self, web_ctx: WebContext) -> None:
        web_assert_element_text_equals(web_ctx, "id", "el", "Hello")

    def test_text_mismatch_raises(self, web_ctx: WebContext) -> None:
        with pytest.raises(AssertionError, match="Element text"):
            web_assert_element_text_equals(web_ctx, "id", "el", "Wrong")

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_assert_element_text_equals(no_driver_ctx, "id", "el", "Hello")


class TestWebAssertElementAttribute:
    def test_attribute_matches(self, web_ctx: WebContext) -> None:
        web_assert_element_attribute(web_ctx, "id", "el", "href", "https://link.com")

    def test_attribute_mismatch_raises(self, web_ctx: WebContext) -> None:
        with pytest.raises(AssertionError, match="Element attribute"):
            web_assert_element_attribute(web_ctx, "id", "el", "href", "wrong")

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_assert_element_attribute(no_driver_ctx, "id", "el", "href", "val")


class TestWebAssertPageNotContains:
    def test_not_contains_passes(self, web_ctx: WebContext) -> None:
        web_assert_page_not_contains(web_ctx, "Goodbye")

    def test_contains_raises(self, web_ctx: WebContext) -> None:
        with pytest.raises(AssertionError, match="should not contain"):
            web_assert_page_not_contains(web_ctx, "Hello")

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_assert_page_not_contains(no_driver_ctx, "Hello")


# --- Store / Extract ---


class TestWebStoreElementText:
    def test_store_text(self, web_ctx: WebContext) -> None:
        web_store_element_text(web_ctx, "id", "el", "var")
        assert web_ctx.variables["var"] == "Hello"

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_store_element_text(no_driver_ctx, "id", "el", "var")


class TestWebStoreElementAttribute:
    def test_store_attribute(self, web_ctx: WebContext) -> None:
        web_store_element_attribute(web_ctx, "id", "el", "href", "var")
        assert web_ctx.variables["var"] == "https://link.com"

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_store_element_attribute(no_driver_ctx, "id", "el", "href", "var")


class TestWebStoreCurrentUrl:
    def test_store_url(self, web_ctx: WebContext) -> None:
        web_store_current_url(web_ctx, "var")
        assert web_ctx.variables["var"] == "https://example.com/page"

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_store_current_url(no_driver_ctx, "var")


# --- Navigation ---


class TestWebRefreshPage:
    def test_refresh(self, web_ctx: WebContext) -> None:
        web_refresh_page(web_ctx)
        assert web_ctx.driver.refreshed is True  # type: ignore[attr-defined]

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_refresh_page(no_driver_ctx)


class TestWebNavigateBack:
    def test_back(self, web_ctx: WebContext) -> None:
        web_navigate_back(web_ctx)
        assert web_ctx.driver.back_called is True  # type: ignore[attr-defined]

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_navigate_back(no_driver_ctx)


class TestWebNavigateForward:
    def test_forward(self, web_ctx: WebContext) -> None:
        web_navigate_forward(web_ctx)
        assert web_ctx.driver.forward_called is True  # type: ignore[attr-defined]

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_navigate_forward(no_driver_ctx)


class TestWebSwitchToFrame:
    def test_switch_frame(self, web_ctx: WebContext) -> None:
        web_switch_to_frame(web_ctx, "id", "frame1")
        assert web_ctx.driver.frame_switched == [("id", "frame1")]  # type: ignore[attr-defined]

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_switch_to_frame(no_driver_ctx, "id", "frame1")


class TestWebSwitchToDefault:
    def test_switch_default(self, web_ctx: WebContext) -> None:
        web_switch_to_default(web_ctx)
        assert web_ctx.driver.default_switched is True  # type: ignore[attr-defined]

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_switch_to_default(no_driver_ctx)


# --- Cookies ---


class TestWebStoreCookie:
    def test_store_cookie(self, web_ctx: WebContext) -> None:
        web_store_cookie(web_ctx, "session", "var")
        assert web_ctx.variables["var"] == "abc123"

    def test_cookie_not_found_raises(self, web_ctx: WebContext) -> None:
        with pytest.raises(AssertionError, match="Cookie 'missing' not found"):
            web_store_cookie(web_ctx, "missing", "var")

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_store_cookie(no_driver_ctx, "session", "var")


class TestWebAssertCookieExists:
    def test_cookie_exists(self, web_ctx: WebContext) -> None:
        web_assert_cookie_exists(web_ctx, "session")

    def test_cookie_missing_raises(self, web_ctx: WebContext) -> None:
        with pytest.raises(AssertionError, match="Cookie 'missing' not found"):
            web_assert_cookie_exists(web_ctx, "missing")

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_assert_cookie_exists(no_driver_ctx, "session")


class TestWebDeleteCookie:
    def test_delete_cookie(self, web_ctx: WebContext) -> None:
        web_delete_cookie(web_ctx, "session")
        assert "session" in web_ctx.driver.deleted_cookies  # type: ignore[attr-defined]

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_delete_cookie(no_driver_ctx, "session")


# --- Config ---


class TestWebSetImplicitWait:
    def test_set_implicit_wait(self, web_ctx: WebContext) -> None:
        web_set_implicit_wait(web_ctx, 10.0)
        assert web_ctx.implicit_wait == 10.0


class TestWebSetPageLoadTimeout:
    def test_set_page_load_timeout(self, web_ctx: WebContext) -> None:
        web_set_page_load_timeout(web_ctx, 60.0)
        assert web_ctx.page_load_timeout == 60.0


class TestWebSetWindowSize:
    def test_set_window_size(self, web_ctx: WebContext) -> None:
        web_set_window_size(web_ctx, 1920, 1080)
        assert web_ctx.window_size == (1920, 1080)
        assert web_ctx.driver.window_size == (1920, 1080)  # type: ignore[attr-defined]

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_set_window_size(no_driver_ctx, 1920, 1080)


class TestWebTakeScreenshot:
    def test_take_screenshot_with_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = WebContext(driver=MockDriver(), screenshots_dir=tmpdir)
            web_take_screenshot(ctx, "shot.png")
            expected = os.path.join(tmpdir, "shot.png")
            assert ctx.last_screenshot == expected
            assert ctx.driver.screenshots == [expected]  # type: ignore[attr-defined]

    def test_take_screenshot_absolute_path(self, web_ctx: WebContext) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "abs.png")
            web_take_screenshot(web_ctx, path)
            assert web_ctx.last_screenshot == path

    def test_no_driver_raises(self, no_driver_ctx: WebContext) -> None:
        with pytest.raises(RuntimeError, match="No browser driver"):
            web_take_screenshot(no_driver_ctx, "shot.png")
