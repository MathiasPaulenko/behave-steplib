"""Data step definitions for behave — generic variables and environment."""

from __future__ import annotations

from typing import Any

from steplib.core.decorators import step
from steplib.core.registry import StepRegistry
from steplib.modules.data.actions import (
    data_assert_env_equals,
    data_assert_env_exists,
    data_assert_variable_equals,
    data_assert_variable_exists,
    data_assert_variable_not_exists,
    data_delete_env_var,
    data_delete_variable,
    data_extract_key_path,
    data_load_env_file,
    data_load_json_file,
    data_load_yaml_file,
    data_set_env_var,
    data_set_variable,
    data_store_env_var,
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


_ALL_STEPS = [
    step_set_variable,
    step_variable_equals,
    step_variable_exists,
    step_variable_not_exists,
    step_delete_variable,
    step_load_yaml,
    step_load_json_file,
    step_extract_key_path,
    # Env
    step_set_env_var,
    step_delete_env_var,
    step_env_equals,
    step_env_exists,
    step_store_env_var,
    step_load_env_file,
]


def register(registry: StepRegistry) -> None:
    """Register all data steps into the given registry."""
    for step_fn in _ALL_STEPS:
        registry.add(step_fn)
