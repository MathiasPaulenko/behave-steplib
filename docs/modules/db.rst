DB Module
=========

The DB module provides steps for testing databases with SQLAlchemy. It
covers connection configuration, query execution (with and without bind
parameters), result assertions, column assertions, transaction
management, table assertions and store/extract operations — 22 steps
in total, all with ``es`` and ``pt`` translations.

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

Connection management
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Pattern
     - Description
   * - ``I connect to the database``
     - Create a database connection from the stored connection string.
   * - ``I disconnect from the database``
     - Close the database connection and dispose the engine.

Queries
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I execute the SQL query {query}``
     - Execute a SQL query and store the result in ``variables["_last_result"]``.
   * - ``I execute the SQL query {query} with params {params}``
     - Execute a SQL query with bind parameters (JSON dict) and store the result.

Row count assertions
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``the query returns {count:d} rows``
     - Assert the last query returned a specific number of rows.
   * - ``the query returns more than {count:d} rows``
     - Assert the query returns more than a specific number of rows.
   * - ``the query returns fewer than {count:d} rows``
     - Assert the query returns fewer than a specific number of rows.

Column assertions
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``the column {column} in the first row equals {value}``
     - Assert a column value in the first row of the last query.
   * - ``the column {column} in the first row does not equal {value}``
     - Assert a column value does NOT equal a value.
   * - ``the column {column} in the first row contains {value}``
     - Assert a column value contains a substring.
   * - ``the column {column} in the first row is null``
     - Assert a column value in the first row is NULL.
   * - ``the column {column} in the first row is not null``
     - Assert a column value in the first row is NOT NULL.
   * - ``the scalar query {query} equals {value}``
     - Execute a scalar query and assert the result equals a value.

Table assertions
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Pattern
     - Description
   * - ``the table {table} exists``
     - Assert that a table exists in the database.
   * - ``the table {table} has {count:d} rows``
     - Assert that a table has a specific number of rows.

Transactions
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Pattern
     - Description
   * - ``I begin a database transaction``
     - Begin a transaction on the current database connection.
   * - ``I rollback the database transaction``
     - Rollback the current database transaction.
   * - ``I commit the database transaction``
     - Commit the current database transaction.

Store and extract
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I store the column {column} from the first row as {variable}``
     - Store a column value from the last query result as a variable.
   * - ``I store the row count as {variable}``
     - Store the row count of the last query as a variable.
   * - ``I store the scalar query {query} as {variable}``
     - Execute a scalar query and store the result as a variable.

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
