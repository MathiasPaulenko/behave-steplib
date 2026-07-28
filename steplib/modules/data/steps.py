"""Data step definitions for behave — generic variables and environment."""

from __future__ import annotations

from typing import Any

from steplib.core.decorators import step
from steplib.core.registry import StepRegistry
from steplib.modules.data.actions import (
    data_assert_env_equals,
    data_assert_env_exists,
    data_assert_env_not_equals,
    data_assert_env_not_exists,
    data_assert_variable_contains,
    data_assert_variable_ends_with,
    data_assert_variable_equals,
    data_assert_variable_exists,
    data_assert_variable_greater_than,
    data_assert_variable_has_length,
    data_assert_variable_is_empty,
    data_assert_variable_is_not_empty,
    data_assert_variable_less_than,
    data_assert_variable_matches,
    data_assert_variable_not_equals,
    data_assert_variable_not_exists,
    data_assert_variable_starts_with,
    data_clear_variables,
    data_copy_variable,
    data_delete_env_var,
    data_delete_variable,
    data_extract_key_path,
    data_increment_variable,
    data_load_env_file,
    data_load_json_file,
    data_load_yaml_file,
    data_set_env_from_variable,
    data_set_env_var,
    data_set_variable,
    data_set_variable_json,
    data_store_env_var,
    data_wait,
)
from steplib.modules.data.context import DataContext


def _get_data(context: Any) -> DataContext:
    """Get the DataContext from context.steplib, creating it if needed."""
    steplib = getattr(context, "steplib", None)
    if steplib is None:
        raise RuntimeError(
            "context.steplib is not initialized. "
            "Call autoload(context) or load(context, ...) in before_all."
        )
    data = getattr(steplib, "data", None)
    if data is None:
        data = DataContext()
        steplib.data = data
    return data


# --- Variable steps ---


@step(
    "I set the variable {name} to {value}",
    category="data",
    description="Set a generic variable in the data context.",
    example='Given I set the variable "user_id" to "42"',
    i18n={
        "es": "establezco la variable {name} a {value}",
        "pt": "defino a variável {name} como {value}",
    },
)
def step_set_variable(context: Any, name: str, value: str) -> None:
    """Set a generic variable."""
    data_set_variable(_get_data(context), name.strip('"'), value.strip('"'))


@step(
    "the variable {name} equals {value}",
    category="data",
    description="Assert that a variable equals an expected value.",
    example='Then the variable "user_id" equals "42"',
    i18n={
        "es": "la variable {name} es igual a {value}",
        "pt": "a variável {name} é igual a {value}",
    },
)
def step_variable_equals(context: Any, name: str, value: str) -> None:
    """Assert variable equals."""
    data_assert_variable_equals(_get_data(context), name.strip('"'), value.strip('"'))


@step(
    "the variable {name} exists",
    category="data",
    description="Assert that a variable exists in the data context.",
    example='Then the variable "user_id" exists',
    i18n={
        "es": "la variable {name} existe",
        "pt": "a variável {name} existe",
    },
)
def step_variable_exists(context: Any, name: str) -> None:
    """Assert variable exists."""
    data_assert_variable_exists(_get_data(context), name.strip('"'))


@step(
    "the variable {name} does not exist",
    category="data",
    description="Assert that a variable does not exist in the data context.",
    example='Then the variable "old_key" does not exist',
    i18n={
        "es": "la variable {name} no existe",
        "pt": "a variável {name} não existe",
    },
)
def step_variable_not_exists(context: Any, name: str) -> None:
    """Assert variable does not exist."""
    data_assert_variable_not_exists(_get_data(context), name.strip('"'))


@step(
    "I delete the variable {name}",
    category="data",
    description="Delete a variable from the data context.",
    example='When I delete the variable "temp"',
    i18n={
        "es": "elimino la variable {name}",
        "pt": "excluo a variável {name}",
    },
)
def step_delete_variable(context: Any, name: str) -> None:
    """Delete a variable."""
    data_delete_variable(_get_data(context), name.strip('"'))


@step(
    "I load the YAML file {path} into the variable {name}",
    category="data",
    description="Load a YAML file and store the parsed content as a variable.",
    example='Given I load the YAML file "config.yaml" into the variable "config"',
    i18n={
        "es": "cargo el archivo YAML {path} en la variable {name}",
        "pt": "carrego o arquivo YAML {path} na variável {name}",
    },
)
def step_load_yaml(context: Any, path: str, name: str) -> None:
    """Load YAML file into variable."""
    data_load_yaml_file(_get_data(context), path.strip('"'), name.strip('"'))


@step(
    "I load the JSON file {path} into the variable {name}",
    category="data",
    description="Load a JSON file and store the parsed content as a variable.",
    example='Given I load the JSON file "data.json" into the variable "payload"',
    i18n={
        "es": "cargo el archivo JSON {path} en la variable {name}",
        "pt": "carrego o arquivo JSON {path} na variável {name}",
    },
)
def step_load_json_file(context: Any, path: str, name: str) -> None:
    """Load JSON file into variable."""
    data_load_json_file(_get_data(context), path.strip('"'), name.strip('"'))


@step(
    "I extract the key path {key_path} from the variable {name} as {target}",
    category="data",
    description="Extract a value from a variable using dot-path navigation.",
    example='Then I extract the key path "user.id" from the variable "data" as "user_id"',
    i18n={
        "es": "extraigo la ruta de clave {key_path} de la variable {name} como {target}",
        "pt": "extraio o caminho de chave {key_path} da variável {name} como {target}",
    },
)
def step_extract_key_path(
    context: Any,
    key_path: str,
    name: str,
    target: str,
) -> None:
    """Extract a value via dot-path navigation."""
    data_extract_key_path(
        _get_data(context),
        name.strip('"'),
        key_path.strip('"'),
        target.strip('"'),
    )


# --- Environment variable steps ---


@step(
    "I set the environment variable {key} to {value}",
    category="data",
    description="Set an environment variable (restored after the scenario).",
    example='Given I set the environment variable "API_KEY" to "secret123"',
    i18n={
        "es": "establezco la variable de entorno {key} a {value}",
        "pt": "defino a variável de ambiente {key} como {value}",
    },
)
def step_set_env_var(context: Any, key: str, value: str) -> None:
    """Set an environment variable."""
    data_set_env_var(_get_data(context), key.strip('"'), value.strip('"'))


@step(
    "I delete the environment variable {key}",
    category="data",
    description="Delete an environment variable (restored after the scenario).",
    example='When I delete the environment variable "TEMP_KEY"',
    i18n={
        "es": "elimino la variable de entorno {key}",
        "pt": "excluo a variável de ambiente {key}",
    },
)
def step_delete_env_var(context: Any, key: str) -> None:
    """Delete an environment variable."""
    data_delete_env_var(_get_data(context), key.strip('"'))


@step(
    "the environment variable {key} equals {value}",
    category="data",
    description="Assert that an environment variable equals an expected value.",
    example='Then the environment variable "API_KEY" equals "secret123"',
    i18n={
        "es": "la variable de entorno {key} es igual a {value}",
        "pt": "a variável de ambiente {key} é igual a {value}",
    },
)
def step_env_equals(context: Any, key: str, value: str) -> None:
    """Assert env var equals."""
    data_assert_env_equals(key.strip('"'), value.strip('"'))


@step(
    "the environment variable {key} exists",
    category="data",
    description="Assert that an environment variable exists.",
    example='Then the environment variable "API_KEY" exists',
    i18n={
        "es": "la variable de entorno {key} existe",
        "pt": "a variável de ambiente {key} existe",
    },
)
def step_env_exists(context: Any, key: str) -> None:
    """Assert env var exists."""
    data_assert_env_exists(key.strip('"'))


@step(
    "I store the environment variable {key} as {variable}",
    category="data",
    description="Store an environment variable's value into a data variable.",
    example='Then I store the environment variable "HOME" as "home_dir"',
    i18n={
        "es": "guardo la variable de entorno {key} como {variable}",
        "pt": "armazeno a variável de ambiente {key} como {variable}",
    },
)
def step_store_env_var(context: Any, key: str, variable: str) -> None:
    """Store env var into a data variable."""
    data_store_env_var(_get_data(context), key.strip('"'), variable.strip('"'))


@step(
    "I load environment variables from file {path}",
    category="data",
    description="Load environment variables from a .env-style file.",
    example='Given I load environment variables from file ".env"',
    i18n={
        "es": "cargo variables de entorno desde el archivo {path}",
        "pt": "carrego variáveis de ambiente do arquivo {path}",
    },
)
def step_load_env_file(context: Any, path: str) -> None:
    """Load env vars from a .env file."""
    data_load_env_file(_get_data(context), path.strip('"'))


# --- Extended variable assertions ---


@step(
    "the variable {name} does not equal {value}",
    category="data",
    description="Assert that a variable does not equal a value.",
    example='Then the variable "status" does not equal "error"',
    i18n={
        "es": "la variable {name} no es igual a {value}",
        "pt": "a variável {name} não é igual a {value}",
    },
)
def step_variable_not_equals(context: Any, name: str, value: str) -> None:
    """Assert variable does not equal."""
    data_assert_variable_not_equals(_get_data(context), name.strip('"'), value.strip('"'))


@step(
    "the variable {name} contains {text}",
    category="data",
    description="Assert that a variable's string value contains a substring.",
    example='Then the variable "message" contains "success"',
    i18n={
        "es": "la variable {name} contiene {text}",
        "pt": "a variável {name} contém {text}",
    },
)
def step_variable_contains(context: Any, name: str, text: str) -> None:
    """Assert variable contains substring."""
    data_assert_variable_contains(_get_data(context), name.strip('"'), text.strip('"'))


@step(
    "the variable {name} is empty",
    category="data",
    description="Assert that a variable is empty.",
    example='Then the variable "errors" is empty',
    i18n={
        "es": "la variable {name} está vacía",
        "pt": "a variável {name} está vazia",
    },
)
def step_variable_is_empty(context: Any, name: str) -> None:
    """Assert variable is empty."""
    data_assert_variable_is_empty(_get_data(context), name.strip('"'))


@step(
    "the variable {name} is not empty",
    category="data",
    description="Assert that a variable is not empty.",
    example='Then the variable "results" is not empty',
    i18n={
        "es": "la variable {name} no está vacía",
        "pt": "a variável {name} não está vazia",
    },
)
def step_variable_is_not_empty(context: Any, name: str) -> None:
    """Assert variable is not empty."""
    data_assert_variable_is_not_empty(_get_data(context), name.strip('"'))


@step(
    "the variable {name} has length {count:d}",
    category="data",
    description="Assert that a variable has a specific length.",
    example='Then the variable "items" has length 5',
    i18n={
        "es": "la variable {name} tiene longitud {count:d}",
        "pt": "a variável {name} tem comprimento {count:d}",
    },
)
def step_variable_has_length(context: Any, name: str, count: int) -> None:
    """Assert variable has length."""
    data_assert_variable_has_length(_get_data(context), name.strip('"'), count)


# --- Extended env assertions ---


@step(
    "the environment variable {key} does not equal {value}",
    category="data",
    description="Assert that an environment variable does not equal a value.",
    example='Then the environment variable "MODE" does not equal "production"',
    i18n={
        "es": "la variable de entorno {key} no es igual a {value}",
        "pt": "a variável de ambiente {key} não é igual a {value}",
    },
)
def step_env_not_equals(context: Any, key: str, value: str) -> None:
    """Assert env var does not equal."""
    data_assert_env_not_equals(key.strip('"'), value.strip('"'))


@step(
    "the environment variable {key} does not exist",
    category="data",
    description="Assert that an environment variable does not exist.",
    example='Then the environment variable "DEBUG" does not exist',
    i18n={
        "es": "la variable de entorno {key} no existe",
        "pt": "a variável de ambiente {key} não existe",
    },
)
def step_env_not_exists(context: Any, key: str) -> None:
    """Assert env var does not exist."""
    data_assert_env_not_exists(key.strip('"'))


# --- Variable manipulation ---


@step(
    "I copy the variable {source} to {target}",
    category="data",
    description="Copy a variable to a new name.",
    example='When I copy the variable "original" to "backup"',
    i18n={
        "es": "copio la variable {source} a {target}",
        "pt": "copio a variável {source} para {target}",
    },
)
def step_copy_variable(context: Any, source: str, target: str) -> None:
    """Copy a variable."""
    data_copy_variable(_get_data(context), source.strip('"'), target.strip('"'))


@step(
    "I clear all variables",
    category="data",
    description="Remove all variables from the data context.",
    example="When I clear all variables",
    i18n={
        "es": "limpio todas las variables",
        "pt": "limpo todas as variáveis",
    },
)
def step_clear_variables(context: Any) -> None:
    """Clear all variables."""
    data_clear_variables(_get_data(context))


@step(
    "I set the variable {name} to the JSON {json}",
    category="data",
    description="Set a variable to a parsed JSON value.",
    example='Given I set the variable "config" to the JSON \'{"debug": true}\'',
    i18n={
        "es": "establezco la variable {name} al JSON {json}",
        "pt": "defino a variável {name} como o JSON {json}",
    },
)
def step_set_variable_json(context: Any, name: str, json_str: str) -> None:
    """Set a variable from a JSON string."""
    data_set_variable_json(_get_data(context), name.strip('"'), json_str.strip("'").strip('"'))


@step(
    "I set the environment variable {key} from the variable {variable}",
    category="data",
    description="Set an environment variable from a data variable's value.",
    example='When I set the environment variable "TOKEN" from the variable "api_token"',
    i18n={
        "es": "establezco la variable de entorno {key} desde la variable {variable}",
        "pt": "defino a variável de ambiente {key} da variável {variable}",
    },
)
def step_set_env_from_variable(context: Any, key: str, variable: str) -> None:
    """Set env var from a data variable."""
    data_set_env_from_variable(_get_data(context), variable.strip('"'), key.strip('"'))


# --- Extended variable assertions ---


@step(
    "the variable {name} matches the pattern {pattern}",
    category="data",
    description="Assert that a variable's value matches a regex pattern.",
    example='Then the variable "email" matches the pattern ".*@.*\\..*"',
    i18n={
        "es": "la variable {name} coincide con el patrón {pattern}",
        "pt": "a variável {name} corresponde ao padrão {pattern}",
    },
)
def step_variable_matches(context: Any, name: str, pattern: str) -> None:
    """Assert variable matches regex pattern."""
    data_assert_variable_matches(
        _get_data(context), name.strip('"'), pattern.strip('"')
    )


@step(
    "the variable {name} starts with {text}",
    category="data",
    description="Assert that a variable's value starts with the given text.",
    example='Then the variable "greeting" starts with "Hello"',
    i18n={
        "es": "la variable {name} comienza con {text}",
        "pt": "a variável {name} começa com {text}",
    },
)
def step_variable_starts_with(context: Any, name: str, text: str) -> None:
    """Assert variable starts with text."""
    data_assert_variable_starts_with(
        _get_data(context), name.strip('"'), text.strip('"')
    )


@step(
    "the variable {name} ends with {text}",
    category="data",
    description="Assert that a variable's value ends with the given text.",
    example='Then the variable "filename" ends with ".csv"',
    i18n={
        "es": "la variable {name} termina con {text}",
        "pt": "a variável {name} termina com {text}",
    },
)
def step_variable_ends_with(context: Any, name: str, text: str) -> None:
    """Assert variable ends with text."""
    data_assert_variable_ends_with(
        _get_data(context), name.strip('"'), text.strip('"')
    )


@step(
    "I increment the variable {name} by {amount:d}",
    category="data",
    description="Increment a numeric variable by a given amount.",
    example='When I increment the variable "counter" by 1',
    i18n={
        "es": "incremento la variable {name} en {amount:d}",
        "pt": "incremento a variável {name} em {amount:d}",
    },
)
def step_increment_variable(context: Any, name: str, amount: int) -> None:
    """Increment a numeric variable."""
    data_increment_variable(_get_data(context), name.strip('"'), amount)


@step(
    "the variable {name} is greater than {value}",
    category="data",
    description="Assert that a variable's numeric value is greater than a threshold.",
    example='Then the variable "count" is greater than 10',
    i18n={
        "es": "la variable {name} es mayor que {value}",
        "pt": "a variável {name} é maior que {value}",
    },
)
def step_variable_greater_than(context: Any, name: str, value: str) -> None:
    """Assert variable is greater than value."""
    data_assert_variable_greater_than(
        _get_data(context), name.strip('"'), value.strip('"')
    )


@step(
    "the variable {name} is less than {value}",
    category="data",
    description="Assert that a variable's numeric value is less than a threshold.",
    example='Then the variable "count" is less than 100',
    i18n={
        "es": "la variable {name} es menor que {value}",
        "pt": "a variável {name} é menor que {value}",
    },
)
def step_variable_less_than(context: Any, name: str, value: str) -> None:
    """Assert variable is less than value."""
    data_assert_variable_less_than(
        _get_data(context), name.strip('"'), value.strip('"')
    )


# --- Utility steps ---


@step(
    "I wait for {seconds:f} seconds",
    category="data",
    description="Sleep for a given number of seconds.",
    example="When I wait for 2.5 seconds",
    i18n={
        "es": "espero {seconds:f} segundos",
        "pt": "eu espero {seconds:f} segundos",
    },
)
def step_wait(context: Any, seconds: float) -> None:
    """Wait for a number of seconds."""
    data_wait(seconds)


_ALL_STEPS = [
    step_set_variable,
    step_variable_equals,
    step_variable_exists,
    step_variable_not_exists,
    step_delete_variable,
    step_load_yaml,
    step_load_json_file,
    step_extract_key_path,
    # Extended variable assertions
    step_variable_not_equals,
    step_variable_contains,
    step_variable_is_empty,
    step_variable_is_not_empty,
    step_variable_has_length,
    # Regex + string assertions
    step_variable_matches,
    step_variable_starts_with,
    step_variable_ends_with,
    # Numeric assertions
    step_variable_greater_than,
    step_variable_less_than,
    # Variable manipulation
    step_copy_variable,
    step_clear_variables,
    step_set_variable_json,
    step_increment_variable,
    # Env
    step_set_env_var,
    step_delete_env_var,
    step_env_equals,
    step_env_exists,
    step_store_env_var,
    step_load_env_file,
    # Extended env assertions
    step_env_not_equals,
    step_env_not_exists,
    # Env from variable
    step_set_env_from_variable,
    # Utility
    step_wait,
]


def register(registry: StepRegistry) -> None:
    """Register all data steps into the given registry."""
    for step_fn in _ALL_STEPS:
        registry.add(step_fn)
