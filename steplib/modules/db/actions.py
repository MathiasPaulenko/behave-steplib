"""Pure action functions for the DB module."""

from __future__ import annotations

from typing import Any

from steplib.modules.db.context import DbContext


def db_set_connection_string(db_ctx: DbContext, connection_string: str) -> None:
    """Set the database connection string.

    Args:
        db_ctx: The DB context to operate on.
        connection_string: A SQLAlchemy-compatible connection string.

    """
    db_ctx.connection_string = connection_string


def db_query(db_ctx: DbContext, query: str) -> list[dict[str, Any]]:
    """Execute a SQL query and return rows as a list of dicts.

    Args:
        db_ctx: The DB context to operate on.
        query: The SQL query string.

    Returns:
        A list of dictionaries, one per row, keyed by column name.

    Raises:
        RuntimeError: If no database connection is configured.

    """
    if db_ctx.connection is None:
        raise RuntimeError("No database connection configured in DbContext.")
    result = db_ctx.connection.execute(query)
    # DatabaseClient.execute() returns list[dict] directly.
    if isinstance(result, list):
        return result
    # SQLAlchemy-like result: has keys() and fetchall().
    columns = list(result.keys())
    return [dict(zip(columns, row, strict=False)) for row in result.fetchall()]


def db_assert_row_count(
    db_ctx: DbContext,
    query: str,
    expected: int,
) -> None:
    """Assert that a query returns exactly *expected* rows.

    Args:
        db_ctx: The DB context to operate on.
        query: The SQL query string.
        expected: The expected number of rows.

    Raises:
        AssertionError: If the row count does not match.

    """
    rows = db_query(db_ctx, query)
    actual = len(rows)
    if actual != expected:
        raise AssertionError(
            f"Expected {expected} rows, got {actual}."
        )


def db_assert_column_equals(
    db_ctx: DbContext,
    query: str,
    column: str,
    expected: str,
) -> None:
    """Assert that a column in the first row of a query equals *expected*.

    Args:
        db_ctx: The DB context to operate on.
        query: The SQL query string.
        column: The column name to check.
        expected: The expected value (compared as string).

    Raises:
        AssertionError: If the query returns no rows, the column is missing,
            or the value does not match.

    """
    rows = db_query(db_ctx, query)
    if not rows:
        raise AssertionError("Query returned no rows.")
    if column not in rows[0]:
        raise AssertionError(f"Column '{column}' not found in result.")
    actual = str(rows[0][column])
    if actual != str(expected):
        raise AssertionError(
            f"Column '{column}': expected '{expected}', got '{actual}'."
        )


def db_store(db_ctx: DbContext, variable: str, value: Any) -> None:
    """Store a *value* under *variable* name in the DB context.

    Args:
        db_ctx: The DB context to operate on.
        variable: The variable name.
        value: The value to store.

    """
    db_ctx.variables[variable] = value
