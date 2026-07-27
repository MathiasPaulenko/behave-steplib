Quickstart
==========

A complete walkthrough from install to running your first feature.

1. Install
----------

.. code-block:: bash

   pip install "behave-steplib[api]"

2. Set up your environment
--------------------------

Create ``features/environment.py``:

.. code-block:: python

   from steplib.behave import autoload

   def before_all(context):
       context.steplib = autoload(context)

   def before_scenario(context, scenario):
       context.steplib.reset()

   def after_scenario(context, scenario):
       context.steplib.cleanup()

Or generate it with the CLI:

.. code-block:: bash

   steplib init

This writes ``features/environment.py`` with the scaffold above.

3. Write a feature
------------------

.. code-block:: gherkin

   Feature: API health check

     Scenario: GET users returns 200
       Given the API base url is "https://api.example.com"
       When I send a GET request to "/users"
       Then the response status is 200
       And the response body is valid JSON
       And the JSON path "$.users[0].name" equals "Ada"

4. Run
------

.. code-block:: bash

   behave

Loading specific modules
------------------------

If you prefer to load only specific modules instead of auto-discovering all
installed plugins:

.. code-block:: python

   from steplib.behave import load

   def before_all(context):
       context.steplib = load(context, "steplib.modules.api.steps")

You can pass multiple module paths:

.. code-block:: python

   def before_all(context):
       context.steplib = load(
           context,
           "steplib.modules.api.steps",
           "steplib.modules.db.steps",
       )

Filtering by category or backend
--------------------------------

``autoload`` accepts optional filters to narrow which steps are registered
with behave. This is useful when you have multiple extras installed but only
want a subset active in a given run.

.. code-block:: python

   from steplib.behave import autoload

   def before_all(context):
       context.steplib = autoload(
           context,
           categories=["api"],
           backends={"api": "httpx"},
       )

- ``categories`` — only keep steps whose ``category`` is in the list.
- ``backends`` — mapping of category to backend name; only keep steps whose
  ``backend`` matches. Steps without a backend are always kept.

Multilingual features
---------------------

Steps are defined in English and translated to Spanish and Portuguese. All
patterns are registered with behave simultaneously, so you can mix languages
in the same project without configuration:

.. code-block:: gherkin

   # English
   When I send a GET request to "/users"

   # Spanish
   Cuando envío una petición GET a "/users"

   # Portuguese
   Quando envio uma requisição GET para "/users"

See :doc:`/i18n` for details on adding translations.

Next steps
----------

- :doc:`/autoload` — full reference for ``autoload`` and ``load``.
- :doc:`/cli` — inspect and validate your step library from the terminal.
- :doc:`/modules/api` — complete API step reference.
