"""Output formatters for the steplib CLI."""

from __future__ import annotations

import json
from typing import Any

from steplib.core.metadata import StepInfo


def format_step_table(steps: list[StepInfo]) -> str:
    """Format a list of steps as a simple aligned table.

    Args:
        steps: The step metadata entries to render.

    Returns:
        A multi-line string with columns: PATTERN, CATEGORY, BACKEND, DESCRIPTION.

    """
    if not steps:
        return "No steps found."

    headers = ("PATTERN", "CATEGORY", "BACKEND", "DESCRIPTION")
    rows: list[tuple[str, str, str, str]] = []
    for info in steps:
        rows.append(
            (
                info.pattern,
                info.category,
                info.backend or "-",
                (info.description or "").split("\n")[0][:60],
            )
        )

    col_widths = [max(len(str(row[i])) for row in [headers, *rows]) for i in range(len(headers))]

    lines: list[str] = []
    header_line = "  ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers)))
    lines.append(header_line)
    lines.append("  ".join("-" * col_widths[i] for i in range(len(headers))))
    for row in rows:
        lines.append("  ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers))))
    return "\n".join(lines)


def format_step_detail(info: StepInfo) -> str:
    """Format a single step's metadata for detailed display.

    Args:
        info: The step metadata to render.

    Returns:
        A multi-line string with all metadata fields.

    """
    lines: list[str] = [
        f"Pattern:    {info.pattern}",
        f"Category:   {info.category}",
        f"Backend:    {info.backend or '-'}",
        f"Module:     {info.module}",
        f"Function:   {info.qualified_name}",
    ]

    if info.description:
        lines.append(f"Description: {info.description}")
    if info.example:
        lines.append(f"Example:    {info.example}")
    if info.tags:
        lines.append(f"Tags:       {', '.join(info.tags)}")
    if info.version:
        lines.append(f"Version:    {info.version}")
    if info.deprecated:
        lines.append(f"Deprecated: {info.deprecated}")
    if info.requires:
        lines.append(f"Requires:   {', '.join(info.requires)}")

    if info.parameters:
        lines.append("Parameters:")
        for param in info.parameters:
            type_name = param.type.__name__ if isinstance(param.type, type) else str(param.type)
            default_hint = f", default {param.default!r}" if param.default is not None else ""
            required_hint = " (required)" if param.required else ""
            lines.append(f"  - {param.name}: {type_name}{required_hint}{default_hint}")

    if info.i18n:
        lines.append("Translations:")
        for lang, translated in info.i18n.items():
            lines.append(f"  [{lang}] {translated}")

    return "\n".join(lines)


def format_step_json(steps: list[StepInfo]) -> str:
    """Format a list of steps as a JSON array.

    Args:
        steps: The step metadata entries to serialize.

    Returns:
        A JSON string with pattern, category, backend, and description per step.

    """
    data: list[dict[str, Any]] = []
    for info in steps:
        data.append(
            {
                "pattern": info.pattern,
                "category": info.category,
                "backend": info.backend,
                "description": info.description,
                "module": info.module,
                "tags": info.tags,
                "version": info.version,
                "deprecated": info.deprecated,
                "example": info.example,
                "i18n": info.i18n,
            }
        )
    return json.dumps(data, indent=2, ensure_ascii=False)


def format_step_detail_json(info: StepInfo) -> str:
    """Format a single step's metadata as JSON.

    Args:
        info: The step metadata to serialize.

    Returns:
        A JSON string with all metadata fields.

    """
    data: dict[str, Any] = {
        "pattern": info.pattern,
        "category": info.category,
        "backend": info.backend,
        "description": info.description,
        "module": info.module,
        "function": info.qualified_name,
        "example": info.example,
        "tags": info.tags,
        "version": info.version,
        "deprecated": info.deprecated,
        "requires": info.requires,
        "i18n": info.i18n,
        "parameters": [
            {
                "name": p.name,
                "type": p.type.__name__ if isinstance(p.type, type) else str(p.type),
                "required": p.required,
                "default": p.default,
                "description": p.description,
                "choices": p.choices,
            }
            for p in info.parameters
        ],
    }
    return json.dumps(data, indent=2, ensure_ascii=False)
