"""CLI step definitions for behave — shell command execution."""

from __future__ import annotations

from typing import Any

from steplib.core.decorators import step
from steplib.core.registry import StepRegistry
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


def _get_cli(context: Any) -> CLIContext:
    """Get the CLIContext from context.steplib, creating it if needed."""
    steplib = getattr(context, "steplib", None)
    if steplib is None:
        raise RuntimeError(
            "context.steplib is not initialized. "
            "Call autoload(context) or load(context, ...) in before_all."
        )
    cli = getattr(steplib, "cli", None)
    if cli is None:
        cli = CLIContext()
        steplib.cli = cli
    return cli


def _strip_quotes(value: str) -> str:
    """Strip surrounding quotes from a string argument."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


# ---------------------------------------------------------------------------
# Command steps
# ---------------------------------------------------------------------------


@step(
    "I run the command {command}",
    category="cli",
    description="Run a shell command and store the exit code, stdout, and stderr.",
    example='When I run the command "echo hello"',
    i18n={
        "es": "Ejecuto el comando {command}",
        "pt": "Eu executo o comando {command}",
    },
)
def step_run_command(context: Any, command: str) -> None:
    """Run a shell command."""
    cli_run_command(_get_cli(context), _strip_quotes(command))


@step(
    "the command exit code equals {code:d}",
    category="cli",
    description="Assert that the last command's exit code equals the expected value.",
    example="Then the command exit code equals 0",
    i18n={
        "es": "el código de salida del comando es {code:d}",
        "pt": "o código de saída do comando é {code:d}",
    },
)
def step_exit_code_equals(context: Any, code: int) -> None:
    """Assert exit code equals expected."""
    cli_assert_exit_code(_get_cli(context), code)


@step(
    "the command output contains {text}",
    category="cli",
    description="Assert that the last command's stdout contains the given text.",
    example='Then the command output contains "hello"',
    i18n={
        "es": "la salida del comando contiene {text}",
        "pt": "a saída do comando contém {text}",
    },
)
def step_output_contains(context: Any, text: str) -> None:
    """Assert stdout contains text."""
    cli_assert_output_contains(_get_cli(context), _strip_quotes(text))


@step(
    "the command output equals {text}",
    category="cli",
    description="Assert that the last command's stdout equals the given text.",
    example='Then the command output equals "hello\\n"',
    i18n={
        "es": "la salida del comando es {text}",
        "pt": "a saída do comando é {text}",
    },
)
def step_output_equals(context: Any, text: str) -> None:
    """Assert stdout equals text."""
    cli_assert_output_equals(_get_cli(context), _strip_quotes(text))


@step(
    "the command error output contains {text}",
    category="cli",
    description="Assert that the last command's stderr contains the given text.",
    example='Then the command error output contains "error"',
    i18n={
        "es": "la salida de error del comando contiene {text}",
        "pt": "a saída de erro do comando contém {text}",
    },
)
def step_stderr_contains(context: Any, text: str) -> None:
    """Assert stderr contains text."""
    cli_assert_stderr_contains(_get_cli(context), _strip_quotes(text))


@step(
    "I run the command {command} with timeout {seconds:d}",
    category="cli",
    description="Run a shell command with a custom timeout in seconds.",
    example='When I run the command "sleep 1" with timeout 5',
    i18n={
        "es": "Ejecuto el comando {command} con tiempo límite {seconds:d}",
        "pt": "Eu executo o comando {command} com tempo limite {seconds:d}",
    },
)
def step_run_command_with_timeout(
    context: Any, command: str, seconds: int
) -> None:
    """Run a shell command with timeout."""
    cli_run_command_with_timeout(
        _get_cli(context), _strip_quotes(command), seconds
    )


@step(
    "I store the command output as {variable}",
    category="cli",
    description="Store the last command's stdout into a variable.",
    example='Then I store the command output as "result"',
    i18n={
        "es": "Guardo la salida del comando como {variable}",
        "pt": "Eu armazeno a saída do comando como {variable}",
    },
)
def step_store_output(context: Any, variable: str) -> None:
    """Store command output in a variable."""
    cli_store_output(_get_cli(context), _strip_quotes(variable))


@step(
    "the command output does not contain {text}",
    category="cli",
    description="Assert that the last command's stdout does NOT contain the given text.",
    example='Then the command output does not contain "error"',
    i18n={
        "es": "la salida del comando no contiene {text}",
        "pt": "a saída do comando não contém {text}",
    },
)
def step_output_not_contains(context: Any, text: str) -> None:
    """Assert stdout does not contain text."""
    cli_assert_output_not_contains(_get_cli(context), _strip_quotes(text))


@step(
    "I store the command error output as {variable}",
    category="cli",
    description="Store the last command's stderr into a variable.",
    example='Then I store the command error output as "errors"',
    i18n={
        "es": "Guardo la salida de error del comando como {variable}",
        "pt": "Eu armazeno a saída de erro do comando como {variable}",
    },
)
def step_store_stderr(context: Any, variable: str) -> None:
    """Store command stderr in a variable."""
    cli_store_stderr(_get_cli(context), _strip_quotes(variable))


@step(
    "the command output matches the pattern {pattern}",
    category="cli",
    description="Assert that the last command's stdout matches a regex pattern.",
    example='Then the command output matches the pattern "\\d+\\.\\d+"',
    i18n={
        "es": "la salida del comando coincide con el patrón {pattern}",
        "pt": "a saída do comando corresponde ao padrão {pattern}",
    },
)
def step_output_matches(context: Any, pattern: str) -> None:
    """Assert stdout matches regex pattern."""
    cli_assert_output_matches(_get_cli(context), _strip_quotes(pattern))


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

_ALL_STEPS = [
    step_run_command,
    step_exit_code_equals,
    step_output_contains,
    step_output_not_contains,
    step_output_equals,
    step_output_matches,
    step_stderr_contains,
    step_run_command_with_timeout,
    step_store_output,
    step_store_stderr,
]


def register(registry: StepRegistry) -> None:
    """Register all cli steps into the given registry."""
    for step_fn in _ALL_STEPS:
        registry.add(step_fn)
