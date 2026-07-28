"""Tests for cli module step definitions."""

from __future__ import annotations

import subprocess
import sys
from types import SimpleNamespace
from typing import Any

import pytest

from steplib.modules.cli.context import CLIContext
from steplib.modules.cli.steps import (
    step_exit_code_equals,
    step_output_contains,
    step_output_equals,
    step_output_matches,
    step_output_not_contains,
    step_run_command,
    step_run_command_with_timeout,
    step_stderr_contains,
    step_store_output,
    step_store_stderr,
)


def _make_context() -> Any:
    """Create a mock context with steplib.cli."""
    ctx = SimpleNamespace()
    ctx.steplib = SimpleNamespace()
    ctx.steplib.cli = CLIContext()
    return ctx


# ---------------------------------------------------------------------------
# Command steps
# ---------------------------------------------------------------------------


class TestStepRunCommand:
    def test_run_command(self) -> None:
        ctx = _make_context()
        step_run_command(ctx, "echo hello")
        assert ctx.steplib.cli.exit_code == 0
        assert "hello" in ctx.steplib.cli.stdout

    def test_run_command_strips_quotes(self) -> None:
        ctx = _make_context()
        step_run_command(ctx, '"echo hello"')
        assert ctx.steplib.cli.exit_code == 0


class TestStepExitCodeEquals:
    def test_exit_code_matches(self) -> None:
        ctx = _make_context()
        step_run_command(ctx, "exit 0")
        step_exit_code_equals(ctx, 0)

    def test_exit_code_mismatch(self) -> None:
        ctx = _make_context()
        step_run_command(ctx, "exit 1")
        with pytest.raises(AssertionError, match="Expected exit code 0"):
            step_exit_code_equals(ctx, 0)


class TestStepOutputContains:
    def test_output_contains(self) -> None:
        ctx = _make_context()
        step_run_command(ctx, "echo hello world")
        step_output_contains(ctx, "hello")

    def test_output_not_contains(self) -> None:
        ctx = _make_context()
        step_run_command(ctx, "echo hello")
        with pytest.raises(AssertionError, match="Expected stdout to contain"):
            step_output_contains(ctx, "goodbye")


class TestStepOutputEquals:
    def test_output_equals(self) -> None:
        ctx = _make_context()
        step_run_command(ctx, "echo hello")
        step_output_equals(ctx, "hello\n")

    def test_output_not_equals(self) -> None:
        ctx = _make_context()
        step_run_command(ctx, "echo hello")
        with pytest.raises(AssertionError, match="Expected stdout to be"):
            step_output_equals(ctx, "world\n")


class TestStepStderrContains:
    def test_stderr_contains(self) -> None:
        ctx = _make_context()
        step_run_command(ctx, "echo error_msg >&2")
        step_stderr_contains(ctx, "error_msg")

    def test_stderr_not_contains(self) -> None:
        ctx = _make_context()
        step_run_command(ctx, "echo hello >&2")
        with pytest.raises(AssertionError, match="Expected stderr to contain"):
            step_stderr_contains(ctx, "goodbye")


class TestStepRunCommandWithTimeout:
    def test_run_with_timeout(self) -> None:
        ctx = _make_context()
        step_run_command_with_timeout(ctx, "echo hello", 5)
        assert ctx.steplib.cli.exit_code == 0
        assert "hello" in ctx.steplib.cli.stdout

    def test_timeout_exceeded(self) -> None:
        ctx = _make_context()
        with pytest.raises(subprocess.TimeoutExpired):
            step_run_command_with_timeout(
                ctx, f'"{sys.executable} -c \"import time; time.sleep(10)\""', 1
            )


class TestStepStoreOutput:
    def test_store_output(self) -> None:
        ctx = _make_context()
        step_run_command(ctx, "echo hello")
        step_store_output(ctx, "result")
        assert ctx.steplib.cli.variables["result"] == "hello\n"


class TestStepOutputNotContains:
    def test_not_contains(self) -> None:
        ctx = _make_context()
        step_run_command(ctx, "echo hello")
        step_output_not_contains(ctx, '"error"')

    def test_contains_raises(self) -> None:
        ctx = _make_context()
        step_run_command(ctx, "echo hello")
        with pytest.raises(AssertionError, match="to NOT contain"):
            step_output_not_contains(ctx, '"hello"')


class TestStepStoreStderr:
    def test_store_stderr(self) -> None:
        ctx = _make_context()
        ctx.steplib.cli.exit_code = 1
        ctx.steplib.cli.stderr = "some error"
        step_store_stderr(ctx, "errors")
        assert ctx.steplib.cli.variables["errors"] == "some error"


class TestStepOutputMatches:
    def test_matches(self) -> None:
        ctx = _make_context()
        ctx.steplib.cli.exit_code = 0
        ctx.steplib.cli.stdout = "version 1.2.3"
        step_output_matches(ctx, r'"\d+\.\d+\.\d+"')

    def test_does_not_match(self) -> None:
        ctx = _make_context()
        ctx.steplib.cli.exit_code = 0
        ctx.steplib.cli.stdout = "no version here"
        with pytest.raises(AssertionError, match="to match pattern"):
            step_output_matches(ctx, r'"\d+\.\d+\.\d+"')
