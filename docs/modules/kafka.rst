Kafka Module
============

The Kafka module provides steps for testing Kafka producers and consumers.
It covers bootstrap server configuration, message production (single, JSON,
batch), message consumption (with optional timeout), assertions on consumed
messages, store/extract operations and advanced producer/consumer
configuration — 20 steps in total, all with ``es`` and ``pt`` translations.

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
   * - ``the Kafka consumer group is {group}``
     - Set the Kafka consumer group ID.
   * - ``the Kafka auto offset reset is {strategy}``
     - Set the auto offset reset strategy (``earliest`` or ``latest``).
   * - ``the Kafka producer config is {config}``
     - Set additional Kafka producer configuration overrides from JSON.
   * - ``the Kafka consumer config is {config}``
     - Set additional Kafka consumer configuration overrides from JSON.

Produce
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 70 30

   * - Pattern
     - Description
   * - ``I produce a message to topic {topic} with key {key} and value {value}``
     - Produce a message to a Kafka topic.
   * - ``I produce a JSON message to topic {topic} with key {key} and payload {payload}``
     - Produce a JSON-serialized message to a Kafka topic.
   * - ``I produce {count:d} messages to topic {topic}``
     - Produce multiple messages to a Kafka topic from a behave table.

Consume
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I consume messages from topic {topic}``
     - Consume messages from a Kafka topic and store them in
       ``variables["_last_messages"]``.
   * - ``I consume messages from topic {topic} with timeout {timeout_ms:d} ms``
     - Consume messages from a Kafka topic with a custom timeout.

Assertions
~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``the consumed messages count is {count:d}``
     - Assert the number of consumed messages.
   * - ``the number of messages is greater than {count:d}``
     - Assert the number of consumed messages is greater than a value.
   * - ``a consumed message contains {text}``
     - Assert at least one consumed message value contains text.
   * - ``the message at index {index:d} has key {key}``
     - Assert the key of the message at a given index equals a value.
   * - ``the message at index {index:d} has value {value}``
     - Assert the value of the message at a given index equals a value.
   * - ``a message value matches the pattern {pattern}``
     - Assert at least one message value matches a regex pattern.
   * - ``the messages are in order {keys}``
     - Assert message keys appear in a specific comma-separated order.

Store and extract
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 65 35

   * - Pattern
     - Description
   * - ``I store the value of message at index {index:d} as {variable}``
     - Store the value of a consumed message as a variable.
   * - ``I store the key of message at index {index:d} as {variable}``
     - Store the key of a consumed message as a variable.
   * - ``I store the message count as {variable}``
     - Store the number of consumed messages as a variable.

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
