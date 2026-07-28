"""Pure action functions for the Kafka module."""

from __future__ import annotations

from typing import Any

from steplib.core.exceptions import MissingDependencyError
from steplib.modules.kafka.context import KafkaContext


def _normalize_value(value: Any) -> str:
    """Normalize a value to its string representation for comparison.

    Python's ``str(True)`` returns ``"True"``, but JSON/Kafka messages
    naturally use ``"true"`` / ``"false"`` / ``"null"``.  This helper
    ensures booleans and ``None`` use their JSON-style lowercase
    representation.
    """
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    return str(value)


def kafka_set_bootstrap_servers(kafka_ctx: KafkaContext, servers: str) -> None:
    """Set the Kafka bootstrap servers.

    Args:
        kafka_ctx: The Kafka context to operate on.
        servers: Comma-separated bootstrap server addresses.

    """
    kafka_ctx.bootstrap_servers = servers


def kafka_produce(
    kafka_ctx: KafkaContext,
    topic: str,
    key: str | None = None,
    value: str = "",
) -> None:
    """Produce a message to a Kafka topic.

    Args:
        kafka_ctx: The Kafka context to operate on.
        topic: The target Kafka topic.
        key: Optional message key. ``None`` for no key.
        value: The message value.

    Raises:
        MissingDependencyError: If kafka-python-ng is not installed.

    """
    try:
        from kafka import KafkaProducer
    except ImportError as exc:
        raise MissingDependencyError("kafka", "kafka-python-ng") from exc

    if kafka_ctx.producer is None:
        producer_config: dict[str, Any] = {
            "bootstrap_servers": kafka_ctx.bootstrap_servers,
            "value_serializer": lambda x: x.encode("utf-8") if isinstance(x, str) else x,
        }
        producer_config.update(kafka_ctx.producer_config)
        kafka_ctx.producer = KafkaProducer(**producer_config)
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

    Args:
        kafka_ctx: The Kafka context to operate on.
        topic: The Kafka topic to consume from.
        timeout_ms: Poll timeout in milliseconds.
        max_records: Maximum number of records to consume.

    Returns:
        A list of dicts with ``key``, ``value``, ``topic``, ``partition``,
        and ``offset`` keys.

    Raises:
        MissingDependencyError: If kafka-python-ng is not installed.

    """
    try:
        from kafka import KafkaConsumer
    except ImportError as exc:
        raise MissingDependencyError("kafka", "kafka-python-ng") from exc

    if kafka_ctx.consumer is None:
        consumer_config: dict[str, Any] = {
            "bootstrap_servers": kafka_ctx.bootstrap_servers,
            "auto_offset_reset": kafka_ctx.auto_offset_reset,
            "group_id": kafka_ctx.consumer_group,
            "enable_auto_commit": True,
            "consumer_timeout_ms": timeout_ms,
            "value_deserializer": lambda x: x.decode("utf-8") if x else "",
            "key_deserializer": lambda x: x.decode("utf-8") if x else None,
        }
        consumer_config.update(kafka_ctx.consumer_config)
        kafka_ctx.consumer = KafkaConsumer(topic, **consumer_config)

    messages: list[dict[str, Any]] = []
    for _ in range(max_records):
        records = kafka_ctx.consumer.poll(timeout_ms=timeout_ms, max_records=1)
        if not records:
            break
        for _topic, msgs in records.items():
            for msg in msgs:
                messages.append(
                    {
                        "key": msg.key,
                        "value": msg.value,
                        "topic": msg.topic,
                        "partition": msg.partition,
                        "offset": msg.offset,
                    }
                )
    return messages


def kafka_assert_message_count(
    messages: list[dict[str, Any]],
    expected: int,
) -> None:
    """Assert that the number of messages equals *expected*.

    Args:
        messages: The list of consumed messages.
        expected: The expected number of messages.

    Raises:
        AssertionError: If the count does not match.

    """
    actual = len(messages)
    if actual != expected:
        raise AssertionError(f"Expected {expected} messages, got {actual}.")


def kafka_assert_message_contains(
    messages: list[dict[str, Any]],
    text: str,
) -> None:
    """Assert that at least one message value contains *text*.

    Args:
        messages: The list of consumed messages.
        text: The substring to search for in message values.

    Raises:
        AssertionError: If no message value contains *text*.

    """
    for msg in messages:
        if text in _normalize_value(msg.get("value", "")):
            return
    raise AssertionError(f"No message contains '{text}'.")


# --- Produce advanced ---


def kafka_produce_json(
    kafka_ctx: KafkaContext,
    topic: str,
    key: str | None = None,
    value: dict[str, Any] | None = None,
) -> None:
    """Produce a JSON-serialized message to a Kafka topic.

    Args:
        kafka_ctx: The Kafka context to operate on.
        topic: The target Kafka topic.
        key: Optional message key. ``None`` for no key.
        value: The dict to serialize as JSON and send.

    Raises:
        MissingDependencyError: If kafka-python-ng is not installed.

    """
    import json

    kafka_produce(kafka_ctx, topic, key=key, value=json.dumps(value or {}))


def kafka_produce_multiple(
    kafka_ctx: KafkaContext,
    topic: str,
    messages: list[dict[str, str]],
) -> None:
    """Produce multiple messages to a Kafka topic.

    Args:
        kafka_ctx: The Kafka context to operate on.
        topic: The target Kafka topic.
        messages: A list of dicts with ``key`` and ``value`` keys.

    Raises:
        MissingDependencyError: If kafka-python-ng is not installed.

    """
    for msg in messages:
        kafka_produce(
            kafka_ctx,
            topic,
            key=msg.get("key"),
            value=msg.get("value", ""),
        )


# --- Extended assertions ---


def kafka_assert_message_key_equals(
    messages: list[dict[str, Any]],
    index: int,
    expected: str,
) -> None:
    """Assert that the key of the message at *index* equals *expected*.

    Args:
        messages: The list of consumed messages.
        index: The zero-based message index.
        expected: The expected key value.

    Raises:
        AssertionError: If the index is out of range or the key does not match.

    """
    if index < 0 or index >= len(messages):
        raise AssertionError(
            f"Message index {index} out of range (0-{len(messages) - 1})."
            if messages
            else f"Message index {index} out of range (empty message list)."
        )
    actual = _normalize_value(messages[index].get("key", ""))
    if actual != _normalize_value(expected):
        raise AssertionError(f"Message {index} key: expected '{expected}', got '{actual}'.")


def kafka_assert_message_value_equals(
    messages: list[dict[str, Any]],
    index: int,
    expected: str,
) -> None:
    """Assert that the value of the message at *index* equals *expected*.

    Args:
        messages: The list of consumed messages.
        index: The zero-based message index.
        expected: The expected value.

    Raises:
        AssertionError: If the index is out of range or the value does not match.

    """
    if index < 0 or index >= len(messages):
        raise AssertionError(
            f"Message index {index} out of range (0-{len(messages) - 1})."
            if messages
            else f"Message index {index} out of range (empty message list)."
        )
    actual = _normalize_value(messages[index].get("value", ""))
    if actual != _normalize_value(expected):
        raise AssertionError(f"Message {index} value: expected '{expected}', got '{actual}'.")


def kafka_assert_message_value_matches_regex(
    messages: list[dict[str, Any]],
    pattern: str,
) -> None:
    """Assert that at least one message value matches *pattern* (regex).

    Args:
        messages: The list of consumed messages.
        pattern: The regex pattern to match against message values.

    Raises:
        AssertionError: If no message value matches the pattern.

    """
    import re

    try:
        regex = re.compile(pattern)
    except re.error as exc:
        raise AssertionError(f"Invalid regex pattern '{pattern}': {exc}") from exc
    for msg in messages:
        if regex.search(_normalize_value(msg.get("value", ""))):
            return
    raise AssertionError(f"No message value matches pattern '{pattern}'.")


def kafka_assert_message_count_greater_than(
    messages: list[dict[str, Any]],
    minimum: int,
) -> None:
    """Assert that the number of messages is greater than *minimum*.

    Args:
        messages: The list of consumed messages.
        minimum: The minimum number of messages (exclusive).

    Raises:
        AssertionError: If the count is not greater than *minimum*.

    """
    actual = len(messages)
    if actual <= minimum:
        raise AssertionError(f"Expected more than {minimum} messages, got {actual}.")


def kafka_assert_message_order(
    messages: list[dict[str, Any]],
    expected_keys: list[str],
) -> None:
    """Assert that message keys appear in the order specified by *expected_keys*.

    Args:
        messages: The list of consumed messages.
        expected_keys: The expected sequence of message keys.

    Raises:
        AssertionError: If the message keys do not match the expected order.

    """
    actual_keys = [_normalize_value(msg.get("key", "")) for msg in messages]
    normalized_expected = [_normalize_value(k) for k in expected_keys]
    if actual_keys != normalized_expected:
        raise AssertionError(f"Message order: expected {expected_keys}, got {actual_keys}.")


# --- Store / Extract ---


def kafka_store_message_value(
    messages: list[dict[str, Any]],
    index: int,
    kafka_ctx: KafkaContext,
    variable: str,
) -> None:
    """Store the value of the message at *index* as a variable.

    Args:
        messages: The list of consumed messages.
        index: The zero-based message index.
        kafka_ctx: The Kafka context to store into.
        variable: The variable name to store under.

    Raises:
        AssertionError: If the index is out of range.

    """
    if index < 0 or index >= len(messages):
        raise AssertionError(
            f"Message index {index} out of range (0-{len(messages) - 1})."
            if messages
            else f"Message index {index} out of range (empty message list)."
        )
    kafka_ctx.variables[variable] = messages[index].get("value", "")


def kafka_store_message_key(
    messages: list[dict[str, Any]],
    index: int,
    kafka_ctx: KafkaContext,
    variable: str,
) -> None:
    """Store the key of the message at *index* as a variable.

    Args:
        messages: The list of consumed messages.
        index: The zero-based message index.
        kafka_ctx: The Kafka context to store into.
        variable: The variable name to store under.

    Raises:
        AssertionError: If the index is out of range.

    """
    if index < 0 or index >= len(messages):
        raise AssertionError(
            f"Message index {index} out of range (0-{len(messages) - 1})."
            if messages
            else f"Message index {index} out of range (empty message list)."
        )
    kafka_ctx.variables[variable] = messages[index].get("key", "")


def kafka_store_message_count(
    messages: list[dict[str, Any]],
    kafka_ctx: KafkaContext,
    variable: str,
) -> None:
    """Store the message count as a variable.

    Args:
        messages: The list of consumed messages.
        kafka_ctx: The Kafka context to store into.
        variable: The variable name to store under.

    """
    kafka_ctx.variables[variable] = len(messages)


# --- Config ---


def kafka_set_consumer_group(kafka_ctx: KafkaContext, group: str) -> None:
    """Set the Kafka consumer group ID.

    Args:
        kafka_ctx: The Kafka context to operate on.
        group: The consumer group ID.

    """
    kafka_ctx.consumer_group = group


def kafka_set_auto_offset_reset(kafka_ctx: KafkaContext, strategy: str) -> None:
    """Set the auto offset reset strategy.

    Args:
        kafka_ctx: The Kafka context to operate on.
        strategy: ``"earliest"`` or ``"latest"``.

    Raises:
        ValueError: If the strategy is not valid.

    """
    if strategy not in ("earliest", "latest"):
        raise ValueError(
            f"Invalid auto_offset_reset: '{strategy}'. Must be 'earliest' or 'latest'."
        )
    kafka_ctx.auto_offset_reset = strategy


def kafka_set_producer_config(kafka_ctx: KafkaContext, config: dict[str, Any]) -> None:
    """Set additional producer configuration overrides.

    Args:
        kafka_ctx: The Kafka context to operate on.
        config: A dict of producer configuration key-value pairs.

    """
    kafka_ctx.producer_config.update(config)


def kafka_set_consumer_config(kafka_ctx: KafkaContext, config: dict[str, Any]) -> None:
    """Set additional consumer configuration overrides.

    Args:
        kafka_ctx: The Kafka context to operate on.
        config: A dict of consumer configuration key-value pairs.

    """
    kafka_ctx.consumer_config.update(config)
