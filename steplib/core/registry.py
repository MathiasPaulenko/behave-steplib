"""Central registry for step metadata and behave integration."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, Protocol

from steplib.core.decorators import get_step_infos
from steplib.core.exceptions import DuplicateStepError, StepContractError
from steplib.core.i18n import expand_patterns
from steplib.core.metadata import StepInfo

# User-facing decorator name used in error messages.
_STEP_DECORATOR_NAME = "step"


class BehaveLikeRegistry(Protocol):
    """Minimal protocol for behave's step registration API."""

    def step(  # noqa: D102
        self,
        pattern: str,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...


class StepRegistry:
    """Stores ``StepInfo`` entries and optionally registers them with behave.

    Args:
        auto_register_behave: When ``True``, each pattern is also registered
            with behave's global step registry via ``behave.step``.

    """

    def __init__(self, auto_register_behave: bool = True) -> None:
        """Initialize an empty registry."""
        self._steps: list[StepInfo] = []
        self._patterns: dict[tuple[str, str | None], StepInfo] = {}
        self._auto_register = auto_register_behave

    # --- public API ---

    def add(self, fn: Callable[..., Any]) -> None:
        """Register all step metadata attached to *fn*.

        Extracts ``StepInfo`` entries from ``fn.__steplib_steps__``, expands
        i18n translations, checks for duplicates, and optionally registers
        each pattern with behave.

        Args:
            fn: A function decorated with ``@step``.

        Raises:
            StepContractError: If *fn* has no steplib step metadata.
            DuplicateStepError: If a pattern is already registered for the
                same backend.

        """
        infos = get_step_infos(fn)
        if not infos:
            raise StepContractError(
                f"Function '{fn.__qualname__}' is not a steplib step "
                f"(no @{_STEP_DECORATOR_NAME} metadata found)."
            )
        for info in infos:
            self._add_info(info, fn)

    def filter(
        self,
        category: str | None = None,
        backend: str | None = None,
        tag: str | None = None,
    ) -> list[StepInfo]:
        """Return steps matching the given filters (all optional, AND-combined)."""
        result: list[StepInfo] = []
        for info in self._steps:
            if category is not None and info.category != category:
                continue
            if backend is not None and info.backend != backend:
                continue
            if tag is not None and tag not in info.tags:
                continue
            result.append(info)
        return result

    def get(self, pattern: str, backend: str | None = None) -> StepInfo | None:
        """Return the ``StepInfo`` for *pattern* (optionally filtered by backend).

        When *backend* is ``None``, returns the first match regardless of backend.
        """
        if backend is not None:
            return self._patterns.get((pattern, backend))
        # Search across all backends for the given pattern.
        for (pat, _be), info in self._patterns.items():
            if pat == pattern:
                return info
        return None

    def find(self, pattern: str, backend: str | None = None) -> StepInfo | None:
        """Alias for :meth:`get`."""
        return self.get(pattern, backend)

    def available_backends(self, category: str | None = None) -> set[str]:
        """Return the set of backends present in the registry."""
        backends: set[str] = set()
        for info in self._steps:
            if info.backend is None:
                continue
            if category is not None and info.category != category:
                continue
            backends.add(info.backend)
        return backends

    def available_categories(self) -> set[str]:
        """Return the set of categories present in the registry."""
        return {info.category for info in self._steps}

    @property
    def steps(self) -> list[StepInfo]:
        """All registered ``StepInfo`` entries (unfiltered)."""
        return list(self._steps)

    def replace_steps(self, kept: list[StepInfo]) -> None:
        """Replace the registry's contents with *kept* steps only.

        Used by discovery filters to narrow the registry after loading.
        Rebuilds the internal pattern index from the kept steps.
        """
        self._steps = list(kept)
        self._patterns = {}
        for info in kept:
            for _lang, pattern in expand_patterns(info):
                self._patterns[(pattern, info.backend)] = info

    def __len__(self) -> int:
        """Return the number of registered steps."""
        return len(self._steps)

    def __iter__(self) -> Iterator[StepInfo]:
        """Iterate over registered ``StepInfo`` entries."""
        return iter(self._steps)

    # --- internals ---

    def _add_info(self, info: StepInfo, fn: Callable[..., Any]) -> None:
        for _lang, pattern in expand_patterns(info):
            key = (pattern, info.backend)
            if key in self._patterns:
                raise DuplicateStepError(pattern, info.backend)
            self._patterns[key] = info
            if self._auto_register:
                self._register_with_behave(pattern, fn)
        self._steps.append(info)

    @staticmethod
    def _register_with_behave(pattern: str, fn: Callable[..., Any]) -> None:
        """Register a single pattern with behave's global step registry."""
        try:
            from behave import step as behave_step  # noqa: PLC0415
        except ImportError:  # pragma: no cover
            return
        behave_step(pattern)(fn)
