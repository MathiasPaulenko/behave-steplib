"""behave-steplib — reusable step libraries for Behave BDD."""

from __future__ import annotations

try:
    from steplib._version import __version__ as __version__
except ImportError:  # pragma: no cover
    __version__ = "0.0.0+unknown"

from steplib.core import Param, StepInfo, StepRegistry, step

__all__ = [
    "Param",
    "StepInfo",
    "StepRegistry",
    "__version__",
    "step",
]
