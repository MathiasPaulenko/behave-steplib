# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-07-28

### Added

- **IO module** (`steplib.modules.io`): 38 file, JSON, CSV and directory
  testing steps. File CRUD (read, write, append, delete, copy, move, rename,
  create empty), file assertions (exists, not exists, same, size, extension),
  JSON operations (load, save, path get/set/delete, validity, schema match,
  diff, merge, type check), CSV operations (create, write row, save, header
  row), directory operations (create, exists, not exists, list, delete) and
  read file as lines.
- **CLI module** (`steplib.modules.cli`): 10 shell command execution steps
  with subprocess. Command execution (with optional timeout), exit code
  assertions, stdout assertions (contains, not contains, equals, matches
  pattern), stderr assertions, and storing output (stdout and stderr) into
  variables.
- **Data module extensions**: 6 new steps — regex match
  (`the variable {name} matches the pattern {pattern}`), starts with, ends
  with, increment variable, greater than, less than, and a wait/sleep utility
  (`I wait for {seconds:f} seconds`). Data module now has 32 steps.
- **Tests**: 861 tests covering core, all modules, CLI and behave integration.

### Changed

- Total step count increased from 131 to 211 across 7 modules.
- README and Sphinx documentation updated with IO and CLI module sections,
  updated step counts, and new feature examples.

## [1.0.0] - 2026-07-27

### Added

- **Core package** (`steplib.core`): `@step` decorator, `StepInfo` metadata,
  `StepRegistry` with behave integration, `Param` dataclass with `TypeRegistry`,
  `SteplibState` lifecycle management, i18n pattern expansion and validation,
  static step contract validation, ecosystem integration helpers
  (`behave-kit`, `behave-tables`, `behave-data`).
- **API module** (`steplib.modules.api`): 55 HTTP testing steps with stdlib
  (urllib), httpx and requests backends. Configuration (base URL, headers,
  timeout, query params, proxy), authentication (basic auth, bearer token),
  SSL/redirect control, cookie management, requests (plain, body, form data,
  JSON body, query params, headers from table), status/body/JSON Path/header/
  response-time assertions, JSON Schema validation, store/extract operations,
  variable reuse and table comparison.
- **Web module** (`steplib.modules.web`): 34 browser testing steps with
  Selenium (Chrome, Firefox, headless). Configuration (base URL, implicit
  wait, page load timeout, window size), navigation (navigate, refresh, back,
  forward, frame switching), interactions (click, type, clear, select,
  screenshot), waits (element present, element visible, text), assertions
  (title, URL, element presence/visibility/enabled/text/attribute, page
  content), cookies (exists, delete, store) and store/extract operations.
- **DB module** (`steplib.modules.db`): 22 database testing steps with
  SQLAlchemy. Connection management (connect, disconnect), query execution
  (plain and with bind parameters), row count assertions (exact, greater
  than, fewer than), column assertions (equals, not equals, contains, null,
  not null), scalar queries, table assertions (exists, row count),
  transaction management (begin, rollback, commit) and store/extract
  operations.
- **Kafka module** (`steplib.modules.kafka`): 20 Kafka producer/consumer
  testing steps with kafka-python-ng. Configuration (bootstrap servers,
  consumer group, auto offset reset, producer/consumer config overrides),
  message production (single, JSON, batch from table), consumption (with
  optional timeout), assertions (count, greater than, contains, key/value
  by index, regex match, order) and store/extract operations.
- **Behave integration** (`steplib.behave`): `autoload(context)` for entry-point
  discovery, `load(context, *modules)` for explicit loading, `before_all` and
  `after_scenario` hooks.
- **CLI** (`steplib.cli`): `steplib list / show / validate / init` powered by
  Typer with table and JSON output formats. List supports `--category`,
  `--backend` and `--tag` filters.
- **i18n**: Spanish (`es`) and Portuguese (`pt`) translations for all 131
  steps across all modules. Both `i18n` dictionary and stacked decorator
  patterns supported.
- **Tests**: 467 tests covering core, modules, CLI and behave integration.
  Coverage gate at 80% (current: 82%).
- **CI/CD**: GitHub Actions workflows for CI (lint, typecheck, test, coverage),
  release (build, PyPI publish with attestations, GitHub release) and docs
  (Sphinx + furo, GitHub Pages deployment).
- **Documentation**: Sphinx documentation with furo theme, autodoc API
  reference, getting started guides, module references with complete step
  listings, architecture docs, step contract guide and i18n guide.
- **Community files**: `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`,
  pull request template, bug report and feature request issue templates.
- **Project setup**: `pyproject.toml` with hatchling + hatch-vcs, `Makefile`,
  `LICENSE` (MIT), `steplib/py.typed` marker, `.markdownlint.json`.

### Technical

- `mypy --strict` clean across 38 source files.
- `ruff` clean with `E`, `F`, `W`, `I`, `N`, `UP`, `B`, `SIM` rules.
- Python 3.11+ required.
- Zero mandatory runtime dependencies beyond `behave`, `parse` and `typer`.
