"""Contract tests for the shipped step library.

These tests catch the two classes of drift that broke in practice:

* ``StepInfo.example`` texts that do not parse their own pattern (docs bug).
* Registration-order ambiguities: behave's ``find_match`` returns the first
  matcher that parses a step text, so a generic pattern registered before
  its specific variant silently steals it — including in es/pt translations.
"""

from __future__ import annotations

import importlib
import re

import parse
import pytest

from steplib.core.i18n import expand_patterns
from steplib.core.registry import StepRegistry
from steplib.core.validation import validate_steps

MODULES = ["api", "cli", "data", "db", "io", "kafka", "web"]

_GHERKIN_KEYWORD = re.compile(r"^(Given|When|Then|And|But)\s+")


def _library() -> StepRegistry:
    """Build the full step library without behave registration."""
    registry = StepRegistry(auto_register_behave=False)
    for name in MODULES:
        importlib.import_module(f"steplib.modules.{name}.steps").register(registry)
    return registry


@pytest.fixture(scope="module")
def library() -> StepRegistry:
    """Full registry, built once per test module."""
    return _library()


def _example_text(example: str) -> str:
    """Strip the Gherkin keyword from a StepInfo example."""
    return _GHERKIN_KEYWORD.sub("", example.strip())


def _sample_text(pattern: str) -> str:
    """Render a pattern into sample step text using placeholder values."""

    def repl(match: re.Match[str]) -> str:
        type_hint = match.group(2) or ""
        if type_hint.endswith(":d"):
            return "5"
        if type_hint.endswith(":f"):
            return "5.0"
        return '"x"'

    return re.sub(r"\{([^}:]+)(:[^}]*)?\}", repl, pattern)


def test_validate_steps_has_no_errors(library: StepRegistry) -> None:
    """The shipped library must pass its own `steplib validate` checks."""
    assert validate_steps(library) == []


@pytest.mark.parametrize("module", MODULES)
def test_examples_parse_their_own_pattern(module: str) -> None:
    """Every step's ``example`` must parse its own base pattern."""
    registry = StepRegistry(auto_register_behave=False)
    importlib.import_module(f"steplib.modules.{module}.steps").register(registry)
    for info in registry.steps:
        if not info.example:
            continue
        text = _example_text(info.example)
        result = parse.Parser(info.pattern).parse(text)
        assert result is not None, (
            f"[{info.category}] example does not parse its own pattern\n"
            f"  pattern: {info.pattern}\n"
            f"  example: {info.example}"
        )


def test_first_match_is_the_right_step(library: StepRegistry) -> None:
    """Sample text for every expanded pattern resolves to its own step.

    behave's find_match returns the first parser that accepts the text, so
    a generic pattern registered before a specific one steals its steps.
    This checks the full registration order across en/es/pt.
    """
    expanded: list[tuple[str, str]] = []
    for info in library.steps:
        for lang, pattern in expand_patterns(info):
            expanded.append((lang, pattern))
    parsers = [(pattern, parse.Parser(pattern)) for _lang, pattern in expanded]

    wrong: list[str] = []
    for lang, pattern in expanded:
        text = _sample_text(pattern)
        first = next(
            (p for p, parser in parsers if parser.parse(text) is not None),
            None,
        )
        if first is not None and first != pattern:
            wrong.append(f"[{lang}] {text!r} resolves to {first!r} instead of {pattern!r}")
    assert wrong == [], "Registration-order ambiguity:\n" + "\n".join(wrong)


def test_known_ambiguous_texts_resolve_to_specific_step(
    library: StepRegistry,
) -> None:
    """Regression: specific variants must win over generic patterns."""
    parsers = [(info, parse.Parser(info.pattern)) for info in library.steps]
    expected: dict[str, str] = {
        'the response header "X" is not "Y"': "step_response_header_not_equals",
        'the response header "X" is "Y"': "step_response_header_equals",
        'I set the variable "c" to the JSON "{"a": 1}"': "step_set_variable_json",
        'I read the file "f" as lines into "v"': "step_read_file_as_lines",
        'I consume messages from topic "t" using a timeout of 5000 ms': (
            "step_consume_with_timeout"
        ),
    }
    for text, func_name in expected.items():
        for info, parser in parsers:
            if parser.parse(text) is not None:
                assert info.func.__name__ == func_name, (
                    f"{text!r} resolved to {info.func.__name__}, expected {func_name}"
                )
                break
        else:  # pragma: no cover - nothing matched at all
            pytest.fail(f"No step matched {text!r}")


def test_translations_parse_their_own_example_shape(
    library: StepRegistry,
) -> None:
    """Every translated pattern must keep the same placeholders."""
    for info in library.steps:
        base_names = sorted(_placeholder_names(info.pattern))
        for lang, pattern in info.i18n.items():
            names = _placeholder_names(pattern)
            assert sorted(names) == base_names, (
                f"[{lang}] placeholder names differ for {info.pattern!r}: {names}"
            )
            assert names == _placeholder_names(info.pattern), (
                f"[{lang}] placeholder order differs for {info.pattern!r} "
                f"(behave passes arguments positionally): {names}"
            )


def _placeholder_names(pattern: str) -> list[str]:
    return [m.group(1) for m in re.finditer(r"\{([^}:]+)(?::[^}]*)?\}", pattern)]


def test_all_steps_have_example(library: StepRegistry) -> None:
    """Every registered step should document a runnable example."""
    missing = [s.pattern for s in library.steps if not s.example]
    assert missing == []
