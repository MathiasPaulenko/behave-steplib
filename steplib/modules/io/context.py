"""IOContext: per-scenario state for the io module (files, JSON, CSV)."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from typing import Any, TextIO


@dataclass
class IOContext:
    """Holds all io-module state for a scenario.

    Lives at ``context.steplib.io`` and is reset between scenarios.

    Attributes:
        variables: User-defined variables stored by file steps.
        _last_json: The last parsed JSON value (dict or list).
        _csv_writer: Active CSV writer instance, if any.
        _csv_file: Underlying file handle for the CSV writer, if any.

    """

    variables: dict[str, Any] = field(default_factory=dict)
    _last_json: Any = None
    _csv_writer: csv.DictWriter[str] | None = None
    _csv_file: TextIO | None = None

    def reset(self) -> None:
        """Reset per-scenario state, closing any open CSV writer."""
        self.variables = {}
        self._last_json = None
        self._close_csv()
        self._csv_writer = None
        self._csv_file = None

    def cleanup(self) -> None:
        """Clean up resources after the scenario."""
        self._close_csv()

    def _close_csv(self) -> None:
        """Close the CSV file handle if open."""
        if self._csv_file is not None and not self._csv_file.closed:
            self._csv_file.close()
