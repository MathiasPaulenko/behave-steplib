"""Tests for static step contract validation."""

from __future__ import annotations

from steplib.core.decorators import step
from steplib.core.params import Param
from steplib.core.registry import StepRegistry
from steplib.core.validation import validate_steps


def _make_registry(*fns: object) -> StepRegistry:
    """Build a registry and add all decorated functions."""
    reg = StepRegistry(auto_register_behave=False)
    for fn in fns:
        reg.add(fn)  # type: ignore[arg-type]
    return reg


def test_valid_steps_no_errors() -> None:
    """validate_steps should return no errors for well-formed steps."""

    @step("I send a {method} request to {url}", category="api", backend="httpx")
    def step_send(context, method, url):  # type: ignore[no-untyped-def]
        pass

    reg = _make_registry(step_send)
    errors = validate_steps(reg)
    assert errors == []


def test_param_names_mismatch_detected() -> None:
    """validate_steps should flag parameters declared but not in pattern."""

    @step(
        "I do {thing}",
        category="test",
        parameters=[Param(name="thing"), Param(name="missing")],
    )
    def step_mismatch(context, thing):  # type: ignore[no-untyped-def]
        pass

    reg = _make_registry(step_mismatch)
    errors = validate_steps(reg)
    assert any("declared but not in the pattern" in e for e in errors)


def test_i18n_placeholder_mismatch_detected() -> None:
    """validate_steps should flag i18n translations with mismatched placeholders."""

    @step(
        "I send a {method} request to {url}",
        category="api",
        i18n={"es": "envío una petición a {url}"},
    )
    def step_i18n_bad(context, method, url):  # type: ignore[no-untyped-def]
        pass

    reg = _make_registry(step_i18n_bad)
    errors = validate_steps(reg)
    assert any("Placeholder mismatch" in e for e in errors)


def test_i18n_unsupported_language_detected() -> None:
    """validate_steps should flag unsupported language codes."""

    @step(
        "I do {thing}",
        category="test",
        i18n={"fr": "je fais {thing}"},
    )
    def step_lang_bad(context, thing):  # type: ignore[no-untyped-def]
        pass

    reg = _make_registry(step_lang_bad)
    errors = validate_steps(reg)
    assert any("Unsupported language" in e for e in errors)


def test_stacked_patterns_placeholder_mismatch_detected() -> None:
    """validate_steps should flag stacked patterns with different placeholders."""

    @step("I do {thing}", category="test")
    @step("I see {other}", category="test")
    def step_stacked(context, thing):  # type: ignore[no-untyped-def]
        pass

    reg = _make_registry(step_stacked)
    errors = validate_steps(reg)
    assert any("Stacked step" in e for e in errors)


def test_stacked_patterns_consistent_no_errors() -> None:
    """validate_steps should pass for stacked patterns with same placeholders."""

    @step("I do {thing}", category="test")
    @step("I perform {thing}", category="test")
    def step_stacked_ok(context, thing):  # type: ignore[no-untyped-def]
        pass

    reg = _make_registry(step_stacked_ok)
    errors = validate_steps(reg)
    assert errors == []


def test_empty_category_detected() -> None:
    """validate_steps should flag steps with empty category."""
    # We can't easily create a StepInfo with empty category via the decorator
    # since category is required, so we test via a direct registry manipulation.
    reg = StepRegistry(auto_register_behave=False)

    @step("I do {thing}", category="test")
    def step_ok(context, thing):  # type: ignore[no-untyped-def]
        pass

    reg.add(step_ok)
    # Manually corrupt the category to test the check
    # Since StepInfo is frozen, we need to object.__setattr__
    info = reg.steps[0]
    object.__setattr__(info, "category", "")
    errors = validate_steps(reg)
    assert any("no category" in e for e in errors)


def test_validate_empty_registry() -> None:
    """validate_steps should return no errors for an empty registry."""
    reg = StepRegistry(auto_register_behave=False)
    errors = validate_steps(reg)
    assert errors == []
