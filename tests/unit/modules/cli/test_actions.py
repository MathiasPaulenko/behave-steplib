"""Tests for cli module actions (pure functions)."""

from __future__ import annotations

import subprocess
import sys

import pytest

from steplib.modules.cli.actions import (
    cli_assert_exit_code,
    cli_assert_output_contains,
    cli_assert_output_equals,
    cli_assert_output_matches,
    cli_assert_output_not_contains,
    cli_assert_stderr_contains,
    cli_run_command,
    cli_run_command_with_timeout,
    cli_store_output,
    cli_store_stderr,
)
from steplib.modules.cli.context import CLIContext

# ---------------------------------------------------------------------------
# Run command
# ---------------------------------------------------------------------------


class TestRunCommand:
    def test_run_success(self) -> None:
        ctx = CLIContext()
        cli_run_command(ctx, "echo hello")
        assert ctx.exit_code == 0
        assert "hello" in ctx.stdout

    def test_run_failure(self) -> None:
        ctx = CLIContext()
        cli_run_command(ctx, "exit 1")
        assert ctx.exit_code == 1

    def test_run_with_stderr(self) -> None:
        ctx = CLIContext()
        cli_run_command(ctx, "echo error_msg >&2")
        assert "error_msg" in ctx.stderr


# ---------------------------------------------------------------------------
# Run command with timeout
# ---------------------------------------------------------------------------


class TestRunCommandWithTimeout:
    def test_run_with_timeout_success(self) -> None:
        ctx = CLIContext()
        cli_run_command_with_timeout(ctx, "echo hello", 5)
        assert ctx.exit_code == 0
        assert "hello" in ctx.stdout

    def test_run_timeout_exceeded(self) -> None:
        ctx = CLIContext()
        with pytest.raises(subprocess.TimeoutExpired):
            cli_run_command_with_timeout(
                ctx, f"{sys.executable} -c \"import time; time.sleep(10)\"", 1
            )


# ---------------------------------------------------------------------------
# Assert exit code
# ---------------------------------------------------------------------------


class TestAssertExitCode:
    def test_exit_code_matches(self) -> None:
        ctx = CLIContext()
        cli_run_command(ctx, "exit 0")
        cli_assert_exit_code(ctx, 0)

    def test_exit_code_mismatch(self) -> None:
        ctx = CLIContext()
        cli_run_command(ctx, "exit 1")
        with pytest.raises(AssertionError, match="Expected exit code 0"):
            cli_assert_exit_code(ctx, 0)

    def test_no_command_run(self) -> None:
        ctx = CLIContext()
        with pytest.raises(RuntimeError, match="No command has been executed"):
            cli_assert_exit_code(ctx, 0)


# ---------------------------------------------------------------------------
# Assert output contains
# ---------------------------------------------------------------------------


class TestAssertOutputContains:
    def test_output_contains(self) -> None:
        ctx = CLIContext()
        cli_run_command(ctx, "echo hello world")
        cli_assert_output_contains(ctx, "hello")

    def test_output_not_contains(self) -> None:
        ctx = CLIContext()
        cli_run_command(ctx, "echo hello")
        with pytest.raises(AssertionError, match="Expected stdout to contain"):
            cli_assert_output_contains(ctx, "goodbye")

    def test_no_command_run(self) -> None:
        ctx = CLIContext()
        with pytest.raises(RuntimeError, match="No command has been executed"):
            cli_assert_output_contains(ctx, "hello")


# ---------------------------------------------------------------------------
# Assert output equals
# ---------------------------------------------------------------------------


class TestAssertOutputEquals:
    def test_output_equals(self) -> None:
        ctx = CLIContext()
        cli_run_command(ctx, "echo hello")
        cli_assert_output_equals(ctx, "hello\n")

    def test_output_not_equals(self) -> None:
        ctx = CLIContext()
        cli_run_command(ctx, "echo hello")
        with pytest.raises(AssertionError, match="Expected stdout to be"):
            cli_assert_output_equals(ctx, "world\n")

    def test_no_command_run(self) -> None:
        ctx = CLIContext()
        with pytest.raises(RuntimeError, match="No command has been executed"):
            cli_assert_output_equals(ctx, "hello")


# ---------------------------------------------------------------------------
# Assert stderr contains
# ---------------------------------------------------------------------------


class TestAssertStderrContains:
    def test_stderr_contains(self) -> None:
        ctx = CLIContext()
        cli_run_command(ctx, "echo error_msg >&2")
        cli_assert_stderr_contains(ctx, "error_msg")

    def test_stderr_not_contains(self) -> None:
        ctx = CLIContext()
        cli_run_command(ctx, "echo hello >&2")
        with pytest.raises(AssertionError, match="Expected stderr to contain"):
            cli_assert_stderr_contains(ctx, "goodbye")

    def test_no_command_run(self) -> None:
        ctx = CLIContext()
        with pytest.raises(RuntimeError, match="No command has been executed"):
            cli_assert_stderr_contains(ctx, "error")


# ---------------------------------------------------------------------------
# Store output
# ---------------------------------------------------------------------------


class TestStoreOutput:
    def test_store_output(self) -> None:
        ctx = CLIContext()
        cli_run_command(ctx, "echo hello")
        cli_store_output(ctx, "result")
        assert ctx.variables["result"] == "hello\n"

    def test_no_command_run(self) -> None:
        ctx = CLIContext()
        with pytest.raises(RuntimeError, match="No command has been executed"):
            cli_store_output(ctx, "result")


# ---------------------------------------------------------------------------
# Context lifecycle
# ---------------------------------------------------------------------------


class TestCLIContext:
    def test_reset(self) -> None:
        ctx = CLIContext()
        ctx.exit_code = 1
        ctx.stdout = "output"
        ctx.stderr = "error"
        ctx.variables["key"] = "value"
        ctx.reset()
        assert ctx.exit_code is None
        assert ctx.stdout == ""
        assert ctx.stderr == ""
        assert ctx.variables == {}

    def test_cleanup(self) -> None:
        ctx = CLIContext()
        ctx.exit_code = 1
        ctx.stdout = "output"
        ctx.cleanup()
        assert ctx.exit_code is None
        assert ctx.stdout == ""


# --- New action tests ---


class TestAssertOutputNotContains:
    def test_not_contains(self) -> None:
        ctx = CLIContext()
        ctx.exit_code = 0
        ctx.stdout = "hello world"
        cli_assert_output_not_contains(ctx, "error")

    def test_contains_raises(self) -> None:
        ctx = CLIContext()
        ctx.exit_code = 0
        ctx.stdout = "hello error world"
        with pytest.raises(AssertionError, match="to NOT contain"):
            cli_assert_output_not_contains(ctx, "error")

    def test_no_command_run(self) -> None:
        ctx = CLIContext()
        with pytest.raises(RuntimeError, match="No command has been executed"):
            cli_assert_output_not_contains(ctx, "x")


class TestStoreStderr:
    def test_store_stderr(self) -> None:
        ctx = CLIContext()
        ctx.exit_code = 1
        ctx.stderr = "some error"
        cli_store_stderr(ctx, "errors")
        assert ctx.variables["errors"] == "some error"

    def test_no_command_run(self) -> None:
        ctx = CLIContext()
        with pytest.raises(RuntimeError, match="No command has been executed"):
            cli_store_stderr(ctx, "x")


class TestAssertOutputMatches:
    def test_matches(self) -> None:
        ctx = CLIContext()
        ctx.exit_code = 0
        ctx.stdout = "version 1.2.3"
        cli_assert_output_matches(ctx, r"\d+\.\d+\.\d+")

    def test_does_not_match(self) -> None:
        ctx = CLIContext()
        ctx.exit_code = 0
        ctx.stdout = "no version here"
        with pytest.raises(AssertionError, match="to match pattern"):
            cli_assert_output_matches(ctx, r"\d+\.\d+\.\d+")

    def test_no_command_run(self) -> None:
        ctx = CLIContext()
        with pytest.raises(RuntimeError, match="No command has been executed"):
            cli_assert_output_matches(ctx, r".*")


class TestBug18InvalidRegexPattern:
    """Regression tests for Bug 18: cli_assert_output_matches should raise
    AssertionError, not re.error, when the regex pattern is invalid."""

    def test_invalid_regex_raises_assertion_error(self) -> None:
        ctx = CLIContext()
        ctx.exit_code = 0
        ctx.stdout = "some output"
        with pytest.raises(AssertionError, match="Invalid regex pattern"):
            cli_assert_output_matches(ctx, "[invalid(")
