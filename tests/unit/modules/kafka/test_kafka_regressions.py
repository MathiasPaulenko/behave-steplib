"""Regression tests for Kafka module bugs found in the audit."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from steplib.modules.kafka.context import KafkaContext


def _kafka_ctx() -> KafkaContext:
    return KafkaContext(bootstrap_servers="localhost:9092")


class TestProducerConsumerConfigValidation:
    """JSON config strings must decode to objects, not other types."""

    def test_set_producer_config_rejects_json_array(self):
        from steplib.modules.kafka.steps import step_set_producer_config

        ctx = SimpleNamespace(steplib=SimpleNamespace(kafka=_kafka_ctx()))
        with pytest.raises(AssertionError):
            step_set_producer_config(ctx, '["a", "b"]')

    def test_set_consumer_config_rejects_json_array(self):
        from steplib.modules.kafka.steps import step_set_consumer_config

        ctx = SimpleNamespace(steplib=SimpleNamespace(kafka=_kafka_ctx()))
        with pytest.raises(AssertionError):
            step_set_consumer_config(ctx, '["a", "b"]')

    def test_valid_config_object_still_works(self):
        from steplib.modules.kafka.steps import step_set_producer_config

        kafka = _kafka_ctx()
        ctx = SimpleNamespace(steplib=SimpleNamespace(kafka=kafka))
        step_set_producer_config(ctx, '{"acks": "all"}')
        assert kafka.producer_config.get("acks") == "all"


class TestKafkaCleanupResilience:
    """Producer close failure must not skip consumer close."""

    def test_cleanup_continues_after_producer_close_failure(self):
        class BadProducer:
            def close(self) -> None:
                raise RuntimeError("producer close failed")

        class GoodConsumer:
            def __init__(self) -> None:
                self.closed = False

            def close(self) -> None:
                self.closed = True

        kafka = _kafka_ctx()
        kafka.producer = BadProducer()  # type: ignore[assignment]
        consumer = GoodConsumer()
        kafka.consumer = consumer  # type: ignore[assignment]

        with pytest.raises(RuntimeError, match="producer close failed"):
            kafka.cleanup()

        assert consumer.closed is True
        assert kafka.producer is None
        assert kafka.consumer is None
