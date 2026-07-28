"""Pure action functions for the io module (files, JSON, CSV)."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from steplib.core.exceptions import MissingDependencyError
from steplib.modules.io.context import IOContext


def _normalize_value(value: Any) -> str:
    """Normalize a value to its string representation for comparison.

    Python's ``str(True)`` returns ``"True"``, but JSON uses lowercase
    ``"true"``.  This helper ensures booleans and ``None`` are compared
    using their JSON representation.
    """
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    return str(value)


# ---------------------------------------------------------------------------
# File actions
# ---------------------------------------------------------------------------


def io_read_file(io_ctx: IOContext, path: str, variable: str) -> None:
    """Read a file and store its content in a variable.

    Args:
        io_ctx: The io context.
        path: Path to the file to read.
        variable: Variable name to store the file content.

    Raises:
        FileNotFoundError: If the file does not exist.

    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    io_ctx.variables[variable] = file_path.read_text(encoding="utf-8")


def io_write_file(io_ctx: IOContext, path: str, content: str) -> None:
    """Write content to a file, overwriting if it exists.

    Args:
        io_ctx: The io context.
        path: Path to the file to write.
        content: Content to write.

    """
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


def io_append_file(io_ctx: IOContext, path: str, content: str) -> None:
    """Append content to a file, creating it if it does not exist.

    Args:
        io_ctx: The io context.
        path: Path to the file to append to.
        content: Content to append.

    """
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("a", encoding="utf-8") as f:
        f.write(content)


def io_delete_file(io_ctx: IOContext, path: str) -> None:
    """Delete a file.

    Args:
        io_ctx: The io context.
        path: Path to the file to delete.

    Raises:
        FileNotFoundError: If the file does not exist.

    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    file_path.unlink()


def io_copy_file(io_ctx: IOContext, source: str, destination: str) -> None:
    """Copy a file from source to destination.

    Args:
        io_ctx: The io context.
        source: Path to the source file.
        destination: Path to the destination.

    Raises:
        FileNotFoundError: If the source file does not exist.

    """
    src = Path(source)
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
    dst = Path(destination)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())


def io_move_file(io_ctx: IOContext, source: str, destination: str) -> None:
    """Move a file from source to destination.

    Args:
        io_ctx: The io context.
        source: Path to the source file.
        destination: Path to the destination.

    Raises:
        FileNotFoundError: If the source file does not exist.

    """
    src = Path(source)
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
    dst = Path(destination)
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dst)


def io_rename_file(io_ctx: IOContext, path: str, new_path: str) -> None:
    """Rename a file.

    Args:
        io_ctx: The io context.
        path: Current path of the file.
        new_path: New path for the file.

    Raises:
        FileNotFoundError: If the file does not exist.

    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    new = Path(new_path)
    new.parent.mkdir(parents=True, exist_ok=True)
    file_path.rename(new)


def io_assert_file_exists(io_ctx: IOContext, path: str) -> None:
    """Assert that a file exists.

    Args:
        io_ctx: The io context.
        path: Path to check.

    Raises:
        AssertionError: If the file does not exist.

    """
    if not Path(path).exists():
        raise AssertionError(f"File does not exist: {path}")


def io_assert_file_not_exists(io_ctx: IOContext, path: str) -> None:
    """Assert that a file does not exist.

    Args:
        io_ctx: The io context.
        path: Path to check.

    Raises:
        AssertionError: If the file exists.

    """
    if Path(path).exists():
        raise AssertionError(f"File exists but should not: {path}")


def io_assert_files_same(io_ctx: IOContext, path1: str, path2: str) -> None:
    """Assert that two files have the same content.

    Args:
        io_ctx: The io context.
        path1: First file path.
        path2: Second file path.

    Raises:
        AssertionError: If files differ or do not exist.

    """
    p1, p2 = Path(path1), Path(path2)
    if not p1.exists():
        raise AssertionError(f"File does not exist: {path1}")
    if not p2.exists():
        raise AssertionError(f"File does not exist: {path2}")
    if p1.read_bytes() != p2.read_bytes():
        raise AssertionError(f"Files '{path1}' and '{path2}' are not the same.")


def io_get_file_size(io_ctx: IOContext, path: str, variable: str) -> None:
    """Get the size of a file in bytes and store it in a variable.

    Args:
        io_ctx: The io context.
        path: Path to the file.
        variable: Variable name to store the file size.

    Raises:
        FileNotFoundError: If the file does not exist.

    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    io_ctx.variables[variable] = file_path.stat().st_size


def io_get_file_extension(io_ctx: IOContext, path: str, variable: str) -> None:
    """Get the extension of a file and store it in a variable.

    Args:
        io_ctx: The io context.
        path: Path to the file.
        variable: Variable name to store the file extension.

    Raises:
        FileNotFoundError: If the file does not exist.

    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    io_ctx.variables[variable] = file_path.suffix


def io_create_empty_file(io_ctx: IOContext, path: str) -> None:
    """Create an empty file at the given path.

    Args:
        io_ctx: The io context.
        path: Path where the empty file should be created.

    """
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.touch()


# ---------------------------------------------------------------------------
# JSON actions
# ---------------------------------------------------------------------------


def io_load_json(io_ctx: IOContext, path: str) -> None:
    """Load a JSON file and store it as ``_last_json``.

    Args:
        io_ctx: The io context.
        path: Path to the JSON file.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.

    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    io_ctx._last_json = json.loads(file_path.read_text(encoding="utf-8"))


def io_save_json(io_ctx: IOContext, path: str) -> None:
    """Save ``_last_json`` to a file.

    Args:
        io_ctx: The io context.
        path: Path to write the JSON file.

    Raises:
        RuntimeError: If there is no loaded JSON to save.

    """
    if io_ctx._last_json is None:
        raise RuntimeError("No JSON loaded. Use 'I load the JSON file' first.")
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(io_ctx._last_json, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _navigate_key_path(data: Any, key_path: str) -> Any:
    """Navigate a dot-path through nested dicts/lists.

    Supports integer indices for lists (e.g. ``items.0.name``).
    """
    current: Any = data
    for part in key_path.split("."):
        if isinstance(current, list):
            try:
                idx = int(part)
            except ValueError as exc:
                raise KeyError(
                    f"Cannot index list with non-integer '{part}' in path '{key_path}'."
                ) from exc
            if idx < 0 or idx >= len(current):
                raise KeyError(
                    f"Index {idx} out of range for list of length {len(current)}."
                )
            current = current[idx]
        elif isinstance(current, dict):
            if part not in current:
                raise KeyError(f"Key '{part}' not found in path '{key_path}'.")
            current = current[part]
        else:
            raise KeyError(
                f"Cannot navigate into non-container value at '{part}' in path '{key_path}'."
            )
    return current


def io_assert_json_path_equals(io_ctx: IOContext, key_path: str, value: str) -> None:
    """Assert that a JSON key path equals a value.

    Args:
        io_ctx: The io context.
        key_path: Dot-separated path (e.g. ``user.name``).
        value: Expected value (compared after stripping quotes).

    Raises:
        AssertionError: If the path does not exist or value differs.
        RuntimeError: If no JSON is loaded.

    """
    if io_ctx._last_json is None:
        raise RuntimeError("No JSON loaded.")
    try:
        actual = _navigate_key_path(io_ctx._last_json, key_path)
    except KeyError as exc:
        raise AssertionError(str(exc)) from exc
    if _normalize_value(actual) != _normalize_value(value):
        raise AssertionError(
            f"JSON path '{key_path}': expected '{value}', got '{actual}'."
        )


def io_store_json_path(io_ctx: IOContext, key_path: str, variable: str) -> None:
    """Store a JSON key path value into a variable.

    Args:
        io_ctx: The io context.
        key_path: Dot-separated path.
        variable: Variable name to store the value.

    Raises:
        KeyError: If the path does not exist.
        RuntimeError: If no JSON is loaded.

    """
    if io_ctx._last_json is None:
        raise RuntimeError("No JSON loaded.")
    io_ctx.variables[variable] = _navigate_key_path(io_ctx._last_json, key_path)


def io_update_json_path(io_ctx: IOContext, key_path: str, value: str) -> None:
    """Update a JSON key path to a new value in-place.

    Args:
        io_ctx: The io context.
        key_path: Dot-separated path.
        value: New value.

    Raises:
        KeyError: If the path does not exist.
        RuntimeError: If no JSON is loaded.

    """
    if io_ctx._last_json is None:
        raise RuntimeError("No JSON loaded.")
    parts = key_path.split(".")
    current: Any = io_ctx._last_json
    for part in parts[:-1]:
        if isinstance(current, list):
            try:
                idx = int(part)
            except ValueError as exc:
                raise KeyError(
                    f"Cannot index list with non-integer '{part}' in path '{key_path}'."
                ) from exc
            if idx < 0 or idx >= len(current):
                raise KeyError(
                    f"Index {idx} out of range for list of length {len(current)}."
                )
            current = current[idx]
        elif isinstance(current, dict):
            if part not in current:
                raise KeyError(f"Key '{part}' not found in path '{key_path}'.")
            current = current[part]
        else:
            raise KeyError(f"Cannot navigate into non-container at '{part}'.")
    last = parts[-1]
    if isinstance(current, list):
        try:
            idx = int(last)
        except ValueError as exc:
            raise KeyError(
                f"Cannot index list with non-integer '{last}' in path '{key_path}'."
            ) from exc
        if idx < 0 or idx >= len(current):
            raise KeyError(
                f"Index {idx} out of range for list of length {len(current)}."
            )
        current[idx] = value
    elif isinstance(current, dict):
        current[last] = value
    else:
        raise KeyError(f"Cannot set value on non-container at '{last}'.")


def io_create_json_path(io_ctx: IOContext, key_path: str, value: str) -> None:
    """Create a nested JSON key path with a value.

    Args:
        io_ctx: The io context.
        key_path: Dot-separated path.
        value: Value to set at the path.

    Raises:
        RuntimeError: If no JSON is loaded.
        KeyError: If a parent key conflicts with a non-dict value.

    """
    if io_ctx._last_json is None:
        raise RuntimeError("No JSON loaded.")
    if not isinstance(io_ctx._last_json, dict):
        raise RuntimeError("Loaded JSON is not a dict; cannot create key path.")
    parts = key_path.split(".")
    current: dict[str, Any] = io_ctx._last_json
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        elif not isinstance(current[part], dict):
            raise KeyError(
                f"Key '{part}' exists with non-dict value in path '{key_path}'."
            )
        current = current[part]
    current[parts[-1]] = value


def io_delete_json_path(io_ctx: IOContext, key_path: str) -> None:
    """Delete a JSON key path.

    Args:
        io_ctx: The io context.
        key_path: Dot-separated path.

    Raises:
        KeyError: If the path does not exist.
        RuntimeError: If no JSON is loaded.

    """
    if io_ctx._last_json is None:
        raise RuntimeError("No JSON loaded.")
    parts = key_path.split(".")
    current: Any = io_ctx._last_json
    for part in parts[:-1]:
        if isinstance(current, list):
            try:
                idx = int(part)
            except ValueError as exc:
                raise KeyError(
                    f"Cannot index list with non-integer '{part}' in path '{key_path}'."
                ) from exc
            if idx < 0 or idx >= len(current):
                raise KeyError(
                    f"Index {idx} out of range for list of length {len(current)}."
                )
            current = current[idx]
        elif isinstance(current, dict):
            if part not in current:
                raise KeyError(f"Key '{part}' not found in path '{key_path}'.")
            current = current[part]
        else:
            raise KeyError(f"Cannot navigate into non-container at '{part}'.")
    last = parts[-1]
    if isinstance(current, list):
        try:
            idx = int(last)
        except ValueError as exc:
            raise KeyError(
                f"Cannot index list with non-integer '{last}' in path '{key_path}'."
            ) from exc
        if idx < 0 or idx >= len(current):
            raise KeyError(
                f"Index {idx} out of range for list of length {len(current)}."
            )
        del current[idx]
    elif isinstance(current, dict):
        if last not in current:
            raise KeyError(f"Key '{last}' not found in path '{key_path}'.")
        del current[last]
    else:
        raise KeyError(f"Cannot delete from non-container at '{last}'.")


def io_assert_json_valid(io_ctx: IOContext, json_string: str) -> None:
    """Assert that a string is valid JSON.

    Args:
        io_ctx: The io context.
        json_string: The JSON string to validate.

    Raises:
        AssertionError: If the string is not valid JSON.

    """
    try:
        json.loads(json_string)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Invalid JSON: {exc}") from exc


def io_assert_json_matches_schema(io_ctx: IOContext, schema_path: str) -> None:
    """Assert that ``_last_json`` matches a JSON Schema file.

    Args:
        io_ctx: The io context.
        schema_path: Path to the JSON Schema file.

    Raises:
        FileNotFoundError: If the schema file does not exist.
        RuntimeError: If no JSON is loaded.
        MissingDependencyError: If jsonschema is not installed.
        AssertionError: If validation fails.

    """
    if io_ctx._last_json is None:
        raise RuntimeError("No JSON loaded.")
    p = Path(schema_path)
    if not p.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    try:
        schema = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Schema file is not valid JSON: {exc}") from exc
    try:
        import jsonschema
    except ImportError as exc:
        raise MissingDependencyError("io", "jsonschema") from exc
    try:
        jsonschema.validate(instance=io_ctx._last_json, schema=schema)
    except jsonschema.ValidationError as exc:
        raise AssertionError(f"JSON does not match schema: {exc.message}") from exc


def io_assert_last_json_valid(io_ctx: IOContext) -> None:
    """Assert that the last loaded JSON is valid by re-serializing it.

    Args:
        io_ctx: The io context.

    Raises:
        RuntimeError: If no JSON is loaded.
        AssertionError: If the JSON cannot be re-serialized.

    """
    if io_ctx._last_json is None:
        raise RuntimeError("No JSON loaded.")
    try:
        json.loads(json.dumps(io_ctx._last_json))
    except (TypeError, ValueError) as exc:
        raise AssertionError(f"Last JSON is not valid: {exc}") from exc


def io_get_json_path_type(io_ctx: IOContext, key_path: str, variable: str) -> None:
    """Get the type name of a JSON key path value and store it in a variable.

    Args:
        io_ctx: The io context.
        key_path: Dot-separated path.
        variable: Variable name to store the type name.

    Raises:
        KeyError: If the path does not exist.
        RuntimeError: If no JSON is loaded.

    """
    if io_ctx._last_json is None:
        raise RuntimeError("No JSON loaded.")
    value = _navigate_key_path(io_ctx._last_json, key_path)
    io_ctx.variables[variable] = type(value).__name__


def io_diff_json_objects(io_ctx: IOContext, json1: str, json2: str) -> dict[str, list[str]]:
    """Diff two JSON strings and return the differences.

    Args:
        io_ctx: The io context.
        json1: First JSON string.
        json2: Second JSON string.

    Returns:
        A dict with ``only_in_first``, ``only_in_second``, and ``different`` lists.

    Raises:
        AssertionError: If either string is not valid JSON.

    """
    try:
        d1 = json.loads(json1)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"First argument is not valid JSON: {exc}") from exc
    try:
        d2 = json.loads(json2)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Second argument is not valid JSON: {exc}") from exc
    if not isinstance(d1, dict) or not isinstance(d2, dict):
        if d1 != d2:
            raise AssertionError("JSON values differ.")
        return {"only_in_first": [], "only_in_second": [], "different": []}
    keys1, keys2 = set(d1), set(d2)
    only_in_first = sorted(keys1 - keys2)
    only_in_second = sorted(keys2 - keys1)
    different = sorted(k for k in keys1 & keys2 if d1[k] != d2[k])
    return {
        "only_in_first": only_in_first,
        "only_in_second": only_in_second,
        "different": different,
    }


def io_merge_json(
    io_ctx: IOContext, target_name: str, origin_name: str, priority: str
) -> None:
    """Merge two JSON objects stored as variables.

    Args:
        io_ctx: The io context.
        target_name: Variable name of the target dict.
        origin_name: Variable name of the origin dict.
        priority: ``"origin"`` or ``"target"`` — which dict wins on conflicts.

    Raises:
        KeyError: If either variable does not exist.
        TypeError: If either variable is not a dict.
        ValueError: If priority is not ``"origin"`` or ``"target"``.

    """
    if target_name not in io_ctx.variables:
        raise KeyError(f"Variable '{target_name}' does not exist.")
    if origin_name not in io_ctx.variables:
        raise KeyError(f"Variable '{origin_name}' does not exist.")
    target = io_ctx.variables[target_name]
    origin = io_ctx.variables[origin_name]
    if not isinstance(target, dict) or not isinstance(origin, dict):
        raise TypeError("Both JSON objects must be dicts to merge.")
    if priority == "origin":
        merged = {**target, **origin}
    elif priority == "target":
        merged = {**origin, **target}
    else:
        raise ValueError(f"Priority must be 'origin' or 'target', got '{priority}'.")
    io_ctx.variables[target_name] = merged


# ---------------------------------------------------------------------------
# CSV actions
# ---------------------------------------------------------------------------


def io_create_csv(
    io_ctx: IOContext,
    path: str,
    data: list[dict[str, Any]],
) -> None:
    """Create a CSV file from a list of dicts.

    Args:
        io_ctx: The io context.
        path: Path to the CSV file.
        data: List of row dicts. Fieldnames derived from the first row.

    Raises:
        ValueError: If data is empty.

    """
    if not data:
        raise ValueError("Cannot create CSV from empty data.")
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(data[0].keys())
    with file_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def io_create_csv_writer(
    io_ctx: IOContext,
    path: str,
    fieldnames: list[str],
) -> None:
    """Create a CSV DictWriter and store it in the context.

    Args:
        io_ctx: The io context.
        path: Path to the CSV file.
        fieldnames: List of column names.

    """
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    f = file_path.open("w", encoding="utf-8", newline="")
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    io_ctx._csv_writer = writer
    io_ctx._csv_file = f


def io_close_csv_writer(io_ctx: IOContext) -> None:
    """Close the active CSV writer and its file handle.

    Args:
        io_ctx: The io context.

    Raises:
        RuntimeError: If no CSV writer is active.

    """
    if io_ctx._csv_file is None or io_ctx._csv_writer is None:
        raise RuntimeError("No CSV writer is active.")
    io_ctx._csv_file.close()
    io_ctx._csv_writer = None
    io_ctx._csv_file = None


def io_write_csv_row(io_ctx: IOContext, row: dict[str, Any]) -> None:
    """Write a row to the active CSV writer.

    Args:
        io_ctx: The io context.
        row: Row dict to write.

    Raises:
        RuntimeError: If no CSV writer is active.

    """
    if io_ctx._csv_writer is None:
        raise RuntimeError("No CSV writer is active.")
    io_ctx._csv_writer.writerow(row)


def io_save_csv(io_ctx: IOContext) -> None:
    """Flush the active CSV writer without closing it.

    Args:
        io_ctx: The io context.

    Raises:
        RuntimeError: If no CSV writer is active.

    """
    if io_ctx._csv_file is None or io_ctx._csv_writer is None:
        raise RuntimeError("No CSV writer is active.")
    io_ctx._csv_file.flush()


def io_set_csv_header_row(io_ctx: IOContext, path: str, row: int, variable: str) -> None:
    """Read a CSV file using a specific row as the header and store rows in a variable.

    Skips ``row - 1`` lines, uses line ``row`` as the header, and reads the
    remaining lines as data rows.  The result (a list of dicts) is stored in
    ``io_ctx.variables[variable]``.

    Args:
        io_ctx: The io context.
        path: Path to the CSV file.
        row: 1-based row number to use as the header.
        variable: Variable name to store the list of row dicts.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If ``row`` is less than 1.

    """
    if row < 1:
        raise ValueError("Row number must be 1-based and >= 1.")
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    with file_path.open("r", encoding="utf-8", newline="") as f:
        for _ in range(row - 1):
            f.readline()
        reader = csv.DictReader(f)
        io_ctx.variables[variable] = list(reader)


# ---------------------------------------------------------------------------
# Directory actions
# ---------------------------------------------------------------------------


def io_create_directory(path: str) -> None:
    """Create a directory, including parents.

    Args:
        path: Directory path to create.

    """
    Path(path).mkdir(parents=True, exist_ok=True)


def io_assert_directory_exists(path: str) -> None:
    """Assert that a directory exists.

    Args:
        path: Directory path.

    Raises:
        AssertionError: If the directory does not exist.

    """
    if not Path(path).is_dir():
        raise AssertionError(f"Directory does not exist: {path}")


def io_assert_directory_not_exists(path: str) -> None:
    """Assert that a directory does not exist.

    Args:
        path: Directory path.

    Raises:
        AssertionError: If the directory exists.

    """
    if Path(path).is_dir():
        raise AssertionError(f"Directory exists: {path}")


def io_list_directory(io_ctx: IOContext, path: str, variable: str) -> None:
    """List files in a directory and store them as a variable.

    Args:
        io_ctx: The io context.
        path: Directory path.
        variable: Variable name to store the list of file names.

    Raises:
        FileNotFoundError: If the directory does not exist.

    """
    p = Path(path)
    if not p.is_dir():
        raise FileNotFoundError(f"Directory not found: {path}")
    io_ctx.variables[variable] = sorted(
        entry.name for entry in p.iterdir()
    )


def io_delete_directory(path: str) -> None:
    """Delete a directory and all its contents.

    Args:
        path: Directory path.

    Raises:
        FileNotFoundError: If the directory does not exist.

    """
    import shutil

    p = Path(path)
    if not p.is_dir():
        raise FileNotFoundError(f"Directory not found: {path}")
    shutil.rmtree(p)


def io_read_file_as_lines(
    io_ctx: IOContext, path: str, variable: str
) -> None:
    """Read a file and store its lines as a list in a variable.

    Args:
        io_ctx: The io context.
        path: File path.
        variable: Variable name to store the list of lines.

    Raises:
        FileNotFoundError: If the file does not exist.

    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    io_ctx.variables[variable] = p.read_text(encoding="utf-8").splitlines()
