"""Tests for Web client (MissingDependencyError on missing selenium)."""

from __future__ import annotations

import contextlib

import pytest

from steplib.core.exceptions import MissingDependencyError
from steplib.modules.web.client import get_driver


def test_get_driver_selenium_missing_raises() -> None:
    """get_driver('selenium') should raise MissingDependencyError if selenium is not installed."""
    with contextlib.suppress(ImportError):
        import selenium  # noqa: F401, PLC0415
        # selenium is installed; skip this test.
        return

    with pytest.raises(MissingDependencyError, match="web"):
        get_driver("selenium")


def test_get_driver_unsupported_raises() -> None:
    """get_driver with an unsupported backend should raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported web backend"):
        get_driver("unsupported")
