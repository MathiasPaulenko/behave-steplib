Autoload and Load
=================

The two entry points for integrating behave-steplib with your
``environment.py``.

``autoload(context)``
---------------------

Discovers all installed steplib plugins via Python entry points and registers
their steps with behave. Returns a :class:`~steplib.core.state.SteplibState`
attached to ``context.steplib``.

.. code-block:: python

   from steplib.behave import autoload

   def before_all(context):
       context.steplib = autoload(context)

Optional filters
~~~~~~~~~~~~~~~~

.. code-block:: python

   context.steplib = autoload(
       context,
       categories=["api"],           # only load API steps
       backends={"api": "httpx"},    # use httpx backend for API
   )

``categories``
    A list of category names to keep. Steps whose ``category`` is not in the
    list are removed from the registry before behave sees them.

``backends``
    A mapping of ``category → backend``. For each category present in the
    mapping, only steps whose ``backend`` matches the requested value are
    kept. Steps without a ``backend`` are always kept.

When both are ``None`` (the default), every installed plugin is loaded with
every backend.

``load(context, *modules)``
---------------------------

Imports specific step modules by dotted path. No entry point discovery is
performed — you explicitly name the modules to load.

.. code-block:: python

   from steplib.behave import load

   def before_all(context):
       context.steplib = load(
           context,
           "steplib.modules.api.steps",
           "steplib.modules.db.steps",
       )

Each module must expose a ``register(registry)`` function. If it does not,
an ``AttributeError`` is raised with a clear message.

Lifecycle hooks
---------------

The :class:`~steplib.core.state.SteplibState` object exposes two lifecycle
methods that should be called from behave hooks:

.. code-block:: python

   from steplib.behave import after_scenario, autoload

   def before_all(context):
       context.steplib = autoload(context)

   def before_scenario(context, scenario):
       context.steplib.reset()    # reset per-scenario state

   def after_scenario(context, scenario):
       after_scenario(context, scenario)  # close resources

``reset()``
    Iterates over all module-level attributes on the state (non-underscore)
    and calls ``reset()`` on each that has it. This clears per-scenario data
    such as the last HTTP response or the last query result, while keeping
    configuration (base URL, default headers, connection strings).

``cleanup()``
    Iterates over the same attributes and calls ``cleanup()`` on each that
    has it. This closes HTTP clients, browser drivers, database connections
    and Kafka producers/consumers.

You can also call ``context.steplib.cleanup()`` directly instead of importing
``after_scenario`` — both are equivalent.

How discovery works
-------------------

``autoload`` uses :func:`importlib.metadata.entry_points` to find all
packages that register steps under the ``steplib.plugins`` entry point group:

.. code-block:: toml

   [project.entry-points."steplib.plugins"]
   api = "steplib.modules.api.steps:register"
   web = "steplib.modules.web.steps:register"
   db = "steplib.modules.db.steps:register"
   kafka = "steplib.modules.kafka.steps:register"

Third-party packages can add their own entry points in the same group:

.. code-block:: toml

   [project.entry-points."steplib.plugins"]
   mycompany = "mycompany.steps:register"

When ``autoload`` runs, it loads every entry point in the group and calls
each ``register(registry)`` function. This means any package installed in the
environment that declares a ``steplib.plugins`` entry point is automatically
discovered — no manual imports needed.

API reference
-------------

See :doc:`/api/core` for the full autodoc reference of ``steplib.behave``
and ``steplib.core.state``.
