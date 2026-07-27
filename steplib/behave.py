"""Integration helpers for behave's ``environment.py``.

``before_all`` and ``after_scenario`` can be imported directly as behave
hooks. ``before_scenario`` must be written by the user (it calls
``context.steplib.reset()``).

Usage::

    # features/environment.py
    from steplib.behave import after_scenario, before_all

    def before_scenario(context, scenario):
        context.steplib.reset()
"""

from __future__ import annotations

from typing import Any

from steplib.core.discovery import autoload as _autoload
from steplib.core.discovery import load as _load
from steplib.core.state import SteplibState

__all__ = ["SteplibState", "after_scenario", "autoload", "before_all", "load"]


def autoload(
    context: Any,
    categories: list[str] | None = None,
    backends: dict[str, str] | None = None,
) -> SteplibState:
    """Load all installed steplib plugins and attach state to *context*.

    See :func:`steplib.core.discovery.autoload` for details.

    Args:
        context: The behave context object.
        categories: Optional list of categories to keep (e.g. ``["api"]``).
        backends: Optional mapping of category to backend
            (e.g. ``{"api": "httpx"}``).

    Returns:
        A ``SteplibState`` holding the filtered registry.

    """
    return _autoload(context, categories=categories, backends=backends)


def load(context: Any, *modules: str) -> SteplibState:
    """Load specific step modules by dotted path.

    See :func:`steplib.core.discovery.load` for details.

    Args:
        context: The behave context object.
        *modules: Dotted module paths to import.

    Returns:
        A ``SteplibState`` holding the registry.

    """
    return _load(context, *modules)


def before_all(context: Any) -> SteplibState:
    """Run autoload and attach steplib state to *context*.

    Args:
        context: The behave context object.

    Returns:
        The ``SteplibState`` attached to ``context.steplib``.

    """
    state = autoload(context)
    context.steplib = state
    return state


def after_scenario(context: Any, scenario: Any) -> None:
    """Clean up steplib resources after a scenario.

    Args:
        context: The behave context object.
        scenario: The behave scenario object (unused but required by the hook).

    """
    state = getattr(context, "steplib", None)
    if state is not None and hasattr(state, "cleanup"):
        state.cleanup()
