"""Browser client abstraction: protocol and lazy Selenium driver."""

from __future__ import annotations

from typing import Any, Protocol

from steplib.core.exceptions import MissingDependencyError


class BrowserDriver(Protocol):
    """Protocol for browser driver implementations."""

    def get(self, url: str) -> None:
        """Navigate the browser to *url*."""
        ...

    def find_element(self, by: str, value: str) -> Any:
        """Find a single element on the page."""
        ...

    def find_elements(self, by: str, value: str) -> list[Any]:
        """Find multiple elements on the page."""
        ...

    @property
    def current_url(self) -> str:
        """The current browser URL."""
        ...

    @property
    def title(self) -> str:
        """The current page title."""
        ...

    @property
    def page_source(self) -> str:
        """The current page source HTML."""
        ...

    def quit(self) -> None:
        """Close the browser and release resources."""
        ...

    def click(self, by: str, value: str) -> None:
        """Click an element matching the locator."""
        ...

    def type_text(self, by: str, value: str, text: str) -> None:
        """Type text into an input element."""
        ...

    def clear_input(self, by: str, value: str) -> None:
        """Clear an input element."""
        ...

    def select_option(self, by: str, value: str, option: str) -> None:
        """Select an option from a <select> element by visible text."""
        ...

    def is_element_visible(self, by: str, value: str) -> bool:
        """Check if an element is visible on the page."""
        ...

    def is_element_enabled(self, by: str, value: str) -> bool:
        """Check if an element is enabled."""
        ...

    def get_element_text(self, by: str, value: str) -> str:
        """Get the text content of an element."""
        ...

    def get_element_attribute(self, by: str, value: str, attr: str) -> str:
        """Get an attribute value from an element."""
        ...

    def take_screenshot(self, path: str) -> None:
        """Take a screenshot and save to *path*."""
        ...

    def refresh(self) -> None:
        """Refresh the current page."""
        ...

    def back(self) -> None:
        """Navigate back in browser history."""
        ...

    def forward(self) -> None:
        """Navigate forward in browser history."""
        ...

    def switch_to_frame(self, by: str, value: str) -> None:
        """Switch to an iframe element."""
        ...

    def switch_to_default(self) -> None:
        """Switch back to the default content."""
        ...

    def get_cookie(self, name: str) -> dict[str, Any] | None:
        """Get a cookie by name."""
        ...

    def get_cookies(self) -> list[dict[str, Any]]:
        """Get all cookies."""
        ...

    def delete_cookie(self, name: str) -> None:
        """Delete a cookie by name."""
        ...

    def set_window_size(self, width: int, height: int) -> None:
        """Set the browser window size."""
        ...


class SeleniumDriver:
    """Browser driver backed by Selenium (requires the ``[web]`` extra)."""

    _driver: Any
    _By: Any

    def __init__(self, browser: str = "chrome", headless: bool = True) -> None:
        """Initialize the Selenium driver, importing lazily.

        Args:
            browser: ``"chrome"`` or ``"firefox"``.
            headless: Whether to run the browser in headless mode.

        Raises:
            MissingDependencyError: If Selenium is not installed.
            ValueError: If the browser is not supported.

        """
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
        except ImportError as exc:
            raise MissingDependencyError("web", "selenium") from exc

        self._By = By

        if browser.lower() == "chrome":
            opts: Any = webdriver.ChromeOptions()
            if headless:
                opts.add_argument("--headless")
            self._driver = webdriver.Chrome(options=opts)
        elif browser.lower() == "firefox":
            opts = webdriver.FirefoxOptions()
            if headless:
                opts.add_argument("--headless")
            self._driver = webdriver.Firefox(options=opts)
        else:
            raise ValueError(f"Unsupported browser: {browser}")

    def get(self, url: str) -> None:
        """Navigate to *url*."""
        self._driver.get(url)

    def find_element(self, by: str, value: str) -> Any:
        """Find a single element by *by* strategy and *value*.

        Args:
            by: The Selenium ``By`` strategy name (e.g. ``"id"``, ``"xpath"``).
            value: The locator value.

        Returns:
            The matched Selenium WebElement.

        """
        return self._driver.find_element(getattr(self._By, by.upper()), value)

    def find_elements(self, by: str, value: str) -> list[Any]:
        """Find multiple elements by *by* strategy and *value*.

        Args:
            by: The Selenium ``By`` strategy name (e.g. ``"id"``, ``"xpath"``).
            value: The locator value.

        Returns:
            A list of matched Selenium WebElements.

        """
        return list(self._driver.find_elements(getattr(self._By, by.upper()), value))

    @property
    def current_url(self) -> str:
        """Return the current URL."""
        return str(self._driver.current_url)

    @property
    def title(self) -> str:
        """Return the page title."""
        return str(self._driver.title)

    @property
    def page_source(self) -> str:
        """Return the page source HTML."""
        return str(self._driver.page_source)

    def quit(self) -> None:
        """Quit the browser."""
        self._driver.quit()

    def click(self, by: str, value: str) -> None:
        """Click an element matching the locator."""
        self._driver.find_element(getattr(self._By, by.upper()), value).click()

    def type_text(self, by: str, value: str, text: str) -> None:
        """Type text into an input element, clearing it first."""
        el = self._driver.find_element(getattr(self._By, by.upper()), value)
        el.clear()
        el.send_keys(text)

    def clear_input(self, by: str, value: str) -> None:
        """Clear an input element."""
        self._driver.find_element(getattr(self._By, by.upper()), value).clear()

    def select_option(self, by: str, value: str, option: str) -> None:
        """Select an option from a <select> element by visible text."""
        from selenium.webdriver.support.ui import Select

        el = self._driver.find_element(getattr(self._By, by.upper()), value)
        Select(el).select_by_visible_text(option)

    def is_element_visible(self, by: str, value: str) -> bool:
        """Check if an element is visible on the page."""
        elements = self._driver.find_elements(getattr(self._By, by.upper()), value)
        return bool(elements) and elements[0].is_displayed()

    def is_element_enabled(self, by: str, value: str) -> bool:
        """Check if an element is enabled."""
        el = self._driver.find_element(getattr(self._By, by.upper()), value)
        return bool(el.is_enabled())

    def get_element_text(self, by: str, value: str) -> str:
        """Get the text content of an element."""
        el = self._driver.find_element(getattr(self._By, by.upper()), value)
        return str(el.text)

    def get_element_attribute(self, by: str, value: str, attr: str) -> str:
        """Get an attribute value from an element."""
        el = self._driver.find_element(getattr(self._By, by.upper()), value)
        return el.get_attribute(attr) or ""

    def take_screenshot(self, path: str) -> None:
        """Take a screenshot and save to *path*."""
        self._driver.save_screenshot(path)

    def refresh(self) -> None:
        """Refresh the current page."""
        self._driver.refresh()

    def back(self) -> None:
        """Navigate back in browser history."""
        self._driver.back()

    def forward(self) -> None:
        """Navigate forward in browser history."""
        self._driver.forward()

    def switch_to_frame(self, by: str, value: str) -> None:
        """Switch to an iframe element."""
        el = self._driver.find_element(getattr(self._By, by.upper()), value)
        self._driver.switch_to.frame(el)

    def switch_to_default(self) -> None:
        """Switch back to the default content."""
        self._driver.switch_to.default_content()

    def get_cookie(self, name: str) -> dict[str, Any] | None:
        """Get a cookie by name."""
        cookie = self._driver.get_cookie(name)
        return dict(cookie) if cookie else None

    def get_cookies(self) -> list[dict[str, Any]]:
        """Get all cookies."""
        return [dict(c) for c in self._driver.get_cookies()]

    def delete_cookie(self, name: str) -> None:
        """Delete a cookie by name."""
        self._driver.delete_cookie(name)

    def set_window_size(self, width: int, height: int) -> None:
        """Set the browser window size."""
        self._driver.set_window_size(width, height)


def get_driver(backend: str = "selenium", **kwargs: Any) -> BrowserDriver:
    """Return a browser driver for the given backend.

    Args:
        backend: ``"selenium"`` (only supported for now).
        **kwargs: Additional arguments passed to the driver constructor
            (e.g. ``browser="firefox"``, ``headless=False``).

    Returns:
        A ``BrowserDriver`` instance.

    Raises:
        MissingDependencyError: If the backend's dependency is not installed.
        ValueError: If the backend is not supported.

    """
    if backend == "selenium":
        return SeleniumDriver(**kwargs)
    raise ValueError(f"Unsupported web backend: {backend}")
