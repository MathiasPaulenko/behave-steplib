# Contributing to behave-steplib

Thank you for your interest in contributing to `behave-steplib`! This document outlines the process for contributing to the project.

## Getting started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/<your-username>/behave-steplib.git`
3. Install in development mode: `pip install -e ".[api,requests,dev,docs]"`
4. Create a branch: `git checkout -b my-feature`

## Development workflow

### Code style

- **Linter**: `make lint` (runs `ruff check .` and `mypy steplib`) — must pass with no errors
- **Type checker**: `mypy --strict` on `steplib` — must pass with no errors
- **Line length**: 100 characters
- **Python version**: 3.11+ (use `from __future__ import annotations` for forward refs)
- **Imports**: Sorted with `ruff` (isort rules enabled)

### Testing

- All new code must have unit tests
- Integration and e2e tests live under `tests/integration/` and `tests/e2e/`
- Run the full suite before pushing:

```bash
make test
```

- Check coverage:

```bash
make test-cov
```

Coverage must stay >= 80%.

### Type safety

- All public APIs must have type hints
- `mypy --strict` must pass — no `Any` without justification, no untyped functions
- The package ships a `py.typed` marker; keep public signatures stable

### Design principles

- **Modular**: Each technology (`api`, `web`, `db`, `kafka`) is an optional extra with lazy imports
- **Zero mandatory dependencies**: Core depends only on `behave`, `parse` and `typer`
- **Auto-registered**: Steps register themselves via plugin entry points and `autoload(context)`
- **Multilingual**: Steps are defined in English with `es` and `pt` translations registered with behave
- **Typed**: Full type hints, `mypy --strict` clean, `py.typed` marker included

## Pull request process

1. **Create an issue first** for new features or breaking changes — discuss before implementing
2. **Write tests** for your changes — unit tests for logic, integration/e2e tests for behave interaction
3. **Run all checks**:

   ```bash
   make lint
   make test-cov
   make check-dist
   ```

4. **Keep PRs focused** — one feature or fix per PR
5. **Update documentation** if your change affects the public API (README and `docs/`)
6. **Add translations** for any new step in `es` and `pt` when applicable
7. **Use conventional commit messages**:

   - `feat: add kafka producer step`
   - `fix: preserve i18n patterns on reload`
   - `docs: update api module reference`
   - `test: add e2e tests for web module`
   - `refactor: simplify autoload discovery`

8. **Fill out the PR template** — all sections must be completed

## Project structure

```text
steplib/                   # Source code
├── __init__.py            # Public exports
├── behave.py              # autoload(), load() integration with behave
├── core/                  # Registry, step metadata, i18n, plugin discovery
├── cli/                   # steplib CLI (Typer): list / show / validate / init
└── modules/               # Technology step modules (optional extras)
    ├── api/               # HTTP steps (httpx/requests/stdlib) (extra: api, requests)
    ├── web/               # selenium-based UI steps  (extra: web)
    ├── db/                # sqlalchemy DB steps      (extra: db)
    └── kafka/             # kafka steps              (extra: kafka)

tests/
├── unit/                  # Unit tests
├── integration/           # Integration tests
└── e2e/                   # End-to-end behave runs

docs/                      # Sphinx + furo documentation
ref/                       # Reference documents (not shipped)
```

## Reporting bugs

Use the bug report issue template. Include:

- Python version
- Behave version
- behave-steplib version and installed extras
- Minimal reproduction (feature file + environment.py)
- Expected vs actual behavior

## Suggesting features

Use the feature request issue template. Explain:

- The use case
- Which extra/module it belongs to
- Whether it requires new dependencies
- Whether it needs multilingual translations

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
