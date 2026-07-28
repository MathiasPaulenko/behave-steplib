"""Extended tests for Kafka step functions (thin wrappers around actions)."""

from __future__ import annotations

import sys
import types
from types import SimpleNamespace
from typing import Any

import pytest

from steplib.core.state import SteplibState
from steplib.modules.kafka.context import KafkaContext
from steplib.modules.kafka.steps import (
    step_consume_messages,
    step_consume_with_timeout,
    step_message_count_greater_than,
    step_message_key_equals,
    step_message_order,
    step_message_value_equals,
    step_message_value_matches_regex,
    step_set_auto_offset_reset,
    step_set_consumer_config,
    step_set_consumer_group,
    step_set_producer_config,
    step_store_message_count,
    step_store_message_key,
    step_store_message_value,
)

_DEFAULT_MESSAGES: list[dict[str, Any]] = [
    {"value": "hello world", "key": "id", "topic": "events", "partition": 0, "offset": 0},
]


def _make_context(messages: list[dict[str, Any]] | None = None) -> SimpleNamespace:
    """Create a behave-like context with steplib state and KafkaContext."""
    context = SimpleNamespace()
    state = SteplibState(context, registry=None)  # type: ignore[arg-type]
    state.kafka = KafkaContext()  # type: ignore[attr-defined]
    state.kafka.variables["_last_messages"] = (  # type: ignore[attr-defined]
        messages if messages is not None else _DEFAULT_MESSAGES
    )
    context.steplib = state
    return context


# --- Config ---


def test_step_set_consumer_group() -> None:
    context = _make_context()
    step_set_consumer_group(context, '"my-group"')
    assert context.steplib.kafka.consumer_group == "my-group"  # type: ignore[attr-defined]


def test_step_set_auto_offset_reset() -> None:
    context = _make_context()
    step_set_auto_offset_reset(context, '"latest"')
    assert context.steplib.kafka.auto_offset_reset == "latest"  # type: ignore[attr-defined]


def test_step_set_auto_offset_reset_invalid() -> None:
    context = _make_context()
    with pytest.raises(ValueError, match="Invalid auto_offset_reset"):
        step_set_auto_offset_reset(context, '"middle"')


def test_step_set_producer_config() -> None:
    context = _make_context()
    step_set_producer_config(context, '\'{"acks": "all", "retries": 3}\'')
    assert context.steplib.kafka.producer_config["acks"] == "all"  # type: ignore[attr-defined]
    assert context.steplib.kafka.producer_config["retries"] == 3  # type: ignore[attr-defined]


def test_step_set_consumer_config() -> None:
    context = _make_context()
    step_set_consumer_config(context, '\'{"enable.auto.commit": false}\'')
    assert context.steplib.kafka.consumer_config["enable.auto.commit"] is False  # type: ignore[attr-defined]


# --- Extended assertions ---


def test_step_message_key_equals() -> None:
    context = _make_context(messages=[{"key": "user1", "value": "hello"}])
    step_message_key_equals(context, 0, '"user1"')


def test_step_message_key_equals_raises() -> None:
    context = _make_context(messages=[{"key": "user1", "value": "hello"}])
    with pytest.raises(AssertionError, match="Message 0 key"):
        step_message_key_equals(context, 0, '"user2"')


def test_step_message_value_equals() -> None:
    context = _make_context(messages=[{"key": "user1", "value": "hello"}])
    step_message_value_equals(context, 0, '"hello"')


def test_step_message_value_equals_raises() -> None:
    context = _make_context(messages=[{"key": "user1", "value": "hello"}])
    with pytest.raises(AssertionError, match="Message 0 value"):
        step_message_value_equals(context, 0, '"world"')


def test_step_message_value_matches_regex() -> None:
    context = _make_context(messages=[{"value": "user-123"}, {"value": "other"}])
    step_message_value_matches_regex(context, r'"user-\d+"')


def test_step_message_value_matches_regex_raises() -> None:
    context = _make_context(messages=[{"value": "other"}])
    with pytest.raises(AssertionError, match="No message value matches"):
        step_message_value_matches_regex(context, r'"user-\d+"')


def test_step_message_count_greater_than() -> None:
    context = _make_context(messages=[{"value": "a"}, {"value": "b"}])
    step_message_count_greater_than(context, 1)


def test_step_message_count_greater_than_raises() -> None:
    context = _make_context(messages=[{"value": "a"}])
    with pytest.raises(AssertionError, match="Expected more than"):
        step_message_count_greater_than(context, 1)


def test_step_message_order() -> None:
    context = _make_context(messages=[
        {"key": "a", "value": "1"},
        {"key": "b", "value": "2"},
        {"key": "c", "value": "3"},
    ])
    step_message_order(context, '"a,b,c"')


def test_step_message_order_raises() -> None:
    context = _make_context(messages=[
        {"key": "a", "value": "1"},
        {"key": "b", "value": "2"},
    ])
    with pytest.raises(AssertionError, match="Message order"):
        step_message_order(context, '"b,a"')


# --- Store / Extract ---


def test_step_store_message_value() -> None:
    context = _make_context(messages=[{"key": "k1", "value": "v1"}, {"key": "k2", "value": "v2"}])
    step_store_message_value(context, 0, '"first_val"')
    assert context.steplib.kafka.variables["first_val"] == "v1"  # type: ignore[attr-defined]


def test_step_store_message_value_out_of_range() -> None:
    context = _make_context(messages=[{"key": "k1", "value": "v1"}])
    with pytest.raises(AssertionError, match="out of range"):
        step_store_message_value(context, 5, '"val"')


def test_step_store_message_key() -> None:
    context = _make_context(messages=[{"key": "k1", "value": "v1"}, {"key": "k2", "value": "v2"}])
    step_store_message_key(context, 1, '"second_key"')
    assert context.steplib.kafka.variables["second_key"] == "k2"  # type: ignore[attr-defined]


def test_step_store_message_key_out_of_range() -> None:
    context = _make_context(messages=[{"key": "k1", "value": "v1"}])
    with pytest.raises(AssertionError, match="out of range"):
        step_store_message_key(context, 5, '"key"')


def test_step_store_message_count() -> None:
    context = _make_context(messages=[{"value": "a"}, {"value": "b"}, {"value": "c"}])
    step_store_message_count(context, '"total"')
    assert context.steplib.kafka.variables["total"] == 3  # type: ignore[attr-defined]


def test_step_store_message_count_empty() -> None:
    context = _make_context(messages=[])
    step_store_message_count(context, '"total"')
    assert context.steplib.kafka.variables["total"] == 0  # type: ignore[attr-defined]


# --- Consume (with mocked kafka module) ---


def _inject_fake_kafka(captured: dict[str, object]) -> None:
    """Inject a fake kafka module into sys.modules that captures consumer config."""

    class FakeConsumer:
        def __init__(self, topic: str, **kwargs: object) -> None:
            captured.update(kwargs)

        def poll(self, timeout_ms: int, max_records: int) -> dict[object, list[object]]:
            return {}

        def close(self) -> None:
            pass

    fake_mod = types.ModuleType("kafka")
    fake_mod.KafkaConsumer = FakeConsumer  # type: ignore[attr-defined]
    sys.modules["kafka"] = fake_mod


def _remove_fake_kafka() -> None:
    """Remove the fake kafka module from sys.modules."""
    sys.modules.pop("kafka", None)


def test_step_consume_messages() -> None:
    context = _make_context()
    captured: dict[str, object] = {}
    _inject_fake_kafka(captured)
    try:
        step_consume_messages(context, '"test-topic"')
    finally:
        _remove_fake_kafka()
    assert context.steplib.kafka.variables["_last_messages"] == []  # type: ignore[attr-defined]


def test_step_consume_with_timeout() -> None:
    context = _make_context()
    captured: dict[str, object] = {}
    _inject_fake_kafka(captured)
    try:
        step_consume_with_timeout(context, '"test-topic"', 10000)
    finally:
        _remove_fake_kafka()
    assert context.steplib.kafka.variables["_last_messages"] == []  # type: ignore[attr-defined]
