---
name: Bug report
about: Report a bug in behave-steplib
title: "[BUG] "
labels: bug
assignees: ""
---

## Describe the bug

A clear and concise description of what the bug is.

## To reproduce

Steps to reproduce the behavior:

1. Set up `features/environment.py` with: `from steplib.behave import autoload`
2. Feature file: `...`
3. Run: `behave features/`
4. See error

**Minimal reproduction** (feature file + environment.py):

```gherkin
# Paste your .feature file here
```

```python
# Paste your environment.py here
```

## Expected behavior

What you expected to happen.

## Actual behavior

What actually happened.

## Environment

- Python version: [e.g. 3.12.4]
- Behave version: [e.g. 1.3.3]
- behave-steplib version: [e.g. 1.0.0]
- Installed extras: [e.g. api, requests, web, db, kafka, all]
- OS: [e.g. Windows 11, Ubuntu 24.04]

## Additional context

Any other context about the problem (logs, screenshots, etc.).
