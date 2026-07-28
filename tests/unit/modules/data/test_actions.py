"""Tests for data module actions (pure functions)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from steplib.modules.data.actions import (
    data_assert_env_equals,
    data_assert_env_exists,
    data_assert_env_not_equals,
    data_assert_env_not_exists,
    data_assert_variable_contains,
    data_assert_variable_equals,
    data_assert_variable_exists,
    data_assert_variable_has_length,
    data_assert_variable_is_empty,
    data_assert_variable_is_not_empty,
    data_assert_variable_not_equals,
    data_assert_variable_not_exists,
    data_clear_variables,
    data_copy_variable,
    data_delete_env_var,
    data_delete_variable,
    data_extract_key_path,
    data_load_env_file,
    data_load_json_file,
    data_load_yaml_file,
    data_set_env_from_variable,
    data_set_env_var,
    data_set_variable,
    data_set_variable_json,
    data_store_env_var,
)
from steplib.modules.data.context import DataContext

# --- Variable actions ---


class TestSetVariable:
    def test_set_string(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "name", "Ada")
        assert ctx.variables["name"] == "Ada"

    def test_overwrite(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "x", "1")
        data_set_variable(ctx, "x", "2")
        assert ctx.variables["x"] == "2"


class TestAssertVariableEquals:
    def test_equals(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "name", "Ada")
        data_assert_variable_equals(ctx, "name", "Ada")

    def test_not_equals(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "name", "Ada")
        with pytest.raises(AssertionError, match="expected 'Bob'"):
            data_assert_variable_equals(ctx, "name", "Bob")

    def test_missing(self) -> None:
        ctx = DataContext()
        with pytest.raises(AssertionError, match="does not exist"):
            data_assert_variable_equals(ctx, "missing", "x")


class TestAssertVariableExists:
    def test_exists(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "x", "1")
        data_assert_variable_exists(ctx, "x")

    def test_not_exists(self) -> None:
        ctx = DataContext()
        with pytest.raises(AssertionError, match="does not exist"):
            data_assert_variable_exists(ctx, "missing")


class TestAssertVariableNotExists:
    def test_not_exists(self) -> None:
        ctx = DataContext()
        data_assert_variable_not_exists(ctx, "missing")

    def test_exists_raises(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "x", "1")
        with pytest.raises(AssertionError, match="should not exist"):
            data_assert_variable_not_exists(ctx, "x")


class TestDeleteVariable:
    def test_delete(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "x", "1")
        data_delete_variable(ctx, "x")
        assert "x" not in ctx.variables

    def test_delete_missing(self) -> None:
        ctx = DataContext()
        with pytest.raises(KeyError, match="does not exist"):
            data_delete_variable(ctx, "missing")


class TestLoadJsonFile:
    def test_load_json(self, tmp_path: Path) -> None:
        data = {"user": {"id": 42, "name": "Ada"}}
        f = tmp_path / "data.json"
        f.write_text(json.dumps(data), encoding="utf-8")

        ctx = DataContext()
        data_load_json_file(ctx, str(f), "payload")
        assert ctx.variables["payload"] == data

    def test_file_not_found(self) -> None:
        ctx = DataContext()
        with pytest.raises(FileNotFoundError, match="JSON file not found"):
            data_load_json_file(ctx, "missing.json", "x")


class TestLoadYamlFile:
    def test_load_yaml(self, tmp_path: Path) -> None:
        pytest.importorskip("yaml")
        f = tmp_path / "config.yaml"
        f.write_text("server:\n  host: localhost\n  port: 8080\n", encoding="utf-8")

        ctx = DataContext()
        data_load_yaml_file(ctx, str(f), "config")
        assert ctx.variables["config"]["server"]["host"] == "localhost"
        assert ctx.variables["config"]["server"]["port"] == 8080

    def test_file_not_found(self) -> None:
        ctx = DataContext()
        with pytest.raises(FileNotFoundError, match="YAML file not found"):
            data_load_yaml_file(ctx, "missing.yaml", "x")


class TestExtractKeyPath:
    def test_simple_path(self) -> None:
        ctx = DataContext()
        ctx.variables["data"] = {"user": {"id": 42}}
        data_extract_key_path(ctx, "data", "user.id", "user_id")
        assert ctx.variables["user_id"] == 42

    def test_list_index(self) -> None:
        ctx = DataContext()
        ctx.variables["data"] = {"items": [{"name": "a"}, {"name": "b"}]}
        data_extract_key_path(ctx, "data", "items.1.name", "second")
        assert ctx.variables["second"] == "b"

    def test_missing_source(self) -> None:
        ctx = DataContext()
        with pytest.raises(KeyError, match="Source variable"):
            data_extract_key_path(ctx, "missing", "a.b", "target")

    def test_missing_key(self) -> None:
        ctx = DataContext()
        ctx.variables["data"] = {"user": {"id": 1}}
        with pytest.raises(KeyError, match="Key 'name' not found"):
            data_extract_key_path(ctx, "data", "user.name", "name")

    def test_index_out_of_range(self) -> None:
        ctx = DataContext()
        ctx.variables["data"] = {"items": [1, 2]}
        with pytest.raises(KeyError, match="Index 5 out of range"):
            data_extract_key_path(ctx, "data", "items.5", "val")

    def test_non_integer_index_on_list(self) -> None:
        ctx = DataContext()
        ctx.variables["data"] = {"items": [1, 2]}
        with pytest.raises(KeyError, match="non-integer key"):
            data_extract_key_path(ctx, "data", "items.abc", "val")

    def test_navigate_into_scalar(self) -> None:
        ctx = DataContext()
        ctx.variables["data"] = {"x": 42}
        with pytest.raises(KeyError, match="non-dict/list value"):
            data_extract_key_path(ctx, "data", "x.y", "val")


# --- Environment variable actions ---


class TestSetEnvVar:
    def test_set_new(self) -> None:
        ctx = DataContext()
        key = "STEPLIB_TEST_NEW_VAR"
        assert key not in os.environ
        data_set_env_var(ctx, key, "hello")
        assert os.environ[key] == "hello"
        ctx.cleanup()
        assert key not in os.environ

    def test_set_overwrite_and_restore(self) -> None:
        ctx = DataContext()
        key = "STEPLIB_TEST_RESTORE"
        os.environ[key] = "original"
        data_set_env_var(ctx, key, "modified")
        assert os.environ[key] == "modified"
        ctx.cleanup()
        assert os.environ[key] == "original"


class TestDeleteEnvVar:
    def test_delete_and_restore(self) -> None:
        ctx = DataContext()
        key = "STEPLIB_TEST_DELETE"
        os.environ[key] = "original"
        data_delete_env_var(ctx, key)
        assert key not in os.environ
        ctx.cleanup()
        assert os.environ[key] == "original"

    def test_delete_nonexistent(self) -> None:
        ctx = DataContext()
        key = "STEPLIB_TEST_DELETE_NONEXIST"
        assert key not in os.environ
        data_delete_env_var(ctx, key)
        assert key not in os.environ
        ctx.cleanup()
        assert key not in os.environ


class TestAssertEnvEquals:
    def test_equals(self) -> None:
        key = "STEPLIB_TEST_ENV_EQ"
        os.environ[key] = "value"
        try:
            data_assert_env_equals(key, "value")
        finally:
            del os.environ[key]

    def test_not_equals(self) -> None:
        key = "STEPLIB_TEST_ENV_NEQ"
        os.environ[key] = "value"
        try:
            with pytest.raises(AssertionError, match="expected 'other'"):
                data_assert_env_equals(key, "other")
        finally:
            del os.environ[key]

    def test_missing(self) -> None:
        with pytest.raises(AssertionError, match="not set"):
            data_assert_env_equals("STEPLIB_NONEXISTENT_12345", "x")


class TestAssertEnvExists:
    def test_exists(self) -> None:
        key = "STEPLIB_TEST_ENV_EXISTS"
        os.environ[key] = "1"
        try:
            data_assert_env_exists(key)
        finally:
            del os.environ[key]

    def test_not_exists(self) -> None:
        with pytest.raises(AssertionError, match="not set"):
            data_assert_env_exists("STEPLIB_NONEXISTENT_67890")


class TestStoreEnvVar:
    def test_store(self) -> None:
        ctx = DataContext()
        key = "STEPLIB_TEST_STORE"
        os.environ[key] = "secret"
        try:
            data_store_env_var(ctx, key, "token")
            assert ctx.variables["token"] == "secret"
        finally:
            del os.environ[key]

    def test_store_missing(self) -> None:
        ctx = DataContext()
        with pytest.raises(AssertionError, match="not set"):
            data_store_env_var(ctx, "STEPLIB_NONEXISTENT_99999", "x")


class TestLoadEnvFile:
    def test_load_simple(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text(
            '# comment\nAPI_KEY=secret123\nDEBUG=true\nEMPTY=\nQUOTED="hello world"\n',
            encoding="utf-8",
        )
        ctx = DataContext()
        data_load_env_file(ctx, str(f))
        assert os.environ["API_KEY"] == "secret123"
        assert os.environ["DEBUG"] == "true"
        assert os.environ["EMPTY"] == ""
        assert os.environ["QUOTED"] == "hello world"
        ctx.cleanup()

    def test_file_not_found(self) -> None:
        ctx = DataContext()
        with pytest.raises(FileNotFoundError, match="Env file not found"):
            data_load_env_file(ctx, "missing.env")


# --- Extended variable assertion actions ---


class TestAssertVariableNotEquals:
    def test_not_equals(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "x", "1")
        data_assert_variable_not_equals(ctx, "x", "2")

    def test_equals_raises(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "x", "1")
        with pytest.raises(AssertionError, match="should not equal"):
            data_assert_variable_not_equals(ctx, "x", "1")

    def test_missing(self) -> None:
        ctx = DataContext()
        with pytest.raises(AssertionError, match="does not exist"):
            data_assert_variable_not_equals(ctx, "missing", "1")


class TestAssertVariableContains:
    def test_contains(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "msg", "hello world")
        data_assert_variable_contains(ctx, "msg", "world")

    def test_not_contains_raises(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "msg", "hello")
        with pytest.raises(AssertionError, match="expected to contain"):
            data_assert_variable_contains(ctx, "msg", "bye")

    def test_missing(self) -> None:
        ctx = DataContext()
        with pytest.raises(AssertionError, match="does not exist"):
            data_assert_variable_contains(ctx, "missing", "x")


class TestAssertVariableIsEmpty:
    def test_empty_string(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "x", "")
        data_assert_variable_is_empty(ctx, "x")

    def test_empty_list(self) -> None:
        ctx = DataContext()
        ctx.variables["x"] = []
        data_assert_variable_is_empty(ctx, "x")

    def test_empty_dict(self) -> None:
        ctx = DataContext()
        ctx.variables["x"] = {}
        data_assert_variable_is_empty(ctx, "x")

    def test_none(self) -> None:
        ctx = DataContext()
        ctx.variables["x"] = None
        data_assert_variable_is_empty(ctx, "x")

    def test_not_empty_raises(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "x", "value")
        with pytest.raises(AssertionError, match="is not empty"):
            data_assert_variable_is_empty(ctx, "x")

    def test_missing(self) -> None:
        ctx = DataContext()
        with pytest.raises(AssertionError, match="does not exist"):
            data_assert_variable_is_empty(ctx, "missing")


class TestAssertVariableIsNotEmpty:
    def test_not_empty_string(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "x", "value")
        data_assert_variable_is_not_empty(ctx, "x")

    def test_not_empty_list(self) -> None:
        ctx = DataContext()
        ctx.variables["x"] = [1]
        data_assert_variable_is_not_empty(ctx, "x")

    def test_empty_string_raises(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "x", "")
        with pytest.raises(AssertionError, match="is empty"):
            data_assert_variable_is_not_empty(ctx, "x")

    def test_empty_list_raises(self) -> None:
        ctx = DataContext()
        ctx.variables["x"] = []
        with pytest.raises(AssertionError, match="is empty"):
            data_assert_variable_is_not_empty(ctx, "x")

    def test_none_raises(self) -> None:
        ctx = DataContext()
        ctx.variables["x"] = None
        with pytest.raises(AssertionError, match="is empty"):
            data_assert_variable_is_not_empty(ctx, "x")

    def test_missing(self) -> None:
        ctx = DataContext()
        with pytest.raises(AssertionError, match="does not exist"):
            data_assert_variable_is_not_empty(ctx, "missing")


class TestAssertVariableHasLength:
    def test_string_length(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "x", "hello")
        data_assert_variable_has_length(ctx, "x", 5)

    def test_list_length(self) -> None:
        ctx = DataContext()
        ctx.variables["x"] = [1, 2, 3]
        data_assert_variable_has_length(ctx, "x", 3)

    def test_dict_length(self) -> None:
        ctx = DataContext()
        ctx.variables["x"] = {"a": 1, "b": 2}
        data_assert_variable_has_length(ctx, "x", 2)

    def test_wrong_length_raises(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "x", "hello")
        with pytest.raises(AssertionError, match="expected length 10"):
            data_assert_variable_has_length(ctx, "x", 10)

    def test_no_length_raises(self) -> None:
        ctx = DataContext()
        ctx.variables["x"] = 42
        with pytest.raises(AssertionError, match="has no length"):
            data_assert_variable_has_length(ctx, "x", 1)

    def test_missing(self) -> None:
        ctx = DataContext()
        with pytest.raises(AssertionError, match="does not exist"):
            data_assert_variable_has_length(ctx, "missing", 1)


# --- Variable manipulation actions ---


class TestCopyVariable:
    def test_copy(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "original", "value")
        data_copy_variable(ctx, "original", "backup")
        assert ctx.variables["backup"] == "value"
        assert ctx.variables["original"] == "value"

    def test_copy_missing(self) -> None:
        ctx = DataContext()
        with pytest.raises(KeyError, match="does not exist"):
            data_copy_variable(ctx, "missing", "target")


class TestClearVariables:
    def test_clear(self) -> None:
        ctx = DataContext()
        data_set_variable(ctx, "a", "1")
        data_set_variable(ctx, "b", "2")
        data_clear_variables(ctx)
        assert ctx.variables == {}

    def test_clear_empty(self) -> None:
        ctx = DataContext()
        data_clear_variables(ctx)
        assert ctx.variables == {}


class TestSetVariableJson:
    def test_set_json(self) -> None:
        ctx = DataContext()
        data_set_variable_json(ctx, "config", '{"debug": true, "port": 8080}')
        assert ctx.variables["config"] == {"debug": True, "port": 8080}

    def test_set_json_list(self) -> None:
        ctx = DataContext()
        data_set_variable_json(ctx, "items", '[1, 2, 3]')
        assert ctx.variables["items"] == [1, 2, 3]

    def test_invalid_json(self) -> None:
        ctx = DataContext()
        with pytest.raises(json.JSONDecodeError):
            data_set_variable_json(ctx, "x", "{invalid}")


class TestSetEnvFromVariable:
    def test_set_env_from_var(self) -> None:
        ctx = DataContext()
        key = "STEPLIB_TEST_ENV_FROM_VAR"
        data_set_variable(ctx, "token", "secret123")
        data_set_env_from_variable(ctx, "token", key)
        assert os.environ[key] == "secret123"
        ctx.cleanup()
        assert key not in os.environ

    def test_missing_variable(self) -> None:
        ctx = DataContext()
        with pytest.raises(KeyError, match="does not exist"):
            data_set_env_from_variable(ctx, "missing", "KEY")


# --- Extended env assertion actions ---


class TestAssertEnvNotEquals:
    def test_not_equals(self) -> None:
        key = "STEPLIB_TEST_ENV_NEQ2"
        os.environ[key] = "value"
        try:
            data_assert_env_not_equals(key, "other")
        finally:
            del os.environ[key]

    def test_equals_raises(self) -> None:
        key = "STEPLIB_TEST_ENV_NEQ3"
        os.environ[key] = "value"
        try:
            with pytest.raises(AssertionError, match="should not equal"):
                data_assert_env_not_equals(key, "value")
        finally:
            del os.environ[key]

    def test_missing(self) -> None:
        with pytest.raises(AssertionError, match="not set"):
            data_assert_env_not_equals("STEPLIB_NONEXISTENT_11111", "x")


class TestAssertEnvNotExists:
    def test_not_exists(self) -> None:
        data_assert_env_not_exists("STEPLIB_NONEXISTENT_22222")

    def test_exists_raises(self) -> None:
        key = "STEPLIB_TEST_ENV_EXISTS2"
        os.environ[key] = "1"
        try:
            with pytest.raises(AssertionError, match="should not be set"):
                data_assert_env_not_exists(key)
        finally:
            del os.environ[key]
