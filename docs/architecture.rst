Architecture
============

Overview
--------

behave-steplib is organised in layers:

.. code-block:: text

   ┌──────────────────────────────────────────────────┐
   │                environment.py                     │
   │   autoload(context) / load(context, *modules)     │
   └───────────────────────┬──────────────────────────┘
                           │
   ┌───────────────────────▼──────────────────────────┐
   │                    steplib.behave                  │
   │   Thin wrappers: autoload, load, before_all,      │
   │   after_scenario                                   │
   └───────────────────────┬──────────────────────────┘
                           │
   ┌───────────────────────▼──────────────────────────┐
   │                steplib.core                       │
   │  Registry · Discovery · Decorators · Metadata ·   │
   │  i18n · Params · State · Validation · Ecosystem   │
   └───────────────────────┬──────────────────────────┘
                           │ entry points (steplib.plugins)
   ┌───────────────────────▼──────────────────────────┐
   │                steplib.modules                     │
   │    api · web · db · kafka                         │
   │  Each module: steps · actions · context · client  │
   └──────────────────────────────────────────────────┘

Core package (``steplib.core``)
-------------------------------

The core package contains the infrastructure that is independent of any
specific technology:

- **``decorators``** — the ``@step`` decorator and ``get_step_infos`` helper.
  Attaches :class:`StepInfo` metadata to functions.
- **``metadata``** — the :class:`StepInfo` frozen dataclass.
- **``params``** — the :class:`Param` dataclass, built-in type names and the
  :class:`TypeRegistry` for custom types.
- **``registry``** — :class:`StepRegistry`, the central store for step
  metadata. Optionally registers patterns with behave.
- **``discovery``** — ``autoload`` and ``load``; discovers plugins via entry
  points and populates a registry.
- **``i18n``** — pattern expansion and consistency validation for
  translations.
- **``state``** — :class:`SteplibState`, attached to ``context.steplib``;
  holds the registry and module namespaces.
- **``validation``** — static validation of step contracts.
- **``ecosystem``** — lazy integration with ``behave-kit``, ``behave-tables``
  and ``behave-data``.
- **``exceptions``** — ``SteplibError``, ``MissingDependencyError``,
  ``DuplicateStepError``, ``StepContractError``.

Module pattern (``steplib.modules.*``)
--------------------------------------

Each technology module follows the same four-file pattern:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - File
     - Responsibility
   * - ``steps.py``
     - Step definitions (``@step`` decorators) and ``register(registry)``.
       Thin wrappers that delegate to ``actions.py``.
   * - ``actions.py``
     - Pure action functions operating on the module's context. Fully
       testable without behave.
   * - ``context.py``
     - Per-scenario state dataclass (e.g. :class:`ApiContext`). Holds
       configuration, last request/response, variables. Exposes ``reset()``
       and ``cleanup()``.
   * - ``client.py``
     - Backend abstraction with a ``Protocol`` and one or more lazy-loaded
       implementations (e.g. ``UrllibHTTPClient``, ``HttpxHTTPClient``,
       ``RequestsHTTPClient``).

This separation ensures that step definitions are thin, logic is testable,
and backends are swappable.

Discovery flow
--------------

1. ``autoload(context)`` creates a :class:`StepRegistry`.
2. It loads every entry point in the ``steplib.plugins`` group.
3. Each entry point's ``register(registry)`` function is called, which adds
   decorated step functions to the registry.
4. The registry expands i18n patterns, checks for duplicates and optionally
   registers each pattern with behave via ``behave.step(pattern)(fn)``.
5. Optional ``categories`` / ``backends`` filters narrow the registry.
6. A :class:`SteplibState` is created and returned.

Backend selection
-----------------

Each module can support multiple backends. For example, the API module
supports:

- **stdlib** (``urllib``) — default, no extra dependencies.
- **httpx** — requires the ``[api]`` extra.
- **requests** — requires the ``[requests]`` extra.

Backends are differentiated by the ``backend`` field on :class:`StepInfo`.
When using ``autoload``, you can select which backend to activate per
category:

.. code-block:: python

   autoload(context, backends={"api": "httpx"})

Without explicit filters, all backends are registered. Steps without a
``backend`` value are always kept.

Plugin extension
----------------

Third-party packages can extend behave-steplib by declaring an entry point in
the same group:

.. code-block:: toml

   # pyproject.toml of a third-party package
   [project.entry-points."steplib.plugins"]
   mycompany = "mycompany.steps:register"

The ``register`` function receives a :class:`StepRegistry` and adds steps
using the standard ``@step`` decorator:

.. code-block:: python

   # mycompany/steps.py
   from steplib import step

   @step("the invoice total is {total:f}", category="invoice")
   def step_invoice_total(context, total):
       ...

   def register(registry):
       registry.add(step_invoice_total)

Once the package is installed, ``autoload(context)`` discovers it
automatically.

API reference
-------------

See :doc:`/api/core` for the full autodoc reference of ``steplib.core.registry``,
``steplib.core.state`` and ``steplib.core.exceptions``.
