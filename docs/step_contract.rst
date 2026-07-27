Step Contract
=============

A behave-steplib step is a regular Python function decorated with
``@steplib.step``. The decorator attaches structured metadata
(:class:`~steplib.core.metadata.StepInfo`) used for documentation, validation
and the CLI, while delegating to behave's native step registration under the
hood.

Design principles
-----------------

- **Cohesive** — a step does one action or one assertion.
- **Pure logic** — the implementation delegates to action functions; it
  contains no selectors, queries or protocol details.
- **Parameterisable** — every relevant constant enters via the pattern or
  ``context.config.userdata``.

The ``@step`` decorator
-----------------------

.. code-block:: python

   from steplib import Param, step

   @step(
       "I send a {method} request to {url}",
       category="api",
       backend="httpx",
       description="Send an HTTP request and store the response.",
       parameters=[
           Param("method", type=str, required=True, default="GET",
                 description="HTTP method (GET, POST, PUT, PATCH, DELETE)."),
           Param("url", type=str, required=True,
                 description="Request URL (relative URLs resolve against base_url)."),
       ],
       example='When I send a GET request to "/users"',
       i18n={
           "es": "envío una petición {method} a {url}",
           "pt": "envio uma requisição {method} para {url}",
       },
       tags=["api", "http"],
       version="1.0.0",
   )
   def step_send_request(context, method, url):
       ...

Stacked decorators
~~~~~~~~~~~~~~~~~~

The same step can expose multiple patterns (one per language or per backend)
by applying the decorator multiple times on the same function. Each call
generates an independent :class:`~steplib.core.metadata.StepInfo` entry while
sharing the implementation:

.. code-block:: python

   @step("I send a {method} request to {url}", backend="httpx", category="api")
   @step("I send a {method} request to {url}", backend="requests", category="api")
   def step_send_request(context, method, url):
       ...

When declaring multiple backends for the same concept, use ``backend`` to
differentiate them and let ``autoload`` filter the active variant.

Metadata fields
---------------

.. list-table::
   :header-rows: 1
   :widths: 18 12 70

   * - Field
     - Required
     - Description
   * - ``pattern``
     - Yes
     - Matching pattern for behave (``parse`` / ``cfparse`` / ``re``).
   * - ``category``
     - Yes
     - Module or domain: ``api``, ``web``, ``db``, ``kafka``, ...
   * - ``description``
     - Recommended
     - Human-readable explanation. Defaults to the function docstring.
   * - ``parameters``
     - Optional
     - List of typed :class:`~steplib.core.params.Param` descriptors.
   * - ``example``
     - Recommended
     - Example usage in Gherkin.
   * - ``tags``
     - Optional
     - Tags for grouping and filtering in the CLI.
   * - ``version``
     - Optional
     - Semantic version of the step.
   * - ``deprecated``
     - Optional
     - ``True``, a deprecation message, or ``False`` (default).
   * - ``backend``
     - Optional
     - Underlying technology: ``httpx``, ``requests``, ``urllib``,
       ``sqlalchemy``, ``selenium``, ``kafka-python-ng``, ...
   * - ``i18n``
     - Optional
     - Translations of the pattern keyed by language code.
   * - ``requires``
     - Optional
     - Context attributes the step needs (e.g. ``["steplib.api.client"]``).

Parameter types (``Param``)
---------------------------

.. code-block:: python

   from steplib.core import Param

   Param(
       name="method",
       type=str,               # or a registered type name like "HttpMethod"
       required=True,
       default="GET",
       description="HTTP method (GET, POST, PUT, PATCH, DELETE).",
       choices=["GET", "POST", "PUT", "PATCH", "DELETE"],
   )

Built-in type names usable in patterns:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Name
     - Python type
   * - ``str``
     - ``str``
   * - ``int``
     - ``int``
   * - ``float``
     - ``float``
   * - ``bool``
     - ``bool``
   * - ``None``
     - ``NoneType``
   * - ``Json``
     - ``str`` (placeholder; real parsing via ``register_type``)
   * - ``Url``
     - ``str``
   * - ``HttpMethod``
     - ``str``
   * - ``Date``
     - ``str``
   * - ``Regex``
     - ``str``

Registering custom types
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from steplib.core import register_type

   register_type("Json", str)  # register a custom type name

Custom types are resolved by :func:`~steplib.core.params.resolve_type` when
validating parameter declarations.

Step function signature
-----------------------

The decorated function receives ``context`` followed by the parameters
extracted from the pattern, in the order they appear:

.. code-block:: python

   @step("I wait {seconds:d} seconds")
   def step_wait(context, seconds):
       ...

Optional parameters with defaults that do not appear in the pattern are
injected as keyword arguments:

.. code-block:: python

   @step("I wait a bit")
   def step_wait_default(context, seconds=1):
       ...

Context namespaces
------------------

Steps operate on ``context.steplib``. Each module reserves a namespace:

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Namespace
     - Class
     - Module
   * - ``context.steplib.api``
     - :class:`~steplib.modules.api.context.ApiContext`
     - ``steplib.modules.api``
   * - ``context.steplib.web``
     - :class:`~steplib.modules.web.context.WebContext`
     - ``steplib.modules.web``
   * - ``context.steplib.db``
     - :class:`~steplib.modules.db.context.DbContext`
     - ``steplib.modules.db``
   * - ``context.steplib.kafka``
     - :class:`~steplib.modules.kafka.context.KafkaContext`
     - ``steplib.modules.kafka``

Module namespaces are created lazily by each module's ``_get_*`` helper on
first use, and reset/closed by :class:`~steplib.core.state.SteplibState`
lifecycle methods.

Ecosystem integration
---------------------

Steps can leverage existing ecosystem libraries without duplicating
functionality:

- **``behave-kit``** — soft assertions, typed context, ``env``, fixtures,
  ``assert_json_equals``.
- **``behave-tables``** — convert ``context.table`` to dicts, columns, models.
- **``behave-data``** — load test data from CSV / JSON / YAML / Excel.

.. code-block:: python

   from behave_kit import assert_soft
   from behave_tables import wrap
   from steplib import step

   @step("the users should be", category="example")
   def step_check_users(context):
       expected = wrap(context.table).as_dicts()
       actual = context.steplib.api.last_response.json()
       for exp, act in zip(expected, actual, strict=False):
           assert_soft(exp == act)

Validation
----------

``steplib validate`` checks:

1. Each ``pattern`` is parseable by ``parse``.
2. Declared ``Param`` names match pattern placeholders.
3. No duplicate patterns within the same backend.
4. ``i18n`` translations have the same placeholders as the base pattern.
5. Stacked patterns share the same placeholders and order.
6. Each step has a ``category``.

API reference
-------------

See :doc:`/api/core` for the full autodoc reference of ``steplib.core.decorators``,
``steplib.core.metadata`` and ``steplib.core.params``.
