"""DB step definitions for behave."""

from __future__ import annotations

from typing import Any

from steplib.core.decorators import step
from steplib.core.registry import StepRegistry
from steplib.modules.db.actions import (
    db_query,
    db_set_connection_string,
)
from steplib.modules.db.context import DbContext


def _get_db(context: Any) -> DbContext:
    """Get the DbContext from context.steplib, creating it if needed."""
    steplib = getattr(context, "steplib", None)
    if steplib is None:
        raise RuntimeError(
            "context.steplib is not initialized. "
            "Call autoload(context) or load(context, ...) in before_all."
        )
    db = getattr(steplib, "db", None)
    if db is None:
        db = DbContext()
        steplib.db = db
    return db


@step(
    "the database connection string is {connection_string}",
    category="db",
    description="Set the SQLAlchemy connection string for database queries.",
    example='Given the database connection string is "sqlite:///test.db"',
    i18n={
        "es": "la cadena de conexión de la base de datos es {connection_string}",
        "pt": "a string de conexão do banco de dados é {connection_string}",
    },
)
def step_set_db_connection(context: Any, connection_string: str) -> None:
    """Set the database connection string."""
    db_set_connection_string(_get_db(context), connection_string.strip('"'))


@step(
    "I execute the SQL query {query}",
    category="db",
    description="Execute a SQL query and store the result.",
    example='When I execute the SQL query "SELECT * FROM users"',
    i18n={
        "es": "ejecuto la consulta SQL {query}",
        "pt": "executo a consulta SQL {query}",
    },
)
def step_execute_query(context: Any, query: str) -> None:
    """Execute a SQL query."""
    db_ctx = _get_db(context)
    result = db_query(db_ctx, query.strip('"'))
    db_ctx.variables["_last_result"] = result


@step(
    "the query returns {count:d} rows",
    category="db",
    description="Assert the last query returned a specific number of rows.",
    example="Then the query returns 5 rows",
    i18n={
        "es": "la consulta devuelve {count:d} filas",
        "pt": "a consulta retorna {count:d} linhas",
    },
)
def step_query_row_count(context: Any, count: int) -> None:
    """Assert query row count."""
    db_ctx = _get_db(context)
    result = db_ctx.variables.get("_last_result", [])
    actual = len(result)
    if actual != count:
        raise AssertionError(f"Expected {count} rows, got {actual}.")


@step(
    "the column {column} in the first row equals {value}",
    category="db",
    description="Assert a column value in the first row of the last query.",
    example='Then the column "name" in the first row equals "Ada"',
    i18n={
        "es": "la columna {column} en la primera fila es igual a {value}",
        "pt": "a coluna {column} na primeira linha é igual a {value}",
    },
)
def step_column_equals(context: Any, column: str, value: str) -> None:
    """Assert column value in first row."""
    db_ctx = _get_db(context)
    result = db_ctx.variables.get("_last_result", [])
    if not result:
        raise AssertionError("No query result available.")
    col = column.strip('"')
    if col not in result[0]:
        raise AssertionError(f"Column '{col}' not found in result.")
    actual = str(result[0][col])
    expected = value.strip('"')
    if actual != expected:
        raise AssertionError(
            f"Column '{col}': expected '{expected}', got '{actual}'."
        )


_ALL_STEPS = [
    step_set_db_connection,
    step_execute_query,
    step_query_row_count,
    step_column_equals,
]


def register(registry: StepRegistry) -> None:
    """Register all DB steps into the given registry."""
    for step_fn in _ALL_STEPS:
        registry.add(step_fn)
