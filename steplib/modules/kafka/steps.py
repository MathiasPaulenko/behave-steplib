"""Kafka step definitions for behave."""

from __future__ import annotations

from typing import Any

from steplib.core.decorators import step
from steplib.core.registry import StepRegistry
from steplib.modules.kafka.actions import (
    kafka_assert_message_contains,
    kafka_assert_message_count,
    kafka_consume,
    kafka_produce,
    kafka_set_bootstrap_servers,
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


_ALL_STEPS = [
    step_set_kafka_servers,
    step_produce_message,
    step_consume_messages,
    step_message_count,
    step_message_contains,
]


def register(registry: StepRegistry) -> None:
    """Register all Kafka steps into the given registry."""
    for step_fn in _ALL_STEPS:
        registry.add(step_fn)
