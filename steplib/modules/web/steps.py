"""Web step definitions for behave."""

from __future__ import annotations

from typing import Any

from steplib.core.decorators import step
from steplib.core.registry import StepRegistry
from steplib.modules.web.actions import (
    web_assert_cookie_exists,
    web_assert_element_attribute,
    web_assert_element_enabled,
    web_assert_element_not_present,
    web_assert_element_present,
    web_assert_element_text_equals,
    web_assert_element_visible,
    web_assert_page_contains,
    web_assert_page_not_contains,
    web_assert_title,
    web_assert_url_contains,
    web_clear_input,
    web_click,
    web_delete_cookie,
    web_navigate,
    web_navigate_back,
    web_navigate_forward,
    web_refresh_page,
    web_select_option,
    web_set_base_url,
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


# --- Interactions ---


@step(
    "I click the element {by} {value}",
    category="web",
    description="Click an element on the page.",
    example='When I click the element id "submit-button"',
    i18n={
        "es": "hago clic en el elemento {by} {value}",
        "pt": "clico no elemento {by} {value}",
    },
)
def step_click_element(context: Any, by: str, value: str) -> None:
    """Click an element."""
    web_click(_get_web(context), by, value.strip('"'))


@step(
    "I type {text} into the element {by} {value}",
    category="web",
    description="Type text into an input element, clearing it first.",
    example='When I type "Ada Lovelace" into the element id "name"',
    i18n={
        "es": "escribo {text} en el elemento {by} {value}",
        "pt": "digito {text} no elemento {by} {value}",
    },
)
def step_type_text(context: Any, text: str, by: str, value: str) -> None:
    """Type text into an input."""
    web_type_text(_get_web(context), by, value.strip('"'), text.strip('"'))


@step(
    "I clear the element {by} {value}",
    category="web",
    description="Clear an input element.",
    example='When I clear the element id "name"',
    i18n={
        "es": "limpio el elemento {by} {value}",
        "pt": "limpo o elemento {by} {value}",
    },
)
def step_clear_input(context: Any, by: str, value: str) -> None:
    """Clear an input element."""
    web_clear_input(_get_web(context), by, value.strip('"'))


@step(
    "I select {option} from the element {by} {value}",
    category="web",
    description="Select an option from a dropdown by visible text.",
    example='When I select "Argentina" from the element id "country"',
    i18n={
        "es": "selecciono {option} del elemento {by} {value}",
        "pt": "seleciono {option} do elemento {by} {value}",
    },
)
def step_select_option(context: Any, option: str, by: str, value: str) -> None:
    """Select an option from a dropdown."""
    web_select_option(_get_web(context), by, value.strip('"'), option.strip('"'))


# --- Waits ---


@step(
    "I wait for the element {by} {value} to be present",
    category="web",
    description="Wait until an element is present on the page.",
    example='Then I wait for the element id "loading" to be present',
    i18n={
        "es": "espero a que el elemento {by} {value} esté presente",
        "pt": "espero que o elemento {by} {value} esteja presente",
    },
)
def step_wait_for_element(context: Any, by: str, value: str) -> None:
    """Wait for element to be present."""
    web_wait_for_element(_get_web(context), by, value.strip('"'))


@step(
    "I wait for the element {by} {value} to be visible",
    category="web",
    description="Wait until an element is visible on the page.",
    example='Then I wait for the element id "modal" to be visible',
    i18n={
        "es": "espero a que el elemento {by} {value} sea visible",
        "pt": "espero que o elemento {by} {value} seja visível",
    },
)
def step_wait_for_element_visible(context: Any, by: str, value: str) -> None:
    """Wait for element to be visible."""
    web_wait_for_element_visible(_get_web(context), by, value.strip('"'))


@step(
    "I wait for the page to contain {text}",
    category="web",
    description="Wait until the page contains specific text.",
    example='Then I wait for the page to contain "Welcome"',
    i18n={
        "es": "espero a que la página contenga {text}",
        "pt": "espero que a página contenha {text}",
    },
)
def step_wait_for_text(context: Any, text: str) -> None:
    """Wait for text to appear on page."""
    web_wait_for_text(_get_web(context), text.strip('"'))


# --- Extended assertions ---


@step(
    "the element {by} {value} is not present",
    category="web",
    description="Assert an element is NOT present on the page.",
    example='Then the element id "error" is not present',
    i18n={
        "es": "el elemento {by} {value} no está presente",
        "pt": "o elemento {by} {value} não está presente",
    },
)
def step_element_not_present(context: Any, by: str, value: str) -> None:
    """Assert element is not present."""
    web_assert_element_not_present(_get_web(context), by, value.strip('"'))


@step(
    "the element {by} {value} is visible",
    category="web",
    description="Assert an element is visible on the page.",
    example='Then the element id "modal" is visible',
    i18n={
        "es": "el elemento {by} {value} es visible",
        "pt": "o elemento {by} {value} é visível",
    },
)
def step_element_visible(context: Any, by: str, value: str) -> None:
    """Assert element is visible."""
    web_assert_element_visible(_get_web(context), by, value.strip('"'))


@step(
    "the element {by} {value} is enabled",
    category="web",
    description="Assert an element is enabled.",
    example='Then the element id "submit" is enabled',
    i18n={
        "es": "el elemento {by} {value} está habilitado",
        "pt": "o elemento {by} {value} está habilitado",
    },
)
def step_element_enabled(context: Any, by: str, value: str) -> None:
    """Assert element is enabled."""
    web_assert_element_enabled(_get_web(context), by, value.strip('"'))


@step(
    "the element {by} {value} text equals {expected}",
    category="web",
    description="Assert an element's text content equals a value.",
    example='Then the element id "greeting" text equals "Hello"',
    i18n={
        "es": "el texto del elemento {by} {value} es igual a {expected}",
        "pt": "o texto do elemento {by} {value} é igual a {expected}",
    },
)
def step_element_text_equals(context: Any, by: str, value: str, expected: str) -> None:
    """Assert element text equals."""
    web_assert_element_text_equals(
        _get_web(context),
        by,
        value.strip('"'),
        expected.strip('"'),
    )


@step(
    "the element {by} {value} attribute {attr} equals {expected}",
    category="web",
    description="Assert an element's attribute equals a value.",
    example='Then the element id "link" attribute "href" equals "https://example.com"',
    i18n={
        "es": "el atributo {attr} del elemento {by} {value} es igual a {expected}",
        "pt": "o atributo {attr} do elemento {by} {value} é igual a {expected}",
    },
)
def step_element_attribute_equals(
    context: Any,
    by: str,
    value: str,
    attr: str,
    expected: str,
) -> None:
    """Assert element attribute equals."""
    web_assert_element_attribute(
        _get_web(context),
        by,
        value.strip('"'),
        attr.strip('"'),
        expected.strip('"'),
    )


@step(
    "the page does not contain {text}",
    category="web",
    description="Assert the page source does NOT contain text.",
    example='Then the page does not contain "Error"',
    i18n={
        "es": "la página no contiene {text}",
        "pt": "a página não contém {text}",
    },
)
def step_page_not_contains(context: Any, text: str) -> None:
    """Assert page does not contain text."""
    web_assert_page_not_contains(_get_web(context), text.strip('"'))


# --- Store / Extract ---


@step(
    "I store the text of element {by} {value} as {variable}",
    category="web",
    description="Store an element's text content as a variable.",
    example='Then I store the text of element id "username" as "user_name"',
    i18n={
        "es": "guardo el texto del elemento {by} {value} como {variable}",
        "pt": "armazeno o texto do elemento {by} {value} como {variable}",
    },
)
def step_store_element_text(context: Any, by: str, value: str, variable: str) -> None:
    """Store element text as variable."""
    web_store_element_text(_get_web(context), by, value.strip('"'), variable.strip('"'))


@step(
    "I store the attribute {attr} of element {by} {value} as {variable}",
    category="web",
    description="Store an element's attribute value as a variable.",
    example='Then I store the attribute "href" of element id "link" as "link_url"',
    i18n={
        "es": "guardo el atributo {attr} del elemento {by} {value} como {variable}",
        "pt": "armazeno o atributo {attr} do elemento {by} {value} como {variable}",
    },
)
def step_store_element_attribute(
    context: Any,
    attr: str,
    by: str,
    value: str,
    variable: str,
) -> None:
    """Store element attribute as variable."""
    web_store_element_attribute(
        _get_web(context),
        by,
        value.strip('"'),
        attr.strip('"'),
        variable.strip('"'),
    )


@step(
    "I store the current URL as {variable}",
    category="web",
    description="Store the current browser URL as a variable.",
    example='Then I store the current URL as "current_url"',
    i18n={
        "es": "guardo la URL actual como {variable}",
        "pt": "armazeno a URL atual como {variable}",
    },
)
def step_store_current_url(context: Any, variable: str) -> None:
    """Store current URL as variable."""
    web_store_current_url(_get_web(context), variable.strip('"'))


# --- Navigation ---


@step(
    "I refresh the page",
    category="web",
    description="Refresh the current page.",
    example="When I refresh the page",
    i18n={
        "es": "refresco la página",
        "pt": "atualizo a página",
    },
)
def step_refresh_page(context: Any) -> None:
    """Refresh the page."""
    web_refresh_page(_get_web(context))


@step(
    "I go back",
    category="web",
    description="Navigate back in browser history.",
    example="When I go back",
    i18n={
        "es": "vuelvo atrás",
        "pt": "volto atrás",
    },
)
def step_navigate_back(context: Any) -> None:
    """Navigate back."""
    web_navigate_back(_get_web(context))


@step(
    "I go forward",
    category="web",
    description="Navigate forward in browser history.",
    example="When I go forward",
    i18n={
        "es": "voy hacia adelante",
        "pt": "vou para frente",
    },
)
def step_navigate_forward(context: Any) -> None:
    """Navigate forward."""
    web_navigate_forward(_get_web(context))


@step(
    "I switch to the frame {by} {value}",
    category="web",
    description="Switch to an iframe element.",
    example='When I switch to the frame id "myframe"',
    i18n={
        "es": "cambio al frame {by} {value}",
        "pt": "mudo para o frame {by} {value}",
    },
)
def step_switch_to_frame(context: Any, by: str, value: str) -> None:
    """Switch to frame."""
    web_switch_to_frame(_get_web(context), by, value.strip('"'))


@step(
    "I switch to the default content",
    category="web",
    description="Switch back to the default content from a frame.",
    example="When I switch to the default content",
    i18n={
        "es": "cambio al contenido por defecto",
        "pt": "mudo para o conteúdo padrão",
    },
)
def step_switch_to_default(context: Any) -> None:
    """Switch to default content."""
    web_switch_to_default(_get_web(context))


# --- Cookies ---


@step(
    "I store the cookie {name} as {variable}",
    category="web",
    description="Store a cookie value as a variable.",
    example='Then I store the cookie "session" as "session_token"',
    i18n={
        "es": "guardo la cookie {name} como {variable}",
        "pt": "armazeno o cookie {name} como {variable}",
    },
)
def step_store_cookie(context: Any, name: str, variable: str) -> None:
    """Store cookie as variable."""
    web_store_cookie(_get_web(context), name.strip('"'), variable.strip('"'))


@step(
    "the cookie {name} exists",
    category="web",
    description="Assert a cookie exists.",
    example='Then the cookie "session" exists',
    i18n={
        "es": "la cookie {name} existe",
        "pt": "o cookie {name} existe",
    },
)
def step_cookie_exists(context: Any, name: str) -> None:
    """Assert cookie exists."""
    web_assert_cookie_exists(_get_web(context), name.strip('"'))


@step(
    "I delete the cookie {name}",
    category="web",
    description="Delete a cookie by name.",
    example='When I delete the cookie "session"',
    i18n={
        "es": "elimino la cookie {name}",
        "pt": "excluo o cookie {name}",
    },
)
def step_delete_cookie(context: Any, name: str) -> None:
    """Delete a cookie."""
    web_delete_cookie(_get_web(context), name.strip('"'))


# --- Config ---


@step(
    "the implicit wait is {seconds:f} seconds",
    category="web",
    description="Set the implicit wait time for element lookups.",
    example="Given the implicit wait is 5.0 seconds",
    i18n={
        "es": "la espera implícita es de {seconds:f} segundos",
        "pt": "a espera implícita é de {seconds:f} segundos",
    },
)
def step_set_implicit_wait(context: Any, seconds: float) -> None:
    """Set implicit wait."""
    web_set_implicit_wait(_get_web(context), seconds)


@step(
    "the page load timeout is {seconds:f} seconds",
    category="web",
    description="Set the page load timeout.",
    example="Given the page load timeout is 60.0 seconds",
    i18n={
        "es": "el tiempo de espera de carga de página es {seconds:f} segundos",
        "pt": "o tempo de espera de carregamento de página é {seconds:f} segundos",
    },
)
def step_set_page_load_timeout(context: Any, seconds: float) -> None:
    """Set page load timeout."""
    web_set_page_load_timeout(_get_web(context), seconds)


@step(
    "the window size is {width:d} x {height:d}",
    category="web",
    description="Set the browser window size.",
    example="Given the window size is 1920 x 1080",
    i18n={
        "es": "el tamaño de la ventana es {width:d} x {height:d}",
        "pt": "o tamanho da janela é {width:d} x {height:d}",
    },
)
def step_set_window_size(context: Any, width: int, height: int) -> None:
    """Set window size."""
    web_set_window_size(_get_web(context), width, height)


@step(
    "I take a screenshot {filename}",
    category="web",
    description="Take a screenshot and save it to a file.",
    example='When I take a screenshot "error.png"',
    i18n={
        "es": "tomo una captura de pantalla {filename}",
        "pt": "tiro uma captura de tela {filename}",
    },
)
def step_take_screenshot(context: Any, filename: str) -> None:
    """Take a screenshot."""
    web_take_screenshot(_get_web(context), filename.strip('"'))


_ALL_STEPS = [
    step_set_web_base_url,
    step_navigate,
    step_page_title,
    step_url_contains,
    step_element_present,
    step_page_contains,
    # Interactions
    step_click_element,
    step_type_text,
    step_clear_input,
    step_select_option,
    # Waits
    step_wait_for_element,
    step_wait_for_element_visible,
    step_wait_for_text,
    # Extended assertions
    step_element_not_present,
    step_element_visible,
    step_element_enabled,
    step_element_text_equals,
    step_element_attribute_equals,
    step_page_not_contains,
    # Store / Extract
    step_store_element_text,
    step_store_element_attribute,
    step_store_current_url,
    # Navigation
    step_refresh_page,
    step_navigate_back,
    step_navigate_forward,
    step_switch_to_frame,
    step_switch_to_default,
    # Cookies
    step_store_cookie,
    step_cookie_exists,
    step_delete_cookie,
    # Config
    step_set_implicit_wait,
    step_set_page_load_timeout,
    step_set_window_size,
    step_take_screenshot,
]


def register(registry: StepRegistry) -> None:
    """Register all web steps into the given registry."""
    for step_fn in _ALL_STEPS:
        registry.add(step_fn)
