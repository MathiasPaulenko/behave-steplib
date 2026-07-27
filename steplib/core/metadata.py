"""Step metadata dataclass."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from steplib.core.params import Param


@dataclass(frozen=True, slots=True)
class StepInfo:
    """Immutable metadata describing a single step registration.

    A function decorated with ``@step`` may produce multiple ``StepInfo``
    entries (one per stacked decorator call). Each entry is expanded into
    one or more patterns via i18n translations.
    """

    pattern: str
    category: str
    func: Callable[..., Any]
    backend: str | None = None
    description: str | None = None
    parameters: list[Param] = field(default_factory=list)
    example: str | None = None
    tags: list[str] = field(default_factory=list)
    version: str | None = None
    deprecated: bool | str = False
    i18n: dict[str, str] = field(default_factory=dict)
    requires: list[str] = field(default_factory=list)

    @property
    def module(self) -> str:
        """Dotted module path of the step function."""
        return self.func.__module__

    @property
    def qualified_name(self) -> str:
        """Fully qualified function name (``module.qualname``)."""
        return f"{self.func.__module__}.{self.func.__qualname__}"

    @property
    def is_deprecated(self) -> bool:
        """Whether this step is marked as deprecated."""
        return bool(self.deprecated)
