"""Tests for DB client (MissingDependencyError on missing sqlalchemy)."""

from __future__ import annotations

import contextlib

import pytest

from steplib.core.exceptions import MissingDependencyError
from steplib.modules.db.client import get_client


def test_get_client_sqlalchemy_missing_raises() -> None:
    """get_client should raise MissingDependencyError if sqlalchemy is not installed."""
    with contextlib.suppress(ImportError):
        import sqlalchemy  # noqa: F401, PLC0415
        # sqlalchemy is installed; skip this test.
        return

    with pytest.raises(MissingDependencyError, match="db"):
        get_client("sqlite:///test.db")
