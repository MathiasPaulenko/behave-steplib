Kafka Module
============

The Kafka module provides steps for testing Kafka producers and consumers.
It covers bootstrap server configuration, message production, message
consumption and assertions on consumed messages.

Installation
------------

.. code-block:: bash

   pip install "behave-steplib[kafka]"

Backends
--------

.. list-table::
   :header-rows: 1
   :widths: 20 25 55

   * - Backend
     - Package
     - Notes
   * - ``kafka-python-ng``
     - ``kafka-python-ng``
     - Kafka producer and consumer. Requires the ``[kafka]`` extra.

Steps
-----

Configuration
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``the Kafka bootstrap servers are {servers}``
     - Set the Kafka bootstrap servers.

Produce
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I produce a message to topic {topic} with key {key} and value {value}``
     - Produce a message to a Kafka topic.

Consume
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``I consume messages from topic {topic}``
     - Consume messages from a Kafka topic and store them in
       ``variables["_last_messages"]``.

Assertions
~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 60 40

   * - Pattern
     - Description
   * - ``the consumed messages count is {count:d}``
     - Assert the number of consumed messages.
   * - ``a consumed message contains {text}``
     - Assert at least one consumed message value contains text.

Example
-------

.. code-block:: gherkin

   Feature: Kafka messaging

     Scenario: Produce and consume a message
       Given the Kafka bootstrap servers are "localhost:9092"
       When I produce a message to topic "events" with key "id" and value "hello"
       And I consume messages from topic "events"
       Then the consumed messages count is 1
       And a consumed message contains "hello"

Producer and consumer lifecycle
-------------------------------

The :class:`~steplib.modules.kafka.context.KafkaContext` holds the producer
and consumer. They are created lazily on first use and closed by
``cleanup()``:

.. code-block:: python

   def before_all(context):
       context.steplib = autoload(context)

   def after_scenario(context, scenario):
       context.steplib.cleanup()  # closes producer and consumer

API reference
-------------

See :doc:`/api/modules` for the full autodoc reference of the Kafka module.
