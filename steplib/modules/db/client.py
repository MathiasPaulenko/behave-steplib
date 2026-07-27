"""Database client abstraction with lazy SQLAlchemy import."""

from __future__ import annotations

from typing import Any

from steplib.core.exceptions import MissingDependencyError


class DatabaseClient:
    """Database client backed by SQLAlchemy (requires the ``[db]`` extra).

    Attributes:
        engine: The SQLAlchemy engine instance.
        connection: The active SQLAlchemy connection.

    """

    def __init__(self, connection_string: str) -> None:
        """Initialize the SQLAlchemy engine, importing lazily.

        Args:
            connection_string: A SQLAlchemy-compatible connection string.

        Raises:
            MissingDependencyError: If SQLAlchemy is not installed.

        """
        try:
            from sqlalchemy import create_engine, text  # noqa: PLC0415
        except ImportError as exc:
            raise MissingDependencyError("db", "sqlalchemy") from exc

        self._text = text
        self.engine = create_engine(connection_string)
        self.connection = self.engine.connect()

    def execute(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a SQL query and return rows as a list of dicts.

        Args:
            query: The SQL query string.
            params: Optional bind parameters.

        Returns:
            A list of dictionaries, one per row, keyed by column name.

        """
        result = self.connection.execute(self._text(query), params or {})
        columns = list(result.keys())
        return [dict(zip(columns, row, strict=False)) for row in result.fetchall()]

    def execute_scalar(self, query: str, params: dict[str, Any] | None = None) -> Any:
        """Execute a SQL query and return a single scalar value.

        Args:
            query: The SQL query string.
            params: Optional bind parameters.

        Returns:
            The first column of the first row.

        """
        result = self.connection.execute(self._text(query), params or {})
        return result.scalar()

    def close(self) -> None:
        """Close the connection and dispose the engine."""
        self.connection.close()
        self.engine.dispose()


def get_client(connection_string: str) -> DatabaseClient:
    """Return a database client for the given connection string.

    Args:
        connection_string: A SQLAlchemy-compatible connection string.

    Returns:
        A ``DatabaseClient`` instance.

    Raises:
        MissingDependencyError: If SQLAlchemy is not installed.

    """
    return DatabaseClient(connection_string)
