IO Module
=========

The IO module provides steps for file, JSON, CSV and directory operations.
It covers file CRUD, file assertions, JSON key-path navigation and
validation, CSV writing and reading, directory management, and reading
files as lines — 38 steps in total, all with ``es`` and ``pt``
translations.

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
- ``_last_json`` — the last loaded JSON object for key-path-based
  assertions.
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
   * - ``I read the file {path} into {variable}``
     - Read a text file and store its content as a variable.
   * - ``I read the file {path} as lines into {variable}``
     - Read a file and store its lines as a list in a variable.
   * - ``I write {content} to the file {path}``
     - Write content to a file (overwrites existing).
   * - ``I append {content} to the file {path}``
     - Append content to a file.
   * - ``I delete the file {path}``
     - Delete a file.
   * - ``I copy the file {source} to {destination}``
     - Copy a file to a new location.
   * - ``I move the file {source} to {destination}``
     - Move a file to a new location.
   * - ``I rename the file {path} to {new_path}``
     - Rename a file.
   * - ``I create an empty file at {path}``
     - Create an empty file.

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
   * - ``the files {path1} and {path2} are the same``
     - Assert that two files have identical content.
   * - ``I get the size of the file {path} as {variable}``
     - Store a file's size in bytes as a variable.
   * - ``I get the extension of the file {path} as {variable}``
     - Store a file's extension as a variable.

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

JSON key paths use dot notation (``user.name``, ``items.0.id``) — not the
``$.`` JSONPath syntax used by the API module.

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I load the JSON file {path} as the last JSON``
     - Load a JSON file into the context's last JSON object.
   * - ``I save the JSON to the file {path}``
     - Save the last JSON object to a file.
   * - ``the JSON key path {key_path} equals {value}``
     - Assert that a JSON key path equals a value.
   * - ``I store the JSON key path {key_path} as {variable}``
     - Store a JSON key path value into a variable.
   * - ``I update the JSON key path {key_path} to {value}``
     - Update a JSON key path value.
   * - ``I create the JSON key path {key_path} with value {value}``
     - Create a new JSON key path with a value.
   * - ``I delete the JSON key path {key_path}``
     - Delete a JSON key path.
   * - ``the JSON {json_string} is valid``
     - Assert that a JSON string is valid JSON.
   * - ``the JSON matches the schema {schema_path}``
     - Assert that the last loaded JSON matches a JSON Schema file.
       Requires the ``[io]`` extra (``jsonschema``).
   * - ``the last JSON is valid``
     - Assert that the last loaded JSON is valid by re-serializing it.
   * - ``I get the type of the JSON key path {key_path} as {variable}``
     - Store the type name of a JSON key path value as a variable.
   * - ``I diff the JSON objects {json1} and {json2}``
     - Diff two JSON objects and store the differences as ``diff_json``.
   * - ``I merge the JSON {origin_name} into {target_name} with {priority} priority``
     - Merge two stored JSON variables; *priority* decides which side wins
       on conflicts (``origin`` or ``target``).

CSV operations
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I create the CSV file {path} from the data {data}``
     - Create a CSV file from a JSON array of objects (keys become the
       header row).
   * - ``I create a CSV writer for file {path} with fieldnames {fieldnames}``
     - Create a CSV writer for incremental writing.
   * - ``I write the CSV row {row}``
     - Write a row (a JSON object) to the active CSV writer.
   * - ``I save the CSV file``
     - Flush the active CSV writer to disk without closing it.
   * - ``I set the header row {row:d} for the CSV file {path} as {variable}``
     - Read a CSV file using a specific row as the header and store the
       rows in a variable.
   * - ``I close the CSV writer``
     - Close the active CSV writer and its file handle.

Example
-------

.. code-block:: gherkin

   Feature: File and data operations

     Scenario: File CRUD
       Given I create the directory "output/logs"
       When I write "hello world" to the file "output/logs/test.txt"
       Then the file "output/logs/test.txt" exists
       When I read the file "output/logs/test.txt" as lines into "lines"
       Then the variable "lines" has length 1
       When I delete the directory "output"
       Then the directory "output" does not exist

     Scenario: JSON operations
       Given I load the JSON file "data/config.json" as the last JSON
       Then the JSON key path "version" equals "1.0"
       And the JSON matches the schema "schemas/config.json"
       And the last JSON is valid
       When I store the JSON key path "name" as "config_name"
       Then the variable "config_name" equals "myapp"

     Scenario: CSV operations
       When I create the CSV file "output/data.csv" from the data '[{"name":"Alice","age":30}]'
       Given I set the header row 1 for the CSV file "output/data.csv" as "rows"
       Then the variable "rows" has length 1

API reference
-------------

See :doc:`/api/modules` for the full autodoc reference of the IO module.
