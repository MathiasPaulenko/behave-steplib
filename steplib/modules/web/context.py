"""WebContext: per-scenario browser state for the Web module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WebContext:
    """Holds all browser state for a scenario.

    Lives at ``context.steplib.web`` and is reset between scenarios.

    Attributes:
        driver: The browser driver instance (e.g. ``SeleniumDriver``).
        base_url: The base URL for resolving relative navigations.
        implicit_wait: Implicit wait time in seconds for element lookups.
        page_load_timeout: Page load timeout in seconds.
        window_size: Optional (width, height) tuple for the browser window.
        screenshots_dir: Directory path where screenshots are saved.
        last_screenshot: Path to the last screenshot taken.
        variables: User-defined variables stored by steps.
        backend: The backend name (e.g. ``"selenium"``).

    """

    driver: Any = None
    base_url: str = ""
    implicit_wait: float = 10.0
    page_load_timeout: float = 30.0
    window_size: tuple[int, int] | None = None
    screenshots_dir: str = ""
    last_screenshot: str = ""
    variables: dict[str, Any] = field(default_factory=dict)
    backend: str = "selenium"

    def reset(self) -> None:
        """Reset per-scenario state, keeping the driver and configuration."""
        self.variables = {}
        self.last_screenshot = ""

    def cleanup(self) -> None:
        """Close the browser driver if it exists."""
        if self.driver is not None and hasattr(self.driver, "quit"):
            self.driver.quit()
            self.driver = None
