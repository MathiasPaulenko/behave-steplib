"""DataContext: per-scenario state for the data module (variables + env)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DataContext:
    """Holds all data-module state for a scenario.

    Lives at ``context.steplib.data`` and is reset between scenarios.

    Attributes:
        variables: User-defined variables stored by steps.
        _env_backup: Snapshot of environment variables modified during the
            scenario, so they can be restored on reset/cleanup.

    """

    variables: dict[str, Any] = field(default_factory=dict)
    _env_backup: dict[str, str | None] = field(default_factory=dict)

    def reset(self) -> None:
        """Reset per-scenario state, restoring any modified env vars."""
        self.variables = {}
        for key, original in self._env_backup.items():
            if original is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original
        self._env_backup = {}

    def cleanup(self) -> None:
        """Restore any modified env vars after the scenario."""
        for key, original in self._env_backup.items():
            if original is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original
        self._env_backup = {}
