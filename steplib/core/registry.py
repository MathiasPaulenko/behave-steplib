"""Central registry for step metadata and behave integration."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, Protocol

from steplib.core.decorators import get_step_infos
from steplib.core.exceptions import DuplicateStepError, StepContractError
from steplib.core.i18n import expand_patterns
from steplib.core.matcher import SteplibMatcher
from steplib.core.metadata import StepInfo

# User-facing decorator name used in error messages.
_STEP_DECORATOR_NAME = "step"


class BehaveLikeRegistry(Protocol):
    """Minimal protocol for behave's step registration API."""

    def step(
        self,
        pattern: str,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a step pattern with behave.

        Args:
            pattern: The behave matching pattern.

        Returns:
            A decorator that attaches the function to the pattern.

        """
        ...


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
        self._registered_with_behave = False

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
        """Return steps matching the given filters (all optional, AND-combined).

        Args:
            category: Filter by category (e.g. ``"api"``).
            backend: Filter by backend (e.g. ``"httpx"``).
            tag: Filter by tag.

        Returns:
            A list of ``StepInfo`` entries matching all provided filters.

        """
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

    def search(
        self,
        pattern: str | None = None,
        category: str | None = None,
        backend: str | None = None,
        tag: str | None = None,
    ) -> list[StepInfo]:
        """Return steps matching partial text and/or filters (all optional, AND-combined).

        Unlike :meth:`filter`, the *pattern* argument performs a case-insensitive
        substring match against the step pattern text.

        Args:
            pattern: Partial text to search for (case-insensitive substring).
            category: Filter by category (e.g. ``"api"``).
            backend: Filter by backend (e.g. ``"httpx"``).
            tag: Filter by tag.

        Returns:
            A list of ``StepInfo`` entries matching all provided criteria.

        """
        result: list[StepInfo] = []
        for info in self._steps:
            if pattern is not None and pattern.lower() not in info.pattern.lower():
                continue
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

        Args:
            pattern: The step pattern to look up.
            backend: Optional backend to narrow the search.

        Returns:
            The matching ``StepInfo`` or ``None`` if not found.

        """
        if backend is not None:
            return self._patterns.get((pattern, backend))
        # Search across all backends for the given pattern.
        for (pat, _be), info in self._patterns.items():
            if pat == pattern:
                return info
        return None

    def find(self, pattern: str, backend: str | None = None) -> StepInfo | None:
        """Alias for :meth:`get`.

        Args:
            pattern: The step pattern to look up.
            backend: Optional backend to narrow the search.

        Returns:
            The matching ``StepInfo`` or ``None`` if not found.

        """
        return self.get(pattern, backend)

    def available_backends(self, category: str | None = None) -> set[str]:
        """Return the set of backends present in the registry.

        Args:
            category: Optional category to narrow the search.

        Returns:
            A set of backend names.

        """
        backends: set[str] = set()
        for info in self._steps:
            if info.backend is None:
                continue
            if category is not None and info.category != category:
                continue
            backends.add(info.backend)
        return backends

    def available_categories(self) -> set[str]:
        """Return the set of categories present in the registry.

        Returns:
            A set of category names.

        """
        return {info.category for info in self._steps}

    @property
    def steps(self) -> list[StepInfo]:
        """All registered ``StepInfo`` entries (unfiltered)."""
        return list(self._steps)

    def replace_steps(self, kept: list[StepInfo]) -> None:
        """Replace the registry's contents with *kept* steps only.

        Used by discovery filters to narrow the registry after loading.
        Rebuilds the internal pattern index from the kept steps.

        Args:
            kept: The ``StepInfo`` entries to keep.

        """
        self._steps = list(kept)
        self._patterns = {}
        for info in kept:
            for _lang, pattern in expand_patterns(info):
                self._patterns[(pattern, info.backend)] = info
        self._registered_with_behave = False

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
        self._steps.append(info)

    def register_with_behave(self) -> None:
        """Register the base pattern of every stored step with behave.

        Only the English base pattern is registered. Translations are kept in
        the registry metadata for CLI/validation use but are not exposed to
        behave's matcher, because mixed-language patterns often share prefixes
        and cause ``AmbiguousStep`` errors.
        """
        if self._registered_with_behave:
            return
        seen: set[tuple[str, str | None]] = set()
        for info in self._steps:
            key = (info.pattern, info.backend)
            if key in seen:
                continue
            seen.add(key)
            self._register_with_behave(info.pattern, info.func)
        self._registered_with_behave = True

    @staticmethod
    def _register_with_behave(pattern: str, fn: Callable[..., Any]) -> None:
        """Register a single pattern with behave's global step registry.

        Uses ``SteplibMatcher`` to avoid ``AmbiguousStep`` errors between
        positive and negative forms that share the same fixed words.
        """
        try:
            from behave import step as behave_step
            from behave.matchers import (
                has_registered_step_matcher_class,
                register_step_matcher_class,
                use_step_matcher,
            )
        except ImportError:  # pragma: no cover
            return

        if not has_registered_step_matcher_class(SteplibMatcher.NAME):
            register_step_matcher_class(SteplibMatcher.NAME, SteplibMatcher)
        use_step_matcher(SteplibMatcher.NAME)
        behave_step(pattern)(fn)
