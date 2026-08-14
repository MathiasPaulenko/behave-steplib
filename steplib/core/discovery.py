"""Discovery and loading of steplib plugins via entry points."""

from __future__ import annotations

import importlib
from collections.abc import Callable
from importlib.metadata import entry_points
from typing import Any

from steplib.core.metadata import StepInfo
from steplib.core.registry import StepRegistry
from steplib.core.state import SteplibState

_ENTRY_POINT_GROUP = "steplib.plugins"


def _create_registry(auto_register_behave: bool = True) -> StepRegistry:
    """Create a fresh ``StepRegistry``.

    Args:
        auto_register_behave: Whether to register steps with behave automatically.

    Returns:
        A new empty ``StepRegistry`` instance.

    """
    return StepRegistry(auto_register_behave=auto_register_behave)


def _load_entry_points(registry: StepRegistry) -> None:
    """Discover and invoke ``register(registry)`` for all steplib plugins.

    Args:
        registry: The registry to pass to each plugin's ``register`` function.

    """
    for ep in entry_points(group=_ENTRY_POINT_GROUP):
        register_fn: Callable[[StepRegistry], None] = ep.load()
        register_fn(registry)


def autoload(
    context: Any,
    categories: list[str] | None = None,
    backends: dict[str, str] | None = None,
) -> SteplibState:
    """Load all installed steplib plugins and attach state to *context*.

    Args:
        context: The behave context object.
        categories: Optional list of categories to keep (e.g. ``["api"]``).
            When ``None``, all categories are loaded.
        backends: Optional mapping of category → backend to keep
            (e.g. ``{"api": "httpx"}``). When ``None``, all backends are loaded.

    Returns:
        A ``SteplibState`` holding the filtered registry.

    """
    registry = _create_registry(auto_register_behave=False)
    _load_entry_points(registry)
    _apply_filters(registry, categories, backends)
    registry.register_with_behave()
    return SteplibState(context, registry)


def load(context: Any, *modules: str) -> SteplibState:
    """Load specific step modules by dotted path and attach state to *context*.

    Args:
        context: The behave context object.
        *modules: Dotted module paths to import (e.g.
            ``"steplib.modules.api.steps"``). Each module must expose a
            ``register(registry)`` function.

    Returns:
        A ``SteplibState`` holding the registry.

    """
    registry = _create_registry(auto_register_behave=False)
    for module_name in modules:
        mod = importlib.import_module(module_name)
        register_fn = getattr(mod, "register", None)
        if register_fn is None:
            raise AttributeError(
                f"Module '{module_name}' does not expose a 'register(registry)' function."
            )
        register_fn(registry)
    registry.register_with_behave()
    return SteplibState(context, registry)


def get_registry() -> StepRegistry:
    """Build a registry from all installed plugins without behave registration.

    Used by the CLI to query step metadata outside of a behave run.
    """
    registry = _create_registry(auto_register_behave=False)
    _load_entry_points(registry)
    return registry


def _apply_filters(
    registry: StepRegistry,
    categories: list[str] | None,
    backends: dict[str, str] | None,
) -> None:
    """Remove steps that do not match the given category/backend filters.

    Filtering is destructive: non-matching entries are removed from the
    registry's internal storage so that behave only sees the requested steps.
    """
    if categories is None and backends is None:
        return

    keep: list[StepInfo] = []
    for info in registry.steps:
        if categories is not None and info.category not in categories:
            continue
        if backends is not None:
            desired = backends.get(info.category)
            if desired is not None and info.backend != desired:
                continue
        keep.append(info)

    registry.replace_steps(keep)
