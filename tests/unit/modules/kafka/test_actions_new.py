"""Tests for new Kafka actions (pure functions)."""

from __future__ import annotations

import sys
import types

import pytest

from steplib.modules.kafka.actions import (
    kafka_assert_message_count_greater_than,
    kafka_assert_message_key_equals,
    kafka_assert_message_order,
    kafka_assert_message_value_equals,
    kafka_assert_message_value_matches_regex,
    kafka_consume,
    kafka_set_auto_offset_reset,
    kafka_set_consumer_config,
    kafka_set_consumer_group,
    kafka_set_producer_config,
    kafka_store_message_count,
    kafka_store_message_key,
    kafka_store_message_value,
)
from steplib.modules.kafka.context import KafkaContext


@pytest.fixture()
def kafka_ctx() -> KafkaContext:
    """Return a KafkaContext for testing."""
    return KafkaContext()


# --- Extended assertions ---


class TestKafkaAssertMessageKeyEquals:
    def test_key_matches(self) -> None:
        messages = [{"key": "user1", "value": "hello"}, {"key": "user2", "value": "world"}]
        kafka_assert_message_key_equals(messages, 0, "user1")

    def test_key_mismatch_raises(self) -> None:
        messages = [{"key": "user1", "value": "hello"}]
        with pytest.raises(AssertionError, match="Message 0 key"):
            kafka_assert_message_key_equals(messages, 0, "user2")

    def test_index_out_of_range_raises(self) -> None:
        messages = [{"key": "user1", "value": "hello"}]
        with pytest.raises(AssertionError, match="out of range"):
            kafka_assert_message_key_equals(messages, 5, "user1")


class TestKafkaAssertMessageValueEquals:
    def test_value_matches(self) -> None:
        messages = [{"key": "user1", "value": "hello"}, {"key": "user2", "value": "world"}]
        kafka_assert_message_value_equals(messages, 0, "hello")

    def test_value_mismatch_raises(self) -> None:
        messages = [{"key": "user1", "value": "hello"}]
        with pytest.raises(AssertionError, match="Message 0 value"):
            kafka_assert_message_value_equals(messages, 0, "world")

    def test_index_out_of_range_raises(self) -> None:
        messages = [{"key": "user1", "value": "hello"}]
        with pytest.raises(AssertionError, match="out of range"):
            kafka_assert_message_value_equals(messages, 5, "hello")


class TestKafkaAssertMessageValueMatchesRegex:
    def test_regex_matches(self) -> None:
        messages = [{"value": "user-123"}, {"value": "other"}]
        kafka_assert_message_value_matches_regex(messages, r"user-\d+")

    def test_regex_no_match_raises(self) -> None:
        messages = [{"value": "other"}]
        with pytest.raises(AssertionError, match="No message value matches"):
            kafka_assert_message_value_matches_regex(messages, r"user-\d+")

    def test_empty_messages_raises(self) -> None:
        with pytest.raises(AssertionError, match="No message value matches"):
            kafka_assert_message_value_matches_regex([], r"user-\d+")


class TestKafkaAssertMessageCountGreaterThan:
    def test_count_greater_passes(self) -> None:
        messages = [{"value": "a"}, {"value": "b"}]
        kafka_assert_message_count_greater_than(messages, 1)

    def test_count_greater_fails(self) -> None:
        messages = [{"value": "a"}]
        with pytest.raises(AssertionError, match="Expected more than"):
            kafka_assert_message_count_greater_than(messages, 1)


class TestKafkaAssertMessageOrder:
    def test_order_matches(self) -> None:
        messages = [
            {"key": "a", "value": "1"},
            {"key": "b", "value": "2"},
            {"key": "c", "value": "3"},
        ]
        kafka_assert_message_order(messages, ["a", "b", "c"])

    def test_order_mismatch_raises(self) -> None:
        messages = [
            {"key": "a", "value": "1"},
            {"key": "b", "value": "2"},
        ]
        with pytest.raises(AssertionError, match="Message order"):
            kafka_assert_message_order(messages, ["b", "a"])


# --- Store / Extract ---


class TestKafkaStoreMessageValue:
    def test_store_value(self, kafka_ctx: KafkaContext) -> None:
        messages = [{"key": "k1", "value": "v1"}, {"key": "k2", "value": "v2"}]
        kafka_store_message_value(messages, 0, kafka_ctx, "first_val")
        assert kafka_ctx.variables["first_val"] == "v1"

    def test_store_value_out_of_range_raises(self, kafka_ctx: KafkaContext) -> None:
        messages = [{"key": "k1", "value": "v1"}]
        with pytest.raises(AssertionError, match="out of range"):
            kafka_store_message_value(messages, 5, kafka_ctx, "val")


class TestKafkaStoreMessageKey:
    def test_store_key(self, kafka_ctx: KafkaContext) -> None:
        messages = [{"key": "k1", "value": "v1"}, {"key": "k2", "value": "v2"}]
        kafka_store_message_key(messages, 1, kafka_ctx, "second_key")
        assert kafka_ctx.variables["second_key"] == "k2"

    def test_store_key_out_of_range_raises(self, kafka_ctx: KafkaContext) -> None:
        messages = [{"key": "k1", "value": "v1"}]
        with pytest.raises(AssertionError, match="out of range"):
            kafka_store_message_key(messages, 5, kafka_ctx, "key")


class TestKafkaStoreMessageCount:
    def test_store_count(self, kafka_ctx: KafkaContext) -> None:
        messages = [{"value": "a"}, {"value": "b"}, {"value": "c"}]
        kafka_store_message_count(messages, kafka_ctx, "total")
        assert kafka_ctx.variables["total"] == 3

    def test_store_count_empty(self, kafka_ctx: KafkaContext) -> None:
        kafka_store_message_count([], kafka_ctx, "total")
        assert kafka_ctx.variables["total"] == 0


# --- Config ---


class TestKafkaSetConsumerGroup:
    def test_set_group(self, kafka_ctx: KafkaContext) -> None:
        kafka_set_consumer_group(kafka_ctx, "my-group")
        assert kafka_ctx.consumer_group == "my-group"


class TestKafkaSetAutoOffsetReset:
    def test_set_earliest(self, kafka_ctx: KafkaContext) -> None:
        kafka_set_auto_offset_reset(kafka_ctx, "earliest")
        assert kafka_ctx.auto_offset_reset == "earliest"

    def test_set_latest(self, kafka_ctx: KafkaContext) -> None:
        kafka_set_auto_offset_reset(kafka_ctx, "latest")
        assert kafka_ctx.auto_offset_reset == "latest"

    def test_invalid_strategy_raises(self, kafka_ctx: KafkaContext) -> None:
        with pytest.raises(ValueError, match="Invalid auto_offset_reset"):
            kafka_set_auto_offset_reset(kafka_ctx, "middle")


class TestKafkaSetProducerConfig:
    def test_set_producer_config(self, kafka_ctx: KafkaContext) -> None:
        kafka_set_producer_config(kafka_ctx, {"acks": "all", "retries": 3})
        assert kafka_ctx.producer_config["acks"] == "all"
        assert kafka_ctx.producer_config["retries"] == 3

    def test_set_producer_config_merges(self, kafka_ctx: KafkaContext) -> None:
        kafka_set_producer_config(kafka_ctx, {"acks": "all"})
        kafka_set_producer_config(kafka_ctx, {"retries": 3})
        assert kafka_ctx.producer_config == {"acks": "all", "retries": 3}


class TestKafkaSetConsumerConfig:
    def test_set_consumer_config(self, kafka_ctx: KafkaContext) -> None:
        kafka_set_consumer_config(kafka_ctx, {"enable.auto.commit": False})
        assert kafka_ctx.consumer_config["enable.auto.commit"] is False

    def test_set_consumer_config_merges(self, kafka_ctx: KafkaContext) -> None:
        kafka_set_consumer_config(kafka_ctx, {"enable.auto.commit": False})
        kafka_set_consumer_config(kafka_ctx, {"auto.offset.reset": "earliest"})
        assert kafka_ctx.consumer_config == {
            "enable.auto.commit": False,
            "auto.offset.reset": "earliest",
        }


# --- Context lifecycle with new fields ---


class TestKafkaContextNewFields:
    def test_default_values(self) -> None:
        ctx = KafkaContext()
        assert ctx.consumer_group == "steplib-group"
        assert ctx.auto_offset_reset == "earliest"
        assert ctx.producer_config == {}
        assert ctx.consumer_config == {}

    def test_reset_preserves_group_clears_config(self) -> None:
        ctx = KafkaContext()
        ctx.consumer_group = "test-group"
        ctx.producer_config = {"acks": "all"}
        ctx.consumer_config = {"enable.auto.commit": False}
        ctx.variables["key"] = "value"
        ctx.reset()
        assert ctx.consumer_group == "test-group"
        assert ctx.producer_config == {}
        assert ctx.consumer_config == {}
        assert ctx.variables == {}


# --- Config propagation regression tests ---


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


class TestKafkaConsumeConfigPropagation:
    """Regression tests: kafka_consume must respect context config."""

    def test_consume_uses_auto_offset_reset_from_context(self) -> None:
        """kafka_consume should use auto_offset_reset from context, not hardcoded."""
        ctx = KafkaContext()
        ctx.auto_offset_reset = "latest"
        captured: dict[str, object] = {}
        _inject_fake_kafka(captured)
        try:
            kafka_consume(ctx, "test-topic", timeout_ms=100, max_records=1)
        finally:
            _remove_fake_kafka()
        assert captured.get("auto_offset_reset") == "latest"

    def test_consume_uses_consumer_group_from_context(self) -> None:
        """kafka_consume should use consumer_group from context."""
        ctx = KafkaContext()
        ctx.consumer_group = "my-test-group"
        captured: dict[str, object] = {}
        _inject_fake_kafka(captured)
        try:
            kafka_consume(ctx, "test-topic", timeout_ms=100, max_records=1)
        finally:
            _remove_fake_kafka()
        assert captured.get("group_id") == "my-test-group"

    def test_consume_merges_consumer_config_overrides(self) -> None:
        """kafka_consume should merge consumer_config overrides."""
        ctx = KafkaContext()
        ctx.consumer_config = {"enable.auto.commit": False}
        captured: dict[str, object] = {}
        _inject_fake_kafka(captured)
        try:
            kafka_consume(ctx, "test-topic", timeout_ms=100, max_records=1)
        finally:
            _remove_fake_kafka()
        assert captured.get("enable.auto.commit") is False


class TestKafkaContextReset:
    """Tests for KafkaContext.reset() to verify config leak prevention."""

    def test_reset_clears_producer_config(self) -> None:
        """reset() should clear producer_config to prevent cross-scenario leaks."""
        ctx = KafkaContext()
        ctx.producer_config = {"acks": "all", "linger.ms": 10}
        ctx.reset()
        assert ctx.producer_config == {}

    def test_reset_clears_consumer_config(self) -> None:
        """reset() should clear consumer_config to prevent cross-scenario leaks."""
        ctx = KafkaContext()
        ctx.consumer_config = {"enable.auto.commit": False, "max.poll.records": 50}
        ctx.reset()
        assert ctx.consumer_config == {}

    def test_reset_preserves_bootstrap_servers(self) -> None:
        """reset() should preserve bootstrap_servers (set in before_all)."""
        ctx = KafkaContext()
        ctx.bootstrap_servers = "broker1:9092,broker2:9092"
        ctx.reset()
        assert ctx.bootstrap_servers == "broker1:9092,broker2:9092"
