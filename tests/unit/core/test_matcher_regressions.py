"""Regression tests for SteplibMatcher behave-parity bugs."""

from __future__ import annotations

import json

import pytest
from behave.matchers import (
    MatchWithError,
    ParseMatcher,
    get_step_matcher_factory,
    has_registered_step_matcher_class,
    register_step_matcher_class,
    register_type,
    use_step_matcher,
)

from steplib.core.matcher import SteplibMatcher


@pytest.fixture()
def steplib_matcher_class():
    """Ensure SteplibMatcher is registered and the parse matcher is restored."""
    if not has_registered_step_matcher_class(SteplibMatcher.NAME):
        register_step_matcher_class(SteplibMatcher.NAME, SteplibMatcher)
    factory = get_step_matcher_factory()
    previous = factory.current_matcher.NAME
    yield
    use_step_matcher(previous)


def _match_func(context, data):
    """No-op step function."""


class TestMatchesExcludesMatchWithError:
    """matches() must mirror behave: conversion errors are not matches."""

    def test_match_with_error_is_not_a_match(self, steplib_matcher_class):
        """A step text that parses but fails conversion must not be 'matched'.

        behave calls ``existing.matches(new_pattern_text)`` while registering
        steps to detect ambiguity. Treating a MatchWithError as a match raises
        a spurious AmbiguousStep for distinct patterns.
        """
        register_type(Json=json.loads)
        try:
            matcher = SteplibMatcher(_match_func, "the body is {data:Json}", "then")
            matched = matcher.match("the body is {other:Json}")
            assert isinstance(matched, MatchWithError)
            assert matcher.matches("the body is {other:Json}") is False
        finally:
            ParseMatcher.TYPE_REGISTRY.pop("Json", None)

    def test_identical_pattern_text_is_a_match(self, steplib_matcher_class):
        """Mirroring behave: an identical pattern text counts as a match.

        This is what makes behave raise AmbiguousStep for true duplicate
        registrations instead of silently shadowing the first matcher.
        """
        matcher = SteplibMatcher(_match_func, "the status is {a:d}", "then")
        assert matcher.matches("the status is {a:d}") is True


class TestRegistrationOrdering:
    """More specific patterns must win regardless of registration order."""

    def test_general_pattern_does_not_shadow_specific(self):
        """behave's find_match returns the first matcher in registration
        order, so register_with_behave must sort patterns by specificity —
        otherwise a general pattern added first swallows step texts meant
        for the more specific one."""
        from behave.step_registry import registry as behave_registry

        from steplib.core.decorators import step
        from steplib.core.registry import StepRegistry

        def general(context, value):
            """General pattern step."""

        def specific(context, value):
            """Specific pattern step."""

        general = step("the audit status is {value}", category="test")(general)
        specific = step("the audit status is not {value}", category="test")(specific)

        saved = {k: list(v) for k, v in behave_registry.steps.items()}
        try:
            registry = StepRegistry(auto_register_behave=False)
            registry.add(general)
            registry.add(specific)
            registry.register_with_behave()

            step_like = type("S", (), {})()
            step_like.name = "the audit status is not 5"
            step_like.step_type = "when"
            match = behave_registry.find_match(step_like)
            assert match is not None
            assert match.func is specific
            assert match.func is not general
        finally:
            behave_registry.steps.clear()
            behave_registry.steps.update(saved)


class TestRegisterTypeTargeting:
    """steplib.register_type must reach the shared parse type registry."""

    def test_register_type_works_with_non_parse_matcher_active(self):
        """Types must land on ParseMatcher's registry regardless of the
        currently active behave matcher (e.g. 're' or 'cfparse')."""
        from steplib.core.params import register_type

        factory = get_step_matcher_factory()
        previous = factory.current_matcher.NAME
        if not has_registered_step_matcher_class(SteplibMatcher.NAME):
            register_step_matcher_class(SteplibMatcher.NAME, SteplibMatcher)
        try:
            use_step_matcher("re")
            register_type("AuditWord", str)
            assert ParseMatcher.has_registered_type("AuditWord")
            matcher = SteplibMatcher(_match_func, "the word is {w:AuditWord}", "then")
            assert matcher.check_match("the word is hello") is not None
        finally:
            use_step_matcher(previous)
            ParseMatcher.TYPE_REGISTRY.pop("AuditWord", None)
