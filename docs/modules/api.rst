API Module
==========

The API module provides steps for testing HTTP APIs. It supports three
backends — ``stdlib`` (urllib, default), ``httpx`` (requires ``[api]``) and
``requests`` — and covers configuration, requests, assertions and response
storage.

Installation
------------

.. code-block:: bash

   pip install "behave-steplib[api]"

The ``stdlib`` backend (urllib) is always available with no extra
dependencies. Install the ``[api]`` extra to use ``httpx``.

Backends
--------

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Backend
     - Package
     - Notes
   * - ``stdlib``
     - (none)
     - Default. Uses ``urllib`` from the standard library. No extra
       dependencies.
   * - ``httpx``
     - ``httpx``
     - HTTP/2 support, async-capable, cookie persistence. Requires the
       ``[api]`` extra.
   * - ``requests``
     - ``requests``
     - Legacy compatibility. Requires the ``requests`` package.

Select a backend via ``autoload``:

.. code-block:: python

   autoload(context, backends={"api": "httpx"})

Steps
-----

Configuration
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Pattern
     - Description
   * - ``the API base url is {url}``
     - Set the base URL for subsequent requests.
   * - ``I set the API header {name} to {value}``
     - Set a default header sent with every request.
   * - ``I set the API timeout to {seconds:d} seconds``
     - Set the request timeout in seconds.

Translations: every configuration step has ``es`` and ``pt`` translations.

Requests
~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``I send a {method} request to {url}``
     - Send an HTTP request and store the response.
   * - ``I send a {method} request to {url} with body``
     - Send a request with a body from the step's text (``context.text``).

The ``{method}`` placeholder accepts any HTTP method string (``GET``,
``POST``, ``PUT``, ``PATCH``, ``DELETE``, ``HEAD``, ``OPTIONS``). Relative
URLs are resolved against the base URL set with ``the API base url is``.

Assertions
~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``the response status is {status:d}``
     - Assert the last response status code.
   * - ``the response body contains {text}``
     - Assert the response body contains a substring.
   * - ``the response body is valid JSON``
     - Assert the response body is valid JSON.
   * - ``the JSON path {path} equals {value}``
     - Assert a JSON path in the response equals a value.
   * - ``the response header {name} is {value}``
     - Assert a response header equals a value.
   * - ``I store the response body as {variable}``
     - Store the response body as a named variable.

Table comparison
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``the response matches the table``
     - Compare the response JSON with a behave table. Requires the
       ``[tables]`` and ``[kit]`` extras.

Example
-------

.. code-block:: gherkin

   Feature: API health check

     Scenario: GET users returns 200
       Given the API base url is "https://api.example.com"
       When I send a GET request to "/users"
       Then the response status is 200
       And the response body is valid JSON
       And the JSON path "$.users[0].name" equals "Ada"

     Scenario: POST creates a user
       Given the API base url is "https://api.example.com"
       When I send a POST request to "/users" with body
         """
         {"name": "Ada", "email": "ada@example.com"}
         """
       Then the response status is 201
       And the response header "Content-Type" is "application/json"
       And I store the response body as "created_user"

JSONPath syntax
---------------

The ``the JSON path {path} equals {value}`` step supports a simple JSONPath
subset:

- ``$`` — the root object.
- ``$.field`` — access a field.
- ``$.field.nested`` — nested access.
- ``$.items[0]`` — array index.

Examples:

.. code-block:: gherkin

   Then the JSON path "$" equals "..."
   Then the JSON path "$.users" equals "..."
   Then the JSON path "$.users[0].name" equals "Ada"
   Then the JSON path "$.items[2].price" equals "19.99"

API reference
-------------

See :doc:`/api/modules` for the full autodoc reference of the API module.
