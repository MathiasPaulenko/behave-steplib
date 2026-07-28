API Module
==========

The API module provides steps for testing HTTP APIs. It supports three
backends — ``stdlib`` (urllib, default), ``httpx`` (requires ``[api]``) and
``requests`` — and covers configuration, requests, assertions and response
storage.

Installation
------------

.. code-block:: bash

   pip install "behave-steplib[api]"        # httpx backend
   pip install "behave-steplib[requests]"   # requests backend

The ``stdlib`` backend (urllib) is always available with no extra
dependencies. Install the ``[api]`` extra to use ``httpx``, or the
``[requests]`` extra to use ``requests``.

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
     - Session-based with cookie persistence. Requires the
       ``[requests]`` extra.

Select a backend via ``autoload``:

.. code-block:: python

   autoload(context, backends={"api": "httpx"})
   autoload(context, backends={"api": "requests"})
   autoload(context, backends={"api": "stdlib"})  # default, no extra needed

Steps
-----

The API module provides 55 steps organised into eight categories. All steps
have ``es`` and ``pt`` translations unless noted otherwise.

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
   * - ``I set the query parameter {name} to {value}``
     - Set a default query parameter sent with every request.
   * - ``I remove the query parameter {name}``
     - Remove a previously set query parameter.
   * - ``I remove the header {name}``
     - Remove a previously set default header.
   * - ``I clear the request data``
     - Reset headers, params, auth, cookies, and last response.
   * - ``I set the proxy to {url}``
     - Set a proxy URL for both HTTP and HTTPS requests.

Authentication
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``I set basic authentication with username {user} and password {password}``
     - Set basic auth credentials for subsequent requests.
   * - ``I set the bearer token to {token}``
     - Set a Bearer token in the Authorization header.

SSL and redirects
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Pattern
     - Description
   * - ``I disable SSL verification``
     - Disable SSL certificate verification for subsequent requests.
   * - ``I enable SSL verification``
     - Enable SSL certificate verification for subsequent requests.
   * - ``I disable redirects``
     - Disable following redirects for subsequent requests.
   * - ``I enable redirects``
     - Enable following redirects for subsequent requests.
   * - ``I save cookies from the response``
     - Extract Set-Cookie headers from the last response and store them.

Requests
~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I send a {method} request to {url}``
     - Send an HTTP request and store the response.
   * - ``I send a {method} request to {url} with body``
     - Send a request with a body from the step's text (``context.text``).
   * - ``I send a {method} request to {url} with form data``
     - Send a request with form-encoded data from the step table.
   * - ``I send a {method} request to {url} with JSON body``
     - Send a request with a JSON body from the step's text.
   * - ``I send a {method} request to {url} with query parameters``
     - Send a request with query parameters from the step table.
   * - ``I send a {method} request to {url} with headers``
     - Send a request with extra headers from the step table.

The ``{method}`` placeholder accepts any HTTP method string (``GET``,
``POST``, ``PUT``, ``PATCH``, ``DELETE``, ``HEAD``, ``OPTIONS``). Relative
URLs are resolved against the base URL set with ``the API base url is``.

Status and body assertions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``the response status is {status:d}``
     - Assert the last response status code.
   * - ``the response status is one of {statuses}``
     - Assert the status is one of a comma-separated list (e.g. ``200, 201, 202``).
   * - ``the response body contains {text}``
     - Assert the response body contains a substring.
   * - ``the response body does not contain {text}``
     - Assert the response body does not contain a substring.
   * - ``the response body is valid JSON``
     - Assert the response body is valid JSON.
   * - ``the response matches the JSON schema``
     - Validate the response body against a JSON Schema from the step text.

JSON Path assertions
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``the JSON path {path} equals {value}``
     - Assert a JSON path in the response equals a value.
   * - ``the JSON path {path} does not equal {value}``
     - Assert a JSON path value does not equal a value.
   * - ``the JSON path {path} exists``
     - Assert that a JSON path exists in the response.
   * - ``the JSON path {path} contains {value}``
     - Assert a JSON path value contains a value (for lists or strings).
   * - ``the JSON path {path} is null``
     - Assert that a JSON path value is null.
   * - ``the JSON path {path} is not null``
     - Assert that a JSON path value is not null.
   * - ``the JSON path {path} has length {length:d}``
     - Assert a JSON path value (list or string) has a specific length.
   * - ``the JSON path {path} has type {type}``
     - Assert the value at a JSON path is of a specific type.
   * - ``the JSON path {path} matches the pattern {pattern}``
     - Assert a JSON path string value matches a regex pattern.

Header assertions
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``the response header {name} is {value}``
     - Assert a response header equals a value.
   * - ``the response header {name} is not {value}``
     - Assert a response header does not equal a value.
   * - ``the response header {name} contains {value}``
     - Assert a response header contains a substring.
   * - ``the response has header {name}``
     - Assert that a response header exists.
   * - ``the response does not have header {name}``
     - Assert that a response header does not exist.
   * - ``the response content type is {content_type}``
     - Assert the Content-Type response header equals a value.
   * - ``the response content type contains {content_type}``
     - Assert the Content-Type response header contains a substring.

Response time assertions
~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``the response time is less than {seconds:d} seconds``
     - Assert the response time is under a threshold.
   * - ``the response time is greater than {seconds:d} seconds``
     - Assert the response time exceeds a threshold.
   * - ``the response time is between {min:d} and {max:d} seconds``
     - Assert the response time is within a range.

Store and extract
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``I store the response body as {variable}``
     - Store the response body as a named variable.
   * - ``I store the JSON path {path} as {variable}``
     - Store the value at a JSON path from the response as a variable.
   * - ``I store the response header {name} as {variable}``
     - Store a response header value as a named variable.
   * - ``I store the response status as {variable}``
     - Store the last response status code as a named variable.
   * - ``I store the response time as {variable}``
     - Store the last response time in milliseconds as a variable.
   * - ``I use the variable {variable} as the header {name}``
     - Set a header from a previously stored variable.
   * - ``I use the variable {variable} as the query parameter {name}``
     - Set a query parameter from a previously stored variable.
   * - ``the variable {variable} equals {value}``
     - Assert that a stored variable equals a value.

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
