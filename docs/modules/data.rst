Data Module
===========

The data module provides generic, cross-module variable management and
environment variable handling. It fills a real gap: each technology module
(``api``, ``web``, ``db``, ``kafka``) has its own ``store``/``variables``
namespace, but without generic steps there is no way to share data across
modules or manage environment variables in a scenario-safe way.

The data module stores variables in ``context.steplib.data.variables`` and
tracks environment variable modifications so they are automatically restored
after each scenario — 26 steps in total, all with ``es`` and ``pt``
translations.

Installation
------------

The data module has no mandatory third-party dependencies. It uses only the
Python standard library (``json``, ``os``, ``pathlib``). YAML file loading
requires ``PyYAML`` to be installed separately:

.. code-block:: bash

   pip install pyyaml

No extra is needed — the data module is always available when steplib is
installed.

Context
-------

The :class:`~steplib.modules.data.context.DataContext` lives at
``context.steplib.data``. It holds:

- ``variables`` — a ``dict[str, Any]`` for user-defined variables.
- ``_env_backup`` — internal snapshot of environment variables modified
  during the scenario, so they are restored on ``reset()`` / ``cleanup()``.

.. code-block:: python

   def before_all(context):
       context.steplib = autoload(context)

   def before_scenario(context, scenario):
       context.steplib.reset()  # clears variables, restores env vars

   def after_scenario(context, scenario):
       context.steplib.cleanup()  # restores any modified env vars

Steps
-----

Variable management
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I set the variable {name} to {value}``
     - Set a generic variable in the data context.
   * - ``the variable {name} equals {value}``
     - Assert that a variable equals an expected value.
   * - ``the variable {name} does not equal {value}``
     - Assert that a variable does not equal a value.
   * - ``the variable {name} exists``
     - Assert that a variable exists.
   * - ``the variable {name} does not exist``
     - Assert that a variable does not exist.
   * - ``the variable {name} contains {text}``
     - Assert that a variable's string value contains a substring.
   * - ``the variable {name} is empty``
     - Assert that a variable is empty (empty string, list, dict, or None).
   * - ``the variable {name} is not empty``
     - Assert that a variable is not empty.
   * - ``the variable {name} has length {count:d}``
     - Assert that a variable has a specific length.
   * - ``I delete the variable {name}``
     - Delete a variable from the data context.
   * - ``I copy the variable {source} to {target}``
     - Copy a variable to a new name.
   * - ``I clear all variables``
     - Remove all variables from the data context.
   * - ``I set the variable {name} to the JSON {json}``
     - Set a variable to a parsed JSON value.

File loading
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I load the YAML file {path} into the variable {name}``
     - Load a YAML file and store the parsed content as a variable.
   * - ``I load the JSON file {path} into the variable {name}``
     - Load a JSON file and store the parsed content as a variable.
   * - ``I extract the key path {key_path} from the variable {name} as {target}``
     - Extract a value from a variable using dot-path navigation
       (e.g. ``user.address.city``). List indices are supported via
       integer keys (e.g. ``items.0.name``).

Environment variables
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I set the environment variable {key} to {value}``
     - Set an environment variable (restored after the scenario).
   * - ``I delete the environment variable {key}``
     - Delete an environment variable (restored after the scenario).
   * - ``the environment variable {key} equals {value}``
     - Assert that an environment variable equals an expected value.
   * - ``the environment variable {key} does not equal {value}``
     - Assert that an environment variable does not equal a value.
   * - ``the environment variable {key} exists``
     - Assert that an environment variable exists.
   * - ``the environment variable {key} does not exist``
     - Assert that an environment variable does not exist.
   * - ``I store the environment variable {key} as {variable}``
     - Store an environment variable's value into a data variable.
   * - ``I set the environment variable {key} from the variable {variable}``
     - Set an environment variable from a data variable's value.
   * - ``I load environment variables from file {path}``
     - Load environment variables from a ``.env``-style file.

Example
-------

.. code-block:: gherkin

   Feature: Data management

     Scenario: Set and assert variables
       Given I set the variable "user_id" to "42"
       Then the variable "user_id" equals "42"
       And the variable "user_id" exists
       And the variable "user_id" has length 2
       When I delete the variable "user_id"
       Then the variable "user_id" does not exist

     Scenario: Load and extract from JSON
       Given I load the JSON file "data/user.json" into the variable "user"
       When I extract the key path "address.city" from the variable "user" as "city"
       Then the variable "city" equals "Berlin"

     Scenario: Environment variables
       Given I set the environment variable "API_KEY" to "secret123"
       Then the environment variable "API_KEY" equals "secret123"
       And the environment variable "API_KEY" exists
       When I store the environment variable "API_KEY" as "api_key"
       Then the variable "api_key" equals "secret123"

Environment variable safety
----------------------------

All environment variable modifications (set, delete, load from file) are
tracked in an internal backup. When ``reset()`` or ``cleanup()`` is called
(typically from ``before_scenario`` / ``after_scenario``), the original
values are restored. This prevents test pollution between scenarios.

API reference
-------------

See :doc:`/api/modules` for the full autodoc reference of the data module.
