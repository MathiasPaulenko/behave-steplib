"""Pure action functions for the Kafka module."""

from __future__ import annotations

from typing import Any

from steplib.core.exceptions import MissingDependencyError
from steplib.modules.kafka.context import KafkaContext


def kafka_set_bootstrap_servers(kafka_ctx: KafkaContext, servers: str) -> None:
    """Set the Kafka bootstrap servers."""
    kafka_ctx.bootstrap_servers = servers


def kafka_produce(
    kafka_ctx: KafkaContext,
    topic: str,
    key: str | None = None,
    value: str = "",
) -> None:
    """Produce a message to a Kafka topic.

    Raises:
        MissingDependencyError: If kafka-python-ng is not installed.

    """
    try:
        from kafka import KafkaProducer  # noqa: PLC0415
    except ImportError as exc:
        raise MissingDependencyError("kafka", "kafka-python-ng") from exc

    if kafka_ctx.producer is None:
        kafka_ctx.producer = KafkaProducer(
            bootstrap_servers=kafka_ctx.bootstrap_servers,
            value_serializer=lambda x: x.encode("utf-8") if isinstance(x, str) else x,
        )
    kafka_ctx.producer.send(
        topic,
        key=key.encode("utf-8") if key is not None else None,
        value=value,
    )
    if hasattr(kafka_ctx.producer, "flush"):
        kafka_ctx.producer.flush()


def kafka_consume(
    kafka_ctx: KafkaContext,
    topic: str,
    timeout_ms: int = 5000,
    max_records: int = 100,
) -> list[dict[str, Any]]:
    """Consume messages from a Kafka topic.

    Returns a list of dicts with ``key``, ``value``, ``topic``, ``partition``,
    and ``offset`` keys.

    Raises:
        MissingDependencyError: If kafka-python-ng is not installed.

    """
    try:
        from kafka import KafkaConsumer  # noqa: PLC0415
    except ImportError as exc:
        raise MissingDependencyError("kafka", "kafka-python-ng") from exc

    if kafka_ctx.consumer is None:
        kafka_ctx.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=kafka_ctx.bootstrap_servers,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            consumer_timeout_ms=timeout_ms,
            value_deserializer=lambda x: x.decode("utf-8") if x else "",
            key_deserializer=lambda x: x.decode("utf-8") if x else None,
        )

    messages: list[dict[str, Any]] = []
    for _ in range(max_records):
        records = kafka_ctx.consumer.poll(timeout_ms=timeout_ms, max_records=1)
        if not records:
            break
        for _topic, msgs in records.items():
            for msg in msgs:
                messages.append({
                    "key": msg.key,
                    "value": msg.value,
                    "topic": msg.topic,
                    "partition": msg.partition,
                    "offset": msg.offset,
                })
    return messages


def kafka_assert_message_count(
    messages: list[dict[str, Any]],
    expected: int,
) -> None:
    """Assert that the number of messages equals *expected*."""
    actual = len(messages)
    if actual != expected:
        raise AssertionError(f"Expected {expected} messages, got {actual}.")


def kafka_assert_message_contains(
    messages: list[dict[str, Any]],
    text: str,
) -> None:
    """Assert that at least one message value contains *text*."""
    for msg in messages:
        if text in str(msg.get("value", "")):
            return
    raise AssertionError(f"No message contains '{text}'.")
