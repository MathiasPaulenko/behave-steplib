"""The ``@step`` decorator and related helpers.

The decorator stores ``StepInfo`` metadata on the decorated function. When
multiple decorators are stacked on the same function, each call appends a
new ``StepInfo`` entry to ``fn.__steplib_steps__``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from steplib.core.metadata import StepInfo
from steplib.core.params import Param

# Attribute name used to store step metadata on decorated functions.
_STEPLIB_ATTR = "__steplib_steps__"


def step(  # noqa: PLR0913
    pattern: str,
    *,
    category: str,
    backend: str | None = None,
    description: str | None = None,
    parameters: list[Param] | None = None,
    example: str | None = None,
    tags: list[str] | None = None,
    version: str | None = None,
    deprecated: bool | str = False,
    i18n: dict[str, str] | None = None,
    requires: list[str] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Attach ``StepInfo`` metadata to a step function.

    Can be stacked to register multiple patterns (e.g. for i18n or
    alternative backends) on the same implementation function.

    Args:
        pattern: The behave matching pattern (e.g. ``"I send a {method} request to {url}"``).
        category: Module/domain category (e.g. ``"api"``, ``"web"``).
        backend: Underlying technology (e.g. ``"httpx"``, ``"requests"``).
        description: Human-readable description; defaults to the function docstring.
        parameters: Typed parameter descriptors.
        example: Example usage in Gherkin.
        tags: Tags for grouping/filtering in the CLI.
        version: Semver of the step.
        deprecated: ``True``, a deprecation message, or ``False``.
        i18n: Translations of the pattern keyed by language code.
        requires: Context attributes the step needs (e.g. ``["steplib.api.client"]``).

    Returns:
        A decorator that records the metadata and returns the function unchanged.

    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        info = StepInfo(
            pattern=pattern,
            category=category,
            func=fn,
            backend=backend,
            description=description or fn.__doc__,
            parameters=parameters or [],
            example=example,
            tags=tags or [],
            version=version,
            deprecated=deprecated,
            i18n=i18n or {},
            requires=requires or [],
        )
        existing: list[StepInfo] = getattr(fn, _STEPLIB_ATTR, [])
        # Create a new list to avoid mutating a shared parent list.
        new_list = list(existing)
        new_list.append(info)
        setattr(fn, _STEPLIB_ATTR, new_list)
        return fn

    return decorator


def get_step_infos(fn: Callable[..., Any]) -> list[StepInfo]:
    """Return all ``StepInfo`` entries attached to a decorated function.

    Args:
        fn: A function decorated with ``@step``.

    Returns:
        A list of ``StepInfo`` objects (empty if the function is not a steplib step).

    """
    return list(getattr(fn, _STEPLIB_ATTR, []))
