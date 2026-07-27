"""Tests for Kafka actions (MissingDependencyError on missing kafka-python-ng)."""

from __future__ import annotations

import contextlib

import pytest

from steplib.core.exceptions import MissingDependencyError
from steplib.modules.kafka.actions import kafka_consume, kafka_produce
from steplib.modules.kafka.context import KafkaContext


def test_kafka_produce_missing_dependency_raises() -> None:
    """kafka_produce should raise MissingDependencyError if kafka is not installed."""
    with contextlib.suppress(ImportError):
        import kafka  # noqa: F401, PLC0415
        # kafka is installed; skip this test.
        return

    ctx = KafkaContext()
    with pytest.raises(MissingDependencyError, match="kafka"):
        kafka_produce(ctx, topic="test", value="hello")


def test_kafka_consume_missing_dependency_raises() -> None:
    """kafka_consume should raise MissingDependencyError if kafka is not installed."""
    with contextlib.suppress(ImportError):
        import kafka  # noqa: F401, PLC0415
        # kafka is installed; skip this test.
        return

    ctx = KafkaContext()
    with pytest.raises(MissingDependencyError, match="kafka"):
        kafka_consume(ctx, topic="test")
