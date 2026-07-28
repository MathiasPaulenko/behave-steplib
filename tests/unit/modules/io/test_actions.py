"""Tests for io module actions (pure functions)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from steplib.modules.io.actions import (
    io_append_file,
    io_assert_directory_exists,
    io_assert_directory_not_exists,
    io_assert_file_exists,
    io_assert_file_not_exists,
    io_assert_files_same,
    io_assert_json_matches_schema,
    io_assert_json_path_equals,
    io_assert_json_valid,
    io_assert_last_json_valid,
    io_close_csv_writer,
    io_copy_file,
    io_create_csv,
    io_create_csv_writer,
    io_create_directory,
    io_create_empty_file,
    io_create_json_path,
    io_delete_directory,
    io_delete_file,
    io_delete_json_path,
    io_diff_json_objects,
    io_get_file_extension,
    io_get_file_size,
    io_get_json_path_type,
    io_list_directory,
    io_load_json,
    io_merge_json,
    io_move_file,
    io_read_file,
    io_read_file_as_lines,
    io_rename_file,
    io_save_csv,
    io_save_json,
    io_set_csv_header_row,
    io_store_json_path,
    io_update_json_path,
    io_write_csv_row,
    io_write_file,
)
from steplib.modules.io.context import IOContext

# ---------------------------------------------------------------------------
# File actions
# ---------------------------------------------------------------------------


class TestReadFile:
    def test_read_file(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello world", encoding="utf-8")
        ctx = IOContext()
        io_read_file(ctx, str(f), "content")
        assert ctx.variables["content"] == "hello world"

    def test_file_not_found(self) -> None:
        ctx = IOContext()
        with pytest.raises(FileNotFoundError, match="File not found"):
            io_read_file(ctx, "missing.txt", "content")


class TestWriteFile:
    def test_write_file(self, tmp_path: Path) -> None:
        ctx = IOContext()
        path = tmp_path / "out.txt"
        io_write_file(ctx, str(path), "hello")
        assert path.read_text(encoding="utf-8") == "hello"

    def test_write_creates_parent_dirs(self, tmp_path: Path) -> None:
        ctx = IOContext()
        path = tmp_path / "sub" / "dir" / "out.txt"
        io_write_file(ctx, str(path), "hello")
        assert path.read_text(encoding="utf-8") == "hello"


class TestAppendFile:
    def test_append_to_existing(self, tmp_path: Path) -> None:
        f = tmp_path / "log.txt"
        f.write_text("line1\n", encoding="utf-8")
        ctx = IOContext()
        io_append_file(ctx, str(f), "line2\n")
        assert f.read_text(encoding="utf-8") == "line1\nline2\n"

    def test_append_creates_file(self, tmp_path: Path) -> None:
        ctx = IOContext()
        path = tmp_path / "new.txt"
        io_append_file(ctx, str(path), "content")
        assert path.read_text(encoding="utf-8") == "content"


class TestDeleteFile:
    def test_delete_file(self, tmp_path: Path) -> None:
        f = tmp_path / "temp.txt"
        f.write_text("data", encoding="utf-8")
        ctx = IOContext()
        io_delete_file(ctx, str(f))
        assert not f.exists()

    def test_delete_nonexistent(self) -> None:
        ctx = IOContext()
        with pytest.raises(FileNotFoundError, match="File not found"):
            io_delete_file(ctx, "missing.txt")


class TestCopyFile:
    def test_copy_file(self, tmp_path: Path) -> None:
        src = tmp_path / "src.txt"
        src.write_text("data", encoding="utf-8")
        dst = tmp_path / "dst.txt"
        ctx = IOContext()
        io_copy_file(ctx, str(src), str(dst))
        assert dst.read_text(encoding="utf-8") == "data"

    def test_copy_nonexistent_source(self, tmp_path: Path) -> None:
        ctx = IOContext()
        with pytest.raises(FileNotFoundError, match="Source file not found"):
            io_copy_file(ctx, str(tmp_path / "missing.txt"), str(tmp_path / "dst.txt"))


class TestMoveFile:
    def test_move_file(self, tmp_path: Path) -> None:
        src = tmp_path / "old.txt"
        src.write_text("data", encoding="utf-8")
        dst = tmp_path / "new.txt"
        ctx = IOContext()
        io_move_file(ctx, str(src), str(dst))
        assert not src.exists()
        assert dst.read_text(encoding="utf-8") == "data"


class TestRenameFile:
    def test_rename_file(self, tmp_path: Path) -> None:
        f = tmp_path / "old.txt"
        f.write_text("data", encoding="utf-8")
        ctx = IOContext()
        io_rename_file(ctx, str(f), str(tmp_path / "new.txt"))
        assert not f.exists()
        assert (tmp_path / "new.txt").read_text(encoding="utf-8") == "data"


class TestAssertFileExists:
    def test_exists(self, tmp_path: Path) -> None:
        f = tmp_path / "file.txt"
        f.touch()
        ctx = IOContext()
        io_assert_file_exists(ctx, str(f))

    def test_not_exists_raises(self, tmp_path: Path) -> None:
        ctx = IOContext()
        with pytest.raises(AssertionError, match="File does not exist"):
            io_assert_file_exists(ctx, str(tmp_path / "missing.txt"))


class TestAssertFileNotExists:
    def test_not_exists(self, tmp_path: Path) -> None:
        ctx = IOContext()
        io_assert_file_not_exists(ctx, str(tmp_path / "missing.txt"))

    def test_exists_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "file.txt"
        f.touch()
        ctx = IOContext()
        with pytest.raises(AssertionError, match="File exists but should not"):
            io_assert_file_not_exists(ctx, str(f))


class TestAssertFilesSame:
    def test_same_content(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("same", encoding="utf-8")
        f2.write_text("same", encoding="utf-8")
        ctx = IOContext()
        io_assert_files_same(ctx, str(f1), str(f2))

    def test_different_content(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("same", encoding="utf-8")
        f2.write_text("different", encoding="utf-8")
        ctx = IOContext()
        with pytest.raises(AssertionError, match="are not the same"):
            io_assert_files_same(ctx, str(f1), str(f2))


class TestGetFileSize:
    def test_get_size(self, tmp_path: Path) -> None:
        f = tmp_path / "data.bin"
        f.write_bytes(b"hello")
        ctx = IOContext()
        io_get_file_size(ctx, str(f), "size")
        assert ctx.variables["size"] == 5


class TestGetFileExtension:
    def test_get_extension(self, tmp_path: Path) -> None:
        f = tmp_path / "image.png"
        f.touch()
        ctx = IOContext()
        io_get_file_extension(ctx, str(f), "ext")
        assert ctx.variables["ext"] == ".png"


class TestCreateEmptyFile:
    def test_create_empty(self, tmp_path: Path) -> None:
        ctx = IOContext()
        path = tmp_path / "empty.txt"
        io_create_empty_file(ctx, str(path))
        assert path.exists()
        assert path.stat().st_size == 0


# ---------------------------------------------------------------------------
# JSON actions
# ---------------------------------------------------------------------------


class TestLoadJson:
    def test_load_json(self, tmp_path: Path) -> None:
        f = tmp_path / "data.json"
        f.write_text('{"name": "Alice", "age": 30}', encoding="utf-8")
        ctx = IOContext()
        io_load_json(ctx, str(f))
        assert ctx._last_json == {"name": "Alice", "age": 30}

    def test_file_not_found(self) -> None:
        ctx = IOContext()
        with pytest.raises(FileNotFoundError, match="JSON file not found"):
            io_load_json(ctx, "missing.json")


class TestSaveJson:
    def test_save_json(self, tmp_path: Path) -> None:
        ctx = IOContext()
        ctx._last_json = {"key": "value"}
        path = tmp_path / "out.json"
        io_save_json(ctx, str(path))
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded == {"key": "value"}

    def test_no_json_loaded(self, tmp_path: Path) -> None:
        ctx = IOContext()
        with pytest.raises(RuntimeError, match="No JSON loaded"):
            io_save_json(ctx, str(tmp_path / "out.json"))


class TestAssertJsonPathEquals:
    def test_path_equals(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"user": {"name": "Alice"}}
        io_assert_json_path_equals(ctx, "user.name", "Alice")

    def test_path_not_equals(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"user": {"name": "Alice"}}
        with pytest.raises(AssertionError, match="expected"):
            io_assert_json_path_equals(ctx, "user.name", "Bob")

    def test_path_not_found(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"user": {"name": "Alice"}}
        with pytest.raises(AssertionError, match="not found"):
            io_assert_json_path_equals(ctx, "user.email", "test@test.com")

    def test_no_json_loaded(self) -> None:
        ctx = IOContext()
        with pytest.raises(RuntimeError, match="No JSON loaded"):
            io_assert_json_path_equals(ctx, "key", "value")


class TestStoreJsonPath:
    def test_store_path(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"user": {"id": 42}}
        io_store_json_path(ctx, "user.id", "user_id")
        assert ctx.variables["user_id"] == 42

    def test_list_index(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"items": ["a", "b", "c"]}
        io_store_json_path(ctx, "items.1", "second")
        assert ctx.variables["second"] == "b"


class TestUpdateJsonPath:
    def test_update_path(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"user": {"name": "Alice"}}
        io_update_json_path(ctx, "user.name", "Bob")
        assert ctx._last_json["user"]["name"] == "Bob"

    def test_update_list_index(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"items": ["a", "b", "c"]}
        io_update_json_path(ctx, "items.1", "B")
        assert ctx._last_json["items"][1] == "B"

    def test_update_list_index_out_of_range(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"items": ["a", "b"]}
        with pytest.raises(KeyError, match="Index 5 out of range"):
            io_update_json_path(ctx, "items.5", "x")

    def test_update_list_non_integer_index(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"items": ["a", "b"]}
        with pytest.raises(KeyError, match="Cannot index list with non-integer"):
            io_update_json_path(ctx, "items.foo", "x")

    def test_update_missing_intermediate_key(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"user": {"name": "Alice"}}
        with pytest.raises(KeyError, match="Key 'profile' not found"):
            io_update_json_path(ctx, "user.profile.age", 30)

    def test_update_no_json_loaded(self) -> None:
        ctx = IOContext()
        with pytest.raises(RuntimeError, match="No JSON loaded"):
            io_update_json_path(ctx, "key", "value")


class TestCreateJsonPath:
    def test_create_nested_path(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"user": {}}
        io_create_json_path(ctx, "user.address.city", "Madrid")
        assert ctx._last_json["user"]["address"]["city"] == "Madrid"

    def test_create_overwrites_missing_intermediate(self) -> None:
        ctx = IOContext()
        ctx._last_json = {}
        io_create_json_path(ctx, "a.b.c", "value")
        assert ctx._last_json == {"a": {"b": {"c": "value"}}}

    def test_create_conflict_with_non_dict_value(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"user": "scalar"}
        with pytest.raises(KeyError, match="exists with non-dict value"):
            io_create_json_path(ctx, "user.name", "Alice")

    def test_create_conflict_with_nested_non_dict_value(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"user": {"name": "Alice"}}
        with pytest.raises(KeyError, match="exists with non-dict value"):
            io_create_json_path(ctx, "user.name.first", "Alice")

    def test_create_no_json_loaded(self) -> None:
        ctx = IOContext()
        with pytest.raises(RuntimeError, match="No JSON loaded"):
            io_create_json_path(ctx, "key", "value")

    def test_create_on_non_dict_json(self) -> None:
        ctx = IOContext()
        ctx._last_json = [1, 2, 3]
        with pytest.raises(RuntimeError, match="not a dict"):
            io_create_json_path(ctx, "key", "value")


class TestDeleteJsonPath:
    def test_delete_path(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"user": {"name": "Alice", "password": "secret"}}
        io_delete_json_path(ctx, "user.password")
        assert "password" not in ctx._last_json["user"]

    def test_delete_list_index(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"items": ["a", "b", "c"]}
        io_delete_json_path(ctx, "items.1")
        assert ctx._last_json["items"] == ["a", "c"]

    def test_delete_list_index_out_of_range(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"items": ["a", "b"]}
        with pytest.raises(KeyError, match="Index 5 out of range"):
            io_delete_json_path(ctx, "items.5")

    def test_delete_list_non_integer_index(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"items": ["a", "b"]}
        with pytest.raises(KeyError, match="Cannot index list with non-integer"):
            io_delete_json_path(ctx, "items.foo")

    def test_delete_missing_key(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"user": {"name": "Alice"}}
        with pytest.raises(KeyError, match="Key 'age' not found"):
            io_delete_json_path(ctx, "user.age")

    def test_delete_no_json_loaded(self) -> None:
        ctx = IOContext()
        with pytest.raises(RuntimeError, match="No JSON loaded"):
            io_delete_json_path(ctx, "key")


class TestAssertJsonValid:
    def test_valid_json(self) -> None:
        ctx = IOContext()
        io_assert_json_valid(ctx, '{"key": "value"}')

    def test_invalid_json(self) -> None:
        ctx = IOContext()
        with pytest.raises(AssertionError, match="Invalid JSON"):
            io_assert_json_valid(ctx, "{not valid}")


class TestAssertJsonMatchesSchema:
    def test_matches_schema(self, tmp_path: Path) -> None:
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(json.dumps(schema), encoding="utf-8")
        ctx = IOContext()
        ctx._last_json = {"name": "Alice"}
        io_assert_json_matches_schema(ctx, str(schema_file))

    def test_does_not_match_schema(self, tmp_path: Path) -> None:
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(json.dumps(schema), encoding="utf-8")
        ctx = IOContext()
        ctx._last_json = {"age": 30}
        with pytest.raises(AssertionError, match="does not match schema"):
            io_assert_json_matches_schema(ctx, str(schema_file))

    def test_no_json_loaded(self, tmp_path: Path) -> None:
        schema_file = tmp_path / "schema.json"
        schema_file.write_text("{}", encoding="utf-8")
        ctx = IOContext()
        with pytest.raises(RuntimeError, match="No JSON loaded"):
            io_assert_json_matches_schema(ctx, str(schema_file))

    def test_schema_file_not_found(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"a": 1}
        with pytest.raises(FileNotFoundError, match="Schema file not found"):
            io_assert_json_matches_schema(ctx, "missing.json")

    def test_missing_dependency(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """If jsonschema is not installed, MissingDependencyError is raised (not RuntimeError)."""
        import builtins

        real_import = builtins.__import__

        def _block_jsonschema(name: str, *args: object, **kwargs: object) -> object:
            if name == "jsonschema":
                raise ImportError("No module named 'jsonschema'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _block_jsonschema)
        schema_file = tmp_path / "schema.json"
        schema_file.write_text("{}", encoding="utf-8")
        ctx = IOContext()
        ctx._last_json = {"a": 1}

        from steplib.core.exceptions import MissingDependencyError

        with pytest.raises(MissingDependencyError):
            io_assert_json_matches_schema(ctx, str(schema_file))


class TestAssertLastJsonValid:
    def test_valid_last_json(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"name": "Alice", "age": 30}
        io_assert_last_json_valid(ctx)

    def test_no_json_loaded(self) -> None:
        ctx = IOContext()
        with pytest.raises(RuntimeError, match="No JSON loaded"):
            io_assert_last_json_valid(ctx)


class TestGetJsonPathType:
    def test_get_type(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"user": {"age": 30}}
        io_get_json_path_type(ctx, "user.age", "type_var")
        assert ctx.variables["type_var"] == "int"


class TestDiffJsonObjects:
    def test_no_diff(self) -> None:
        ctx = IOContext()
        result = io_diff_json_objects(ctx, '{"a": 1}', '{"a": 1}')
        assert result["only_in_first"] == []
        assert result["only_in_second"] == []
        assert result["different"] == []

    def test_with_diff(self) -> None:
        ctx = IOContext()
        result = io_diff_json_objects(
            ctx, '{"a": 1, "b": 2}', '{"a": 1, "c": 3}'
        )
        assert result["only_in_first"] == ["b"]
        assert result["only_in_second"] == ["c"]


class TestMergeJson:
    def test_merge_origin_priority(self) -> None:
        ctx = IOContext()
        ctx.variables["target"] = {"a": 1, "b": 2}
        ctx.variables["origin"] = {"b": 3, "c": 4}
        io_merge_json(ctx, "target", "origin", "origin")
        assert ctx.variables["target"] == {"a": 1, "b": 3, "c": 4}

    def test_merge_target_priority(self) -> None:
        ctx = IOContext()
        ctx.variables["target"] = {"a": 1, "b": 2}
        ctx.variables["origin"] = {"b": 3, "c": 4}
        io_merge_json(ctx, "target", "origin", "target")
        assert ctx.variables["target"] == {"a": 1, "b": 2, "c": 4}


# ---------------------------------------------------------------------------
# CSV actions
# ---------------------------------------------------------------------------


class TestCreateCsv:
    def test_create_csv(self, tmp_path: Path) -> None:
        ctx = IOContext()
        path = tmp_path / "out.csv"
        io_create_csv(ctx, str(path), [{"a": 1, "b": 2}, {"a": 3, "b": 4}])
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        assert lines[0] == "a,b"
        assert lines[1] == "1,2"
        assert lines[2] == "3,4"

    def test_empty_data_raises(self, tmp_path: Path) -> None:
        ctx = IOContext()
        with pytest.raises(ValueError, match="empty data"):
            io_create_csv(ctx, str(tmp_path / "out.csv"), [])


class TestCsvWriter:
    def test_write_and_close(self, tmp_path: Path) -> None:
        ctx = IOContext()
        path = tmp_path / "writer.csv"
        io_create_csv_writer(ctx, str(path), ["name", "age"])
        io_write_csv_row(ctx, {"name": "Alice", "age": 30})
        io_write_csv_row(ctx, {"name": "Bob", "age": 25})
        io_close_csv_writer(ctx)
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        assert lines[0] == "name,age"
        assert lines[1] == "Alice,30"
        assert lines[2] == "Bob,25"

    def test_close_without_writer(self) -> None:
        ctx = IOContext()
        with pytest.raises(RuntimeError, match="No CSV writer is active"):
            io_close_csv_writer(ctx)

    def test_write_row_without_writer(self) -> None:
        ctx = IOContext()
        with pytest.raises(RuntimeError, match="No CSV writer is active"):
            io_write_csv_row(ctx, {"a": 1})


class TestSaveCsv:
    def test_save_csv(self, tmp_path: Path) -> None:
        ctx = IOContext()
        path = tmp_path / "save.csv"
        io_create_csv_writer(ctx, str(path), ["name", "age"])
        io_write_csv_row(ctx, {"name": "Alice", "age": 30})
        io_save_csv(ctx)
        # File should be flushed and readable while writer is still open
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        assert lines[0] == "name,age"
        assert lines[1] == "Alice,30"
        io_close_csv_writer(ctx)

    def test_save_without_writer(self) -> None:
        ctx = IOContext()
        with pytest.raises(RuntimeError, match="No CSV writer is active"):
            io_save_csv(ctx)


class TestSetCsvHeaderRow:
    def test_set_header_row(self, tmp_path: Path) -> None:
        ctx = IOContext()
        path = tmp_path / "data.csv"
        path.write_text(
            "# comment line\nname,age\nAlice,30\nBob,25\n",
            encoding="utf-8",
        )
        io_set_csv_header_row(ctx, str(path), 2, "rows")
        rows = ctx.variables["rows"]
        assert len(rows) == 2
        assert rows[0] == {"name": "Alice", "age": "30"}
        assert rows[1] == {"name": "Bob", "age": "25"}

    def test_invalid_row(self, tmp_path: Path) -> None:
        ctx = IOContext()
        path = tmp_path / "data.csv"
        path.write_text("name,age\nAlice,30\n", encoding="utf-8")
        with pytest.raises(ValueError, match="must be 1-based"):
            io_set_csv_header_row(ctx, str(path), 0, "rows")

    def test_file_not_found(self) -> None:
        ctx = IOContext()
        with pytest.raises(FileNotFoundError, match="CSV file not found"):
            io_set_csv_header_row(ctx, "missing.csv", 1, "rows")


# ---------------------------------------------------------------------------
# Directory actions
# ---------------------------------------------------------------------------


class TestCreateDirectory:
    def test_create_directory(self, tmp_path: Path) -> None:
        path = tmp_path / "newdir"
        io_create_directory(str(path))
        assert path.is_dir()

    def test_create_nested(self, tmp_path: Path) -> None:
        path = tmp_path / "a" / "b" / "c"
        io_create_directory(str(path))
        assert path.is_dir()

    def test_create_existing_no_error(self, tmp_path: Path) -> None:
        path = tmp_path / "existing"
        path.mkdir()
        io_create_directory(str(path))


class TestAssertDirectoryExists:
    def test_exists(self, tmp_path: Path) -> None:
        io_assert_directory_exists(str(tmp_path))

    def test_not_exists(self, tmp_path: Path) -> None:
        with pytest.raises(AssertionError, match="Directory does not exist"):
            io_assert_directory_exists(str(tmp_path / "missing"))


class TestAssertDirectoryNotExists:
    def test_not_exists(self, tmp_path: Path) -> None:
        io_assert_directory_not_exists(str(tmp_path / "missing"))

    def test_exists_raises(self, tmp_path: Path) -> None:
        with pytest.raises(AssertionError, match="Directory exists"):
            io_assert_directory_not_exists(str(tmp_path))


class TestListDirectory:
    def test_list(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("x", encoding="utf-8")
        (tmp_path / "b.txt").write_text("x", encoding="utf-8")
        ctx = IOContext()
        io_list_directory(ctx, str(tmp_path), "files")
        assert ctx.variables["files"] == ["a.txt", "b.txt"]

    def test_not_found(self) -> None:
        ctx = IOContext()
        with pytest.raises(FileNotFoundError, match="Directory not found"):
            io_list_directory(ctx, "missing_dir", "files")


class TestDeleteDirectory:
    def test_delete(self, tmp_path: Path) -> None:
        path = tmp_path / "todelete"
        path.mkdir()
        (path / "file.txt").write_text("x", encoding="utf-8")
        io_delete_directory(str(path))
        assert not path.exists()

    def test_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="Directory not found"):
            io_delete_directory(str(tmp_path / "missing"))


class TestReadFileAsLines:
    def test_read_lines(self, tmp_path: Path) -> None:
        path = tmp_path / "lines.txt"
        path.write_text("line1\nline2\nline3\n", encoding="utf-8")
        ctx = IOContext()
        io_read_file_as_lines(ctx, str(path), "lines")
        assert ctx.variables["lines"] == ["line1", "line2", "line3"]

    def test_file_not_found(self) -> None:
        ctx = IOContext()
        with pytest.raises(FileNotFoundError, match="File not found"):
            io_read_file_as_lines(ctx, "missing.txt", "lines")


class TestBug9JsonPathEqualsTypeComparison:
    """Regression tests for Bug 9: io_assert_json_path_equals should compare
    values as strings, not directly, to avoid false failures when JSON values
    are non-string types (int, bool, float)."""

    def test_int_value_matches_string(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"count": 42}
        io_assert_json_path_equals(ctx, "count", "42")

    def test_bool_value_matches_string(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"active": True}
        io_assert_json_path_equals(ctx, "active", "true")

    def test_bool_false_matches_string(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"active": False}
        io_assert_json_path_equals(ctx, "active", "false")

    def test_null_matches_string(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"data": None}
        io_assert_json_path_equals(ctx, "data", "null")

    def test_float_value_matches_string(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"price": 3.14}
        io_assert_json_path_equals(ctx, "price", "3.14")

    def test_nested_int_value_matches_string(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"user": {"id": 100}}
        io_assert_json_path_equals(ctx, "user.id", "100")

    def test_int_value_does_not_match_wrong_string(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"count": 42}
        with pytest.raises(AssertionError, match="expected '99'"):
            io_assert_json_path_equals(ctx, "count", "99")


class TestBug11SchemaFileInvalidJson:
    """Regression tests for Bug 11: io_assert_json_matches_schema should raise
    AssertionError, not json.JSONDecodeError, when the schema file contains
    invalid JSON."""

    def test_invalid_schema_file_raises_assertion_error(self, tmp_path: Path) -> None:
        ctx = IOContext()
        ctx._last_json = {"key": "value"}
        schema_file = tmp_path / "bad_schema.json"
        schema_file.write_text("{invalid json", encoding="utf-8")
        with pytest.raises(AssertionError, match="Schema file is not valid JSON"):
            io_assert_json_matches_schema(ctx, str(schema_file))


class TestBug36JsonPathEqualsNormalization:
    """Regression tests for Bug 36: io_assert_json_path_equals should
    normalize the expected value using _normalize_value so that non-string
    inputs (bool, None) are compared using JSON-style lowercase
    representation instead of Python's str() which produces "True"/"False"/"None".
    """

    def test_bool_true_expected_as_bool(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"active": True}
        io_assert_json_path_equals(ctx, "active", True)  # type: ignore[arg-type]

    def test_bool_false_expected_as_bool(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"active": False}
        io_assert_json_path_equals(ctx, "active", False)  # type: ignore[arg-type]

    def test_none_expected_as_none(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"data": None}
        io_assert_json_path_equals(ctx, "data", None)  # type: ignore[arg-type]

    def test_bool_true_does_not_match_false(self) -> None:
        ctx = IOContext()
        ctx._last_json = {"active": True}
        with pytest.raises(AssertionError, match="expected"):
            io_assert_json_path_equals(ctx, "active", False)  # type: ignore[arg-type]
