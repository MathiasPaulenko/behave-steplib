"""Tests for data step functions (thin wrappers around actions)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from steplib.core.state import SteplibState
from steplib.modules.data.context import DataContext
from steplib.modules.data.steps import (
    step_clear_variables,
    step_copy_variable,
    step_delete_env_var,
    step_delete_variable,
    step_env_equals,
    step_env_exists,
    step_env_not_equals,
    step_env_not_exists,
    step_extract_key_path,
    step_load_env_file,
    step_load_json_file,
    step_load_yaml,
    step_set_env_from_variable,
    step_set_env_var,
    step_set_variable,
    step_set_variable_json,
    step_store_env_var,
    step_variable_contains,
    step_variable_equals,
    step_variable_exists,
    step_variable_has_length,
    step_variable_is_empty,
    step_variable_is_not_empty,
    step_variable_not_equals,
    step_variable_not_exists,
)


def _make_context() -> SimpleNamespace:
    """Create a behave-like context with steplib state and DataContext."""
    context = SimpleNamespace()
    state = SteplibState(context, registry=None)  # type: ignore[arg-type]
    state.data = DataContext()  # type: ignore[attr-defined]
    context.steplib = state
    return context


# --- Variable steps ---


def test_step_set_variable() -> None:
    context = _make_context()
    step_set_variable(context, '"user_id"', '"42"')
    assert context.steplib.data.variables["user_id"] == "42"  # type: ignore[attr-defined]


def test_step_variable_equals() -> None:
    context = _make_context()
    step_set_variable(context, '"name"', '"Ada"')
    step_variable_equals(context, '"name"', '"Ada"')


def test_step_variable_equals_raises() -> None:
    context = _make_context()
    step_set_variable(context, '"name"', '"Ada"')
    with pytest.raises(AssertionError, match="expected 'Bob'"):
        step_variable_equals(context, '"name"', '"Bob"')


def test_step_variable_exists() -> None:
    context = _make_context()
    step_set_variable(context, '"x"', '"1"')
    step_variable_exists(context, '"x"')


def test_step_variable_exists_raises() -> None:
    context = _make_context()
    with pytest.raises(AssertionError, match="does not exist"):
        step_variable_exists(context, '"missing"')


def test_step_variable_not_exists() -> None:
    context = _make_context()
    step_variable_not_exists(context, '"missing"')


def test_step_variable_not_exists_raises() -> None:
    context = _make_context()
    step_set_variable(context, '"x"', '"1"')
    with pytest.raises(AssertionError, match="should not exist"):
        step_variable_not_exists(context, '"x"')


def test_step_delete_variable() -> None:
    context = _make_context()
    step_set_variable(context, '"temp"', '"val"')
    step_delete_variable(context, '"temp"')
    assert "temp" not in context.steplib.data.variables  # type: ignore[attr-defined]


def test_step_delete_variable_missing() -> None:
    context = _make_context()
    with pytest.raises(KeyError, match="does not exist"):
        step_delete_variable(context, '"missing"')


def test_step_load_json_file(tmp_path: Path) -> None:
    data = {"user": {"id": 42, "name": "Ada"}}
    f = tmp_path / "data.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    context = _make_context()
    step_load_json_file(context, str(f), '"payload"')
    assert context.steplib.data.variables["payload"] == data  # type: ignore[attr-defined]


def test_step_load_yaml_file(tmp_path: Path) -> None:
    pytest.importorskip("yaml")
    f = tmp_path / "config.yaml"
    f.write_text("server:\n  host: localhost\n  port: 8080\n", encoding="utf-8")

    context = _make_context()
    step_load_yaml(context, str(f), '"config"')
    config = context.steplib.data.variables["config"]  # type: ignore[attr-defined]
    assert config["server"]["host"] == "localhost"
    assert config["server"]["port"] == 8080


def test_step_extract_key_path() -> None:
    context = _make_context()
    context.steplib.data.variables["data"] = {"user": {"id": 42}}  # type: ignore[attr-defined]
    step_extract_key_path(context, '"user.id"', '"data"', '"user_id"')
    assert context.steplib.data.variables["user_id"] == 42  # type: ignore[attr-defined]


def test_step_extract_key_path_list() -> None:
    context = _make_context()
    context.steplib.data.variables["data"] = {"items": [{"name": "a"}, {"name": "b"}]}  # type: ignore[attr-defined]
    step_extract_key_path(context, '"items.1.name"', '"data"', '"second"')
    assert context.steplib.data.variables["second"] == "b"  # type: ignore[attr-defined]


def test_step_extract_key_path_missing_source() -> None:
    context = _make_context()
    with pytest.raises(KeyError, match="Source variable"):
        step_extract_key_path(context, '"a.b"', '"missing"', '"target"')


# --- Environment variable steps ---


def test_step_set_env_var() -> None:
    context = _make_context()
    key = "STEPLIB_STEP_TEST_SET"
    assert key not in os.environ
    step_set_env_var(context, key, '"hello"')
    assert os.environ[key] == "hello"
    context.steplib.data.cleanup()  # type: ignore[attr-defined]
    assert key not in os.environ


def test_step_delete_env_var() -> None:
    context = _make_context()
    key = "STEPLIB_STEP_TEST_DEL"
    os.environ[key] = "original"
    step_delete_env_var(context, key)
    assert key not in os.environ
    context.steplib.data.cleanup()  # type: ignore[attr-defined]
    assert os.environ[key] == "original"


def test_step_env_equals() -> None:
    key = "STEPLIB_STEP_TEST_EQ"
    os.environ[key] = "value"
    try:
        context = _make_context()
        step_env_equals(context, key, '"value"')
    finally:
        del os.environ[key]


def test_step_env_equals_raises() -> None:
    key = "STEPLIB_STEP_TEST_NEQ"
    os.environ[key] = "value"
    try:
        context = _make_context()
        with pytest.raises(AssertionError, match="expected 'other'"):
            step_env_equals(context, key, '"other"')
    finally:
        del os.environ[key]


def test_step_env_equals_missing() -> None:
    context = _make_context()
    with pytest.raises(AssertionError, match="not set"):
        step_env_equals(context, "STEPLIB_NONEXISTENT_STEP", '"x"')


def test_step_env_exists() -> None:
    key = "STEPLIB_STEP_TEST_EXISTS"
    os.environ[key] = "1"
    try:
        context = _make_context()
        step_env_exists(context, key)
    finally:
        del os.environ[key]


def test_step_env_exists_raises() -> None:
    context = _make_context()
    with pytest.raises(AssertionError, match="not set"):
        step_env_exists(context, "STEPLIB_NONEXISTENT_STEP2")


def test_step_store_env_var() -> None:
    key = "STEPLIB_STEP_TEST_STORE"
    os.environ[key] = "secret"
    try:
        context = _make_context()
        step_store_env_var(context, key, '"token"')
        assert context.steplib.data.variables["token"] == "secret"  # type: ignore[attr-defined]
    finally:
        del os.environ[key]


def test_step_store_env_var_missing() -> None:
    context = _make_context()
    with pytest.raises(AssertionError, match="not set"):
        step_store_env_var(context, "STEPLIB_NONEXISTENT_STEP3", '"x"')


def test_step_load_env_file(tmp_path: Path) -> None:
    f = tmp_path / ".env"
    f.write_text(
        '# comment\nAPI_KEY=secret123\nDEBUG=true\nQUOTED="hello world"\n',
        encoding="utf-8",
    )
    context = _make_context()
    step_load_env_file(context, str(f))
    assert os.environ["API_KEY"] == "secret123"
    assert os.environ["DEBUG"] == "true"
    assert os.environ["QUOTED"] == "hello world"
    context.steplib.data.cleanup()  # type: ignore[attr-defined]


def test_step_load_env_file_not_found() -> None:
    context = _make_context()
    with pytest.raises(FileNotFoundError, match="Env file not found"):
        step_load_env_file(context, '"missing.env"')


# --- Extended variable assertion steps ---


def test_step_variable_not_equals() -> None:
    context = _make_context()
    step_set_variable(context, '"x"', '"1"')
    step_variable_not_equals(context, '"x"', '"2"')


def test_step_variable_not_equals_raises() -> None:
    context = _make_context()
    step_set_variable(context, '"x"', '"1"')
    with pytest.raises(AssertionError, match="should not equal"):
        step_variable_not_equals(context, '"x"', '"1"')


def test_step_variable_contains() -> None:
    context = _make_context()
    step_set_variable(context, '"msg"', '"hello world"')
    step_variable_contains(context, '"msg"', '"world"')


def test_step_variable_contains_raises() -> None:
    context = _make_context()
    step_set_variable(context, '"msg"', '"hello"')
    with pytest.raises(AssertionError, match="expected to contain"):
        step_variable_contains(context, '"msg"', '"bye"')


def test_step_variable_is_empty() -> None:
    context = _make_context()
    step_set_variable(context, '"x"', '""')
    step_variable_is_empty(context, '"x"')


def test_step_variable_is_empty_raises() -> None:
    context = _make_context()
    step_set_variable(context, '"x"', '"value"')
    with pytest.raises(AssertionError, match="is not empty"):
        step_variable_is_empty(context, '"x"')


def test_step_variable_is_not_empty() -> None:
    context = _make_context()
    step_set_variable(context, '"x"', '"value"')
    step_variable_is_not_empty(context, '"x"')


def test_step_variable_is_not_empty_raises() -> None:
    context = _make_context()
    step_set_variable(context, '"x"', '""')
    with pytest.raises(AssertionError, match="is empty"):
        step_variable_is_not_empty(context, '"x"')


def test_step_variable_has_length() -> None:
    context = _make_context()
    step_set_variable(context, '"x"', '"hello"')
    step_variable_has_length(context, '"x"', 5)


def test_step_variable_has_length_raises() -> None:
    context = _make_context()
    step_set_variable(context, '"x"', '"hello"')
    with pytest.raises(AssertionError, match="expected length 10"):
        step_variable_has_length(context, '"x"', 10)


# --- Extended env assertion steps ---


def test_step_env_not_equals() -> None:
    key = "STEPLIB_STEP_ENV_NEQ"
    os.environ[key] = "value"
    try:
        context = _make_context()
        step_env_not_equals(context, key, '"other"')
    finally:
        del os.environ[key]


def test_step_env_not_equals_raises() -> None:
    key = "STEPLIB_STEP_ENV_NEQ2"
    os.environ[key] = "value"
    try:
        context = _make_context()
        with pytest.raises(AssertionError, match="should not equal"):
            step_env_not_equals(context, key, '"value"')
    finally:
        del os.environ[key]


def test_step_env_not_exists() -> None:
    context = _make_context()
    step_env_not_exists(context, "STEPLIB_NONEXISTENT_STEP4")


def test_step_env_not_exists_raises() -> None:
    key = "STEPLIB_STEP_ENV_EXISTS3"
    os.environ[key] = "1"
    try:
        context = _make_context()
        with pytest.raises(AssertionError, match="should not be set"):
            step_env_not_exists(context, key)
    finally:
        del os.environ[key]


# --- Variable manipulation steps ---


def test_step_copy_variable() -> None:
    context = _make_context()
    step_set_variable(context, '"original"', '"value"')
    step_copy_variable(context, '"original"', '"backup"')
    assert context.steplib.data.variables["backup"] == "value"  # type: ignore[attr-defined]


def test_step_copy_variable_missing() -> None:
    context = _make_context()
    with pytest.raises(KeyError, match="does not exist"):
        step_copy_variable(context, '"missing"', '"target"')


def test_step_clear_variables() -> None:
    context = _make_context()
    step_set_variable(context, '"a"', '"1"')
    step_set_variable(context, '"b"', '"2"')
    step_clear_variables(context)
    assert context.steplib.data.variables == {}  # type: ignore[attr-defined]


def test_step_set_variable_json() -> None:
    context = _make_context()
    step_set_variable_json(context, '"config"', '\'{"debug": true}\'')
    assert context.steplib.data.variables["config"] == {"debug": True}  # type: ignore[attr-defined]


def test_step_set_variable_json_invalid() -> None:
    context = _make_context()
    with pytest.raises(json.JSONDecodeError):
        step_set_variable_json(context, '"x"', "'{invalid}'")


def test_step_set_env_from_variable() -> None:
    context = _make_context()
    key = "STEPLIB_STEP_ENV_FROM_VAR"
    step_set_variable(context, '"token"', '"secret123"')
    step_set_env_from_variable(context, key, '"token"')
    assert os.environ[key] == "secret123"
    context.steplib.data.cleanup()  # type: ignore[attr-defined]
    assert key not in os.environ


def test_step_set_env_from_variable_missing() -> None:
    context = _make_context()
    with pytest.raises(KeyError, match="does not exist"):
        step_set_env_from_variable(context, "STEPLIB_KEY", '"missing"')
