DB Module
=========

The DB module provides steps for testing databases with SQLAlchemy. It
covers connection configuration, query execution and result assertions.

Installation
------------

.. code-block:: bash

   pip install "behave-steplib[db]"

Backends
--------

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Backend
     - Package
     - Notes
   * - ``sqlalchemy``
     - ``sqlalchemy``
     - Supports SQLite, PostgreSQL, MySQL, Oracle and more via SQLAlchemy
       connection strings. Requires the ``[db]`` extra.

Steps
-----

Configuration
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``the database connection string is {connection_string}``
     - Set the SQLAlchemy connection string for database queries.

Queries
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``I execute the SQL query {query}``
     - Execute a SQL query and store the result in
       ``variables["_last_result"]``.

Assertions
~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``the query returns {count:d} rows``
     - Assert the last query returned a specific number of rows.
   * - ``the column {column} in the first row equals {value}``
     - Assert a column value in the first row of the last query.

Example
-------

.. code-block:: gherkin

   Feature: Database queries

     Scenario: Users table has expected data
       Given the database connection string is "sqlite:///test.db"
       When I execute the SQL query "SELECT * FROM users"
       Then the query returns 3 rows
       And the column "name" in the first row equals "Ada"

Connection lifecycle
--------------------

The :class:`~steplib.modules.db.context.DbContext` holds the SQLAlchemy
engine and connection. They are created lazily by
:class:`~steplib.modules.db.client.DatabaseClient` and closed by
``cleanup()``:

.. code-block:: python

   from steplib.modules.db.client import get_client

   def before_all(context):
       context.steplib = autoload(context)
       context.steplib.db.connection = get_client("sqlite:///test.db")

   def after_scenario(context, scenario):
       context.steplib.cleanup()  # closes the connection and disposes the engine

API reference
-------------

See :doc:`/api/modules` for the full autodoc reference of the DB module.
