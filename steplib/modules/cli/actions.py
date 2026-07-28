"""Pure action functions for the cli module (shell command execution)."""

from __future__ import annotations

import re
import subprocess

from steplib.modules.cli.context import CLIContext


def cli_run_command(cli_ctx: CLIContext, command: str) -> None:
    """Run a shell command and store the exit code, stdout, and stderr.

    Args:
        cli_ctx: The cli context.
        command: The shell command to execute.

    Raises:
        subprocess.TimeoutExpired: If the command times out.

    """
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    cli_ctx.exit_code = result.returncode
    cli_ctx.stdout = result.stdout
    cli_ctx.stderr = result.stderr


def cli_run_command_with_timeout(
    cli_ctx: CLIContext, command: str, seconds: int
) -> None:
    """Run a shell command with a custom timeout.

    Args:
        cli_ctx: The cli context.
        command: The shell command to execute.
        seconds: Timeout in seconds.

    Raises:
        subprocess.TimeoutExpired: If the command times out.

    """
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=seconds,
        check=False,
    )
    cli_ctx.exit_code = result.returncode
    cli_ctx.stdout = result.stdout
    cli_ctx.stderr = result.stderr


def cli_assert_exit_code(cli_ctx: CLIContext, expected: int) -> None:
    """Assert that the last command's exit code equals the expected value.

    Args:
        cli_ctx: The cli context.
        expected: Expected exit code.

    Raises:
        AssertionError: If the exit code does not match.
        RuntimeError: If no command has been run.

    """
    if cli_ctx.exit_code is None:
        raise RuntimeError("No command has been executed.")
    if cli_ctx.exit_code != expected:
        raise AssertionError(
            f"Expected exit code {expected}, got {cli_ctx.exit_code}."
        )


def cli_assert_output_contains(cli_ctx: CLIContext, text: str) -> None:
    """Assert that the last command's stdout contains the given text.

    Args:
        cli_ctx: The cli context.
        text: Text to search for in stdout.

    Raises:
        AssertionError: If stdout does not contain the text.
        RuntimeError: If no command has been run.

    """
    if cli_ctx.exit_code is None:
        raise RuntimeError("No command has been executed.")
    if text not in cli_ctx.stdout:
        raise AssertionError(
            f"Expected stdout to contain '{text}', got: {cli_ctx.stdout!r}"
        )


def cli_assert_output_equals(cli_ctx: CLIContext, text: str) -> None:
    """Assert that the last command's stdout equals the given text.

    Args:
        cli_ctx: The cli context.
        text: Expected stdout content.

    Raises:
        AssertionError: If stdout does not match.
        RuntimeError: If no command has been run.

    """
    if cli_ctx.exit_code is None:
        raise RuntimeError("No command has been executed.")
    if cli_ctx.stdout != text:
        raise AssertionError(
            f"Expected stdout to be '{text}', got: {cli_ctx.stdout!r}"
        )


def cli_assert_stderr_contains(cli_ctx: CLIContext, text: str) -> None:
    """Assert that the last command's stderr contains the given text.

    Args:
        cli_ctx: The cli context.
        text: Text to search for in stderr.

    Raises:
        AssertionError: If stderr does not contain the text.
        RuntimeError: If no command has been run.

    """
    if cli_ctx.exit_code is None:
        raise RuntimeError("No command has been executed.")
    if text not in cli_ctx.stderr:
        raise AssertionError(
            f"Expected stderr to contain '{text}', got: {cli_ctx.stderr!r}"
        )


def cli_store_output(cli_ctx: CLIContext, variable: str) -> None:
    """Store the last command's stdout into a variable.

    Args:
        cli_ctx: The cli context.
        variable: Variable name to store the stdout.

    Raises:
        RuntimeError: If no command has been run.

    """
    if cli_ctx.exit_code is None:
        raise RuntimeError("No command has been executed.")
    cli_ctx.variables[variable] = cli_ctx.stdout


def cli_assert_output_not_contains(cli_ctx: CLIContext, text: str) -> None:
    """Assert that the last command's stdout does NOT contain the given text.

    Args:
        cli_ctx: The cli context.
        text: Text to search for in stdout.

    Raises:
        AssertionError: If stdout contains the text.
        RuntimeError: If no command has been run.

    """
    if cli_ctx.exit_code is None:
        raise RuntimeError("No command has been executed.")
    if text in cli_ctx.stdout:
        raise AssertionError(
            f"Expected stdout to NOT contain '{text}', got: {cli_ctx.stdout!r}"
        )


def cli_store_stderr(cli_ctx: CLIContext, variable: str) -> None:
    """Store the last command's stderr into a variable.

    Args:
        cli_ctx: The cli context.
        variable: Variable name to store the stderr.

    Raises:
        RuntimeError: If no command has been run.

    """
    if cli_ctx.exit_code is None:
        raise RuntimeError("No command has been executed.")
    cli_ctx.variables[variable] = cli_ctx.stderr


def cli_assert_output_matches(
    cli_ctx: CLIContext, pattern: str
) -> None:
    """Assert that the last command's stdout matches a regex pattern.

    Args:
        cli_ctx: The cli context.
        pattern: Regex pattern to match against stdout.

    Raises:
        AssertionError: If stdout does not match the pattern.
        RuntimeError: If no command has been run.

    """
    if cli_ctx.exit_code is None:
        raise RuntimeError("No command has been executed.")
    try:
        if not re.search(pattern, cli_ctx.stdout):
            raise AssertionError(
                f"Expected stdout to match pattern '{pattern}', "
                f"got: {cli_ctx.stdout!r}"
            )
    except re.error as exc:
        raise AssertionError(f"Invalid regex pattern '{pattern}': {exc}") from exc
