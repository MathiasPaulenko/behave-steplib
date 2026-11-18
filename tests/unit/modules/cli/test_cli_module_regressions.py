"""Regression tests for the cli module (shell execution) bugs."""

from __future__ import annotations

import subprocess
from unittest.mock import Mock

import pytest

from steplib.modules.cli.actions import cli_run_command, cli_run_command_with_timeout
from steplib.modules.cli.context import CLIContext


class TestTimeoutState:
    """A timed-out command must not leave stale results in the context."""

    def test_timeout_clears_previous_state(self, monkeypatch):
        ctx = CLIContext()
        ctx.exit_code = 0
        ctx.stdout = "old output"
        ctx.stderr = "old error"

        monkeypatch.setattr(
            subprocess,
            "run",
            Mock(side_effect=subprocess.TimeoutExpired("cmd", 30)),
        )

        with pytest.raises(subprocess.TimeoutExpired):
            cli_run_command(ctx, "sleep 100")

        assert ctx.exit_code is None
        assert ctx.stdout == ""
        assert ctx.stderr == ""

    def test_timeout_clears_previous_state_with_custom_timeout(self, monkeypatch):
        ctx = CLIContext()
        ctx.exit_code = 1

        monkeypatch.setattr(
            subprocess,
            "run",
            Mock(side_effect=subprocess.TimeoutExpired("cmd", 5)),
        )

        with pytest.raises(subprocess.TimeoutExpired):
            cli_run_command_with_timeout(ctx, "sleep 100", 5)

        assert ctx.exit_code is None
