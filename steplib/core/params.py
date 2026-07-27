"""Parameter types and the ``Param`` dataclass for step metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import NoneType
from typing import Any


@dataclass(frozen=True, slots=True)
class Param:
    """Describes a single step parameter extracted from the pattern.

    Attributes:
        name: Placeholder name as it appears in the pattern (e.g. ``"method"``).
        type: Python type or registered type name (e.g. ``int``, ``"Json"``).
        required: Whether the parameter must be present.
        default: Default value when the parameter is not in the pattern.
        description: Human-readable description of the parameter.
        choices: Allowed values after conversion.

    """

    name: str
    type: type[Any] | str = str
    required: bool = False
    default: Any = None
    description: str | None = None
    choices: list[Any] = field(default_factory=list)


# --- Built-in transformable types (names usable in patterns) ---

BUILTIN_TYPES: dict[str, type[Any]] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "None": NoneType,
    "Json": str,  # placeholder; real parsing happens via register_type
    "Url": str,
    "HttpMethod": str,
    "Date": str,
    "Regex": str,
}


class TypeRegistry:
    """Registry of custom types registered via ``register_type``.

    Encapsulates mutable state that was previously a module-level dict,
    avoiding global mutable state.
    """

    def __init__(self) -> None:
        """Initialize an empty type registry."""
        self._types: dict[str, type[Any]] = {}

    def register(self, name: str, py_type: type[Any]) -> None:
        """Register a custom type usable in patterns as ``{value:Name}``.

        Args:
            name: The type name to use in patterns.
            py_type: The Python type the converter returns.

        """
        self._types[name] = py_type

    def resolve(self, type_ref: type[Any] | str) -> type[Any]:
        """Resolve a type reference (type object or name) to a Python type.

        Args:
            type_ref: A type object or a registered type name.

        Returns:
            The resolved Python type, falling back to ``str`` for unknown names.

        """
        if isinstance(type_ref, str):
            if type_ref in self._types:
                return self._types[type_ref]
            if type_ref in BUILTIN_TYPES:
                return BUILTIN_TYPES[type_ref]
            return str
        return type_ref

    def get(self, name: str) -> type[Any] | None:
        """Return the registered type for *name*, or ``None`` if not registered."""
        return self._types.get(name)


# Module-level singleton for backward compatibility.
_DEFAULT_REGISTRY = TypeRegistry()


def register_type(name: str, py_type: type[Any]) -> None:
    """Register a custom type usable in patterns as ``{value:Name}``.

    Delegates to the default :class:`TypeRegistry` instance.

    Args:
        name: The type name to use in patterns.
        py_type: The Python type the converter returns.

    """
    _DEFAULT_REGISTRY.register(name, py_type)


def resolve_type(type_ref: type[Any] | str) -> type[Any]:
    """Resolve a type reference (type object or name) to a Python type.

    Delegates to the default :class:`TypeRegistry` instance.

    Args:
        type_ref: A type object or a registered type name.

    Returns:
        The resolved Python type, falling back to ``str`` for unknown names.

    """
    return _DEFAULT_REGISTRY.resolve(type_ref)
