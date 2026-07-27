Installation
============

Basic install
-------------

.. code-block:: bash

   pip install behave-steplib

This installs the core package with ``behave``, ``parse`` and ``typer`` as the
only runtime dependencies. No HTTP client, browser driver, database engine or
Kafka library is pulled in unless you explicitly request the corresponding
extra.

Extras
------

Each technology module is an optional extra. Install only what your project
needs to keep the dependency surface small.

.. list-table::
   :header-rows: 1
   :widths: 15 30 55

   * - Extra
     - Packages
     - Description
   * - ``[api]``
     - ``httpx``
     - HTTP API testing with httpx (HTTP/2, async, cookies)
   * - ``[web]``
     - ``selenium``
     - Browser testing with Selenium (Chrome, Firefox, headless)
   * - ``[db]``
     - ``sqlalchemy``
     - Database testing with SQLAlchemy (SQLite, PostgreSQL, MySQL, ...)
   * - ``[kafka]``
     - ``kafka-python-ng``
     - Kafka producer and consumer testing
   * - ``[kit]``
     - ``behave-kit``
     - Soft assertions, typed context, fixtures, conditional skip
   * - ``[data]``
     - ``behave-data``
     - Test data loading from CSV, JSON, YAML and Excel files
   * - ``[tables]``
     - ``behave-tables``
     - Behave table conversion helpers (dicts, columns, models)
   * - ``[dev]``
     - pytest, ruff, mypy, build, twine, pre-commit
     - Development and CI tools
   * - ``[docs]``
     - sphinx, furo, myst-parser, sphinx-autodoc-typehints
     - Documentation build tools
   * - ``[all]``
     - api, web, db, kafka, kit, data, tables
     - Every technology extra (excludes dev and docs)

Examples
--------

.. code-block:: bash

   pip install behave-steplib[api]         # HTTP testing only
   pip install "behave-steplib[api,kit]"   # HTTP + soft assertions
   pip install "behave-steplib[all]"       # every technology extra
   pip install "behave-steplib[dev]"       # development tools
   pip install "behave-steplib[docs]"      # documentation build

Python version
--------------

behave-steplib requires **Python 3.11 or newer**. Tested on CPython 3.11,
3.12 and 3.13.

Verifying the installation
--------------------------

.. code-block:: bash

   python -c "import steplib; print(steplib.__version__)"

   steplib --help
