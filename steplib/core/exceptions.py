"""Custom exceptions for steplib."""

from __future__ import annotations


class SteplibError(Exception):
    """Base exception for all steplib errors."""


class MissingDependencyError(SteplibError):
    """Raised when an optional dependency (extra) is not installed.

    Attributes:
        extra: The name of the missing extra (e.g. ``"api"``, ``"kit"``).
        package: The import name of the missing package, if known.

    """

    def __init__(self, extra: str, package: str | None = None) -> None:
        """Initialize the error with the missing extra name."""
        self.extra = extra
        self.package = package
        pkg_hint = f" (package '{package}')" if package else ""
        super().__init__(
            f"Missing optional dependency for extra '{extra}'{pkg_hint}. "
            f"Install it with: pip install behave-steplib[{extra}]"
        )


class DuplicateStepError(SteplibError):
    """Raised when two steps register the same pattern in the same backend."""

    def __init__(self, pattern: str, backend: str | None = None) -> None:
        """Initialize the error with the duplicate pattern and backend."""
        self.pattern = pattern
        self.backend = backend
        backend_hint = f" (backend '{backend}')" if backend else ""
        super().__init__(f"Duplicate step pattern: '{pattern}'{backend_hint}")


class StepContractError(SteplibError):
    """Raised when a step function does not satisfy the step contract."""
