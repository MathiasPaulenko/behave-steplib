"""Per-run and per-scenario state attached to behave's context."""

from __future__ import annotations

from typing import Any, Protocol

from steplib.core.registry import StepRegistry


class BehaveContext(Protocol):
    """Minimal protocol for behave's ``context`` object.

    Attributes:
        config: The behave configuration object.
        steplib: The ``SteplibState`` attached by steplib's autoload/load.

    """

    config: Any
    steplib: Any


class SteplibState:
    """Holds the steplib state attached to ``context.steplib``.

    Modules set their own namespaces as attributes on this object
    (e.g. ``state.api = ApiContext(...)``).

    Args:
        context: The behave context object.
        registry: The ``StepRegistry`` populated during autoload/load.

    """

    def __init__(self, context: Any, registry: StepRegistry) -> None:
        """Initialize state with a behave context and step registry."""
        self._context = context
        self._registry = registry

    @property
    def context(self) -> Any:
        """The behave context."""
        return self._context

    @property
    def registry(self) -> StepRegistry:
        """The step registry."""
        return self._registry

    def reset(self) -> None:
        """Reset per-scenario state.

        Called from ``before_scenario``. Iterates over all module-level
        attributes (non-underscore) and calls ``reset()`` if available.
        """
        for name in list(self.__dict__):
            if name.startswith("_"):
                continue
            attr = getattr(self, name)
            if hasattr(attr, "reset") and callable(attr.reset):
                attr.reset()

    def cleanup(self) -> None:
        """Close resources after a scenario.

        Called from ``after_scenario``. Iterates over all module-level
        attributes (non-underscore) and calls ``cleanup()`` if available.
        """
        for name in list(self.__dict__):
            if name.startswith("_"):
                continue
            attr = getattr(self, name)
            if hasattr(attr, "cleanup") and callable(attr.cleanup):
                attr.cleanup()
