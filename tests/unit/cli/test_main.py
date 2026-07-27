"""Tests for the steplib CLI (Typer commands)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

import steplib.cli.main as cli_main
from steplib.cli.main import app
from steplib.core.decorators import step
from steplib.core.registry import StepRegistry


@pytest.fixture()
def runner() -> CliRunner:
    """Return a Typer CLI runner."""
    return CliRunner()


@pytest.fixture()
def populated_registry(monkeypatch: pytest.MonkeyPatch) -> StepRegistry:
    """Patch get_registry() to return a registry with known steps."""
    registry = StepRegistry(auto_register_behave=False)

    @step(
        "I send a {method} request to {url}",
        category="api",
        backend="httpx",
        description="Send an HTTP request.",
        tags=["smoke"],
    )
    def step_send(context, method, url):  # type: ignore[no-untyped-def]
        pass

    @step("I click {selector}", category="web", backend="selenium")
    def step_click(context, selector):  # type: ignore[no-untyped-def]
        pass

    registry.add(step_send)
    registry.add(step_click)

    monkeypatch.setattr(cli_main, "_get_registry", lambda: registry)
    return registry


def test_list_shows_all_steps(
    runner: CliRunner,
    populated_registry: StepRegistry,
) -> None:
    """steplib list should show all registered steps."""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "I send a {method} request to {url}" in result.output
    assert "I click {selector}" in result.output


def test_list_filter_by_category(
    runner: CliRunner,
    populated_registry: StepRegistry,
) -> None:
    """steplib list --category api should show only API steps."""
    result = runner.invoke(app, ["list", "--category", "api"])
    assert result.exit_code == 0
    assert "I send a {method} request to {url}" in result.output
    assert "I click {selector}" not in result.output


def test_list_filter_by_backend(
    runner: CliRunner,
    populated_registry: StepRegistry,
) -> None:
    """steplib list --backend httpx should show only httpx steps."""
    result = runner.invoke(app, ["list", "--backend", "httpx"])
    assert result.exit_code == 0
    assert "I send a {method} request to {url}" in result.output
    assert "I click {selector}" not in result.output


def test_list_filter_by_category_and_backend(
    runner: CliRunner,
    populated_registry: StepRegistry,
) -> None:
    """steplib list --category api --backend httpx should filter correctly."""
    result = runner.invoke(app, ["list", "--category", "api", "--backend", "httpx"])
    assert result.exit_code == 0
    assert "I send a {method} request to {url}" in result.output
    assert "I click {selector}" not in result.output


def test_list_json_output(
    runner: CliRunner,
    populated_registry: StepRegistry,
) -> None:
    """steplib list --json should output valid JSON."""
    result = runner.invoke(app, ["list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 2
    patterns = {item["pattern"] for item in data}
    assert "I send a {method} request to {url}" in patterns


def test_list_empty(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """steplib list with no steps should show a message."""
    registry = StepRegistry(auto_register_behave=False)
    monkeypatch.setattr(cli_main, "_get_registry", lambda: registry)
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "No steps" in result.output


def test_show_existing_step(
    runner: CliRunner,
    populated_registry: StepRegistry,
) -> None:
    """steplib show should display metadata for a known pattern."""
    result = runner.invoke(app, ["show", "I send a {method} request to {url}"])
    assert result.exit_code == 0
    assert "Pattern:" in result.output
    assert "I send a {method} request to {url}" in result.output
    assert "Category:" in result.output
    assert "api" in result.output


def test_show_nonexistent_step(
    runner: CliRunner,
    populated_registry: StepRegistry,
) -> None:
    """steplib show with an unknown pattern should exit with code 1."""
    result = runner.invoke(app, ["show", "nonexistent pattern"])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_show_json_output(
    runner: CliRunner,
    populated_registry: StepRegistry,
) -> None:
    """steplib show --json should output valid JSON."""
    result = runner.invoke(app, ["show", "I send a {method} request to {url}", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["pattern"] == "I send a {method} request to {url}"
    assert data["category"] == "api"


def test_validate_ok(
    runner: CliRunner,
    populated_registry: StepRegistry,
) -> None:
    """steplib validate should return OK when all steps are valid."""
    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_validate_with_errors(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """steplib validate should report errors for invalid steps."""
    registry = StepRegistry(auto_register_behave=False)

    @step(
        "I send a {method} request to {url}",
        category="api",
        backend="httpx",
        i18n={"es": "envío una petición a {url}"},  # missing {method}
    )
    def step_bad(context, method, url):  # type: ignore[no-untyped-def]
        pass

    registry.add(step_bad)
    monkeypatch.setattr(cli_main, "_get_registry", lambda: registry)
    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 1
    assert "Placeholder mismatch" in result.output


def test_init_creates_environment(
    runner: CliRunner,
    tmp_path: Path,
) -> None:
    """steplib init should create a features/environment.py file."""
    output = tmp_path / "features" / "environment.py"
    result = runner.invoke(app, ["init", "--path", str(output)])
    assert result.exit_code == 0
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "from steplib.behave import autoload" in content
    assert "def before_all(context):" in content
    assert "autoload(context)" in content
    assert "def before_scenario" in content
    assert "def after_scenario" in content
