behave-steplib
==============

Reusable step libraries for `Behave <https://github.com/behave/behave>`_ — share,
discover and install step definitions across projects. Zero mandatory
dependencies; each technology is an optional extra.

behave-steplib provides a modular, auto-registered collection of BDD step
definitions for HTTP APIs, web browsers, databases, Kafka and generic data
management. Steps are defined in English with Spanish (``es``) and Portuguese
(``pt``) translations, fully typed, and discoverable via Python entry points.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: Guide

   autoload
   cli
   i18n
   step_contract
   architecture

.. toctree::
   :maxdepth: 2
   :caption: Modules

   modules/api
   modules/web
   modules/db
   modules/kafka
   modules/data
   modules/io
   modules/cli

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api/core
   api/modules
   changelog


Features at a glance
--------------------

- **Modular** — ``api``, ``web``, ``db``, ``kafka``, ``data``, ``io``, ``cli`` modules activated via extras and lazy imports.
- **Auto-registered** — ``autoload(context)`` registers every installed step in one line.
- **Multilingual** — steps defined in English with ``es`` and ``pt`` translations; all patterns are registered with behave so matching works regardless of active language.
- **Typed** — full type hints, ``mypy --strict`` clean, ``py.typed`` marker included.
- **CLI** — ``steplib list / show / search / validate / init / install`` powered by Typer.
- **Pluggable** — third-party packages can register steps via the ``steplib.plugins`` entry point group.
- **Ecosystem** — integrates with ``behave-kit``, ``behave-tables`` and ``behave-data`` when installed.
- **Backends** — each module supports multiple backends (e.g. stdlib/httpx/requests for API, selenium for web) selectable at autoload time.

Three adoption levels
---------------------

**Level 1 — Automatic wiring:**

.. code-block:: python

   from steplib.behave import autoload

   def before_all(context):
       context.steplib = autoload(context)

   def before_scenario(context, scenario):
       context.steplib.reset()

   def after_scenario(context, scenario):
       context.steplib.cleanup()

**Level 2 — Explicit load:**

.. code-block:: python

   from steplib.behave import load

   def before_all(context):
       context.steplib = load(context, "steplib.modules.api.steps")

**Level 3 — Filtered autoload:**

.. code-block:: python

   from steplib.behave import autoload

   def before_all(context):
       context.steplib = autoload(
           context,
           categories=["api"],
           backends={"api": "httpx"},
       )

Installation
------------

.. code-block:: bash

   pip install behave-steplib

With optional extras:

.. code-block:: bash

   pip install "behave-steplib[api,requests,web,db,kafka,data,io]"

License
-------

MIT — see `LICENSE <https://github.com/MathiasPaulenko/behave-steplib/blob/main/LICENSE>`_.
