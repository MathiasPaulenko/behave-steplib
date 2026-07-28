"""Extended tests for Web step functions (thin wrappers around actions)."""

from __future__ import annotations

import os
import tempfile
from types import SimpleNamespace

import pytest

from steplib.core.state import SteplibState
from steplib.modules.web.context import WebContext
from steplib.modules.web.steps import (
    step_clear_input,
    step_click_element,
    step_cookie_exists,
    step_delete_cookie,
    step_element_attribute_equals,
    step_element_enabled,
    step_element_not_present,
    step_element_text_equals,
    step_element_visible,
    step_navigate_back,
    step_navigate_forward,
    step_page_not_contains,
    step_refresh_page,
    step_select_option,
    step_set_implicit_wait,
    step_set_page_load_timeout,
    step_set_window_size,
    step_store_cookie,
    step_store_current_url,
    step_store_element_attribute,
    step_store_element_text,
    step_switch_to_default,
    step_switch_to_frame,
    step_take_screenshot,
    step_type_text,
    step_wait_for_element,
    step_wait_for_element_visible,
    step_wait_for_text,
)


class MockDriver:
    """Mock browser driver for extended step tests."""

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
        with open(path, "w") as f:
            f.write("mock")


def _make_context(**kwargs: object) -> SimpleNamespace:
    """Create a behave-like context with steplib state and WebContext."""
    context = SimpleNamespace()
    state = SteplibState(context, registry=None)  # type: ignore[arg-type]
    state.web = WebContext(driver=MockDriver(**kwargs))  # type: ignore[attr-defined]
    context.steplib = state
    return context


# --- Interactions ---


def test_step_click_element() -> None:
    context = _make_context()
    step_click_element(context, "id", '"btn"')
    assert context.steplib.web.driver.clicked == [("id", "btn")]  # type: ignore[attr-defined]


def test_step_type_text() -> None:
    context = _make_context()
    step_type_text(context, '"hello"', "id", '"input"')
    assert context.steplib.web.driver.typed == [("id", "input", "hello")]  # type: ignore[attr-defined]


def test_step_clear_input() -> None:
    context = _make_context()
    step_clear_input(context, "id", '"input"')
    assert context.steplib.web.driver.cleared == [("id", "input")]  # type: ignore[attr-defined]


def test_step_select_option() -> None:
    context = _make_context()
    step_select_option(context, '"Option1"', "id", '"sel"')
    assert context.steplib.web.driver.selected == [("id", "sel", "Option1")]  # type: ignore[attr-defined]


# --- Waits ---


def test_step_wait_for_element() -> None:
    context = _make_context()
    step_wait_for_element(context, "id", '"el"')


def test_step_wait_for_element_visible() -> None:
    context = _make_context()
    step_wait_for_element_visible(context, "id", '"el"')


def test_step_wait_for_text() -> None:
    context = _make_context()
    step_wait_for_text(context, '"Hello"')


# --- Extended assertions ---


def test_step_element_not_present() -> None:
    context = _make_context(elements=[])
    step_element_not_present(context, "id", '"missing"')


def test_step_element_not_present_raises() -> None:
    context = _make_context()
    with pytest.raises(AssertionError, match="should not be present"):
        step_element_not_present(context, "id", '"el"')


def test_step_element_visible() -> None:
    context = _make_context()
    step_element_visible(context, "id", '"el"')


def test_step_element_visible_raises() -> None:
    context = _make_context(visible=False)
    with pytest.raises(AssertionError, match="is not visible"):
        step_element_visible(context, "id", '"el"')


def test_step_element_enabled() -> None:
    context = _make_context()
    step_element_enabled(context, "id", '"el"')


def test_step_element_enabled_raises() -> None:
    context = _make_context(enabled=False)
    with pytest.raises(AssertionError, match="is not enabled"):
        step_element_enabled(context, "id", '"el"')


def test_step_element_text_equals() -> None:
    context = _make_context(element_text="Hello")
    step_element_text_equals(context, "id", '"el"', '"Hello"')


def test_step_element_text_equals_raises() -> None:
    context = _make_context(element_text="Hello")
    with pytest.raises(AssertionError, match="Element text"):
        step_element_text_equals(context, "id", '"el"', '"Wrong"')


def test_step_element_attribute_equals() -> None:
    context = _make_context()
    step_element_attribute_equals(context, "id", '"el"', '"href"', '"https://link.com"')


def test_step_element_attribute_equals_raises() -> None:
    context = _make_context()
    with pytest.raises(AssertionError, match="Element attribute"):
        step_element_attribute_equals(context, "id", '"el"', '"href"', '"wrong"')


def test_step_page_not_contains() -> None:
    context = _make_context()
    step_page_not_contains(context, '"Goodbye"')


def test_step_page_not_contains_raises() -> None:
    context = _make_context()
    with pytest.raises(AssertionError, match="should not contain"):
        step_page_not_contains(context, '"Hello"')


# --- Store / Extract ---


def test_step_store_element_text() -> None:
    context = _make_context(element_text="Hello")
    step_store_element_text(context, "id", '"el"', '"var"')
    assert context.steplib.web.variables["var"] == "Hello"  # type: ignore[attr-defined]


def test_step_store_element_attribute() -> None:
    context = _make_context()
    step_store_element_attribute(context, '"href"', "id", '"el"', '"var"')
    assert context.steplib.web.variables["var"] == "https://link.com"  # type: ignore[attr-defined]


def test_step_store_current_url() -> None:
    context = _make_context()
    step_store_current_url(context, '"var"')
    assert context.steplib.web.variables["var"] == "https://example.com/page"  # type: ignore[attr-defined]


# --- Navigation ---


def test_step_refresh_page() -> None:
    context = _make_context()
    step_refresh_page(context)
    assert context.steplib.web.driver.refreshed is True  # type: ignore[attr-defined]


def test_step_navigate_back() -> None:
    context = _make_context()
    step_navigate_back(context)
    assert context.steplib.web.driver.back_called is True  # type: ignore[attr-defined]


def test_step_navigate_forward() -> None:
    context = _make_context()
    step_navigate_forward(context)
    assert context.steplib.web.driver.forward_called is True  # type: ignore[attr-defined]


def test_step_switch_to_frame() -> None:
    context = _make_context()
    step_switch_to_frame(context, "id", '"frame1"')
    assert context.steplib.web.driver.frame_switched == [("id", "frame1")]  # type: ignore[attr-defined]


def test_step_switch_to_default() -> None:
    context = _make_context()
    step_switch_to_default(context)
    assert context.steplib.web.driver.default_switched is True  # type: ignore[attr-defined]


# --- Cookies ---


def test_step_store_cookie() -> None:
    context = _make_context()
    step_store_cookie(context, '"session"', '"var"')
    assert context.steplib.web.variables["var"] == "abc123"  # type: ignore[attr-defined]


def test_step_store_cookie_not_found() -> None:
    context = _make_context()
    with pytest.raises(AssertionError, match="Cookie 'missing' not found"):
        step_store_cookie(context, '"missing"', '"var"')


def test_step_cookie_exists() -> None:
    context = _make_context()
    step_cookie_exists(context, '"session"')


def test_step_cookie_exists_raises() -> None:
    context = _make_context()
    with pytest.raises(AssertionError, match="Cookie 'missing' not found"):
        step_cookie_exists(context, '"missing"')


def test_step_delete_cookie() -> None:
    context = _make_context()
    step_delete_cookie(context, '"session"')
    assert "session" in context.steplib.web.driver.deleted_cookies  # type: ignore[attr-defined]


# --- Config ---


def test_step_set_implicit_wait() -> None:
    context = _make_context()
    step_set_implicit_wait(context, 10.0)
    assert context.steplib.web.implicit_wait == 10.0  # type: ignore[attr-defined]


def test_step_set_page_load_timeout() -> None:
    context = _make_context()
    step_set_page_load_timeout(context, 60.0)
    assert context.steplib.web.page_load_timeout == 60.0  # type: ignore[attr-defined]


def test_step_set_window_size() -> None:
    context = _make_context()
    step_set_window_size(context, 1920, 1080)
    assert context.steplib.web.window_size == (1920, 1080)  # type: ignore[attr-defined]
    assert context.steplib.web.driver.window_size == (1920, 1080)  # type: ignore[attr-defined]


def test_step_take_screenshot() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        context = _make_context()
        context.steplib.web.screenshots_dir = tmpdir  # type: ignore[attr-defined]
        step_take_screenshot(context, '"shot.png"')
        expected = os.path.join(tmpdir, "shot.png")
        assert context.steplib.web.last_screenshot == expected  # type: ignore[attr-defined]
