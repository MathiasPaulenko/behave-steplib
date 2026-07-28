"""CLIContext: per-scenario state for the cli module (shell commands)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CLIContext:
    """Holds all cli-module state for a scenario.

    Lives at ``context.steplib.cli`` and is reset between scenarios.

    Attributes:
        exit_code: Exit code of the last executed command.
        stdout: Standard output of the last executed command.
        stderr: Standard error output of the last executed command.
        variables: User-defined variables stored by steps.

    """

    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    variables: dict[str, Any] = field(default_factory=dict)

    def reset(self) -> None:
        """Reset per-scenario state."""
        self.exit_code = None
        self.stdout = ""
        self.stderr = ""
        self.variables = {}

    def cleanup(self) -> None:
        """Clean up resources after the scenario."""
        self.reset()
