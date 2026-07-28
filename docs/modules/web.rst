Web Module
==========

The Web module provides steps for testing web applications with Selenium.
It covers navigation, interactions, waits, assertions, cookies, frame
handling, store/extract operations and browser configuration — 34 steps
in total, all with ``es`` and ``pt`` translations.

Installation
------------

.. code-block:: bash

   pip install "behave-steplib[web]"

Backends
--------

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Backend
     - Package
     - Notes
   * - ``selenium``
     - ``selenium``
     - Chrome and Firefox with headless support. Requires the ``[web]``
       extra.

Steps
-----

Configuration
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Pattern
     - Description
   * - ``the web base url is {url}``
     - Set the base URL for subsequent navigations.
   * - ``the implicit wait is {seconds:f} seconds``
     - Set the implicit wait time for element lookups.
   * - ``the page load timeout is {seconds:f} seconds``
     - Set the page load timeout.
   * - ``the window size is {width:d} x {height:d}``
     - Set the browser window size.

Navigation
~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Pattern
     - Description
   * - ``I navigate to {url}``
     - Navigate the browser to a URL. Relative URLs resolve against the base URL.
   * - ``I refresh the page``
     - Refresh the current page.
   * - ``I go back``
     - Navigate back in browser history.
   * - ``I go forward``
     - Navigate forward in browser history.
   * - ``I switch to the frame {by} {value}``
     - Switch to an iframe element.
   * - ``I switch to the default content``
     - Switch back to the default content from a frame.

Interactions
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``I click the element {by} {value}``
     - Click an element on the page.
   * - ``I type {text} into the element {by} {value}``
     - Type text into an input element, clearing it first.
   * - ``I clear the element {by} {value}``
     - Clear an input element.
   * - ``I select {option} from the element {by} {value}``
     - Select an option from a dropdown by visible text.
   * - ``I take a screenshot {filename}``
     - Take a screenshot and save it to a file.

Waits
~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``I wait for the element {by} {value} to be present``
     - Wait until an element is present on the page.
   * - ``I wait for the element {by} {value} to be visible``
     - Wait until an element is visible on the page.
   * - ``I wait for the page to contain {text}``
     - Wait until the page contains specific text.

Assertions
~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``the page title is {title}``
     - Assert the page title equals a value.
   * - ``the URL contains {fragment}``
     - Assert the current URL contains a fragment.
   * - ``the element {by} {value} is present``
     - Assert an element is present on the page.
   * - ``the element {by} {value} is not present``
     - Assert an element is NOT present on the page.
   * - ``the element {by} {value} is visible``
     - Assert an element is visible on the page.
   * - ``the element {by} {value} is enabled``
     - Assert an element is enabled.
   * - ``the element {by} {value} text equals {expected}``
     - Assert an element's text content equals a value.
   * - ``the element {by} {value} attribute {attr} equals {expected}``
     - Assert an element's attribute equals a value.
   * - ``the page contains {text}``
     - Assert the page source contains text.
   * - ``the page does not contain {text}``
     - Assert the page source does NOT contain text.

The ``{by}`` placeholder uses Selenium's ``By`` strategy names (``id``,
``name``, ``xpath``, ``css_selector``, ``class_name``, ``tag_name``,
``link_text``, ``partial_link_text``).

Cookies
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Pattern
     - Description
   * - ``the cookie {name} exists``
     - Assert a cookie exists.
   * - ``I delete the cookie {name}``
     - Delete a cookie by name.

Store and extract
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``I store the text of element {by} {value} as {variable}``
     - Store an element's text content as a variable.
   * - ``I store the attribute {attr} of element {by} {value} as {variable}``
     - Store an element's attribute value as a variable.
   * - ``I store the current URL as {variable}``
     - Store the current browser URL as a variable.
   * - ``I store the cookie {name} as {variable}``
     - Store a cookie value as a variable.

Example
-------

.. code-block:: gherkin

   Feature: Web navigation

     Scenario: User visits the login page
       Given the web base url is "https://example.com"
       When I navigate to "/login"
       Then the page title is "Login"
       And the element id "username" is present
       And the page contains "Sign In"

Driver lifecycle
----------------

The :class:`~steplib.modules.web.context.WebContext` holds the browser
driver. It is created lazily and closed by ``cleanup()``:

.. code-block:: python

   from steplib.modules.web.client import get_driver

   def before_all(context):
       context.steplib = autoload(context)
       context.steplib.web.driver = get_driver("selenium", browser="chrome", headless=True)

   def after_scenario(context, scenario):
       context.steplib.cleanup()  # quits the browser

API reference
-------------

See :doc:`/api/modules` for the full autodoc reference of the Web module.
