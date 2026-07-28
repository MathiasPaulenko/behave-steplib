# behave-steplib

Reusable step libraries for [Behave](https://github.com/behave/behave) BDD — share, discover and install step definitions across projects. Zero mandatory dependencies; each technology is an optional extra.

[![CI](https://github.com/MathiasPaulenko/behave-steplib/actions/workflows/ci.yml/badge.svg)](https://github.com/MathiasPaulenko/behave-steplib/actions/workflows/ci.yml)
[![Release](https://github.com/MathiasPaulenko/behave-steplib/actions/workflows/release.yml/badge.svg)](https://github.com/MathiasPaulenko/behave-steplib/actions/workflows/release.yml)
[![PyPI](https://img.shields.io/pypi/v/behave-steplib.svg)](https://pypi.org/project/behave-steplib/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why behave-steplib?

Writing BDD step definitions for HTTP APIs, web browsers, databases and Kafka is repetitive. Every project re-implements the same "send a request", "check the status code", "query the database" steps. behave-steplib provides a curated, typed, multilingual library of reusable steps that you install once and share across projects.

- **Modular** — `api`, `web`, `db`, `kafka` modules activated via extras and lazy imports. Install only what you need.
- **Auto-registered** — `autoload(context)` discovers every installed step via Python entry points and registers it with behave in one line.
- **Multilingual** — steps defined in English with `es` and `pt` translations; all patterns are registered with behave so matching works regardless of the language used in feature files.
- **Typed** — full type hints, `mypy --strict` clean, `py.typed` marker included.
- **CLI** — `steplib list / show / validate / init` powered by Typer for inspecting and validating your step library from the terminal.
- **Pluggable** — third-party packages can register steps via the `steplib.plugins` entry point group; `autoload` discovers them automatically.
- **Ecosystem** — integrates with `behave-kit` (soft assertions), `behave-tables` (table conversion) and `behave-data` (test data loading) when installed.
- **Backends** — each module supports multiple backends (e.g. stdlib/httpx/requests for API, selenium for web) selectable at autoload time.

## Installation

```bash
pip install behave-steplib            # core only (behave, parse, typer)
pip install behave-steplib[api]       # + httpx HTTP client
pip install behave-steplib[requests]  # + requests HTTP client
pip install "behave-steplib[api,requests,web,db,kafka]"  # + all technology extras
pip install "behave-steplib[all]"     # + every technology extra
pip install behave-steplib[dev]       # + pytest, ruff, mypy, build, twine
```

| Extra | Packages | Description |
|-------|----------|-------------|
| `[api]` | `httpx` | HTTP API testing with httpx |
| `[requests]` | `requests` | HTTP API testing with requests |
| `[web]` | `selenium` | Browser testing with Selenium |
| `[db]` | `sqlalchemy` | Database testing with SQLAlchemy |
| `[kafka]` | `kafka-python-ng` | Kafka producer/consumer testing |
| `[kit]` | `behave-kit` | Soft assertions, typed context, fixtures |
| `[data]` | `behave-data` | Test data loading (CSV, JSON, YAML, Excel) |
| `[tables]` | `behave-tables` | Table conversion helpers |
| `[dev]` | pytest, ruff, mypy, build, twine | Development tools |
| `[docs]` | sphinx, furo, myst-parser, sphinx-autodoc-typehints | Documentation tools |
| `[all]` | api, requests, web, db, kafka, kit, data, tables | Everything except dev/docs |

## Requirements

- **Python 3.11+** (tested on CPython 3.11, 3.12, 3.13 and 3.14)
- **behave** — the only mandatory runtime dependency alongside `parse` and `typer`

## Quickstart

### Level 1 — Automatic wiring

Add three hooks to your `environment.py` and every installed step is wired automatically:

```python
# features/environment.py
from steplib.behave import autoload

def before_all(context):
    context.steplib = autoload(context)

def before_scenario(context, scenario):
    context.steplib.reset()

def after_scenario(context, scenario):
    context.steplib.cleanup()
```

Or generate it with the CLI:

```bash
steplib init
```

### Level 2 — Explicit load

Load only the modules you need by dotted path:

```python
from steplib.behave import load

def before_all(context):
    context.steplib = load(context, "steplib.modules.api.steps")
```

### Level 3 — Filtered autoload

When multiple extras are installed, narrow which steps are active:

```python
from steplib.behave import autoload

def before_all(context):
    context.steplib = autoload(
        context,
        categories=["api"],
        backends={"api": "httpx"},
    )
```

### Example feature

```gherkin
Feature: API health check

  Scenario: GET users returns 200
    Given the API base url is "https://api.example.com"
    When I send a GET request to "/users"
    Then the response status is 200
    And the response body is valid JSON
    And the JSON path "$.users[0].name" equals "Ada"
```

### Multilingual features

Steps are defined in English and translated to Spanish and Portuguese. All patterns are registered with behave — no language switch needed:

```gherkin
# es
Cuando envío una petición GET a "/users"
Entonces el estado de la respuesta es 200

# pt
Quando envio uma requisição GET para "/users"
Então o status da resposta é 200
```

## Modules

### API

HTTP API testing with stdlib (urllib), httpx or requests backends. **55 steps** covering configuration, authentication, SSL/redirects, requests (body, form, JSON, query params, headers), status/body/JSON Path/header/response-time assertions, store/extract, variable reuse and table comparison.

```gherkin
Given the API base url is "https://api.example.com"
And I set the bearer token to "eyJhbGciOi..."
When I send a POST request to "/users" with JSON body
  """
  {"name": "Ada", "email": "ada@example.com"}
  """
Then the response status is 201
And the JSON path "$.id" is not null
And the response time is less than 5 seconds
And I store the JSON path "$.id" as "user_id"
```

### Web

Browser testing with Selenium (Chrome, Firefox, headless). **34 steps** covering configuration, navigation, interactions (click, type, clear, select, screenshot), waits, assertions (title, URL, element presence/visibility/enabled/text/attribute, page content), cookies, frame switching and store/extract.

```gherkin
Given the web base url is "https://example.com"
When I navigate to "/login"
And I type "admin" into the element id "username"
And I type "secret" into the element id "password"
And I click the element id "submit"
Then the page title is "Dashboard"
And the element id "welcome" is visible
And I store the text of element id "username" as "displayed_name"
```

### DB

Database testing with SQLAlchemy (SQLite, PostgreSQL, MySQL, ...). **22 steps** covering connection management, query execution (with bind parameters), row count assertions, column assertions (equals, not equals, contains, null, not null), scalar queries, table assertions, transactions and store/extract.

```gherkin
Given the database connection string is "sqlite:///test.db"
When I connect to the database
And I execute the SQL query "SELECT * FROM users"
Then the query returns 3 rows
And the column "name" in the first row equals "Ada"
And the column "email" in the first row contains "@"
And I store the column "id" from the first row as "user_id"
```

### Kafka

Kafka producer and consumer testing with kafka-python-ng. **20 steps** covering bootstrap/group/offset configuration, producer/consumer config overrides, message production (single, JSON, batch from table), consumption (with optional timeout), assertions (count, contains, key/value by index, regex, order) and store/extract.

```gherkin
Given the Kafka bootstrap servers are "localhost:9092"
And the Kafka consumer group is "test-group"
When I produce a message to topic "events" with key "id" and value "hello"
And I consume messages from topic "events" with timeout 10000 ms
Then the consumed messages count is 1
And the message at index 0 has value "hello"
And I store the message count as "total_messages"
```

## CLI

```bash
steplib list                         # list all registered steps
steplib list --category api          # filter by category
steplib list --backend httpx         # filter by backend
steplib list --json                  # output as JSON
steplib show "I send a {method} request to {url}"
steplib validate                     # validate step contracts
steplib init                         # generate features/environment.py
```

## Writing custom steps

Use the `@step` decorator to define your own steps with full metadata:

```python
from steplib import Param, step

@step(
    "the invoice total is {total:f}",
    category="invoice",
    description="Assert the invoice total matches.",
    parameters=[Param("total", type=float, required=True)],
    example='Then the invoice total is 19.99',
    i18n={
        "es": "el total de la factura es {total:f}",
        "pt": "o total da fatura é {total:f}",
    },
    tags=["invoice"],
    version="1.0.0",
)
def step_invoice_total(context, total):
    assert context.invoice.total == total
```

Register steps in a `register(registry)` function and declare an entry point:

```toml
# pyproject.toml
[project.entry-points."steplib.plugins"]
mycompany = "mycompany.steps:register"
```

Once installed, `autoload(context)` discovers your package automatically.

## Development

```bash
make dev        # install with api, requests, dev and docs extras
make lint       # ruff + mypy --strict
make test-cov   # pytest with >=80% coverage gate
make docs-build # build Sphinx documentation
make build      # build sdist + wheel
```

## Documentation

Full documentation is available at <https://mathiaspaulenko.github.io/behave-steplib>.

## Acknowledgements

- [Behave](https://github.com/behave/behave) — the BDD framework this library extends.
- [parse](https://github.com/r1chardj0n3s/parse) — pattern matching for step definitions.
- [Typer](https://typer.tiangolo.com/) — CLI framework.
- [Sphinx](https://www.sphinx-doc.org/) + [furo](https://pradyunsg.me/furo/) — documentation.

## License

MIT — see [LICENSE](LICENSE).
