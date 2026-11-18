"""Regression tests for Data module bugs found in the audit."""

from __future__ import annotations

import os

from steplib.modules.data.context import DataContext


class TestEnvFileParsing:
    """Common .env formats must be handled."""

    def test_export_prefix_is_accepted(self, tmp_path, monkeypatch):
        from steplib.modules.data.actions import data_load_env_file

        monkeypatch.delenv("STEPLIB_AUDIT_FOO", raising=False)
        monkeypatch.delenv("STEPLIB_AUDIT_BAZ", raising=False)
        env_file = tmp_path / ".env"
        env_file.write_text("export STEPLIB_AUDIT_FOO=bar\nSTEPLIB_AUDIT_BAZ=qux\n")
        ctx = DataContext()
        data_load_env_file(ctx, str(env_file))
        assert os.environ["STEPLIB_AUDIT_FOO"] == "bar"
        assert os.environ["STEPLIB_AUDIT_BAZ"] == "qux"
        assert "export STEPLIB_AUDIT_FOO" not in os.environ
