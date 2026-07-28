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
    step_delete_env_var,
    step_delete_variable,
    step_env_equals,
    step_env_exists,
    step_extract_key_path,
    step_load_env_file,
    step_load_json_file,
    step_load_yaml,
    step_set_env_var,
    step_set_variable,
    step_store_env_var,
    step_variable_equals,
    step_variable_exists,
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
