"""Regression tests for CLI bugs found in the audit."""

from __future__ import annotations

import json

from steplib.cli.formatters import format_step_detail_json
from steplib.core.metadata import Param, StepInfo


def _info(**kwargs) -> StepInfo:
    base: dict = {
        "pattern": "I do {thing}",
        "category": "test",
        "func": lambda ctx: None,
        "description": "",
        "parameters": [],
    }
    base.update(kwargs)
    return StepInfo(**base)


class TestDetailJsonSerialization:
    """show --json must not crash on non-serializable param defaults."""

    def test_non_serializable_default_is_stringified(self):
        param = Param(
            name="thing",
            type=str,
            required=False,
            default=object(),
            description="",
        )
        out = format_step_detail_json(_info(parameters=[param]))
        parsed = json.loads(out)
        assert isinstance(parsed["parameters"][0]["default"], str)

    def test_non_serializable_choice_is_stringified(self):
        param = Param(
            name="thing",
            type=str,
            required=False,
            default=None,
            description="",
            choices=[object()],
        )
        out = format_step_detail_json(_info(parameters=[param]))
        parsed = json.loads(out)
        assert isinstance(parsed["parameters"][0]["choices"][0], str)
