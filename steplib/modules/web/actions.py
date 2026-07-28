"""Pure action functions for the Web module."""

from __future__ import annotations

import time
from typing import Any

from steplib.modules.web.context import WebContext


def web_set_base_url(web_ctx: WebContext, url: str) -> None:
    """Set the base URL for subsequent navigations.

    Args:
        web_ctx: The web context to operate on.
        url: The base URL.

    """
    web_ctx.base_url = url


def web_navigate(web_ctx: WebContext, url: str) -> None:
    """Navigate to *url*, resolving relative URLs against the base URL.

    Args:
        web_ctx: The web context to operate on.
        url: The URL (absolute or relative).

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    if url.startswith(("http://", "https://")):
        web_ctx.driver.get(url)
    elif web_ctx.base_url:
        base = web_ctx.base_url.rstrip("/")
        path = url if url.startswith("/") else f"/{url}"
        web_ctx.driver.get(f"{base}{path}")
    else:
        web_ctx.driver.get(url)


def web_assert_title(web_ctx: WebContext, expected: str) -> None:
    """Assert the page title equals *expected*.

    Args:
        web_ctx: The web context to operate on.
        expected: The expected page title.

    Raises:
        RuntimeError: If no browser driver is configured.
        AssertionError: If the title does not match.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    actual = web_ctx.driver.title
    if actual != expected:
        raise AssertionError(f"Expected title '{expected}', got '{actual}'.")


def web_assert_url_contains(web_ctx: WebContext, fragment: str) -> None:
    """Assert the current URL contains *fragment*.

    Args:
        web_ctx: The web context to operate on.
        fragment: The substring to search for in the current URL.

    Raises:
        RuntimeError: If no browser driver is configured.
        AssertionError: If the URL does not contain *fragment*.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    current = web_ctx.driver.current_url
    if fragment not in current:
        raise AssertionError(f"URL '{current}' does not contain '{fragment}'.")


def web_assert_element_present(web_ctx: WebContext, by: str, value: str) -> None:
    """Assert an element is present on the page.

    Args:
        web_ctx: The web context to operate on.
        by: The Selenium ``By`` strategy name (e.g. ``"id"``, ``"xpath"``).
        value: The locator value.

    Raises:
        RuntimeError: If no browser driver is configured.
        AssertionError: If no element matches the locator.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    elements = web_ctx.driver.find_elements(by, value)
    if not elements:
        raise AssertionError(f"Element '{by}={value}' not found on page.")


def web_assert_page_contains(web_ctx: WebContext, text: str) -> None:
    """Assert the page source contains *text*.

    Args:
        web_ctx: The web context to operate on.
        text: The substring to search for in the page source.

    Raises:
        RuntimeError: If no browser driver is configured.
        AssertionError: If the page does not contain *text*.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    if text not in web_ctx.driver.page_source:
        raise AssertionError(f"Page does not contain text '{text}'.")


def web_store(web_ctx: WebContext, variable: str, value: Any) -> None:
    """Store a *value* under *variable* name in the Web context.

    Args:
        web_ctx: The web context to operate on.
        variable: The variable name.
        value: The value to store.

    """
    web_ctx.variables[variable] = value


# --- Interactions ---


def web_click(web_ctx: WebContext, by: str, value: str) -> None:
    """Click an element on the page.

    Args:
        web_ctx: The web context to operate on.
        by: The Selenium ``By`` strategy name (e.g. ``"id"``, ``"xpath"``).
        value: The locator value.

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    web_ctx.driver.click(by, value)


def web_type_text(web_ctx: WebContext, by: str, value: str, text: str) -> None:
    """Type text into an input element, clearing it first.

    Args:
        web_ctx: The web context to operate on.
        by: The Selenium ``By`` strategy name.
        value: The locator value.
        text: The text to type.

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    web_ctx.driver.type_text(by, value, text)


def web_clear_input(web_ctx: WebContext, by: str, value: str) -> None:
    """Clear an input element.

    Args:
        web_ctx: The web context to operate on.
        by: The Selenium ``By`` strategy name.
        value: The locator value.

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    web_ctx.driver.clear_input(by, value)


def web_select_option(web_ctx: WebContext, by: str, value: str, option: str) -> None:
    """Select an option from a <select> element by visible text.

    Args:
        web_ctx: The web context to operate on.
        by: The Selenium ``By`` strategy name.
        value: The locator value.
        option: The visible text of the option to select.

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    web_ctx.driver.select_option(by, value, option)


# --- Waits ---


def web_wait_for_element(
    web_ctx: WebContext,
    by: str,
    value: str,
    timeout: float | None = None,
) -> None:
    """Wait until an element is present on the page.

    Args:
        web_ctx: The web context to operate on.
        by: The Selenium ``By`` strategy name.
        value: The locator value.
        timeout: Maximum wait in seconds. Defaults to ``implicit_wait``.

    Raises:
        RuntimeError: If no browser driver is configured.
        AssertionError: If the element is not found within the timeout.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    wait = timeout if timeout is not None else web_ctx.implicit_wait
    elapsed = 0.0

    while elapsed < wait:
        elements = web_ctx.driver.find_elements(by, value)
        if elements:
            return
        time.sleep(0.1)
        elapsed += 0.1
    raise AssertionError(f"Element '{by}={value}' not found within {wait}s.")


def web_wait_for_element_visible(
    web_ctx: WebContext,
    by: str,
    value: str,
    timeout: float | None = None,
) -> None:
    """Wait until an element is visible on the page.

    Args:
        web_ctx: The web context to operate on.
        by: The Selenium ``By`` strategy name.
        value: The locator value.
        timeout: Maximum wait in seconds. Defaults to ``implicit_wait``.

    Raises:
        RuntimeError: If no browser driver is configured.
        AssertionError: If the element is not visible within the timeout.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    wait = timeout if timeout is not None else web_ctx.implicit_wait
    elapsed = 0.0

    while elapsed < wait:
        if web_ctx.driver.is_element_visible(by, value):
            return
        time.sleep(0.1)
        elapsed += 0.1
    raise AssertionError(f"Element '{by}={value}' not visible within {wait}s.")


def web_wait_for_text(web_ctx: WebContext, text: str, timeout: float | None = None) -> None:
    """Wait until the page source contains *text*.

    Args:
        web_ctx: The web context to operate on.
        text: The text to wait for.
        timeout: Maximum wait in seconds. Defaults to ``implicit_wait``.

    Raises:
        RuntimeError: If no browser driver is configured.
        AssertionError: If the text does not appear within the timeout.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    wait = timeout if timeout is not None else web_ctx.implicit_wait
    elapsed = 0.0

    while elapsed < wait:
        if text in web_ctx.driver.page_source:
            return
        time.sleep(0.1)
        elapsed += 0.1
    raise AssertionError(f"Text '{text}' not found in page within {wait}s.")


# --- Extended assertions ---


def web_assert_element_not_present(web_ctx: WebContext, by: str, value: str) -> None:
    """Assert an element is NOT present on the page.

    Args:
        web_ctx: The web context to operate on.
        by: The Selenium ``By`` strategy name.
        value: The locator value.

    Raises:
        RuntimeError: If no browser driver is configured.
        AssertionError: If the element IS present.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    elements = web_ctx.driver.find_elements(by, value)
    if elements:
        raise AssertionError(f"Element '{by}={value}' should not be present.")


def web_assert_element_visible(web_ctx: WebContext, by: str, value: str) -> None:
    """Assert an element is visible on the page.

    Args:
        web_ctx: The web context to operate on.
        by: The Selenium ``By`` strategy name.
        value: The locator value.

    Raises:
        RuntimeError: If no browser driver is configured.
        AssertionError: If the element is not visible.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    if not web_ctx.driver.is_element_visible(by, value):
        raise AssertionError(f"Element '{by}={value}' is not visible.")


def web_assert_element_enabled(web_ctx: WebContext, by: str, value: str) -> None:
    """Assert an element is enabled.

    Args:
        web_ctx: The web context to operate on.
        by: The Selenium ``By`` strategy name.
        value: The locator value.

    Raises:
        RuntimeError: If no browser driver is configured.
        AssertionError: If the element is not enabled.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    if not web_ctx.driver.is_element_enabled(by, value):
        raise AssertionError(f"Element '{by}={value}' is not enabled.")


def web_assert_element_text_equals(web_ctx: WebContext, by: str, value: str, expected: str) -> None:
    """Assert an element's text content equals *expected*.

    Args:
        web_ctx: The web context to operate on.
        by: The Selenium ``By`` strategy name.
        value: The locator value.
        expected: The expected text content.

    Raises:
        RuntimeError: If no browser driver is configured.
        AssertionError: If the text does not match.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    actual = web_ctx.driver.get_element_text(by, value)
    if actual != expected:
        raise AssertionError(f"Element text: expected '{expected}', got '{actual}'.")


def web_assert_element_attribute(
    web_ctx: WebContext,
    by: str,
    value: str,
    attr: str,
    expected: str,
) -> None:
    """Assert an element's attribute equals *expected*.

    Args:
        web_ctx: The web context to operate on.
        by: The Selenium ``By`` strategy name.
        value: The locator value.
        attr: The attribute name.
        expected: The expected attribute value.

    Raises:
        RuntimeError: If no browser driver is configured.
        AssertionError: If the attribute does not match.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    actual = web_ctx.driver.get_element_attribute(by, value, attr)
    if actual != expected:
        raise AssertionError(f"Element attribute '{attr}': expected '{expected}', got '{actual}'.")


def web_assert_page_not_contains(web_ctx: WebContext, text: str) -> None:
    """Assert the page source does NOT contain *text*.

    Args:
        web_ctx: The web context to operate on.
        text: The substring that should not be present.

    Raises:
        RuntimeError: If no browser driver is configured.
        AssertionError: If the page contains *text*.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    if text in web_ctx.driver.page_source:
        raise AssertionError(f"Page should not contain text '{text}'.")


# --- Store / Extract ---


def web_store_element_text(web_ctx: WebContext, by: str, value: str, variable: str) -> None:
    """Store an element's text content as a variable.

    Args:
        web_ctx: The web context to operate on.
        by: The Selenium ``By`` strategy name.
        value: The locator value.
        variable: The variable name to store under.

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    web_ctx.variables[variable] = web_ctx.driver.get_element_text(by, value)


def web_store_element_attribute(
    web_ctx: WebContext,
    by: str,
    value: str,
    attr: str,
    variable: str,
) -> None:
    """Store an element's attribute value as a variable.

    Args:
        web_ctx: The web context to operate on.
        by: The Selenium ``By`` strategy name.
        value: The locator value.
        attr: The attribute name.
        variable: The variable name to store under.

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    web_ctx.variables[variable] = web_ctx.driver.get_element_attribute(by, value, attr)


def web_store_current_url(web_ctx: WebContext, variable: str) -> None:
    """Store the current URL as a variable.

    Args:
        web_ctx: The web context to operate on.
        variable: The variable name to store under.

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    web_ctx.variables[variable] = web_ctx.driver.current_url


# --- Navigation ---


def web_refresh_page(web_ctx: WebContext) -> None:
    """Refresh the current page.

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    web_ctx.driver.refresh()


def web_navigate_back(web_ctx: WebContext) -> None:
    """Navigate back in browser history.

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    web_ctx.driver.back()


def web_navigate_forward(web_ctx: WebContext) -> None:
    """Navigate forward in browser history.

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    web_ctx.driver.forward()


def web_switch_to_frame(web_ctx: WebContext, by: str, value: str) -> None:
    """Switch to an iframe element.

    Args:
        web_ctx: The web context to operate on.
        by: The Selenium ``By`` strategy name.
        value: The locator value.

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    web_ctx.driver.switch_to_frame(by, value)


def web_switch_to_default(web_ctx: WebContext) -> None:
    """Switch back to the default content from a frame.

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    web_ctx.driver.switch_to_default()


# --- Cookies ---


def web_store_cookie(web_ctx: WebContext, name: str, variable: str) -> None:
    """Store a cookie value as a variable.

    Args:
        web_ctx: The web context to operate on.
        name: The cookie name.
        variable: The variable name to store under.

    Raises:
        RuntimeError: If no browser driver is configured.
        AssertionError: If the cookie does not exist.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    cookie = web_ctx.driver.get_cookie(name)
    if cookie is None:
        raise AssertionError(f"Cookie '{name}' not found.")
    web_ctx.variables[variable] = cookie.get("value", "")


def web_assert_cookie_exists(web_ctx: WebContext, name: str) -> None:
    """Assert a cookie exists.

    Args:
        web_ctx: The web context to operate on.
        name: The cookie name.

    Raises:
        RuntimeError: If no browser driver is configured.
        AssertionError: If the cookie does not exist.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    if web_ctx.driver.get_cookie(name) is None:
        raise AssertionError(f"Cookie '{name}' not found.")


def web_delete_cookie(web_ctx: WebContext, name: str) -> None:
    """Delete a cookie by name.

    Args:
        web_ctx: The web context to operate on.
        name: The cookie name.

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    web_ctx.driver.delete_cookie(name)


# --- Config ---


def web_set_implicit_wait(web_ctx: WebContext, seconds: float) -> None:
    """Set the implicit wait time.

    Args:
        web_ctx: The web context to operate on.
        seconds: The implicit wait in seconds.

    """
    web_ctx.implicit_wait = seconds


def web_set_page_load_timeout(web_ctx: WebContext, seconds: float) -> None:
    """Set the page load timeout.

    Args:
        web_ctx: The web context to operate on.
        seconds: The page load timeout in seconds.

    """
    web_ctx.page_load_timeout = seconds


def web_set_window_size(web_ctx: WebContext, width: int, height: int) -> None:
    """Set the browser window size.

    Args:
        web_ctx: The web context to operate on.
        width: The window width in pixels.
        height: The window height in pixels.

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    web_ctx.driver.set_window_size(width, height)
    web_ctx.window_size = (width, height)


def web_take_screenshot(web_ctx: WebContext, filename: str) -> None:
    """Take a screenshot and save it.

    Args:
        web_ctx: The web context to operate on.
        filename: The filename (or full path) for the screenshot.

    Raises:
        RuntimeError: If no browser driver is configured.

    """
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    import os

    if web_ctx.screenshots_dir and not os.path.isabs(filename):
        path = os.path.join(web_ctx.screenshots_dir, filename)
    else:
        path = filename
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    web_ctx.driver.take_screenshot(path)
    web_ctx.last_screenshot = path
