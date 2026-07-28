"""Pure action functions for the data module (variables + environment)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from steplib.modules.data.context import DataContext


# --- Variable actions ---


def data_set_variable(data_ctx: DataContext, name: str, value: str) -> None:
    """Set a generic variable in the data context.

    Args:
        data_ctx: The data context to operate on.
        name: The variable name.
        value: The variable value (stored as string).

    """
    data_ctx.variables[name] = value


def data_assert_variable_equals(
    data_ctx: DataContext,
    name: str,
    expected: str,
) -> None:
    """Assert that a variable equals an expected value.

    Args:
        data_ctx: The data context to check.
        name: The variable name.
        expected: The expected value.

    Raises:
        AssertionError: If the variable does not exist or the value differs.

    """
    if name not in data_ctx.variables:
        raise AssertionError(f"Variable '{name}' does not exist.")
    actual = data_ctx.variables[name]
    if str(actual) != expected:
        raise AssertionError(
            f"Variable '{name}': expected '{expected}', got '{actual}'."
        )


def data_assert_variable_exists(data_ctx: DataContext, name: str) -> None:
    """Assert that a variable exists in the data context.

    Args:
        data_ctx: The data context to check.
        name: The variable name.

    Raises:
        AssertionError: If the variable does not exist.

    """
    if name not in data_ctx.variables:
        raise AssertionError(f"Variable '{name}' does not exist.")


def data_assert_variable_not_exists(data_ctx: DataContext, name: str) -> None:
    """Assert that a variable does not exist in the data context.

    Args:
        data_ctx: The data context to check.
        name: The variable name.

    Raises:
        AssertionError: If the variable exists.

    """
    if name in data_ctx.variables:
        raise AssertionError(f"Variable '{name}' should not exist.")


def data_delete_variable(data_ctx: DataContext, name: str) -> None:
    """Delete a variable from the data context.

    Args:
        data_ctx: The data context to operate on.
        name: The variable name.

    Raises:
        KeyError: If the variable does not exist.

    """
    if name not in data_ctx.variables:
        raise KeyError(f"Variable '{name}' does not exist.")
    del data_ctx.variables[name]


def data_load_yaml_file(data_ctx: DataContext, path: str, name: str) -> None:
    """Load a YAML file into a variable as a dict.

    Args:
        data_ctx: The data context to operate on.
        path: Path to the YAML file.
        name: The variable name to store the parsed content.

    Raises:
        MissingDependencyError: If PyYAML is not installed.
        FileNotFoundError: If the file does not exist.

    """
    try:
        import yaml
    except ImportError as exc:
        raise ImportError(
            "PyYAML is required to load YAML files. Install it with: pip install pyyaml"
        ) from exc

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with file_path.open(encoding="utf-8") as f:
        data_ctx.variables[name] = yaml.safe_load(f)


def data_load_json_file(data_ctx: DataContext, path: str, name: str) -> None:
    """Load a JSON file into a variable as a dict.

    Args:
        data_ctx: The data context to operate on.
        path: Path to the JSON file.
        name: The variable name to store the parsed content.

    Raises:
        FileNotFoundError: If the file does not exist.

    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    with file_path.open(encoding="utf-8") as f:
        data_ctx.variables[name] = json.load(f)


def data_extract_key_path(
    data_ctx: DataContext,
    source: str,
    key_path: str,
    target: str,
) -> None:
    """Extract a value from a variable using dot-path navigation.

    Navigates nested dicts/lists using dot-separated keys. List indices
    are supported via integer keys (e.g. ``items.0.name``).

    Args:
        data_ctx: The data context to operate on.
        source: The source variable name.
        key_path: Dot-separated path (e.g. ``user.address.city``).
        target: The target variable name to store the extracted value.

    Raises:
        KeyError: If the source variable does not exist.
        KeyError: If any key in the path is not found.

    """
    if source not in data_ctx.variables:
        raise KeyError(f"Source variable '{source}' does not exist.")

    current: Any = data_ctx.variables[source]
    for key in key_path.split("."):
        if isinstance(current, list):
            try:
                idx = int(key)
            except ValueError as exc:
                raise KeyError(
                    f"Cannot index list with non-integer key '{key}' in path '{key_path}'."
                ) from exc
            if idx < 0 or idx >= len(current):
                raise KeyError(
                    f"Index {idx} out of range in path '{key_path}'."
                )
            current = current[idx]
        elif isinstance(current, dict):
            if key not in current:
                raise KeyError(
                    f"Key '{key}' not found in path '{key_path}'."
                )
            current = current[key]
        else:
            raise KeyError(
                f"Cannot navigate into non-dict/list value at '{key}' in path '{key_path}'."
            )

    data_ctx.variables[target] = current


# --- Environment variable actions ---


def data_set_env_var(data_ctx: DataContext, key: str, value: str) -> None:
    """Set an environment variable, backing up the original for restoration.

    Args:
        data_ctx: The data context (used for backup tracking).
        key: The environment variable name.
        value: The value to set.

    """
    if key not in data_ctx._env_backup:
        data_ctx._env_backup[key] = os.environ.get(key)
    os.environ[key] = value


def data_delete_env_var(data_ctx: DataContext, key: str) -> None:
    """Delete an environment variable, backing up the original for restoration.

    Args:
        data_ctx: The data context (used for backup tracking).
        key: The environment variable name.

    """
    if key not in data_ctx._env_backup:
        data_ctx._env_backup[key] = os.environ.get(key)
    os.environ.pop(key, None)


def data_assert_env_equals(key: str, expected: str) -> None:
    """Assert that an environment variable equals an expected value.

    Args:
        key: The environment variable name.
        expected: The expected value.

    Raises:
        AssertionError: If the env var does not exist or differs.

    """
    actual = os.environ.get(key)
    if actual is None:
        raise AssertionError(f"Environment variable '{key}' is not set.")
    if actual != expected:
        raise AssertionError(
            f"Environment variable '{key}': expected '{expected}', got '{actual}'."
        )


def data_assert_env_exists(key: str) -> None:
    """Assert that an environment variable exists.

    Args:
        key: The environment variable name.

    Raises:
        AssertionError: If the env var does not exist.

    """
    if key not in os.environ:
        raise AssertionError(f"Environment variable '{key}' is not set.")


def data_store_env_var(
    data_ctx: DataContext,
    key: str,
    variable: str,
) -> None:
    """Store an environment variable's value into a data variable.

    Args:
        data_ctx: The data context to operate on.
        key: The environment variable name.
        variable: The target variable name.

    Raises:
        AssertionError: If the env var does not exist.

    """
    if key not in os.environ:
        raise AssertionError(f"Environment variable '{key}' is not set.")
    data_ctx.variables[variable] = os.environ[key]


def data_load_env_file(data_ctx: DataContext, path: str) -> None:
    """Load environment variables from a .env-style file.

    Parses simple ``KEY=VALUE`` lines. Lines starting with ``#`` are
    ignored. Quoted values (single or double) are unquoted.

    Args:
        data_ctx: The data context (used for backup tracking).
        path: Path to the .env file.

    Raises:
        FileNotFoundError: If the file does not exist.

    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Env file not found: {path}")

    with file_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            data_set_env_var(data_ctx, key, value)
