"""Tests for i18n helpers."""

from __future__ import annotations

from steplib.core.decorators import step
from steplib.core.i18n import (
    SUPPORTED_LANGS,
    expand_patterns,
    extract_placeholders,
    validate_i18n_consistency,
)


def test_extract_placeholders() -> None:
    """extract_placeholders should return ordered placeholder names."""
    assert extract_placeholders("I send a {method} request to {url}") == ["method", "url"]
    assert extract_placeholders("no placeholders") == []
    assert extract_placeholders("{value:Json} parsed") == ["value"]


def test_expand_patterns_without_i18n() -> None:
    """A step without i18n should expand to just the base English pattern."""

    @step("I do {thing}", category="test")
    def my_step(context, thing):  # type: ignore[no-untyped-def]
        pass

    info = my_step.__steplib_steps__[0]  # type: ignore[attr-defined]
    pairs = expand_patterns(info)
    assert pairs == [("en", "I do {thing}")]


def test_expand_patterns_with_i18n() -> None:
    """A step with i18n should expand to base + translations."""

    @step(
        "I send a {method} request to {url}",
        category="api",
        i18n={
            "es": "envío una petición {method} a {url}",
            "pt": "envio uma requisição {method} para {url}",
        },
    )
    def step_send(context, method, url):  # type: ignore[no-untyped-def]
        pass

    info = step_send.__steplib_steps__[0]  # type: ignore[attr-defined]
    pairs = expand_patterns(info)
    assert len(pairs) == 3
    langs = [lang for lang, _ in pairs]
    assert "en" in langs
    assert "es" in langs
    assert "pt" in langs


def test_validate_i18n_consistency_ok() -> None:
    """Consistent i18n should produce no errors."""

    @step(
        "I send a {method} request to {url}",
        category="api",
        i18n={"es": "envío una petición {method} a {url}"},
    )
    def step_send(context, method, url):  # type: ignore[no-untyped-def]
        pass

    info = step_send.__steplib_steps__[0]  # type: ignore[attr-defined]
    errors = validate_i18n_consistency(info)
    assert errors == []


def test_validate_i18n_consistency_mismatch() -> None:
    """Mismatched placeholders should produce errors."""

    @step(
        "I send a {method} request to {url}",
        category="api",
        i18n={"es": "envío una petición a {url}"},  # missing {method}
    )
    def step_send(context, method, url):  # type: ignore[no-untyped-def]
        pass

    info = step_send.__steplib_steps__[0]  # type: ignore[attr-defined]
    errors = validate_i18n_consistency(info)
    assert len(errors) == 1
    assert "Placeholder mismatch" in errors[0]


def test_validate_i18n_unsupported_lang() -> None:
    """Unsupported language codes should produce errors."""

    @step(
        "I do {thing}",
        category="test",
        i18n={"fr": "je fais {thing}"},
    )
    def my_step(context, thing):  # type: ignore[no-untyped-def]
        pass

    info = my_step.__steplib_steps__[0]  # type: ignore[attr-defined]
    errors = validate_i18n_consistency(info)
    assert len(errors) == 1
    assert "fr" in errors[0]


def test_supported_langs() -> None:
    """SUPPORTED_LANGS should include en, es, pt."""
    assert "en" in SUPPORTED_LANGS
    assert "es" in SUPPORTED_LANGS
    assert "pt" in SUPPORTED_LANGS
