"""Pure action functions for the Web module."""

from __future__ import annotations

from typing import Any

from steplib.modules.web.context import WebContext


def web_set_base_url(web_ctx: WebContext, url: str) -> None:
    """Set the base URL for subsequent navigations."""
    web_ctx.base_url = url


def web_navigate(web_ctx: WebContext, url: str) -> None:
    """Navigate to *url*, resolving relative URLs against the base URL."""
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
    """Assert the page title equals *expected*."""
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    actual = web_ctx.driver.title
    if actual != expected:
        raise AssertionError(f"Expected title '{expected}', got '{actual}'.")


def web_assert_url_contains(web_ctx: WebContext, fragment: str) -> None:
    """Assert the current URL contains *fragment*."""
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    current = web_ctx.driver.current_url
    if fragment not in current:
        raise AssertionError(f"URL '{current}' does not contain '{fragment}'.")


def web_assert_element_present(web_ctx: WebContext, by: str, value: str) -> None:
    """Assert an element is present on the page."""
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    elements = web_ctx.driver.find_elements(by, value)
    if not elements:
        raise AssertionError(f"Element '{by}={value}' not found on page.")


def web_assert_page_contains(web_ctx: WebContext, text: str) -> None:
    """Assert the page source contains *text*."""
    if web_ctx.driver is None:
        raise RuntimeError("No browser driver configured in WebContext.")
    if text not in web_ctx.driver.page_source:
        raise AssertionError(f"Page does not contain text '{text}'.")


def web_store(web_ctx: WebContext, variable: str, value: Any) -> None:
    """Store a *value* under *variable* name in the Web context."""
    web_ctx.variables[variable] = value
