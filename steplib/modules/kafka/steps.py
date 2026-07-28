"""Kafka step definitions for behave."""

from __future__ import annotations

from typing import Any

from steplib.core.decorators import step
from steplib.core.registry import StepRegistry
from steplib.modules.kafka.actions import (
    kafka_assert_message_contains,
    kafka_assert_message_count,
    kafka_assert_message_count_greater_than,
    kafka_assert_message_key_equals,
    kafka_assert_message_order,
    kafka_assert_message_value_equals,
    kafka_assert_message_value_matches_regex,
    kafka_consume,
    kafka_produce,
    kafka_produce_json,
    kafka_produce_multiple,
    kafka_set_auto_offset_reset,
    kafka_set_bootstrap_servers,
    kafka_set_consumer_config,
    kafka_set_consumer_group,
    kafka_set_producer_config,
    kafka_store_message_count,
    kafka_store_message_key,
    kafka_store_message_value,
)
from steplib.modules.kafka.context import KafkaContext


def _get_kafka(context: Any) -> KafkaContext:
    """Get the KafkaContext from context.steplib, creating it if needed."""
    steplib = getattr(context, "steplib", None)
    if steplib is None:
        raise RuntimeError(
            "context.steplib is not initialized. "
            "Call autoload(context) or load(context, ...) in before_all."
        )
    kafka = getattr(steplib, "kafka", None)
    if kafka is None:
        kafka = KafkaContext()
        steplib.kafka = kafka
    return kafka


@step(
    "the Kafka bootstrap servers are {servers}",
    category="kafka",
    description="Set the Kafka bootstrap servers.",
    example='Given the Kafka bootstrap servers are "localhost:9092"',
    i18n={
        "es": "los servidores bootstrap de Kafka son {servers}",
        "pt": "os servidores bootstrap do Kafka são {servers}",
    },
)
def step_set_kafka_servers(context: Any, servers: str) -> None:
    """Set Kafka bootstrap servers."""
    kafka_set_bootstrap_servers(_get_kafka(context), servers.strip('"'))


@step(
    "I produce a message to topic {topic} with key {key} and value {value}",
    category="kafka",
    description="Produce a message to a Kafka topic.",
    example='When I produce a message to topic "events" with key "id" and value "hello"',
    i18n={
        "es": "produzco un mensaje al topic {topic} con clave {key} y valor {value}",
        "pt": "produzo uma mensagem para o tópico {topic} com chave {key} e valor {value}",
    },
)
def step_produce_message(context: Any, topic: str, key: str, value: str) -> None:
    """Produce a Kafka message."""
    kafka_produce(
        _get_kafka(context),
        topic=topic.strip('"'),
        key=key.strip('"'),
        value=value.strip('"'),
    )


@step(
    "I consume messages from topic {topic}",
    category="kafka",
    description="Consume messages from a Kafka topic.",
    example='When I consume messages from topic "events"',
    i18n={
        "es": "consumo mensajes del topic {topic}",
        "pt": "consumo mensagens do tópico {topic}",
    },
)
def step_consume_messages(context: Any, topic: str) -> None:
    """Consume Kafka messages."""
    kafka_ctx = _get_kafka(context)
    messages = kafka_consume(kafka_ctx, topic=topic.strip('"'))
    kafka_ctx.variables["_last_messages"] = messages


@step(
    "the consumed messages count is {count:d}",
    category="kafka",
    description="Assert the number of consumed messages.",
    example="Then the consumed messages count is 3",
    i18n={
        "es": "el número de mensajes consumidos es {count:d}",
        "pt": "o número de mensagens consumidas é {count:d}",
    },
)
def step_message_count(context: Any, count: int) -> None:
    """Assert message count."""
    kafka_ctx = _get_kafka(context)
    messages = kafka_ctx.variables.get("_last_messages", [])
    kafka_assert_message_count(messages, count)


@step(
    "a consumed message contains {text}",
    category="kafka",
    description="Assert at least one consumed message contains text.",
    example='Then a consumed message contains "hello"',
    i18n={
        "es": "un mensaje consumido contiene {text}",
        "pt": "uma mensagem consumida contém {text}",
    },
)
def step_message_contains(context: Any, text: str) -> None:
    """Assert a message contains text."""
    kafka_ctx = _get_kafka(context)
    messages = kafka_ctx.variables.get("_last_messages", [])
    kafka_assert_message_contains(messages, text.strip('"'))


# --- Produce advanced ---


@step(
    "I produce a JSON message to topic {topic} with key {key} and payload {payload}",
    category="kafka",
    description="Produce a JSON-serialized message to a Kafka topic.",
    example=(
        'When I produce a JSON message to topic "events"'
        ' with key "user1" and payload \'{"event":"login"}\''
    ),
    i18n={
        "es": "produzco un mensaje JSON al topic {topic} con clave {key} y payload {payload}",
        "pt": "produzo uma mensagem JSON para o tópico {topic} com chave {key} e payload {payload}",
    },
)
def step_produce_json(context: Any, topic: str, key: str, payload: str) -> None:
    """Produce a JSON message."""
    import json

    try:
        parsed = json.loads(payload.strip("'").strip('"'))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Invalid JSON payload: {exc}") from exc
    kafka_produce_json(
        _get_kafka(context),
        topic.strip('"'),
        key=key.strip('"'),
        value=parsed,
    )


@step(
    "I produce {count:d} messages to topic {topic}",
    category="kafka",
    description="Produce multiple messages to a Kafka topic from a table.",
    example='When I produce 3 messages to topic "events"',
    i18n={
        "es": "produzco {count:d} mensajes al topic {topic}",
        "pt": "produzo {count:d} mensagens para o tópico {topic}",
    },
)
def step_produce_multiple(context: Any, count: int, topic: str) -> None:
    """Produce multiple messages from a behave table."""
    kafka_ctx = _get_kafka(context)
    messages = []
    table = getattr(context, "table", None)
    if table is not None and hasattr(table, "rows"):
        for row in table.rows:
            messages.append({"key": row.get("key", ""), "value": row.get("value", "")})
    else:
        for i in range(count):
            messages.append({"key": str(i), "value": f"message-{i}"})
    kafka_produce_multiple(kafka_ctx, topic.strip('"'), messages)


# --- Extended assertions ---


@step(
    "the message at index {index:d} has key {key}",
    category="kafka",
    description="Assert the key of the message at a given index equals a value.",
    example='Then the message at index 0 has key "user1"',
    i18n={
        "es": "el mensaje en el índice {index:d} tiene la clave {key}",
        "pt": "a mensagem no índice {index:d} tem a chave {key}",
    },
)
def step_message_key_equals(context: Any, index: int, key: str) -> None:
    """Assert message key equals."""
    kafka_ctx = _get_kafka(context)
    messages = kafka_ctx.variables.get("_last_messages", [])
    kafka_assert_message_key_equals(messages, index, key.strip('"'))


@step(
    "the message at index {index:d} has value {value}",
    category="kafka",
    description="Assert the value of the message at a given index equals a value.",
    example='Then the message at index 0 has value "hello"',
    i18n={
        "es": "el mensaje en el índice {index:d} tiene el valor {value}",
        "pt": "a mensagem no índice {index:d} tem o valor {value}",
    },
)
def step_message_value_equals(context: Any, index: int, value: str) -> None:
    """Assert message value equals."""
    kafka_ctx = _get_kafka(context)
    messages = kafka_ctx.variables.get("_last_messages", [])
    kafka_assert_message_value_equals(messages, index, value.strip('"'))


@step(
    "a message value matches the pattern {pattern}",
    category="kafka",
    description="Assert at least one message value matches a regex pattern.",
    example='Then a message value matches the pattern "user-\\d+"',
    i18n={
        "es": "un valor de mensaje coincide con el patrón {pattern}",
        "pt": "um valor de mensagem corresponde ao padrão {pattern}",
    },
)
def step_message_value_matches_regex(context: Any, pattern: str) -> None:
    """Assert message value matches regex."""
    kafka_ctx = _get_kafka(context)
    messages = kafka_ctx.variables.get("_last_messages", [])
    kafka_assert_message_value_matches_regex(messages, pattern.strip('"'))


@step(
    "the number of messages is greater than {count:d}",
    category="kafka",
    description="Assert the number of consumed messages is greater than a value.",
    example="Then the number of messages is greater than 0",
    i18n={
        "es": "el número de mensajes es mayor que {count:d}",
        "pt": "o número de mensagens é maior que {count:d}",
    },
)
def step_message_count_greater_than(context: Any, count: int) -> None:
    """Assert message count is greater than."""
    kafka_ctx = _get_kafka(context)
    messages = kafka_ctx.variables.get("_last_messages", [])
    kafka_assert_message_count_greater_than(messages, count)


@step(
    "the messages are in order {keys}",
    category="kafka",
    description="Assert message keys appear in a specific comma-separated order.",
    example='Then the messages are in order "user1,user2,user3"',
    i18n={
        "es": "los mensajes están en el orden {keys}",
        "pt": "as mensagens estão na ordem {keys}",
    },
)
def step_message_order(context: Any, keys: str) -> None:
    """Assert message order."""
    kafka_ctx = _get_kafka(context)
    messages = kafka_ctx.variables.get("_last_messages", [])
    expected_keys = [k.strip().strip('"') for k in keys.split(",")]
    kafka_assert_message_order(messages, expected_keys)


# --- Store / Extract ---


@step(
    "I store the value of message at index {index:d} as {variable}",
    category="kafka",
    description="Store the value of a consumed message as a variable.",
    example='Then I store the value of message at index 0 as "first_value"',
    i18n={
        "es": "guardo el valor del mensaje en el índice {index:d} como {variable}",
        "pt": "armazeno o valor da mensagem no índice {index:d} como {variable}",
    },
)
def step_store_message_value(context: Any, index: int, variable: str) -> None:
    """Store message value as variable."""
    kafka_ctx = _get_kafka(context)
    messages = kafka_ctx.variables.get("_last_messages", [])
    kafka_store_message_value(messages, index, kafka_ctx, variable.strip('"'))


@step(
    "I store the key of message at index {index:d} as {variable}",
    category="kafka",
    description="Store the key of a consumed message as a variable.",
    example='Then I store the key of message at index 0 as "first_key"',
    i18n={
        "es": "guardo la clave del mensaje en el índice {index:d} como {variable}",
        "pt": "armazeno a chave da mensagem no índice {index:d} como {variable}",
    },
)
def step_store_message_key(context: Any, index: int, variable: str) -> None:
    """Store message key as variable."""
    kafka_ctx = _get_kafka(context)
    messages = kafka_ctx.variables.get("_last_messages", [])
    kafka_store_message_key(messages, index, kafka_ctx, variable.strip('"'))


@step(
    "I store the message count as {variable}",
    category="kafka",
    description="Store the number of consumed messages as a variable.",
    example='Then I store the message count as "total_messages"',
    i18n={
        "es": "guardo el número de mensajes como {variable}",
        "pt": "armazeno o número de mensagens como {variable}",
    },
)
def step_store_message_count(context: Any, variable: str) -> None:
    """Store message count as variable."""
    kafka_ctx = _get_kafka(context)
    messages = kafka_ctx.variables.get("_last_messages", [])
    kafka_store_message_count(messages, kafka_ctx, variable.strip('"'))


# --- Config ---


@step(
    "the Kafka consumer group is {group}",
    category="kafka",
    description="Set the Kafka consumer group ID.",
    example='Given the Kafka consumer group is "test-group"',
    i18n={
        "es": "el grupo de consumidores Kafka es {group}",
        "pt": "o grupo de consumidores Kafka é {group}",
    },
)
def step_set_consumer_group(context: Any, group: str) -> None:
    """Set consumer group."""
    kafka_set_consumer_group(_get_kafka(context), group.strip('"'))


@step(
    "the Kafka auto offset reset is {strategy}",
    category="kafka",
    description="Set the auto offset reset strategy (earliest or latest).",
    example='Given the Kafka auto offset reset is "earliest"',
    i18n={
        "es": "el auto offset reset de Kafka es {strategy}",
        "pt": "o auto offset reset do Kafka é {strategy}",
    },
)
def step_set_auto_offset_reset(context: Any, strategy: str) -> None:
    """Set auto offset reset."""
    kafka_set_auto_offset_reset(_get_kafka(context), strategy.strip('"'))


@step(
    "I consume messages from topic {topic} with timeout {timeout_ms:d} ms",
    category="kafka",
    description="Consume messages from a Kafka topic with a custom timeout.",
    example='When I consume messages from topic "events" with timeout 10000 ms',
    i18n={
        "es": "consumo mensajes del topic {topic} con tiempo de espera {timeout_ms:d} ms",
        "pt": "consumo mensagens do tópico {topic} com tempo de espera {timeout_ms:d} ms",
    },
)
def step_consume_with_timeout(context: Any, topic: str, timeout_ms: int) -> None:
    """Consume Kafka messages with custom timeout."""
    kafka_ctx = _get_kafka(context)
    messages = kafka_consume(kafka_ctx, topic=topic.strip('"'), timeout_ms=timeout_ms)
    kafka_ctx.variables["_last_messages"] = messages


@step(
    "the Kafka producer config is {config}",
    category="kafka",
    description="Set additional Kafka producer configuration overrides from JSON.",
    example='Given the Kafka producer config is \'{"acks": "all", "retries": 3}\'',
    i18n={
        "es": "la configuración del productor Kafka es {config}",
        "pt": "a configuração do produtor Kafka é {config}",
    },
)
def step_set_producer_config(context: Any, config: str) -> None:
    """Set producer config from JSON string."""
    import json

    try:
        parsed = json.loads(config.strip("'").strip('"'))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Invalid JSON config: {exc}") from exc
    kafka_set_producer_config(_get_kafka(context), parsed)


@step(
    "the Kafka consumer config is {config}",
    category="kafka",
    description="Set additional Kafka consumer configuration overrides from JSON.",
    example="Given the Kafka consumer config is '{\"enable.auto.commit\": false}'",
    i18n={
        "es": "la configuración del consumidor Kafka es {config}",
        "pt": "a configuração do consumidor Kafka é {config}",
    },
)
def step_set_consumer_config(context: Any, config: str) -> None:
    """Set consumer config from JSON string."""
    import json

    try:
        parsed = json.loads(config.strip("'").strip('"'))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Invalid JSON config: {exc}") from exc
    kafka_set_consumer_config(_get_kafka(context), parsed)


_ALL_STEPS = [
    step_set_kafka_servers,
    step_produce_message,
    step_consume_messages,
    step_consume_with_timeout,
    step_message_count,
    step_message_contains,
    # Produce advanced
    step_produce_json,
    step_produce_multiple,
    # Extended assertions
    step_message_key_equals,
    step_message_value_equals,
    step_message_value_matches_regex,
    step_message_count_greater_than,
    step_message_order,
    # Store / Extract
    step_store_message_value,
    step_store_message_key,
    step_store_message_count,
    # Config
    step_set_consumer_group,
    step_set_auto_offset_reset,
    step_set_producer_config,
    step_set_consumer_config,
]


def register(registry: StepRegistry) -> None:
    """Register all Kafka steps into the given registry."""
    for step_fn in _ALL_STEPS:
        registry.add(step_fn)
