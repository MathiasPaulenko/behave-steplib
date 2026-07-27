"""Smoke test for package import."""

import steplib


def test_package_imports() -> None:
    """steplib must be importable and expose a version string."""
    assert hasattr(steplib, "__version__")
    assert isinstance(steplib.__version__, str)
