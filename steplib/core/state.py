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
        backends: Optional mapping of category → selected backend, used by
            modules when lazily creating their clients (e.g. ``api``).

    """

    def __init__(
        self,
        context: Any,
        registry: StepRegistry,
        backends: dict[str, str] | None = None,
    ) -> None:
        """Initialize state with a behave context and step registry."""
        self._context = context
        self._registry = registry
        self.backends = dict(backends or {})

    @property
    def context(self) -> Any:
        """The behave context."""
        return self._context

    @property
    def registry(self) -> StepRegistry:
        """The step registry."""
        return self._registry

    def _run_module_hooks(self, hook: str) -> None:
        """Call *hook* on every module context, re-raising the first error.

        A failing context must not prevent the remaining contexts from
        running their lifecycle hook — otherwise one broken module leaks
        the others' resources.
        """
        first_error: BaseException | None = None
        for name in list(self.__dict__):
            if name.startswith("_"):
                continue
            attr = getattr(self, name)
            method = getattr(attr, hook, None)
            if callable(method):
                try:
                    method()
                except Exception as exc:
                    if first_error is None:
                        first_error = exc
        if first_error is not None:
            raise first_error

    def reset(self) -> None:
        """Reset per-scenario state.

        Called from ``before_scenario``. Iterates over all module-level
        attributes (non-underscore) and calls ``reset()`` if available.
        """
        self._run_module_hooks("reset")

    def cleanup(self) -> None:
        """Close resources after a scenario.

        Called from ``after_scenario``. Iterates over all module-level
        attributes (non-underscore) and calls ``cleanup()`` if available.
        """
        self._run_module_hooks("cleanup")
