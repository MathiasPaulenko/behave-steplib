"""Custom behave step matcher for behave-steplib.

The default ``parse`` matcher accepts any text that can be made to fit a
pattern by letting placeholders absorb arbitrary substrings. This causes
``AmbiguousStep`` errors when two step patterns share the same fixed words,
even if one is clearly more specific (for example,
``the response header {name} is {value}`` and
``the response header {name} is not {value}``).

``SteplibMatcher`` keeps the ``parse`` syntax but adds a skeleton check: a
pattern only matches a step text when both contain the same fixed words in the
same order. This lets more-specific patterns coexist with their shorter
general forms.
"""

from __future__ import annotations

import re
from typing import Any, cast

import parse
from behave.matchers import Match, Matcher
from behave.model_type import Argument

_FIXED_RE = re.compile(r'"[^"]*"|\{[^}]+?\}')


def _skeleton(text: str) -> tuple[str, ...]:
    """Return the fixed (non-placeholder, non-quoted) words of *text*."""
    cleaned = _FIXED_RE.sub(" ", text)
    words = [word for word in re.split(r"\W+", cleaned.lower()) if word]
    return tuple(words)


class SteplibMatcher(Matcher):  # type: ignore[misc]
    """Parse-based matcher that resolves prefix/negative-form ambiguities."""

    NAME = "steplib"
    TYPE_REGISTRY = Matcher.TYPE_REGISTRY

    def __init__(
        self,
        func: Any,
        pattern: str,
        step_type: str | None = None,
        custom_types: Any | None = None,
    ) -> None:
        """Create a matcher for a parsed step pattern."""
        super().__init__(func, pattern, step_type)
        self._skeleton = _skeleton(pattern)
        self._parser = parse.Parser(pattern, extra_types=custom_types or {})

    @property
    def regex_pattern(self) -> str:
        """Expose the internal regex built by ``parse``."""
        return cast(str, self._parser._expression)

    def compile(self) -> SteplibMatcher:
        """Pre-compile the parse expression to detect bad patterns early."""
        _ = self._parser.parse("")
        return self

    def check_match(self, step_text: str) -> list[Argument] | None:
        """Match *step_text* using the parse expression and return arguments."""
        parsed = self._parser.parse(step_text)
        if not parsed:
            return None

        arguments: list[Argument] = []
        for name, value in parsed.named.items():
            start, end = parsed.spans[name]
            original = step_text[start:end]
            arguments.append(Argument(start, end, original, value, name))
        for index, value in enumerate(parsed.fixed):
            start, end = parsed.spans[index]
            original = step_text[start:end]
            arguments.append(Argument(start, end, original, value))
        return arguments

    def matches(self, step_text: str) -> bool:
        """Return ``True`` when *step_text* does not add fixed words.

        This check is used while behave loads step definitions. It prevents
        ``AmbiguousStep`` errors between a short pattern and a more specific
        one that shares the same fixed words. Runtime matching uses
        :meth:`check_match` instead.
        """
        if not set(_skeleton(step_text)).issubset(self._skeleton):
            return False
        matched = self.match(step_text)
        return matched is not None and isinstance(matched, Match)
