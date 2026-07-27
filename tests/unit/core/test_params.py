"""Tests for params and exceptions."""

from __future__ import annotations

from steplib.core.exceptions import MissingDependencyError
from steplib.core.params import Param, register_type, resolve_type


def test_param_defaults() -> None:
    """Param should default type to str and choices to empty list."""
    p = Param(name="method")
    assert p.type is str
    assert p.required is False
    assert p.default is None
    assert p.choices == []


def test_param_frozen() -> None:
    """Param should be immutable."""
    p = Param(name="x", type=int, required=True)
    try:
        p.name = "y"  # type: ignore[misc]
    except AttributeError:
        pass
    else:  # pragma: no cover
        raise AssertionError("Param should be frozen")


def test_resolve_type_builtin() -> None:
    """resolve_type should resolve built-in type names."""
    assert resolve_type("int") is int
    assert resolve_type("str") is str
    assert resolve_type("float") is float
    assert resolve_type("bool") is bool


def test_resolve_type_unknown_returns_str() -> None:
    """resolve_type should fall back to str for unknown names."""
    assert resolve_type("UnknownType") is str


def test_resolve_type_type_object() -> None:
    """resolve_type should pass through type objects."""
    assert resolve_type(int) is int
    assert resolve_type(str) is str


def test_register_and_resolve_custom_type() -> None:
    """register_type should make a type resolvable by name."""
    register_type("MyType", float)
    assert resolve_type("MyType") is float


def test_missing_dependency_error_message() -> None:
    """MissingDependencyError should include install instructions."""
    err = MissingDependencyError("api", "httpx")
    assert "api" in str(err)
    assert "httpx" in str(err)
    assert "pip install" in str(err)
    assert err.extra == "api"
    assert err.package == "httpx"


def test_missing_dependency_error_without_package() -> None:
    """MissingDependencyError should work without a package name."""
    err = MissingDependencyError("kit")
    assert "kit" in str(err)
    assert err.package is None
