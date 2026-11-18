"""DbContext: per-scenario database state for the DB module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DbContext:
    """Holds all database state for a scenario.

    Lives at ``context.steplib.db`` and is reset between scenarios.

    Attributes:
        engine: The SQLAlchemy engine instance.
        connection: The active SQLAlchemy connection.
        connection_string: The SQLAlchemy connection string.
        transaction: The active transaction (if any).
        variables: User-defined variables stored by steps.
        backend: The backend name (e.g. ``"sqlalchemy"``).

    """

    engine: Any = None
    connection: Any = None
    connection_string: str = ""
    transaction: Any = None
    variables: dict[str, Any] = field(default_factory=dict)
    backend: str = "sqlalchemy"

    def reset(self) -> None:
        """Reset per-scenario state, keeping the engine and configuration."""
        self.variables = {}

    def cleanup(self) -> None:
        """Close the database connection if it exists.

        Each resource is released best-effort: a failing rollback or close
        must not prevent the remaining resources from being released. The
        first error is re-raised once everything was attempted.
        """
        first_error: BaseException | None = None
        if self.transaction is not None:
            try:
                if hasattr(self.transaction, "rollback"):
                    self.transaction.rollback()
            except Exception as exc:
                if first_error is None:
                    first_error = exc
            self.transaction = None
        if self.connection is not None:
            try:
                if hasattr(self.connection, "close"):
                    self.connection.close()
            except Exception as exc:
                if first_error is None:
                    first_error = exc
            self.connection = None
        if self.engine is not None:
            try:
                if hasattr(self.engine, "dispose"):
                    self.engine.dispose()
            except Exception as exc:
                if first_error is None:
                    first_error = exc
            self.engine = None
        if first_error is not None:
            raise first_error
