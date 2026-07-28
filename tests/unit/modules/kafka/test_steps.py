"""Tests for Kafka steps (using mock context)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from steplib.core.state import SteplibState
from steplib.modules.kafka.context import KafkaContext
from steplib.modules.kafka.steps import (
    step_message_contains,
    step_message_count,
    step_set_consumer_config,
    step_set_kafka_servers,
    step_set_producer_config,
)


def _make_context(messages: list[dict[str, str]] | None = None) -> SimpleNamespace:
    """Create a behave-like context with steplib state and KafkaContext."""
    context = SimpleNamespace()
    state = SteplibState(context, registry=None)  # type: ignore[arg-type]
    state.kafka = KafkaContext()  # type: ignore[attr-defined]
    state.kafka.variables["_last_messages"] = messages or [  # type: ignore[attr-defined]
        {"value": "hello world", "key": "id", "topic": "events", "partition": 0, "offset": 0},
    ]
    context.steplib = state
    return context


def test_step_set_kafka_servers() -> None:
    """step_set_kafka_servers should set the bootstrap servers."""
    context = _make_context()
    step_set_kafka_servers(context, '"localhost:9092"')
    assert context.steplib.kafka.bootstrap_servers == "localhost:9092"  # type: ignore[attr-defined]


def test_step_message_count() -> None:
    """step_message_count should assert the message count."""
    context = _make_context(messages=[{"value": "a"}, {"value": "b"}])
    step_message_count(context, 2)


def test_step_message_count_mismatch() -> None:
    """step_message_count should raise on mismatch."""
    context = _make_context(messages=[{"value": "a"}])
    with pytest.raises(AssertionError, match="Expected 5 messages"):
        step_message_count(context, 5)


def test_step_message_contains() -> None:
    """step_message_contains should assert a message contains text."""
    context = _make_context()
    step_message_contains(context, '"hello"')


def test_step_message_contains_not_found() -> None:
    """step_message_contains should raise if no message contains text."""
    context = _make_context()
    with pytest.raises(AssertionError, match="No message contains"):
        step_message_contains(context, '"nonexistent"')


class TestBug14KafkaStepsInvalidJson:
    """Regression tests for Bug 14: kafka step functions should raise
    AssertionError, not json.JSONDecodeError, when JSON input is invalid."""

    def test_set_producer_config_invalid_json_raises_assertion(self) -> None:
        context = _make_context()
        with pytest.raises(AssertionError, match="Invalid JSON config"):
            step_set_producer_config(context, "'{invalid json}'")

    def test_set_consumer_config_invalid_json_raises_assertion(self) -> None:
        context = _make_context()
        with pytest.raises(AssertionError, match="Invalid JSON config"):
            step_set_consumer_config(context, "'{invalid json}'")
