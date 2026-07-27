"""Tests for ecosystem helpers (behave-kit, behave-tables, behave-data)."""

from __future__ import annotations

import contextlib

import pytest

from steplib.core.ecosystem import (
    assert_soft,
    check_behave_doctor_available,
    check_behave_model_available,
    wrap_table,
)
from steplib.core.exceptions import MissingDependencyError


def test_assert_soft_missing_dependency() -> None:
    """assert_soft should raise MissingDependencyError if behave-kit is not installed."""
    with contextlib.suppress(ImportError):
        import behave_kit  # noqa: F401, PLC0415
        # behave-kit is installed; assert_soft requires activation, so we
        # only verify the import path works (no MissingDependencyError raised).
        return

    # behave-kit is NOT installed; should raise MissingDependencyError.
    with pytest.raises(MissingDependencyError, match="kit"):
        assert_soft(True)


def test_wrap_table_missing_dependency() -> None:
    """wrap_table should raise MissingDependencyError if behave-tables is not installed."""
    with contextlib.suppress(ImportError):
        import behave_tables  # noqa: F401, PLC0415
        # behave-tables is installed; we can't easily test without a real table.
        return

    # behave-tables is NOT installed; should raise MissingDependencyError.
    with pytest.raises(MissingDependencyError, match="tables"):
        wrap_table(None)


def test_check_behave_model_available() -> None:
    """check_behave_model_available should return a bool."""
    result = check_behave_model_available()
    assert isinstance(result, bool)


def test_check_behave_doctor_available() -> None:
    """check_behave_doctor_available should return a bool."""
    result = check_behave_doctor_available()
    assert isinstance(result, bool)
