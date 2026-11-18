"""Regression tests for IO module bugs found in the audit."""

from __future__ import annotations

import errno
import os

import pytest

from steplib.modules.io.actions import (
    io_create_json_path,
    io_delete_json_path,
    io_move_file,
    io_rename_file,
    io_update_json_path,
)
from steplib.modules.io.context import IOContext


class TestCrossDeviceMove:
    """io_move_file/io_rename_file must work across filesystems."""

    def _simulate_exdev(self, monkeypatch):
        def fake_rename(src, dst, *args):
            raise OSError(errno.EXDEV, "Invalid cross-device link")

        monkeypatch.setattr(os, "rename", fake_rename)

    def test_move_file_across_devices(self, tmp_path, monkeypatch):
        self._simulate_exdev(monkeypatch)
        src = tmp_path / "a.txt"
        dst = tmp_path / "sub" / "b.txt"
        dst.parent.mkdir()
        src.write_text("data")

        io_move_file(IOContext(), str(src), str(dst))

        assert not src.exists()
        assert dst.read_text() == "data"

    def test_rename_file_across_devices(self, tmp_path, monkeypatch):
        self._simulate_exdev(monkeypatch)
        src = tmp_path / "a.txt"
        dst = tmp_path / "b.txt"
        src.write_text("data")

        io_rename_file(IOContext(), str(src), str(dst))

        assert not src.exists()
        assert dst.read_text() == "data"


class TestCsvWriterLifecycle:
    """Creating a second CSV writer must not leak the first handle."""

    def test_create_csv_writer_closes_previous_handle(self, tmp_path):
        from steplib.modules.io.actions import io_create_csv_writer

        ctx = IOContext()

        class FakeFile:
            def __init__(self) -> None:
                self.closed = False

            def close(self) -> None:
                self.closed = True

        fake = FakeFile()
        ctx._csv_file = fake  # type: ignore[assignment]
        ctx._csv_writer = object()  # type: ignore[assignment]

        io_create_csv_writer(ctx, str(tmp_path / "b.csv"), ["a"])

        assert fake.closed is True
        assert ctx._csv_file is not fake


class TestJsonPathKeyValidation:
    """Empty key_path must not create a bogus "" JSON key."""

    def test_create_json_path_rejects_empty_path(self):
        ctx = IOContext()
        ctx._last_json = {"a": 1}
        with pytest.raises((KeyError, ValueError)):
            io_create_json_path(ctx, "", 5)
        assert "" not in ctx._last_json

    def test_update_json_path_rejects_empty_path(self):
        ctx = IOContext()
        ctx._last_json = {"a": 1}
        with pytest.raises((KeyError, ValueError)):
            io_update_json_path(ctx, "", 5)

    def test_delete_json_path_rejects_empty_path(self):
        ctx = IOContext()
        ctx._last_json = {"a": 1}
        with pytest.raises((KeyError, ValueError)):
            io_delete_json_path(ctx, "")

    def test_nested_path_still_works(self):
        ctx = IOContext()
        ctx._last_json = {"a": {}}
        io_create_json_path(ctx, "a.b", 7)
        assert ctx._last_json["a"]["b"] == 7


class _Ctx:
    def __init__(self) -> None:
        from types import SimpleNamespace

        self.steplib = SimpleNamespace(io=IOContext())
        self.text = None


class TestCsvJsonTypeValidation:
    """CSV steps must reject JSON that decodes to non-object types."""

    def test_create_csv_rejects_non_list(self, tmp_path):
        from steplib.modules.io.steps import step_create_csv

        with pytest.raises(AssertionError, match="array of objects"):
            step_create_csv(_Ctx(), str(tmp_path / "o.csv"), '{"a": 1}')

    def test_create_csv_rejects_list_of_scalars(self, tmp_path):
        from steplib.modules.io.steps import step_create_csv

        with pytest.raises(AssertionError, match="array of objects"):
            step_create_csv(_Ctx(), str(tmp_path / "o.csv"), "[1, 2]")

    def test_write_csv_row_rejects_non_dict(self, tmp_path):
        from steplib.modules.io.steps import step_write_csv_row

        with pytest.raises(AssertionError, match="must be a JSON object"):
            step_write_csv_row(_Ctx(), "[1, 2]")
