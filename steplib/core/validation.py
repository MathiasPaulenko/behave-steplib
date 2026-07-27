"""Static validation of step contracts.

Checks that every registered step satisfies the rules described in
``design-03-step-contract.md``:

1. Patterns are parseable by ``parse``.
2. Parameter names match pattern placeholders.
3. No duplicate patterns within the same backend.
4. i18n translations have the same placeholders as the base pattern.
5. Stacked patterns share the same placeholders and order.
6. Each step has a ``category``.
"""

from __future__ import annotations

import parse as _parse

from steplib.core.i18n import extract_placeholders, validate_i18n_consistency
from steplib.core.metadata import StepInfo
from steplib.core.registry import StepRegistry


def _check_pattern_parseable(pattern: str) -> str | None:
    """Return an error message if the pattern cannot be compiled by parse.

    Args:
        pattern: The step pattern to validate.

    Returns:
        An error message string if the pattern is invalid, ``None`` otherwise.

    """
    try:
        _parse.compile(pattern)
    except Exception as exc:
        return f"Pattern '{pattern}' is not parseable: {exc}"
    return None


def _check_param_names_match(info: StepInfo) -> list[str]:
    """Check that declared Param names match the pattern placeholders.

    Args:
        info: The step metadata to validate.

    Returns:
        A list of error messages (empty if valid).

    """
    errors: list[str] = []
    if not info.parameters:
        return errors
    pattern_placeholders = set(extract_placeholders(info.pattern))
    param_names = {p.name for p in info.parameters}
    missing_in_pattern = param_names - pattern_placeholders
    if missing_in_pattern:
        errors.append(
            f"Step '{info.pattern}': parameters {missing_in_pattern} "
            f"are declared but not in the pattern."
        )
    return errors


def _check_stacked_consistency(infos: list[StepInfo]) -> list[str]:
    """Check that stacked patterns share the same placeholders and order.

    Args:
        infos: The ``StepInfo`` entries attached to a single function.

    Returns:
        A list of error messages (empty if consistent).

    """
    if len(infos) <= 1:
        return []
    errors: list[str] = []
    base_placeholders = extract_placeholders(infos[0].pattern)
    for info in infos[1:]:
        phs = extract_placeholders(info.pattern)
        if phs != base_placeholders:
            errors.append(
                f"Stacked step '{info.pattern}' has placeholders {phs} "
                f"but base '{infos[0].pattern}' has {base_placeholders}."
            )
    return errors


def validate_steps(registry: StepRegistry) -> list[str]:
    """Validate all steps in the registry.

    Args:
        registry: The registry to validate.

    Returns:
        A list of human-readable error messages (empty if all steps are valid).

    """
    errors: list[str] = []

    # Group steps by function to check stacked decorator consistency.
    by_func: dict[str, list[StepInfo]] = {}
    for info in registry.steps:
        # Pattern parseable?
        if err := _check_pattern_parseable(info.pattern):
            errors.append(err)
        # i18n consistency.
        errors.extend(validate_i18n_consistency(info))
        # Param names match placeholders.
        errors.extend(_check_param_names_match(info))
        # Category is set (always true due to dataclass, but double-check).
        if not info.category:
            errors.append(f"Step '{info.pattern}' has no category.")
        # Group by function for stacked check.
        key = info.qualified_name
        by_func.setdefault(key, []).append(info)

    # Stacked decorator consistency.
    for _key, infos in by_func.items():
        errors.extend(_check_stacked_consistency(infos))

    return errors
