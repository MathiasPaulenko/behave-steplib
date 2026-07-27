"""Browser client abstraction: protocol and lazy Selenium driver."""

from __future__ import annotations

from typing import Any, Protocol

from steplib.core.exceptions import MissingDependencyError


class BrowserDriver(Protocol):
    """Protocol for browser driver implementations."""

    def get(self, url: str) -> None:
        """Navigate the browser to *url*.

        Args:
            url: The URL to navigate to.

        """
        ...

    def find_element(self, by: str, value: str) -> Any:
        """Find a single element on the page.

        Args:
            by: The locator strategy (e.g. ``"id"``, ``"xpath"``).
            value: The locator value.

        Returns:
            The matched element.

        """
        ...

    def find_elements(self, by: str, value: str) -> list[Any]:
        """Find multiple elements on the page.

        Args:
            by: The locator strategy (e.g. ``"id"``, ``"xpath"``).
            value: The locator value.

        Returns:
            A list of matched elements.

        """
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


class SeleniumDriver:
    """Browser driver backed by Selenium (requires the ``[web]`` extra)."""

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
            from selenium import webdriver  # noqa: PLC0415
            from selenium.webdriver.common.by import By  # noqa: PLC0415
        except ImportError as exc:
            raise MissingDependencyError("web", "selenium") from exc

        self._By = By

        if browser.lower() == "chrome":
            opts = webdriver.ChromeOptions()
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
