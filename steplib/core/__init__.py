"""Core package: registry, discovery, decorators and metadata."""

from __future__ import annotations

from steplib.core.decorators import step
from steplib.core.exceptions import (
    DuplicateStepError,
    MissingDependencyError,
    StepContractError,
    SteplibError,
)
from steplib.core.metadata import StepInfo
from steplib.core.params import Param, register_type, resolve_type
from steplib.core.registry import StepRegistry
from steplib.core.state import SteplibState

__all__ = [
    "DuplicateStepError",
    "MissingDependencyError",
    "Param",
    "StepContractError",
    "StepInfo",
    "StepRegistry",
    "SteplibError",
    "SteplibState",
    "register_type",
    "resolve_type",
    "step",
]
