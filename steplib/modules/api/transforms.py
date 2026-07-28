"""Transformers for the API module: HttpMethod, Url, JsonPath."""

from __future__ import annotations

import json
from typing import Any

VALID_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"})


class HttpMethod:
    """Validates and normalizes HTTP method strings."""

    def __init__(self, method: str) -> None:
        """Initialize and validate the HTTP method."""
        self.value = method.upper().strip()
        if self.value not in VALID_METHODS:
            raise ValueError(
                f"Invalid HTTP method '{method}'. Valid methods: {sorted(VALID_METHODS)}"
            )

    def __str__(self) -> str:
        """Return the method string."""
        return self.value

    def __eq__(self, other: object) -> bool:
        """Compare with another HttpMethod or string."""
        if isinstance(other, HttpMethod):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.upper()
        return False

    def __hash__(self) -> int:
        """Return hash of the method value."""
        return hash(self.value)


class Url:
    """Represents a URL, resolving relative paths against a base URL.

    Args:
        url: The URL string (absolute or relative).
        base_url: Optional base URL for resolving relative URLs.

    """

    def __init__(self, url: str, base_url: str = "") -> None:
        """Initialize and resolve the URL against the base URL."""
        self.raw = url
        self.base_url = base_url.rstrip("/")
        self.value = self._resolve(url, base_url)

    @staticmethod
    def _resolve(url: str, base_url: str) -> str:
        """Resolve *url* against *base_url* if *url* is relative."""
        if url.startswith(("http://", "https://")):
            return url
        if not base_url:
            return url
        base = base_url.rstrip("/")
        path = url if url.startswith("/") else f"/{url}"
        return f"{base}{path}"

    def __str__(self) -> str:
        """Return the resolved URL string."""
        return self.value

    def __eq__(self, other: object) -> bool:
        """Compare with another Url or string."""
        if isinstance(other, Url):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False

    def __hash__(self) -> int:
        """Return hash of the URL value."""
        return hash(self.value)


class JsonPath:
    """Simple JSONPath evaluator supporting ``$.path.to.value`` syntax.

    Args:
        path: A JSONPath expression starting with ``$`` (e.g. ``"$.users[0].name"``).

    """

    def __init__(self, path: str) -> None:
        """Initialize and validate the JSONPath expression."""
        if not path.startswith("$"):
            raise ValueError(f"JsonPath must start with '$', got: '{path}'")
        self.path = path

    def evaluate(self, data: Any) -> Any:
        """Evaluate the path against *data* and return the matched value.

        Args:
            data: The JSON data to traverse (typically a dict or list).

        Returns:
            The value at the matched path.

        Raises:
            KeyError: If the path does not exist in *data*.

        """
        if self.path == "$":
            return data

        # Strip leading "$." or "$"
        expr = self.path[1:]
        if expr.startswith("."):
            expr = expr[1:]

        current: Any = data
        # Split on "." but handle array indexing [n]
        parts = self._tokenize(expr)
        for part in parts:
            current = self._access(current, part)
        return current

    @staticmethod
    def _tokenize(expr: str) -> list[str]:
        """Tokenize a path expression into keys and indices."""
        tokens: list[str] = []
        current = ""
        i = 0
        while i < len(expr):
            ch = expr[i]
            if ch == ".":
                if current:
                    tokens.append(current)
                    current = ""
            elif ch == "[":
                if current:
                    tokens.append(current)
                    current = ""
                j = expr.find("]", i)
                if j == -1:
                    raise ValueError(f"JsonPath has unclosed '[' in expression: '{expr}'")
                idx_str = expr[i + 1 : j]
                tokens.append(f"[{idx_str}]")
                i = j
            else:
                current += ch
            i += 1
        if current:
            tokens.append(current)
        return tokens

    @staticmethod
    def _access(current: Any, token: str) -> Any:
        """Access a single key or index from *current*."""
        if token.startswith("[") and token.endswith("]"):
            idx_str = token[1:-1]
            if not idx_str:
                raise ValueError(f"JsonPath has empty index '[]' in token: '{token}'")
            try:
                idx = int(idx_str)
            except ValueError as exc:
                raise ValueError(
                    f"JsonPath has non-numeric index '{idx_str}' in token: '{token}'"
                ) from exc
            return current[idx]
        return current[token]

    def __str__(self) -> str:
        """Return the path string."""
        return self.path


def parse_json(text: str) -> Any:
    """Parse a JSON string, raising ValueError on invalid input.

    Args:
        text: A JSON string.

    Returns:
        The parsed JSON data.

    Raises:
        json.JSONDecodeError: If the text is not valid JSON.

    """
    return json.loads(text)
