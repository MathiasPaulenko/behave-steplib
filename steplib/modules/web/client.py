"""Browser client abstraction: protocol and lazy Selenium driver."""

from __future__ import annotations

from typing import Any, Protocol

from steplib.core.exceptions import MissingDependencyError


class BrowserDriver(Protocol):
    """Protocol for browser driver implementations."""

    def get(self, url: str) -> None: ...  # noqa: D102

    def find_element(self, by: str, value: str) -> Any: ...  # noqa: D102

    def find_elements(self, by: str, value: str) -> list[Any]: ...  # noqa: D102

    @property
    def current_url(self) -> str: ...  # noqa: D102

    @property
    def title(self) -> str: ...  # noqa: D102

    @property
    def page_source(self) -> str: ...  # noqa: D102

    def quit(self) -> None: ...  # noqa: D102


class SeleniumDriver:
    """Browser driver backed by Selenium (requires the ``[web]`` extra)."""

    def __init__(self, browser: str = "chrome", headless: bool = True) -> None:
        """Initialize the Selenium driver, importing lazily."""
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
        """Find a single element by *by* strategy and *value*."""
        return self._driver.find_element(getattr(self._By, by.upper()), value)

    def find_elements(self, by: str, value: str) -> list[Any]:
        """Find multiple elements by *by* strategy and *value*."""
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
        **kwargs: Additional arguments passed to the driver constructor.

    Raises:
        MissingDependencyError: If the backend's dependency is not installed.

    """
    if backend == "selenium":
        return SeleniumDriver(**kwargs)
    raise ValueError(f"Unsupported web backend: {backend}")
