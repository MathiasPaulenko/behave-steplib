"""steplib CLI — Typer-based terminal interface.

Commands:
    list      List registered steps (with optional --category/--backend filters).
    show      Show detailed metadata for a single step pattern.
    search    Search steps by partial pattern, category, backend or tag.
    validate  Validate step contracts.
    init      Generate a features/environment.py scaffold.
    install   Informative message — use pip install behave-steplib[EXTRA] instead.
"""

from __future__ import annotations

import json as json_module
from pathlib import Path
from typing import Annotated

import typer

from steplib.cli.formatters import (
    format_step_detail,
    format_step_detail_json,
    format_step_json,
    format_step_table,
)
from steplib.core.discovery import get_registry
from steplib.core.registry import StepRegistry
from steplib.core.validation import validate_steps

app = typer.Typer(
    name="steplib",
    help="behave-steplib CLI — manage and inspect BDD step libraries.",
    no_args_is_help=True,
)


def _get_registry() -> StepRegistry:
    """Build a metadata-only registry from installed plugins."""
    return get_registry()


@app.command(name="list")
def list_steps(
    category: Annotated[
        str | None,
        typer.Option("--category", "-c", help="Filter by category (e.g. 'api')."),
    ] = None,
    backend: Annotated[
        str | None,
        typer.Option("--backend", "-b", help="Filter by backend (e.g. 'httpx')."),
    ] = None,
    tag: Annotated[
        str | None,
        typer.Option("--tag", "-t", help="Filter by tag."),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output as JSON."),
    ] = False,
) -> None:
    """List all registered steps, optionally filtered."""
    registry = _get_registry()
    steps = registry.filter(category=category, backend=backend, tag=tag)
    if json_output:
        typer.echo(format_step_json(steps))
    else:
        typer.echo(format_step_table(steps))


@app.command(name="show")
def show_step(
    pattern: Annotated[
        str,
        typer.Argument(help="Step pattern to display (e.g. 'I send a {method} request to {url}')."),
    ],
    backend: Annotated[
        str | None,
        typer.Option("--backend", "-b", help="Filter by backend."),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output as JSON."),
    ] = False,
) -> None:
    """Show detailed metadata for a single step."""
    registry = _get_registry()
    info = registry.find(pattern, backend=backend)
    if info is None:
        typer.echo(f"Step not found: '{pattern}'", err=True)
        raise typer.Exit(code=1)
    if json_output:
        typer.echo(format_step_detail_json(info))
    else:
        typer.echo(format_step_detail(info))


@app.command(name="search")
def search_steps(
    pattern: Annotated[
        str | None,
        typer.Argument(help="Partial text to search for in step patterns."),
    ] = None,
    category: Annotated[
        str | None,
        typer.Option("--category", "-c", help="Filter by category (e.g. 'api')."),
    ] = None,
    backend: Annotated[
        str | None,
        typer.Option("--backend", "-b", help="Filter by backend (e.g. 'httpx')."),
    ] = None,
    tag: Annotated[
        str | None,
        typer.Option("--tag", "-t", help="Filter by tag."),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output as JSON."),
    ] = False,
) -> None:
    """Search steps by partial pattern, category, backend or tag."""
    registry = _get_registry()
    steps = registry.search(
        pattern=pattern,
        category=category,
        backend=backend,
        tag=tag,
    )
    if json_output:
        typer.echo(format_step_json(steps))
    else:
        typer.echo(format_step_table(steps))


@app.command(name="validate")
def validate(
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output as JSON."),
    ] = False,
) -> None:
    """Validate that all registered steps satisfy the step contract."""
    registry = _get_registry()
    errors = validate_steps(registry)
    if json_output:
        data = {"valid": len(errors) == 0, "errors": errors}
        typer.echo(json_module.dumps(data, indent=2, ensure_ascii=False))
    elif errors:
        for error in errors:
            typer.echo(error, err=True)
        raise typer.Exit(code=1)
    else:
        typer.echo("OK")

    if errors and json_output:
        raise typer.Exit(code=1)


@app.command(name="init")
def init_scaffold(
    path: Annotated[
        str,
        typer.Option("--path", "-p", help="Output path for environment.py."),
    ] = "features/environment.py",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output as JSON."),
    ] = False,
) -> None:
    """Generate a features/environment.py with autoload(context)."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        '"""behave environment generated by steplib init."""\n\n'
        "from steplib.behave import autoload\n\n\n"
        "def before_all(context):\n"
        "    context.steplib = autoload(context)\n\n\n"
        "def before_scenario(context, scenario):\n"
        "    context.steplib.reset()\n\n\n"
        "def after_scenario(context, scenario):\n"
        "    context.steplib.cleanup()\n",
        encoding="utf-8",
    )
    if json_output:
        data = {"created": True, "path": str(output)}
        typer.echo(json_module.dumps(data, indent=2, ensure_ascii=False))
    else:
        typer.echo(f"Created {path}")


@app.command(name="install")
def install(
    extra: Annotated[
        str | None,
        typer.Argument(help="Extra name to install (e.g. 'api')."),
    ] = None,
) -> None:
    """Informative message — use pip install behave-steplib[EXTRA] instead.

    behave-steplib does not install packages. Use pip directly to install
    the desired extras.
    """
    available_extras = [
        "api",
        "requests",
        "web",
        "db",
        "kafka",
        "data",
        "io",
        "tables",
        "kit",
        "all",
    ]
    if extra and extra in available_extras:
        typer.echo(
            f"'install' is not a steplib command. "
            f"Use 'pip install behave-steplib[{extra}]' instead."
        )
    elif extra:
        typer.echo(
            f"Unknown extra '{extra}'. "
            f"Available extras: {', '.join(available_extras)}.\n"
            f"Use 'pip install behave-steplib[EXTRA]' to install."
        )
    else:
        typer.echo(
            "'install' is not a steplib command. "
            "Use 'pip install behave-steplib[EXTRA]' instead.\n"
            f"Available extras: {', '.join(available_extras)}."
        )
    raise typer.Exit(code=1)


def main() -> None:
    """Entry point for the steplib CLI."""
    app()


if __name__ == "__main__":
    main()
