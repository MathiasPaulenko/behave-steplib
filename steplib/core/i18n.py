"""Internationalisation helpers for step patterns.

The design mandates that *all* patterns (base + translations) are registered
with behave. No language filtering is performed at registration time; behave
matches the pattern that corresponds to the text in the feature file.
"""

from __future__ import annotations

import re

from steplib.core.metadata import StepInfo

# Languages supported in the MVP.
SUPPORTED_LANGS: frozenset[str] = frozenset({"en", "es", "pt"})
"""Language codes supported by steplib's i18n system."""

# Regex to extract ``{placeholder}`` or ``{placeholder:Type}`` from patterns.
_PLACEHOLDER_RE = re.compile(r"\{([^}:]+)(?::[^}]*)?\}")


def extract_placeholders(pattern: str) -> list[str]:
    """Return the ordered list of placeholder names in a pattern.

    Args:
        pattern: A behave step pattern containing ``{name}`` or ``{name:Type}``
            placeholders.

    Returns:
        The placeholder names in the order they appear in the pattern.

    """
    return _PLACEHOLDER_RE.findall(pattern)


def expand_patterns(info: StepInfo) -> list[tuple[str, str]]:
    """Expand a ``StepInfo`` into ``(lang, pattern)`` pairs.

    The base pattern is tagged ``"en"``. Each entry in ``info.i18n`` adds
    a translated pattern tagged with its language code.

    Args:
        info: The step metadata to expand.

    Returns:
        A list of ``(language_code, pattern_text)`` tuples, starting with
        the base English pattern.

    """
    pairs: list[tuple[str, str]] = [("en", info.pattern)]
    for lang, translated in info.i18n.items():
        pairs.append((lang, translated))
    return pairs


def validate_i18n_consistency(info: StepInfo) -> list[str]:
    """Check that all patterns in a ``StepInfo`` share the same placeholders.

    Args:
        info: The step metadata to validate.

    Returns:
        A list of human-readable error messages (empty if valid).

    """
    errors: list[str] = []
    base_placeholders = extract_placeholders(info.pattern)

    for lang, translated in info.i18n.items():
        if lang not in SUPPORTED_LANGS:
            errors.append(
                f"Unsupported language code '{lang}' in step '{info.pattern}'. "
                f"Supported: {sorted(SUPPORTED_LANGS)}"
            )
        translated_placeholders = extract_placeholders(translated)
        if translated_placeholders != base_placeholders:
            errors.append(
                f"Placeholder mismatch for '{info.pattern}' (lang '{lang}'): "
                f"expected {base_placeholders}, got {translated_placeholders}"
            )
    return errors
