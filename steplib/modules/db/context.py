"""DbContext: per-scenario database state for the DB module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DbContext:
    """Holds all database state for a scenario.

    Lives at ``context.steplib.db`` and is reset between scenarios.
    """

    engine: Any = None
    connection: Any = None
    connection_string: str = ""
    variables: dict[str, Any] = field(default_factory=dict)
    backend: str = "sqlalchemy"

    def reset(self) -> None:
        """Reset per-scenario state, keeping the engine and configuration."""
        self.variables = {}

    def cleanup(self) -> None:
        """Close the database connection if it exists."""
        if self.connection is not None and hasattr(self.connection, "close"):
            self.connection.close()
            self.connection = None
        if self.engine is not None and hasattr(self.engine, "dispose"):
            self.engine.dispose()
            self.engine = None
