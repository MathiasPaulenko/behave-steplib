"""KafkaContext: per-scenario Kafka state for the Kafka module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class KafkaContext:
    """Holds all Kafka state for a scenario.

    Lives at ``context.steplib.kafka`` and is reset between scenarios.

    Attributes:
        producer: The Kafka producer instance.
        consumer: The Kafka consumer instance.
        bootstrap_servers: Comma-separated Kafka bootstrap server addresses.
        variables: User-defined variables stored by steps.
        backend: The backend name (e.g. ``"kafka-python-ng"``).

    """

    producer: Any = None
    consumer: Any = None
    bootstrap_servers: str = "localhost:9092"
    variables: dict[str, Any] = field(default_factory=dict)
    backend: str = "kafka-python-ng"

    def reset(self) -> None:
        """Reset per-scenario state, keeping the producer/consumer config."""
        self.variables = {}

    def cleanup(self) -> None:
        """Close the producer and consumer if they exist."""
        if self.producer is not None and hasattr(self.producer, "close"):
            self.producer.close()
            self.producer = None
        if self.consumer is not None and hasattr(self.consumer, "close"):
            self.consumer.close()
            self.consumer = None
