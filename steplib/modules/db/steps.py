"""DB step definitions for behave."""

from __future__ import annotations

from typing import Any

from steplib.core.decorators import step
from steplib.core.registry import StepRegistry
from steplib.modules.db.actions import (
    _normalize_value,
    db_assert_scalar_equals,
    db_assert_table_exists,
    db_assert_table_row_count,
    db_begin_transaction,
    db_commit,
    db_connect,
    db_disconnect,
    db_query,
    db_query_with_params,
    db_rollback,
    db_set_connection_string,
    db_store_scalar,
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
    actual = _normalize_value(result[0][col])
    expected = value.strip('"')
    if actual != _normalize_value(expected):
        raise AssertionError(f"Column '{col}': expected '{expected}', got '{actual}'.")


# --- Connection management ---


@step(
    "I connect to the database",
    category="db",
    description="Create a database connection from the stored connection string.",
    example="When I connect to the database",
    i18n={
        "es": "me conecto a la base de datos",
        "pt": "conecto ao banco de dados",
    },
)
def step_db_connect(context: Any) -> None:
    """Connect to the database."""
    db_connect(_get_db(context))


@step(
    "I disconnect from the database",
    category="db",
    description="Close the database connection and dispose the engine.",
    example="Then I disconnect from the database",
    i18n={
        "es": "me desconecto de la base de datos",
        "pt": "desconecto do banco de dados",
    },
)
def step_db_disconnect(context: Any) -> None:
    """Disconnect from the database."""
    db_disconnect(_get_db(context))


# --- Extended assertions ---


@step(
    "the query returns more than {count:d} rows",
    category="db",
    description="Assert the query returns more than a specific number of rows.",
    example="Then the query returns more than 0 rows",
    i18n={
        "es": "la consulta devuelve más de {count:d} filas",
        "pt": "a consulta retorna mais de {count:d} linhas",
    },
)
def step_query_row_count_greater_than(context: Any, count: int) -> None:
    """Assert query row count is greater than."""
    db_ctx = _get_db(context)
    result = db_ctx.variables.get("_last_result", [])
    actual = len(result)
    if actual <= count:
        raise AssertionError(f"Expected more than {count} rows, got {actual}.")


@step(
    "the query returns fewer than {count:d} rows",
    category="db",
    description="Assert the query returns fewer than a specific number of rows.",
    example="Then the query returns fewer than 100 rows",
    i18n={
        "es": "la consulta devuelve menos de {count:d} filas",
        "pt": "a consulta retorna menos de {count:d} linhas",
    },
)
def step_query_row_count_less_than(context: Any, count: int) -> None:
    """Assert query row count is less than."""
    db_ctx = _get_db(context)
    result = db_ctx.variables.get("_last_result", [])
    actual = len(result)
    if actual >= count:
        raise AssertionError(f"Expected fewer than {count} rows, got {actual}.")


@step(
    "the column {column} in the first row contains {value}",
    category="db",
    description="Assert a column value in the first row contains a substring.",
    example='Then the column "email" in the first row contains "@"',
    i18n={
        "es": "la columna {column} en la primera fila contiene {value}",
        "pt": "a coluna {column} na primeira linha contém {value}",
    },
)
def step_column_contains(context: Any, column: str, value: str) -> None:
    """Assert column value contains substring."""
    db_ctx = _get_db(context)
    result = db_ctx.variables.get("_last_result", [])
    if not result:
        raise AssertionError("No query result available.")
    col = column.strip('"')
    if col not in result[0]:
        raise AssertionError(f"Column '{col}' not found in result.")
    actual = _normalize_value(result[0][col])
    expected = value.strip('"')
    if expected not in actual:
        raise AssertionError(f"Column '{col}': expected to contain '{expected}', got '{actual}'.")


@step(
    "the column {column} in the first row does not equal {value}",
    category="db",
    description="Assert a column value in the first row does NOT equal a value.",
    example='Then the column "status" in the first row does not equal "deleted"',
    i18n={
        "es": "la columna {column} en la primera fila no es igual a {value}",
        "pt": "a coluna {column} na primeira linha não é igual a {value}",
    },
)
def step_column_not_equals(context: Any, column: str, value: str) -> None:
    """Assert column value does not equal."""
    db_ctx = _get_db(context)
    result = db_ctx.variables.get("_last_result", [])
    if not result:
        raise AssertionError("No query result available.")
    col = column.strip('"')
    if col not in result[0]:
        raise AssertionError(f"Column '{col}' not found in result.")
    actual = _normalize_value(result[0][col])
    expected = value.strip('"')
    if actual == _normalize_value(expected):
        raise AssertionError(f"Column '{col}': should not equal '{expected}'.")


@step(
    "the column {column} in the first row is null",
    category="db",
    description="Assert a column value in the first row is NULL.",
    example='Then the column "deleted_at" in the first row is null',
    i18n={
        "es": "la columna {column} en la primera fila es nula",
        "pt": "a coluna {column} na primeira linha é nula",
    },
)
def step_column_is_null(context: Any, column: str) -> None:
    """Assert column value is null."""
    db_ctx = _get_db(context)
    result = db_ctx.variables.get("_last_result", [])
    if not result:
        raise AssertionError("No query result available.")
    col = column.strip('"')
    if col not in result[0]:
        raise AssertionError(f"Column '{col}' not found in result.")
    if result[0][col] is not None:
        raise AssertionError(f"Column '{col}': expected NULL, got '{result[0][col]}'.")


@step(
    "the column {column} in the first row is not null",
    category="db",
    description="Assert a column value in the first row is NOT NULL.",
    example='Then the column "email" in the first row is not null',
    i18n={
        "es": "la columna {column} en la primera fila no es nula",
        "pt": "a coluna {column} na primeira linha não é nula",
    },
)
def step_column_is_not_null(context: Any, column: str) -> None:
    """Assert column value is not null."""
    db_ctx = _get_db(context)
    result = db_ctx.variables.get("_last_result", [])
    if not result:
        raise AssertionError("No query result available.")
    col = column.strip('"')
    if col not in result[0]:
        raise AssertionError(f"Column '{col}' not found in result.")
    if result[0][col] is None:
        raise AssertionError(f"Column '{col}': expected NOT NULL.")


@step(
    "the scalar query {query} equals {value}",
    category="db",
    description="Execute a scalar query and assert the result equals a value.",
    example='Then the scalar query "SELECT COUNT(*) FROM users" equals "42"',
    i18n={
        "es": "la consulta escalar {query} es igual a {value}",
        "pt": "a consulta escalar {query} é igual a {value}",
    },
)
def step_scalar_equals(context: Any, query: str, value: str) -> None:
    """Assert scalar query equals value."""
    db_assert_scalar_equals(_get_db(context), query.strip('"'), value.strip('"'))


# --- Store / Extract ---


@step(
    "I store the column {column} from the first row as {variable}",
    category="db",
    description="Store a column value from the last query result as a variable.",
    example='Then I store the column "id" from the first row as "user_id"',
    i18n={
        "es": "guardo la columna {column} de la primera fila como {variable}",
        "pt": "armazeno a coluna {column} da primeira linha como {variable}",
    },
)
def step_store_column_value(context: Any, column: str, variable: str) -> None:
    """Store column value as variable."""
    db_ctx = _get_db(context)
    result = db_ctx.variables.get("_last_result", [])
    if not result:
        raise AssertionError("No query result available.")
    col = column.strip('"')
    if col not in result[0]:
        raise AssertionError(f"Column '{col}' not found in result.")
    db_ctx.variables[variable.strip('"')] = result[0][col]


@step(
    "I store the row count as {variable}",
    category="db",
    description="Store the row count of the last query as a variable.",
    example='Then I store the row count as "total_users"',
    i18n={
        "es": "guardo el número de filas como {variable}",
        "pt": "armazeno o número de linhas como {variable}",
    },
)
def step_store_row_count(context: Any, variable: str) -> None:
    """Store row count as variable."""
    db_ctx = _get_db(context)
    result = db_ctx.variables.get("_last_result", [])
    db_ctx.variables[variable.strip('"')] = len(result)


# --- Transactional ---


@step(
    "I begin a database transaction",
    category="db",
    description="Begin a transaction on the current database connection.",
    example="When I begin a database transaction",
    i18n={
        "es": "inicio una transacción de base de datos",
        "pt": "inicio uma transação de banco de dados",
    },
)
def step_begin_transaction(context: Any) -> None:
    """Begin a transaction."""
    db_begin_transaction(_get_db(context))


@step(
    "I rollback the database transaction",
    category="db",
    description="Rollback the current database transaction.",
    example="Then I rollback the database transaction",
    i18n={
        "es": "revierto la transacción de base de datos",
        "pt": "reverto a transação de banco de dados",
    },
)
def step_rollback_transaction(context: Any) -> None:
    """Rollback transaction."""
    db_rollback(_get_db(context))


@step(
    "I commit the database transaction",
    category="db",
    description="Commit the current database transaction.",
    example="Then I commit the database transaction",
    i18n={
        "es": "confirmo la transacción de base de datos",
        "pt": "confirmo a transação de banco de dados",
    },
)
def step_commit_transaction(context: Any) -> None:
    """Commit transaction."""
    db_commit(_get_db(context))


# --- Table assertions ---


@step(
    "the table {table} exists",
    category="db",
    description="Assert that a table exists in the database.",
    example='Then the table "users" exists',
    i18n={
        "es": "la tabla {table} existe",
        "pt": "a tabela {table} existe",
    },
)
def step_table_exists(context: Any, table: str) -> None:
    """Assert table exists."""
    db_assert_table_exists(_get_db(context), table.strip('"'))


@step(
    "the table {table} has {count:d} rows",
    category="db",
    description="Assert that a table has a specific number of rows.",
    example='Then the table "users" has 42 rows',
    i18n={
        "es": "la tabla {table} tiene {count:d} filas",
        "pt": "a tabela {table} tem {count:d} linhas",
    },
)
def step_table_row_count(context: Any, table: str, count: int) -> None:
    """Assert table row count."""
    db_assert_table_row_count(_get_db(context), table.strip('"'), count)


# --- Query with params ---


@step(
    "I execute the SQL query {query} with params {params}",
    category="db",
    description="Execute a SQL query with bind parameters and store the result.",
    example=(
        'When I execute the SQL query "SELECT * FROM users WHERE id = :id"'
        " with params '{\"id\": 1}'"
    ),
    i18n={
        "es": "ejecuto la consulta SQL {query} con parámetros {params}",
        "pt": "executo a consulta SQL {query} com parâmetros {params}",
    },
)
def step_execute_query_with_params(context: Any, query: str, params: str) -> None:
    """Execute a SQL query with bind parameters."""
    import json

    db_ctx = _get_db(context)
    try:
        parsed = json.loads(params.strip("'").strip('"'))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Invalid JSON params: {exc}") from exc
    result = db_query_with_params(db_ctx, query.strip('"'), parsed)
    db_ctx.variables["_last_result"] = result


# --- Store scalar ---


@step(
    "I store the scalar query {query} as {variable}",
    category="db",
    description="Execute a scalar query and store the result as a variable.",
    example='Then I store the scalar query "SELECT COUNT(*) FROM users" as "total"',
    i18n={
        "es": "guardo la consulta escalar {query} como {variable}",
        "pt": "armazeno a consulta escalar {query} como {variable}",
    },
)
def step_store_scalar(context: Any, query: str, variable: str) -> None:
    """Store scalar query result as variable."""
    db_store_scalar(_get_db(context), query.strip('"'), variable.strip('"'))


_ALL_STEPS = [
    step_set_db_connection,
    step_execute_query,
    step_execute_query_with_params,
    step_query_row_count,
    step_column_equals,
    # Connection management
    step_db_connect,
    step_db_disconnect,
    # Extended assertions
    step_query_row_count_greater_than,
    step_query_row_count_less_than,
    step_column_contains,
    step_column_not_equals,
    step_column_is_null,
    step_column_is_not_null,
    step_scalar_equals,
    # Store / Extract
    step_store_column_value,
    step_store_row_count,
    # Transactional
    step_begin_transaction,
    step_rollback_transaction,
    step_commit_transaction,
    # Table assertions
    step_table_exists,
    step_table_row_count,
    # Store scalar
    step_store_scalar,
]


def register(registry: StepRegistry) -> None:
    """Register all DB steps into the given registry."""
    for step_fn in _ALL_STEPS:
        registry.add(step_fn)
