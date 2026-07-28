IO Module
=========

The IO module provides steps for file, JSON, CSV and directory operations.
It covers file CRUD, file assertions, JSON path navigation and validation,
CSV writing and reading, directory management, and reading files as lines —
38 steps in total, all with ``es`` and ``pt`` translations.

Installation
------------

The IO module uses only the Python standard library (``json``, ``csv``,
``pathlib``). JSON Schema validation requires the ``jsonschema`` package:

.. code-block:: bash

   pip install "behave-steplib[io]"

No extra is needed for basic file, JSON, CSV and directory operations —
the IO module is always available when steplib is installed. Install the
``[io]`` extra to enable JSON Schema validation.

Context
-------

The :class:`~steplib.modules.io.context.IOContext` lives at
``context.steplib.io``. It holds:

- ``variables`` — a ``dict[str, Any]`` for user-defined variables.
- ``_last_json`` — the last loaded JSON object for path-based assertions.
- ``_csv_writer`` / ``_csv_file`` — active CSV writer and file handle.

.. code-block:: python

   def before_all(context):
       context.steplib = autoload(context)

   def before_scenario(context, scenario):
       context.steplib.reset()  # clears variables, closes CSV handles

   def after_scenario(context, scenario):
       context.steplib.cleanup()  # closes any open file handles

Steps
-----

File operations
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I read the file {path} as {variable}``
     - Read a text file and store its content as a variable.
   * - ``I write {content} to the file {path}``
     - Write content to a file (overwrites existing).
   * - ``I append {content} to the file {path}``
     - Append content to a file.
   * - ``I delete the file {path}``
     - Delete a file.
   * - ``I copy the file {source} to {target}``
     - Copy a file to a new location.
   * - ``I move the file {source} to {target}``
     - Move a file to a new location.
   * - ``I rename the file {source} to {target}``
     - Rename a file.
   * - ``I create an empty file {path}``
     - Create an empty file.
   * - ``I read the file {path} as lines into {variable}``
     - Read a file and store its lines as a list in a variable.

File assertions
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``the file {path} exists``
     - Assert that a file exists.
   * - ``the file {path} does not exist``
     - Assert that a file does not exist.
   * - ``the file {source} is the same as the file {target}``
     - Assert that two files have identical content.
   * - ``the file size of {path} is greater than {size:d} bytes``
     - Assert that a file's size is greater than a threshold.
   * - ``the file extension of {path} is {extension}``
     - Assert that a file has a specific extension.

Directory operations
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I create the directory {path}``
     - Create a directory, including parents if needed.
   * - ``the directory {path} exists``
     - Assert that a directory exists.
   * - ``the directory {path} does not exist``
     - Assert that a directory does not exist.
   * - ``I list the files in the directory {path} as {variable}``
     - List files in a directory and store them as a variable.
   * - ``I delete the directory {path}``
     - Delete a directory and all its contents.

JSON operations
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I load the JSON file {path}``
     - Load a JSON file into the context's last JSON object.
   * - ``I save the JSON to the file {path}``
     - Save the last JSON object to a file.
   * - ``the JSON path {path} equals {value}``
     - Assert that a JSON path equals a value.
   * - ``I store the JSON path {path} as {variable}``
     - Store a JSON path value into a variable.
   * - ``I update the JSON path {path} to {value}``
     - Update a JSON path value.
   * - ``I create the JSON path {path} with value {value}``
     - Create a new JSON path with a value.
   * - ``I delete the JSON path {path}``
     - Delete a JSON path.
   * - ``the JSON is valid``
     - Assert that the last loaded JSON is valid.
   * - ``the JSON matches the schema {schema_path}``
     - Assert that the last loaded JSON matches a JSON Schema file.
     - Requires the ``[io]`` extra (``jsonschema``).
   * - ``the last JSON is valid``
     - Assert that the last loaded JSON is valid by re-serializing it.
   * - ``the JSON path {path} has type {type}``
     - Assert that a JSON path has a specific type.
   * - ``I diff the JSON with {json}``
     - Diff the last JSON object with another JSON object.
   * - ``I merge the JSON with {json}``
     - Merge the last JSON object with another JSON object.

CSV operations
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I create the CSV file {path} with header {header}``
     - Create a CSV file with a header row.
   * - ``I create a CSV writer for the file {path}``
     - Create a CSV writer for incremental writing.
   * - ``I write the CSV row {row} to the file {path}``
     - Write a row to a CSV file.
   * - ``I save the CSV file``
     - Flush the active CSV writer without closing it.
   * - ``I set the header row {row:d} for the CSV file {path} as {variable}``
     - Read a CSV file using a specific row as the header and store
       rows in a variable.
   * - ``I close the CSV writer``
     - Close the active CSV writer.

Example
-------

.. code-block:: gherkin

   Feature: File and data operations

     Scenario: File CRUD
       Given I create the directory "output/logs"
       When I write "hello world" to the file "output/logs/test.txt"
       Then the file "output/logs/test.txt" exists
       And the file size of "output/logs/test.txt" is greater than 0 bytes
       When I read the file "output/logs/test.txt" as lines into "lines"
       Then the variable "lines" has length 1
       When I delete the directory "output"
       Then the directory "output" does not exist

     Scenario: JSON operations
       Given I load the JSON file "data/config.json"
       Then the JSON path "$.version" equals "1.0"
       And the JSON matches the schema "schemas/config.json"
       And the last JSON is valid
       When I store the JSON path "$.name" as "config_name"
       Then the variable "config_name" equals "myapp"

     Scenario: CSV operations
       When I create the CSV file "output/data.csv" with header "name,age"
       And I write the CSV row "Alice,30" to the file "output/data.csv"
       And I write the CSV row "Bob,25" to the file "output/data.csv"
       And I save the CSV file
       Given I set the header row 1 for the CSV file "output/data.csv" as "rows"
       Then the variable "rows" has length 2

API reference
-------------

See :doc:`/api/modules` for the full autodoc reference of the IO module.
