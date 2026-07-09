"""Tests for the JSON-to-TOON helper module."""

import json

import pytest

from toon_format import encode_json_to_toon


class TestEncodeJsonToToon:
    """Tests for encode_json_to_toon function."""

    def test_basic_encode(self):
        result = encode_json_to_toon('{"name": "Alice", "age": 30}')
        assert "name: Alice" in result
        assert "age: 30" in result

    def test_encode_with_custom_delimiter(self):
        result = encode_json_to_toon('{"items": [1, 2, 3]}', delimiter="|")
        assert result == "items[3|]: 1|2|3"

    def test_encode_with_custom_indent(self):
        result = encode_json_to_toon('{"outer": {"inner": 1}}', indent=4)
        assert "\n    inner: 1" in result

    def test_encode_with_length_marker(self):
        result = encode_json_to_toon('{"items": [1, 2, 3]}', length_marker=True)
        assert "items[#3]:" in result

    def test_encode_invalid_json_raises_error(self):
        with pytest.raises(json.JSONDecodeError):
            encode_json_to_toon('{"broken": invalid}')
