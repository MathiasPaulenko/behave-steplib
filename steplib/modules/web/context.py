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
        variables: User-defined variables stored by steps.
        backend: The backend name (e.g. ``"selenium"``).

    """

    driver: Any = None
    base_url: str = ""
    implicit_wait: float = 10.0
    variables: dict[str, Any] = field(default_factory=dict)
    backend: str = "selenium"

    def reset(self) -> None:
        """Reset per-scenario state, keeping the driver and configuration."""
        self.variables = {}

    def cleanup(self) -> None:
        """Close the browser driver if it exists."""
        if self.driver is not None and hasattr(self.driver, "quit"):
            self.driver.quit()
            self.driver = None
