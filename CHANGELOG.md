# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.1] - 2026-11-18

### Fixed

- `SteplibMatcher.matches()` no longer reports a match when the parse
  result is a `MatchWithError`, which caused spurious `AmbiguousStep`
  errors at registration time whenever a custom type converter failed.
- Registered patterns are now sorted by specificity (most fixed words
  first) and deduplicated by pattern text, so `find_match` resolution no
  longer depends on the order modules list their steps.
- `register_type()` now registers the converter directly on
  `ParseMatcher`'s type registry, so `{value:Name}` conversion works
  regardless of which step matcher is active when called.
- `SteplibState.reset()`/`cleanup()` no longer abort on the first failing
  module context; all contexts run their lifecycle hook and the first
  error is re-raised afterwards.
- The `@step` decorator copies caller-provided `parameters`, `tags`,
  `requires` and `i18n` instead of sharing the mutable references.
- API urllib backend: `verify=False` now actually installs an
  `HTTPSHandler` with the relaxed SSL context — the flag was previously
  built but never attached to the opener.
- Absolute URLs are now detected case-insensitively (`HTTP://...`,
  `Https://...`), both in API requests and web navigation.
- A failed API request no longer leaves a stale `last_response`.
- `api_send_json` serializes any JSON-compatible payload (lists,
  scalars), not only dicts.
- The JSON Schema subset validator supports `type` given as a list
  (`["string", "null"]`) and reports an error for unknown types instead
  of silently passing.
- The response-schema step rejects non-object JSON schemas with a clear
  `AssertionError` instead of an `AttributeError`.
- DB module: `execute()`/`execute_scalar()` and the `db_query*` helpers
  no longer call `keys()`/`fetchall()`/`scalar()` on non-row-producing
  statements, which raised `ResourceClosedError` for `INSERT`/`UPDATE`/
  DDL statements.
- DB module: `DbContext.cleanup()`, `db_disconnect()` and
  `DatabaseClient.close()` continue closing the connection, engine and
  disposing resources even when an earlier cleanup step fails, then
  re-raise the first error.
- IO module: file moves use `shutil.move`, so `I move the file` and
  `I rename the file` work across filesystems (EXDEV).
- IO module: empty `key_path` values are rejected instead of silently
  indexing/creating a `""` JSON key.
- IO module: creating a second CSV writer closes the previous file
  handle, and `IOContext` cleanup/reset closes any active CSV writer.
- IO module: CSV steps reject JSON that decodes to non-object types
  (`{"a": 1}` for the CSV create step, `[1, 2]` for a row) with a clear
  `AssertionError`.
- Web module: `SeleniumDriver` resolves common locator names
  (`css`, `class`, `tag`, `css selector`, `link text`, ...) to the right
  `selenium.webdriver.common.by.By` constants instead of crashing with
  `AttributeError`.
- Web module: a failing `driver.quit()` no longer leaves the driver
  reference populated; cleanup still re-raises the error.
- Kafka module: producer/consumer config steps reject JSON values that
  are not objects, and cleanup closes both producer and consumer even
  when the first close fails.
- Data module: `.env` files now accept the optional `export` prefix
  (`export KEY=value`).
- CLI module: `cli_run_command`/`cli_run_command_with_timeout` clear
  `exit_code`/`stdout`/`stderr` before running and on
  `TimeoutExpired`, so a timed-out command no longer leaves stale state.
- `steplib show --json` no longer crashes when a `Param` declares a
  non-JSON-serializable `default` or `choices`.

### Tests

- Added 51 regression tests covering every fix above.
- Full test suite: 1111 passing.

## [1.6.0] - 2026-10-05

### Fixed

- i18n translations (`es`/`pt`) are now actually registered with behave.
  Previously only the English base patterns were registered, so translated
  feature files got undefined-step errors despite the documentation
  claiming otherwise.
- Fixed runtime step-shadowing: `parse` placeholders can capture trailing
  text, so generic patterns registered before their more specific variants
  silently stole them (`the response header ... is not ...`,
  `I set the variable ... to the JSON ...`,
  `I read the file ... as lines into ...`, plus every `no`/`not` variant
  in the `es`/`pt` translations). All specific patterns now register
  before their generic forms.
- `autoload(context, backends={"api": "httpx"})` no longer removes every
  step of the filtered category — steps without a backend are kept as
  documented, and the selected backend is stored on
  `context.steplib.backends` and used by the API module when creating its
  client.
- `steplib validate` passes on the shipped library: the `es`/`pt`
  translations of `the element {by} {value} attribute {attr} equals
  {expected}` had placeholders in a different order.
- `get_client()` in the API module raises `ValueError` for unknown
  backends instead of silently falling back to urllib.
- The Kafka consumer is recreated when consuming from a different topic
  in the same scenario — the consumer was bound to the first topic.
- `the page load timeout is` and `the implicit wait is` steps now apply
  the values to the active driver, not just to the context.
- SQL statements in the DB module now auto-commit unless an explicit
  transaction was started with `I begin a database transaction` —
  previously `INSERT`/`UPDATE` were rolled back when the connection
  closed.
- `SteplibMatcher` now shares `ParseMatcher`'s type registry, so custom
  types registered via `register_type()`/`behave.register_type()` convert
  `{value:Type}` placeholders at match time.
- The behave step matcher in use before registration is restored
  afterwards; `autoload` no longer leaves the custom matcher active for
  user-defined steps.
- `requests` backend: duplicate `Set-Cookie` headers are recovered from
  the raw response so `I save cookies from the response` behaves like the
  other backends.
- Query parameters sent via step table are merged with the configured
  defaults instead of replacing them.
- `steplib init` refuses to overwrite an existing file; use `--force` to
  overwrite.
- `register_type()` now also registers the converter with behave so
  `{value:Name}` patterns actually convert values.
- `validate_steps` now also flags pattern placeholders missing from
  declared `Param` descriptors.
- Corrected 13 step `example` strings that did not parse their own
  patterns, and fixed the `es`/`pt` pattern of
  `I load the JSON file {path} as the last JSON` so it does not collide
  with the data module's JSON loading step.

### Tests

- Added contract tests that parse every step example against its pattern
  and verify first-match resolution across all registered languages.
- `io` tests that need `jsonschema` are now skipped with
  `pytest.importorskip` when the package is not installed.
- Full test suite: 1053 passing, 4 skipped.

### Documentation

- Rewrote the module pages whose patterns and examples did not match the
  implementation (`api`, `cli`, `db`, `data`, `io`, `kafka`), fixed the
  step counts (API has 54 steps, not 55; 210 total) and fixed README
  examples that used non-existent patterns.
- `docs/changelog.rst` now uses `myst_parser` via `include` with the
  `parser` option (`mdinclude` is not supported by MyST 5).
- Removed the `steplib.modules.kafka.client` autodoc entry — the module
  does not exist.
- Driver/connection lifecycle examples create the module context
  (`WebContext`, `DbContext`) before assigning to it; the previous
  snippets raised `AttributeError`.

## [1.4.0] - 2026-07-28

### Fixed

- Normalized boolean and `None` value comparisons across all assertion
  functions. Replaced direct `str()` conversions in step/action functions
  with `_normalize_value` / `_normalize_json_value` helpers so Python
  booleans (`True`/`False`) and `None` compare against their JSON-style
  string representations (`"true"`, `"false"`, `"null"`) consistently.
  Affected modules: `api`, `db`, `kafka`, `io` and `data`.
- Fixed `api_assert_json_path_contains` to normalize the looked-up value
  before checking list membership.
- Fixed `kafka_assert_message_order` to normalize expected keys before
  comparison.

### Changed

- Added `pyyaml>=6.0` to the `data` optional dependency group to support
  YAML file loading.

### Tests

- Added regression tests for boolean/`None` normalization in `api`, `db`,
  `kafka`, `io` and `data` modules.
- Full test suite: 1027 passing tests.

## [1.3.0] - 2026-07-28

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

- Total step count increased from 131 to 210 across 7 modules.
- README and Sphinx documentation updated with IO and CLI module sections,
  updated step counts, and new feature examples.

## [1.0.0] - 2026-07-27

### Added

- **Core package** (`steplib.core`): `@step` decorator, `StepInfo` metadata,
  `StepRegistry` with behave integration, `Param` dataclass with `TypeRegistry`,
  `SteplibState` lifecycle management, i18n pattern expansion and validation,
  static step contract validation, ecosystem integration helpers
  (`behave-kit`, `behave-tables`, `behave-data`).
- **API module** (`steplib.modules.api`): 54 HTTP testing steps with stdlib
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
