Web Module
==========

The Web module provides steps for testing web applications with Selenium.
It covers navigation, page assertions and element presence checks.

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

Navigation
~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Pattern
     - Description
   * - ``I navigate to {url}``
     - Navigate the browser to a URL. Relative URLs are resolved against the
       base URL.

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
   * - ``the page contains {text}``
     - Assert the page source contains text.

The ``the element {by} {value} is present`` step uses Selenium's ``By``
strategy names (``id``, ``name``, ``xpath``, ``css_selector``, ``class_name``,
``tag_name``, ``link_text``, ``partial_link_text``).

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
