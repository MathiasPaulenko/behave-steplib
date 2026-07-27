"""Tests for API transforms: HttpMethod, Url, JsonPath."""

from __future__ import annotations

import pytest

from steplib.modules.api.transforms import (
    HttpMethod,
    JsonPath,
    Url,
    parse_json,
)


class TestHttpMethod:
    """Tests for HttpMethod."""

    def test_valid_methods(self) -> None:
        """Valid HTTP methods should be accepted and normalized."""
        assert str(HttpMethod("get")) == "GET"
        assert str(HttpMethod("POST")) == "POST"
        assert str(HttpMethod("  delete  ")) == "DELETE"

    def test_invalid_method_raises(self) -> None:
        """Invalid methods should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid HTTP method"):
            HttpMethod("INVALID")

    def test_equality(self) -> None:
        """HttpMethod should compare equal to strings and other HttpMethod."""
        assert HttpMethod("GET") == HttpMethod("get")
        assert HttpMethod("GET") == "GET"
        assert HttpMethod("GET") == "get"
        assert HttpMethod("GET") != HttpMethod("POST")

    def test_hashable(self) -> None:
        """HttpMethod should be hashable."""
        assert hash(HttpMethod("GET")) == hash(HttpMethod("get"))
        assert HttpMethod("GET") in {HttpMethod("GET")}


class TestUrl:
    """Tests for Url."""

    def test_absolute_url(self) -> None:
        """Absolute URLs should not be modified."""
        url = Url("https://example.com/api")
        assert str(url) == "https://example.com/api"

    def test_relative_url_with_base(self) -> None:
        """Relative URLs should be resolved against the base URL."""
        url = Url("/users", base_url="https://api.example.com")
        assert str(url) == "https://api.example.com/users"

    def test_relative_url_no_leading_slash(self) -> None:
        """Relative URLs without leading slash should get one."""
        url = Url("users", base_url="https://api.example.com")
        assert str(url) == "https://api.example.com/users"

    def test_relative_url_no_base(self) -> None:
        """Relative URLs without base should remain as-is."""
        url = Url("/users")
        assert str(url) == "/users"

    def test_base_url_trailing_slash_stripped(self) -> None:
        """Trailing slash in base_url should be stripped."""
        url = Url("/users", base_url="https://api.example.com/")
        assert str(url) == "https://api.example.com/users"

    def test_equality(self) -> None:
        """Url should compare equal to strings."""
        assert Url("https://example.com") == "https://example.com"
        assert Url("/users", base_url="https://api.example.com") == "https://api.example.com/users"


class TestJsonPath:
    """Tests for JsonPath."""

    def test_root_path(self) -> None:
        """$ should return the entire data."""
        data = {"name": "Ada"}
        assert JsonPath("$").evaluate(data) is data

    def test_simple_path(self) -> None:
        """$.key should return the value at key."""
        data = {"name": "Ada", "age": 30}
        assert JsonPath("$.name").evaluate(data) == "Ada"
        assert JsonPath("$.age").evaluate(data) == 30

    def test_nested_path(self) -> None:
        """$.a.b.c should traverse nested dicts."""
        data = {"a": {"b": {"c": "deep"}}}
        assert JsonPath("$.a.b.c").evaluate(data) == "deep"

    def test_array_index(self) -> None:
        """$.items[0] should access array elements."""
        data = {"items": ["first", "second"]}
        assert JsonPath("$.items[0]").evaluate(data) == "first"
        assert JsonPath("$.items[1]").evaluate(data) == "second"

    def test_nested_array_path(self) -> None:
        """$.users[0].name should access nested array + dict."""
        data = {"users": [{"name": "Ada"}, {"name": "Bob"}]}
        assert JsonPath("$.users[0].name").evaluate(data) == "Ada"
        assert JsonPath("$.users[1].name").evaluate(data) == "Bob"

    def test_missing_key_raises(self) -> None:
        """Missing keys should raise KeyError."""
        data = {"name": "Ada"}
        with pytest.raises(KeyError):
            JsonPath("$.missing").evaluate(data)

    def test_invalid_path_raises(self) -> None:
        """Paths not starting with $ should raise ValueError."""
        with pytest.raises(ValueError, match="must start"):
            JsonPath("users")

    def test_str_representation(self) -> None:
        """str() should return the path string."""
        assert str(JsonPath("$.name")) == "$.name"


class TestParseJson:
    """Tests for parse_json."""

    def test_valid_json(self) -> None:
        """Valid JSON should be parsed."""
        assert parse_json('{"name": "Ada"}') == {"name": "Ada"}

    def test_invalid_json_raises(self) -> None:
        """Invalid JSON should raise ValueError."""
        with pytest.raises(ValueError):
            parse_json("not json")
