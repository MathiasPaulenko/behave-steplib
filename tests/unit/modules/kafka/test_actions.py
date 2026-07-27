"""Tests for Kafka actions (pure functions)."""

from __future__ import annotations

import pytest

from steplib.modules.kafka.actions import (
    kafka_assert_message_contains,
    kafka_assert_message_count,
    kafka_set_bootstrap_servers,
)
from steplib.modules.kafka.context import KafkaContext


class TestKafkaSetBootstrapServers:
    """Tests for kafka_set_bootstrap_servers."""

    def test_set_servers(self) -> None:
        """Setting bootstrap servers should update the context."""
        ctx = KafkaContext()
        kafka_set_bootstrap_servers(ctx, "broker1:9092,broker2:9092")
        assert ctx.bootstrap_servers == "broker1:9092,broker2:9092"


class TestKafkaAssertMessageCount:
    """Tests for kafka_assert_message_count."""

    def test_count_matches(self) -> None:
        """Matching count should not raise."""
        messages = [{"value": "a"}, {"value": "b"}, {"value": "c"}]
        kafka_assert_message_count(messages, 3)

    def test_count_mismatch_raises(self) -> None:
        """Mismatched count should raise."""
        messages = [{"value": "a"}]
        with pytest.raises(AssertionError, match="Expected 5 messages"):
            kafka_assert_message_count(messages, 5)


class TestKafkaAssertMessageContains:
    """Tests for kafka_assert_message_contains."""

    def test_contains_text(self) -> None:
        """Containing text should not raise."""
        messages = [{"value": "hello world"}, {"value": "other"}]
        kafka_assert_message_contains(messages, "hello")

    def test_not_contains_raises(self) -> None:
        """Not containing text should raise."""
        messages = [{"value": "other"}]
        with pytest.raises(AssertionError, match="No message contains"):
            kafka_assert_message_contains(messages, "hello")

    def test_empty_messages_raises(self) -> None:
        """Empty messages list should raise."""
        with pytest.raises(AssertionError, match="No message contains"):
            kafka_assert_message_contains([], "hello")


class TestKafkaContextLifecycle:
    """Tests for KafkaContext.reset and cleanup."""

    def test_reset_clears_variables(self) -> None:
        """reset() should clear variables."""
        ctx = KafkaContext()
        ctx.variables["key"] = "value"
        ctx.reset()
        assert ctx.variables == {}

    def test_cleanup_closes_producer_and_consumer(self) -> None:
        """cleanup() should close producer and consumer."""
        ctx = KafkaContext()
        ctx.producer = type("MockProducer", (), {"close": lambda self: None})()
        ctx.consumer = type("MockConsumer", (), {"close": lambda self: None})()
        ctx.cleanup()
        assert ctx.producer is None
        assert ctx.consumer is None
