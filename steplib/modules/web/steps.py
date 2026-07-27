"""Web step definitions for behave."""

from __future__ import annotations

from typing import Any

from steplib.core.decorators import step
from steplib.core.registry import StepRegistry
from steplib.modules.web.actions import (
    web_assert_element_present,
    web_assert_page_contains,
    web_assert_title,
    web_assert_url_contains,
    web_navigate,
    web_set_base_url,
)
from steplib.modules.web.context import WebContext


def _get_web(context: Any) -> WebContext:
    """Get the WebContext from context.steplib, creating it if needed."""
    steplib = getattr(context, "steplib", None)
    if steplib is None:
        raise RuntimeError(
            "context.steplib is not initialized. "
            "Call autoload(context) or load(context, ...) in before_all."
        )
    web = getattr(steplib, "web", None)
    if web is None:
        web = WebContext()
        steplib.web = web
    return web


@step(
    "the web base url is {url}",
    category="web",
    description="Set the base URL for subsequent web navigations.",
    example='Given the web base url is "https://example.com"',
    i18n={
        "es": "la url base web es {url}",
        "pt": "a url base web é {url}",
    },
)
def step_set_web_base_url(context: Any, url: str) -> None:
    """Set the web base URL."""
    web_set_base_url(_get_web(context), url.strip('"'))


@step(
    "I navigate to {url}",
    category="web",
    description="Navigate the browser to a URL.",
    example='When I navigate to "/login"',
    i18n={
        "es": "navego a {url}",
        "pt": "navego para {url}",
    },
)
def step_navigate(context: Any, url: str) -> None:
    """Navigate to a URL."""
    web_navigate(_get_web(context), url.strip('"'))


@step(
    "the page title is {title}",
    category="web",
    description="Assert the page title equals a value.",
    example='Then the page title is "Welcome"',
    i18n={
        "es": "el título de la página es {title}",
        "pt": "o título da página é {title}",
    },
)
def step_page_title(context: Any, title: str) -> None:
    """Assert page title."""
    web_assert_title(_get_web(context), title.strip('"'))


@step(
    "the URL contains {fragment}",
    category="web",
    description="Assert the current URL contains a fragment.",
    example='Then the URL contains "/dashboard"',
    i18n={
        "es": "la URL contiene {fragment}",
        "pt": "a URL contém {fragment}",
    },
)
def step_url_contains(context: Any, fragment: str) -> None:
    """Assert URL contains fragment."""
    web_assert_url_contains(_get_web(context), fragment.strip('"'))


@step(
    "the element {by} {value} is present",
    category="web",
    description="Assert an element is present on the page.",
    example='Then the element id "login-button" is present',
    i18n={
        "es": "el elemento {by} {value} está presente",
        "pt": "o elemento {by} {value} está presente",
    },
)
def step_element_present(context: Any, by: str, value: str) -> None:
    """Assert element is present."""
    web_assert_element_present(_get_web(context), by, value.strip('"'))


@step(
    "the page contains {text}",
    category="web",
    description="Assert the page source contains text.",
    example='Then the page contains "Welcome"',
    i18n={
        "es": "la página contiene {text}",
        "pt": "a página contém {text}",
    },
)
def step_page_contains(context: Any, text: str) -> None:
    """Assert page contains text."""
    web_assert_page_contains(_get_web(context), text.strip('"'))


_ALL_STEPS = [
    step_set_web_base_url,
    step_navigate,
    step_page_title,
    step_url_contains,
    step_element_present,
    step_page_contains,
]


def register(registry: StepRegistry) -> None:
    """Register all web steps into the given registry."""
    for step_fn in _ALL_STEPS:
        registry.add(step_fn)
