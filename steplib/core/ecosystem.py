"""Ecosystem integration helpers for behave-kit, behave-tables and behave-data.

These functions lazily import the corresponding libraries and raise
``MissingDependencyError`` with the appropriate extra name if the library
is not installed.
"""

from __future__ import annotations

from typing import Any

from steplib.core.exceptions import MissingDependencyError, StepContractError


def assert_soft(condition: bool, message: str = "") -> None:
    """Perform a soft assertion using ``behave-kit``.

    Args:
        condition: The condition to assert.
        message: Optional message to display on failure.

    Raises:
        MissingDependencyError: If ``behave-kit`` is not installed.

    """
    try:
        from behave_kit import assert_soft as _assert_soft
    except ImportError as exc:
        raise MissingDependencyError("kit", "behave-kit") from exc
    if message:
        _assert_soft(condition, message)
    else:
        _assert_soft(condition)


def wrap_table(table: Any) -> Any:
    """Wrap a behave table using ``behave-tables`` for easy conversion.

    Args:
        table: The ``context.table`` object from behave.

    Returns:
        A wrapped table object with methods like ``as_dicts()``.

    Raises:
        MissingDependencyError: If ``behave-tables`` is not installed.

    """
    try:
        from behave_tables import wrap as _wrap
    except ImportError as exc:
        raise MissingDependencyError("tables", "behave-tables") from exc
    return _wrap(table)


def load_test_data(source: str, **kwargs: Any) -> Any:
    """Load test data from a file using ``behave-data``.

    Args:
        source: Path or URL to the data file (CSV, JSON, YAML, Excel).
        **kwargs: Additional arguments passed to ``behave-data``.

    Returns:
        The loaded data.

    Raises:
        MissingDependencyError: If ``behave-data`` is not installed.
        StepContractError: If ``behave-data`` is installed but has no ``load`` function.

    """
    try:
        import behave_data
    except ImportError as exc:
        raise MissingDependencyError("data", "behave-data") from exc
    load_fn = getattr(behave_data, "load", None)
    if load_fn is None:
        raise StepContractError("behave-data is installed but does not expose a 'load' function.")
    return load_fn(source, **kwargs)


def check_behave_model_available() -> bool:
    """Check if ``behave-model`` is installed.

    Returns:
        ``True`` if ``behave-model`` is importable, ``False`` otherwise.

    """
    import importlib.util

    return importlib.util.find_spec("behave_model") is not None


def check_behave_doctor_available() -> bool:
    """Check if ``behave-doctor`` is installed.

    Returns:
        ``True`` if ``behave-doctor`` is importable, ``False`` otherwise.

    """
    import importlib.util

    return importlib.util.find_spec("behave_doctor") is not None
