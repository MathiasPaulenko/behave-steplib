# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-27

### Added

- **Core package** (`steplib.core`): `@step` decorator, `StepInfo` metadata,
  `StepRegistry` with behave integration, `Param` dataclass with `TypeRegistry`,
  `SteplibState` lifecycle management, i18n pattern expansion and validation,
  static step contract validation, ecosystem integration helpers
  (`behave-kit`, `behave-tables`, `behave-data`).
- **API module** (`steplib.modules.api`): HTTP testing steps with stdlib
  (urllib), httpx and requests backends. Configuration, requests, assertions
  (status, body, JSON path, headers), response storage and table comparison.
- **Web module** (`steplib.modules.web`): Browser testing steps with Selenium
  (Chrome, Firefox, headless). Navigation, page title, URL, element presence
  and page content assertions.
- **DB module** (`steplib.modules.db`): Database testing steps with SQLAlchemy.
  Connection configuration, query execution, row count and column assertions.
- **Kafka module** (`steplib.modules.kafka`): Kafka producer/consumer testing
  steps with kafka-python-ng. Bootstrap configuration, produce, consume,
  message count and content assertions.
- **Behave integration** (`steplib.behave`): `autoload(context)` for entry-point
  discovery, `load(context, *modules)` for explicit loading, `before_all` and
  `after_scenario` hooks.
- **CLI** (`steplib.cli`): `steplib list / show / validate / init` powered by
  Typer with table and JSON output formats.
- **i18n**: Spanish (`es`) and Portuguese (`pt`) translations for all steps.
  Both `i18n` dictionary and stacked decorator patterns supported.
- **Tests**: 164 tests covering core, modules, CLI and behave integration.
  Coverage gate at 80% (current: 82%).
- **CI/CD**: GitHub Actions workflows for CI (lint, typecheck, test, coverage),
  release (build, PyPI publish with attestations, GitHub release) and docs
  (Sphinx + furo, GitHub Pages deployment).
- **Documentation**: Sphinx documentation with furo theme, autodoc API
  reference, getting started guides, module references and architecture docs.
- **Community files**: `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`,
  pull request template, bug report and feature request issue templates.
- **Project setup**: `pyproject.toml` with hatchling + hatch-vcs, `Makefile`,
  `LICENSE` (MIT), `steplib/py.typed` marker, `.markdownlint.json`.

### Technical

- `mypy --strict` clean across 38 source files.
- `ruff` clean with `E`, `F`, `W`, `I`, `N`, `UP`, `B`, `SIM` rules.
- Python 3.11+ required.
- Zero mandatory runtime dependencies beyond `behave`, `parse` and `typer`.
