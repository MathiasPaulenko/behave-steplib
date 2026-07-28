CLI Module
==========

The CLI module provides steps for shell command execution with
``subprocess``, capturing exit code, stdout and stderr — 10 steps in
total, all with ``es`` and ``pt`` translations.

Installation
------------

The CLI module has no third-party dependencies. It uses only the Python
standard library (``subprocess``, ``re``). No extra is needed — the CLI
module is always available when steplib is installed.

Context
-------

The :class:`~steplib.modules.cli.context.CLIContext` lives at
``context.steplib.cli``. It holds:

- ``exit_code`` — the exit code of the last executed command (``int | None``).
- ``stdout`` — the stdout output of the last command (``str``).
- ``stderr`` — the stderr output of the last command (``str``).
- ``variables`` — a ``dict[str, Any]`` for stored command outputs.

.. code-block:: python

   def before_all(context):
       context.steplib = autoload(context)

   def before_scenario(context, scenario):
       context.steplib.reset()  # clears exit_code, stdout, stderr, variables

   def after_scenario(context, scenario):
       context.steplib.cleanup()  # same as reset

Steps
-----

Command execution
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I run the command {command}``
     - Run a shell command and store exit code, stdout and stderr.
   * - ``I run the command {command} with timeout {timeout:d} seconds``
     - Run a shell command with a timeout (raises on expiry).

Exit code assertions
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``the command exit code is {code:d}``
     - Assert that the last command's exit code equals a value.

Stdout assertions
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``the command output contains {text}``
     - Assert that stdout contains the given text.
   * - ``the command output does not contain {text}``
     - Assert that stdout does NOT contain the given text.
   * - ``the command output equals {text}``
     - Assert that stdout equals the given text.
   * - ``the command output matches the pattern {pattern}``
     - Assert that stdout matches a regex pattern.

Stderr assertions
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``the command stderr contains {text}``
     - Assert that stderr contains the given text.

Store operations
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I store the command output as {variable}``
     - Store the last command's stdout into a variable.
   * - ``I store the command error output as {variable}``
     - Store the last command's stderr into a variable.

Example
-------

.. code-block:: gherkin

   Feature: CLI command testing

     Scenario: Run and assert output
       When I run the command "echo hello"
       Then the command exit code is 0
       And the command output contains "hello"
       And the command output does not contain "error"
       And the command output matches the pattern "hell."
       When I store the command output as "result"
       Then the variable "result" contains "hello"

     Scenario: Error output
       When I run the command "echo error 1>&2"
       Then the command exit code is 0
       And the command stderr contains "error"
       When I store the command error output as "errors"
       Then the variable "errors" contains "error"

     Scenario: Timeout
       When I run the command "sleep 10" with timeout 1 seconds
       # raises subprocess.TimeoutExpired

API reference
-------------

See :doc:`/api/modules` for the full autodoc reference of the CLI module.
