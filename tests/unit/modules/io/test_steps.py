"""Tests for io module step definitions."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from steplib.modules.io.context import IOContext
from steplib.modules.io.steps import (
    step_append_file,
    step_close_csv_writer,
    step_copy_file,
    step_create_csv,
    step_create_csv_writer,
    step_create_directory,
    step_create_empty_file,
    step_create_json_path,
    step_delete_directory,
    step_delete_file,
    step_delete_json_path,
    step_diff_json,
    step_directory_exists,
    step_directory_not_exists,
    step_file_exists,
    step_file_not_exists,
    step_files_same,
    step_get_file_extension,
    step_get_file_size,
    step_get_json_path_type,
    step_json_matches_schema,
    step_json_path_equals,
    step_json_valid,
    step_last_json_valid,
    step_list_directory,
    step_load_json,
    step_merge_json,
    step_move_file,
    step_read_file,
    step_read_file_as_lines,
    step_rename_file,
    step_save_csv,
    step_save_json,
    step_set_csv_header_row,
    step_store_json_path,
    step_update_json_path,
    step_write_csv_row,
    step_write_file,
)


def _make_context() -> Any:
    """Create a mock context with steplib.io."""
    ctx = SimpleNamespace()
    ctx.steplib = SimpleNamespace()
    ctx.steplib.io = IOContext()
    return ctx


# ---------------------------------------------------------------------------
# File steps
# ---------------------------------------------------------------------------


class TestStepReadFile:
    def test_read_file(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello", encoding="utf-8")
        ctx = _make_context()
        step_read_file(ctx, str(f), "content")
        assert ctx.steplib.io.variables["content"] == "hello"


class TestStepWriteFile:
    def test_write_file(self, tmp_path: Path) -> None:
        ctx = _make_context()
        path = tmp_path / "out.txt"
        step_write_file(ctx, "hello", str(path))
        assert path.read_text(encoding="utf-8") == "hello"


class TestStepAppendFile:
    def test_append_file(self, tmp_path: Path) -> None:
        f = tmp_path / "log.txt"
        f.write_text("line1\n", encoding="utf-8")
        ctx = _make_context()
        step_append_file(ctx, "line2\n", str(f))
        assert f.read_text(encoding="utf-8") == "line1\nline2\n"


class TestStepDeleteFile:
    def test_delete_file(self, tmp_path: Path) -> None:
        f = tmp_path / "temp.txt"
        f.write_text("data", encoding="utf-8")
        ctx = _make_context()
        step_delete_file(ctx, str(f))
        assert not f.exists()


class TestStepCopyFile:
    def test_copy_file(self, tmp_path: Path) -> None:
        src = tmp_path / "src.txt"
        src.write_text("data", encoding="utf-8")
        dst = tmp_path / "dst.txt"
        ctx = _make_context()
        step_copy_file(ctx, str(src), str(dst))
        assert dst.read_text(encoding="utf-8") == "data"


class TestStepMoveFile:
    def test_move_file(self, tmp_path: Path) -> None:
        src = tmp_path / "old.txt"
        src.write_text("data", encoding="utf-8")
        dst = tmp_path / "new.txt"
        ctx = _make_context()
        step_move_file(ctx, str(src), str(dst))
        assert dst.read_text(encoding="utf-8") == "data"


class TestStepRenameFile:
    def test_rename_file(self, tmp_path: Path) -> None:
        f = tmp_path / "old.txt"
        f.write_text("data", encoding="utf-8")
        ctx = _make_context()
        step_rename_file(ctx, str(f), str(tmp_path / "new.txt"))
        assert (tmp_path / "new.txt").read_text(encoding="utf-8") == "data"


class TestStepFileExists:
    def test_file_exists(self, tmp_path: Path) -> None:
        f = tmp_path / "file.txt"
        f.touch()
        ctx = _make_context()
        step_file_exists(ctx, str(f))

    def test_file_not_exists_raises(self, tmp_path: Path) -> None:
        ctx = _make_context()
        with pytest.raises(AssertionError):
            step_file_exists(ctx, str(tmp_path / "missing.txt"))


class TestStepFileNotExists:
    def test_file_not_exists(self, tmp_path: Path) -> None:
        ctx = _make_context()
        step_file_not_exists(ctx, str(tmp_path / "missing.txt"))


class TestStepFilesSame:
    def test_files_same(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("same", encoding="utf-8")
        f2.write_text("same", encoding="utf-8")
        ctx = _make_context()
        step_files_same(ctx, str(f1), str(f2))


class TestStepGetFileSize:
    def test_get_file_size(self, tmp_path: Path) -> None:
        f = tmp_path / "data.bin"
        f.write_bytes(b"hello")
        ctx = _make_context()
        step_get_file_size(ctx, str(f), "size")
        assert ctx.steplib.io.variables["size"] == 5


class TestStepGetFileExtension:
    def test_get_file_extension(self, tmp_path: Path) -> None:
        f = tmp_path / "image.png"
        f.touch()
        ctx = _make_context()
        step_get_file_extension(ctx, str(f), "ext")
        assert ctx.steplib.io.variables["ext"] == ".png"


class TestStepCreateEmptyFile:
    def test_create_empty_file(self, tmp_path: Path) -> None:
        ctx = _make_context()
        path = tmp_path / "empty.txt"
        step_create_empty_file(ctx, str(path))
        assert path.exists()


# ---------------------------------------------------------------------------
# JSON steps
# ---------------------------------------------------------------------------


class TestStepLoadJson:
    def test_load_json(self, tmp_path: Path) -> None:
        f = tmp_path / "data.json"
        f.write_text('{"name": "Alice"}', encoding="utf-8")
        ctx = _make_context()
        step_load_json(ctx, str(f))
        assert ctx.steplib.io._last_json == {"name": "Alice"}


class TestStepSaveJson:
    def test_save_json(self, tmp_path: Path) -> None:
        ctx = _make_context()
        ctx.steplib.io._last_json = {"key": "value"}
        path = tmp_path / "out.json"
        step_save_json(ctx, str(path))
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded == {"key": "value"}


class TestStepJsonPathEquals:
    def test_path_equals(self) -> None:
        ctx = _make_context()
        ctx.steplib.io._last_json = {"user": {"name": "Alice"}}
        step_json_path_equals(ctx, "user.name", "Alice")


class TestStepStoreJsonPath:
    def test_store_path(self) -> None:
        ctx = _make_context()
        ctx.steplib.io._last_json = {"user": {"id": 42}}
        step_store_json_path(ctx, "user.id", "user_id")
        assert ctx.steplib.io.variables["user_id"] == 42


class TestStepUpdateJsonPath:
    def test_update_path(self) -> None:
        ctx = _make_context()
        ctx.steplib.io._last_json = {"user": {"name": "Alice"}}
        step_update_json_path(ctx, "user.name", "Bob")
        assert ctx.steplib.io._last_json["user"]["name"] == "Bob"


class TestStepCreateJsonPath:
    def test_create_path(self) -> None:
        ctx = _make_context()
        ctx.steplib.io._last_json = {"user": {}}
        step_create_json_path(ctx, "user.address.city", "Madrid")
        assert ctx.steplib.io._last_json["user"]["address"]["city"] == "Madrid"


class TestStepDeleteJsonPath:
    def test_delete_path(self) -> None:
        ctx = _make_context()
        ctx.steplib.io._last_json = {"user": {"name": "Alice", "password": "secret"}}
        step_delete_json_path(ctx, "user.password")
        assert "password" not in ctx.steplib.io._last_json["user"]


class TestStepJsonValid:
    def test_valid_json(self) -> None:
        ctx = _make_context()
        step_json_valid(ctx, '{"key": "value"}')

    def test_invalid_json(self) -> None:
        ctx = _make_context()
        with pytest.raises(AssertionError, match="Invalid JSON"):
            step_json_valid(ctx, "{not valid}")


class TestStepJsonMatchesSchema:
    def test_matches_schema(self, tmp_path: Path) -> None:
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(json.dumps(schema), encoding="utf-8")
        ctx = _make_context()
        ctx.steplib.io._last_json = {"name": "Alice"}
        step_json_matches_schema(ctx, str(schema_file))

    def test_does_not_match(self, tmp_path: Path) -> None:
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(json.dumps(schema), encoding="utf-8")
        ctx = _make_context()
        ctx.steplib.io._last_json = {"age": 30}
        with pytest.raises(AssertionError, match="does not match schema"):
            step_json_matches_schema(ctx, str(schema_file))


class TestStepLastJsonValid:
    def test_valid_last_json(self) -> None:
        ctx = _make_context()
        ctx.steplib.io._last_json = {"name": "Alice"}
        step_last_json_valid(ctx)

    def test_no_json_loaded(self) -> None:
        ctx = _make_context()
        with pytest.raises(RuntimeError, match="No JSON loaded"):
            step_last_json_valid(ctx)


class TestStepGetJsonPathType:
    def test_get_type(self) -> None:
        ctx = _make_context()
        ctx.steplib.io._last_json = {"user": {"age": 30}}
        step_get_json_path_type(ctx, "user.age", "type_var")
        assert ctx.steplib.io.variables["type_var"] == "int"


class TestStepDiffJson:
    def test_same_json(self) -> None:
        ctx = _make_context()
        step_diff_json(ctx, '{"a": 1}', '{"a": 1}')

    def test_different_json(self) -> None:
        ctx = _make_context()
        with pytest.raises(AssertionError, match="differ"):
            step_diff_json(ctx, '{"a": 1}', '{"a": 2}')


class TestStepMergeJson:
    def test_merge_origin(self) -> None:
        ctx = _make_context()
        ctx.steplib.io.variables["target"] = {"a": 1, "b": 2}
        ctx.steplib.io.variables["origin"] = {"b": 3, "c": 4}
        step_merge_json(ctx, "origin", "target", "origin")
        assert ctx.steplib.io.variables["target"] == {"a": 1, "b": 3, "c": 4}


# ---------------------------------------------------------------------------
# CSV steps
# ---------------------------------------------------------------------------


class TestStepCreateCsv:
    def test_create_csv(self, tmp_path: Path) -> None:
        ctx = _make_context()
        path = tmp_path / "out.csv"
        step_create_csv(ctx, str(path), '[{"a": 1, "b": 2}]')
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        assert lines[0] == "a,b"
        assert lines[1] == "1,2"


class TestStepCsvWriter:
    def test_write_and_close(self, tmp_path: Path) -> None:
        ctx = _make_context()
        path = tmp_path / "writer.csv"
        step_create_csv_writer(ctx, str(path), "name,age")
        step_write_csv_row(ctx, '{"name": "Alice", "age": 30}')
        step_close_csv_writer(ctx)
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        assert lines[0] == "name,age"
        assert lines[1] == "Alice,30"


class TestStepSaveCsv:
    def test_save_csv(self, tmp_path: Path) -> None:
        ctx = _make_context()
        path = tmp_path / "save.csv"
        step_create_csv_writer(ctx, str(path), "name,age")
        step_write_csv_row(ctx, '{"name": "Alice", "age": 30}')
        step_save_csv(ctx)
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        assert lines[0] == "name,age"
        assert lines[1] == "Alice,30"
        step_close_csv_writer(ctx)


class TestStepSetCsvHeaderRow:
    def test_set_header_row(self, tmp_path: Path) -> None:
        ctx = _make_context()
        path = tmp_path / "data.csv"
        path.write_text(
            "# comment line\nname,age\nAlice,30\nBob,25\n",
            encoding="utf-8",
        )
        step_set_csv_header_row(ctx, 2, str(path), "rows")
        rows = ctx.steplib.io.variables["rows"]
        assert len(rows) == 2
        assert rows[0] == {"name": "Alice", "age": "30"}
        assert rows[1] == {"name": "Bob", "age": "25"}


# ---------------------------------------------------------------------------
# Directory steps
# ---------------------------------------------------------------------------


class TestStepCreateDirectory:
    def test_create(self, tmp_path: Path) -> None:
        ctx = _make_context()
        path = tmp_path / "newdir"
        step_create_directory(ctx, str(path))
        assert path.is_dir()


class TestStepDirectoryExists:
    def test_exists(self, tmp_path: Path) -> None:
        ctx = _make_context()
        step_directory_exists(ctx, str(tmp_path))

    def test_not_exists(self, tmp_path: Path) -> None:
        ctx = _make_context()
        with pytest.raises(AssertionError, match="Directory does not exist"):
            step_directory_exists(ctx, str(tmp_path / "missing"))


class TestStepDirectoryNotExists:
    def test_not_exists(self, tmp_path: Path) -> None:
        ctx = _make_context()
        step_directory_not_exists(ctx, str(tmp_path / "missing"))

    def test_exists_raises(self, tmp_path: Path) -> None:
        ctx = _make_context()
        with pytest.raises(AssertionError, match="Directory exists"):
            step_directory_not_exists(ctx, str(tmp_path))


class TestStepListDirectory:
    def test_list(self, tmp_path: Path) -> None:
        ctx = _make_context()
        (tmp_path / "a.txt").write_text("x", encoding="utf-8")
        (tmp_path / "b.txt").write_text("x", encoding="utf-8")
        step_list_directory(ctx, str(tmp_path), "files")
        assert ctx.steplib.io.variables["files"] == ["a.txt", "b.txt"]


class TestStepDeleteDirectory:
    def test_delete(self, tmp_path: Path) -> None:
        ctx = _make_context()
        path = tmp_path / "todelete"
        path.mkdir()
        step_delete_directory(ctx, str(path))
        assert not path.exists()


class TestStepReadFileAsLines:
    def test_read_lines(self, tmp_path: Path) -> None:
        ctx = _make_context()
        path = tmp_path / "lines.txt"
        path.write_text("line1\nline2\nline3\n", encoding="utf-8")
        step_read_file_as_lines(ctx, str(path), "lines")
        assert ctx.steplib.io.variables["lines"] == ["line1", "line2", "line3"]


class TestBug13StepCreateCsvInvalidJson:
    """Regression tests for Bug 13: step_create_csv should raise
    AssertionError, not json.JSONDecodeError, when data is invalid JSON."""

    def test_invalid_json_raises_assertion_error(self, tmp_path: Path) -> None:
        ctx = _make_context()
        with pytest.raises(AssertionError, match="Invalid JSON data for CSV"):
            step_create_csv(ctx, str(tmp_path / "out.csv"), "{invalid json")


class TestBug13StepWriteCsvRowInvalidJson:
    """Regression tests for Bug 13: step_write_csv_row should raise
    AssertionError, not json.JSONDecodeError, when row is invalid JSON."""

    def test_invalid_json_raises_assertion_error(self, tmp_path: Path) -> None:
        ctx = _make_context()
        path = tmp_path / "out.csv"
        step_create_csv_writer(ctx, str(path), "name,age")
        with pytest.raises(AssertionError, match="Invalid JSON row for CSV"):
            step_write_csv_row(ctx, "{invalid json}")
        step_close_csv_writer(ctx)
