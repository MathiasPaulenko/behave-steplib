# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.x.x   | Yes       |

## Reporting a vulnerability

If you discover a security vulnerability in `behave-steplib`, please report it responsibly.

**Do not open a public GitHub issue.**

Instead, email **<security@paulenko.dev>** with:

1. A description of the vulnerability
2. Steps to reproduce (minimal example)
3. Potential impact
4. Suggested fix (if any)

You will receive a response within 48 hours. If the vulnerability is confirmed, a fix will be released as soon as possible and you will be credited (unless you prefer to remain anonymous).

## Security considerations

### What behave-steplib does

- Registers behave step definitions via `behave.use_step_matcher` and `@step` decorators
- Discovers step modules through `steplib.plugins` entry points and `autoload(context)`
- Parses step arguments with the `parse` library
- Provides optional integrations (`httpx`, `selenium`, `sqlalchemy`, `kafka-python-ng`) activated only when the corresponding extra is installed

### What behave-steplib does NOT do

- Does not execute arbitrary code from feature files beyond behave's normal step execution
- Does not modify files on disk (the CLI `init` command writes a single `environment.py` only when explicitly invoked)
- Does not make network requests on its own (network calls happen only inside user-invoked `api`/`web`/`kafka` steps)
- Does not access environment variables or secrets

### Optional dependencies

Each technology extra (`api`, `web`, `db`, `kafka`) is isolated behind lazy imports. Installing `behave-steplib` without extras pulls none of the integration packages, reducing the attack surface. Keep installed extras limited to what your project actually uses.

### Step argument parsing

Step arguments are parsed with the `parse` library using strict type converters. Invalid inputs surface as behave step failures rather than producing silent, unexpected behavior.

### Reporting integration issues

Vulnerabilities in third-party packages (`httpx`, `selenium`, `sqlalchemy`, `kafka-python-ng`) should be reported upstream. Report here only if `behave-steplib` exposes or mishandles them in a way that increases risk.
