"""Pure action functions for the DB module."""

from __future__ import annotations

import re
from typing import Any

from steplib.modules.db.context import DbContext

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$")


def _validate_identifier(name: str) -> str:
    """Validate that *name* is a safe SQL identifier.

    Allows simple identifiers (``users``) and schema-qualified names
    (``public.users``).  Rejects anything containing characters that
    could be used for SQL injection.

    Args:
        name: The identifier to validate.

    Returns:
        The validated identifier.

    Raises:
        ValueError: If the identifier contains unsafe characters.

    """
    if not name or not _IDENTIFIER_RE.match(name):
        raise ValueError(
            f"Invalid SQL identifier '{name}'. "
            "Only alphanumeric characters, underscores, and dots "
            "(for schema-qualified names) are allowed."
        )
    return name


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
        raise AssertionError(f"Expected {expected} rows, got {actual}.")


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
        raise AssertionError(f"Column '{column}': expected '{expected}', got '{actual}'.")


def db_store(db_ctx: DbContext, variable: str, value: Any) -> None:
    """Store a *value* under *variable* name in the DB context.

    Args:
        db_ctx: The DB context to operate on.
        variable: The variable name.
        value: The value to store.

    """
    db_ctx.variables[variable] = value


# --- Connection management ---


def db_connect(db_ctx: DbContext) -> None:
    """Create a database connection from the stored connection string.

    Args:
        db_ctx: The DB context to operate on.

    Raises:
        RuntimeError: If no connection string is configured.
        MissingDependencyError: If SQLAlchemy is not installed.

    """
    if not db_ctx.connection_string:
        raise RuntimeError("No connection string configured in DbContext.")
    from steplib.modules.db.client import get_client

    client = get_client(db_ctx.connection_string)
    db_ctx.engine = client.engine
    db_ctx.connection = client


def db_disconnect(db_ctx: DbContext) -> None:
    """Close the database connection and dispose the engine.

    Args:
        db_ctx: The DB context to operate on.

    """
    if db_ctx.transaction is not None and hasattr(db_ctx.transaction, "rollback"):
        db_ctx.transaction.rollback()
        db_ctx.transaction = None
    if db_ctx.connection is not None and hasattr(db_ctx.connection, "close"):
        db_ctx.connection.close()
        db_ctx.connection = None
    if db_ctx.engine is not None and hasattr(db_ctx.engine, "dispose"):
        db_ctx.engine.dispose()
        db_ctx.engine = None


# --- Query with params ---


def db_query_with_params(
    db_ctx: DbContext,
    query: str,
    params: dict[str, Any],
) -> list[dict[str, Any]]:
    """Execute a SQL query with bind parameters and return rows as a list of dicts.

    Args:
        db_ctx: The DB context to operate on.
        query: The SQL query string.
        params: Bind parameters for the query.

    Returns:
        A list of dictionaries, one per row, keyed by column name.

    Raises:
        RuntimeError: If no database connection is configured.

    """
    if db_ctx.connection is None:
        raise RuntimeError("No database connection configured in DbContext.")
    if hasattr(db_ctx.connection, "execute"):
        result = db_ctx.connection.execute(query, params)
        if isinstance(result, list):
            return result
        columns = list(result.keys())
        return [dict(zip(columns, row, strict=False)) for row in result.fetchall()]
    raise RuntimeError("Database connection does not support execute().")


# --- Scalar ---


def db_query_scalar(
    db_ctx: DbContext,
    query: str,
    params: dict[str, Any] | None = None,
) -> Any:
    """Execute a SQL query and return a single scalar value.

    Args:
        db_ctx: The DB context to operate on.
        query: The SQL query string.
        params: Optional bind parameters.

    Returns:
        The first column of the first row.

    Raises:
        RuntimeError: If no database connection is configured.

    """
    if db_ctx.connection is None:
        raise RuntimeError("No database connection configured in DbContext.")
    if hasattr(db_ctx.connection, "execute_scalar"):
        return db_ctx.connection.execute_scalar(query, params or {})
    if hasattr(db_ctx.connection, "execute"):
        result = db_ctx.connection.execute(query, params or {})
        if hasattr(result, "scalar"):
            return result.scalar()
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                return next(iter(first.values()))
            return first[0] if isinstance(first, (list, tuple)) else first
        return None
    raise RuntimeError("Database connection does not support execute().")


def db_assert_scalar_equals(
    db_ctx: DbContext,
    query: str,
    expected: str,
    params: dict[str, Any] | None = None,
) -> None:
    """Assert that a scalar query result equals *expected*.

    Args:
        db_ctx: The DB context to operate on.
        query: The SQL query string.
        expected: The expected value (compared as string).
        params: Optional bind parameters.

    Raises:
        AssertionError: If the scalar value does not match.

    """
    actual = db_query_scalar(db_ctx, query, params)
    if str(actual) != str(expected):
        raise AssertionError(f"Scalar: expected '{expected}', got '{actual}'.")


# --- Extended assertions ---


def db_assert_row_count_greater_than(
    db_ctx: DbContext,
    query: str,
    minimum: int,
) -> None:
    """Assert that a query returns more than *minimum* rows.

    Args:
        db_ctx: The DB context to operate on.
        query: The SQL query string.
        minimum: The minimum number of rows (exclusive).

    Raises:
        AssertionError: If the row count is not greater than *minimum*.

    """
    rows = db_query(db_ctx, query)
    actual = len(rows)
    if actual <= minimum:
        raise AssertionError(f"Expected more than {minimum} rows, got {actual}.")


def db_assert_row_count_less_than(
    db_ctx: DbContext,
    query: str,
    maximum: int,
) -> None:
    """Assert that a query returns fewer than *maximum* rows.

    Args:
        db_ctx: The DB context to operate on.
        query: The SQL query string.
        maximum: The maximum number of rows (exclusive).

    Raises:
        AssertionError: If the row count is not less than *maximum*.

    """
    rows = db_query(db_ctx, query)
    actual = len(rows)
    if actual >= maximum:
        raise AssertionError(f"Expected fewer than {maximum} rows, got {actual}.")


def db_assert_column_contains(
    db_ctx: DbContext,
    query: str,
    column: str,
    substring: str,
) -> None:
    """Assert that a column in the first row contains *substring*.

    Args:
        db_ctx: The DB context to operate on.
        query: The SQL query string.
        column: The column name to check.
        substring: The substring to search for.

    Raises:
        AssertionError: If the query returns no rows, the column is missing,
            or the value does not contain *substring*.

    """
    rows = db_query(db_ctx, query)
    if not rows:
        raise AssertionError("Query returned no rows.")
    if column not in rows[0]:
        raise AssertionError(f"Column '{column}' not found in result.")
    actual = str(rows[0][column])
    if substring not in actual:
        raise AssertionError(
            f"Column '{column}': expected to contain '{substring}', got '{actual}'."
        )


def db_assert_column_not_equals(
    db_ctx: DbContext,
    query: str,
    column: str,
    expected: str,
) -> None:
    """Assert that a column in the first row does NOT equal *expected*.

    Args:
        db_ctx: The DB context to operate on.
        query: The SQL query string.
        column: The column name to check.
        expected: The value that should not match.

    Raises:
        AssertionError: If the query returns no rows, the column is missing,
            or the value equals *expected*.

    """
    rows = db_query(db_ctx, query)
    if not rows:
        raise AssertionError("Query returned no rows.")
    if column not in rows[0]:
        raise AssertionError(f"Column '{column}' not found in result.")
    actual = str(rows[0][column])
    if actual == str(expected):
        raise AssertionError(f"Column '{column}': should not equal '{expected}'.")


def db_assert_column_is_null(
    db_ctx: DbContext,
    query: str,
    column: str,
) -> None:
    """Assert that a column in the first row is NULL.

    Args:
        db_ctx: The DB context to operate on.
        query: The SQL query string.
        column: The column name to check.

    Raises:
        AssertionError: If the query returns no rows, the column is missing,
            or the value is not NULL.

    """
    rows = db_query(db_ctx, query)
    if not rows:
        raise AssertionError("Query returned no rows.")
    if column not in rows[0]:
        raise AssertionError(f"Column '{column}' not found in result.")
    if rows[0][column] is not None:
        raise AssertionError(f"Column '{column}': expected NULL, got '{rows[0][column]}'.")


def db_assert_column_is_not_null(
    db_ctx: DbContext,
    query: str,
    column: str,
) -> None:
    """Assert that a column in the first row is NOT NULL.

    Args:
        db_ctx: The DB context to operate on.
        query: The SQL query string.
        column: The column name to check.

    Raises:
        AssertionError: If the query returns no rows, the column is missing,
            or the value is NULL.

    """
    rows = db_query(db_ctx, query)
    if not rows:
        raise AssertionError("Query returned no rows.")
    if column not in rows[0]:
        raise AssertionError(f"Column '{column}' not found in result.")
    if rows[0][column] is None:
        raise AssertionError(f"Column '{column}': expected NOT NULL.")


# --- Store / Extract ---


def db_store_column_value(
    db_ctx: DbContext,
    query: str,
    column: str,
    variable: str,
) -> None:
    """Store a column value from the first row of a query as a variable.

    Args:
        db_ctx: The DB context to operate on.
        query: The SQL query string.
        column: The column name to extract.
        variable: The variable name to store under.

    Raises:
        AssertionError: If the query returns no rows or the column is missing.

    """
    rows = db_query(db_ctx, query)
    if not rows:
        raise AssertionError("Query returned no rows.")
    if column not in rows[0]:
        raise AssertionError(f"Column '{column}' not found in result.")
    db_ctx.variables[variable] = rows[0][column]


def db_store_row_count(
    db_ctx: DbContext,
    query: str,
    variable: str,
) -> None:
    """Store the row count of a query as a variable.

    Args:
        db_ctx: The DB context to operate on.
        query: The SQL query string.
        variable: The variable name to store under.

    """
    rows = db_query(db_ctx, query)
    db_ctx.variables[variable] = len(rows)


def db_store_scalar(
    db_ctx: DbContext,
    query: str,
    variable: str,
    params: dict[str, Any] | None = None,
) -> None:
    """Store a scalar query result as a variable.

    Args:
        db_ctx: The DB context to operate on.
        query: The SQL query string.
        variable: The variable name to store under.
        params: Optional bind parameters.

    """
    db_ctx.variables[variable] = db_query_scalar(db_ctx, query, params)


# --- Transactional ---


def db_begin_transaction(db_ctx: DbContext) -> None:
    """Begin a transaction on the current connection.

    Args:
        db_ctx: The DB context to operate on.

    Raises:
        RuntimeError: If no database connection is configured.

    """
    if db_ctx.connection is None:
        raise RuntimeError("No database connection configured in DbContext.")
    if hasattr(db_ctx.connection, "begin"):
        db_ctx.transaction = db_ctx.connection.begin()
    else:
        raise RuntimeError("Database connection does not support begin().")


def db_rollback(db_ctx: DbContext) -> None:
    """Rollback the current transaction.

    Args:
        db_ctx: The DB context to operate on.

    Raises:
        RuntimeError: If no transaction is active.

    """
    if db_ctx.transaction is None:
        raise RuntimeError("No active transaction in DbContext.")
    db_ctx.transaction.rollback()
    db_ctx.transaction = None


def db_commit(db_ctx: DbContext) -> None:
    """Commit the current transaction.

    Args:
        db_ctx: The DB context to operate on.

    Raises:
        RuntimeError: If no transaction is active.

    """
    if db_ctx.transaction is None:
        raise RuntimeError("No active transaction in DbContext.")
    db_ctx.transaction.commit()
    db_ctx.transaction = None


# --- Table assertions ---


def db_assert_table_exists(db_ctx: DbContext, table_name: str) -> None:
    """Assert that a table exists in the database.

    Args:
        db_ctx: The DB context to operate on.
        table_name: The table name to check.

    Raises:
        AssertionError: If the table does not exist.
        ValueError: If the table name is not a valid identifier.

    """
    _validate_identifier(table_name)
    if db_ctx.connection is None:
        raise RuntimeError("No database connection configured in DbContext.")
    try:
        if "sqlite" in db_ctx.connection_string:
            rows = db_query_with_params(
                db_ctx,
                "SELECT name FROM sqlite_master WHERE type='table' AND name=:name",
                {"name": table_name},
            )
        else:
            rows = db_query_with_params(
                db_ctx,
                "SELECT table_name FROM information_schema.tables WHERE table_name = :name",
                {"name": table_name},
            )
    except Exception:
        rows = []
    # Fallback: try a simple SELECT
    if not rows:
        try:
            db_query(db_ctx, f"SELECT 1 FROM {table_name} LIMIT 1")
        except Exception:
            raise AssertionError(f"Table '{table_name}' does not exist.") from None


def db_assert_table_row_count(
    db_ctx: DbContext,
    table_name: str,
    expected: int,
) -> None:
    """Assert that a table has exactly *expected* rows.

    Args:
        db_ctx: The DB context to operate on.
        table_name: The table name to check.
        expected: The expected number of rows.

    Raises:
        AssertionError: If the row count does not match.
        ValueError: If the table name is not a valid identifier.

    """
    _validate_identifier(table_name)
    rows = db_query(db_ctx, f"SELECT COUNT(*) AS cnt FROM {table_name}")
    if not rows:
        raise AssertionError(f"Could not count rows in table '{table_name}'.")
    actual = int(rows[0].get("cnt", 0))
    if actual != expected:
        raise AssertionError(f"Table '{table_name}': expected {expected} rows, got {actual}.")
