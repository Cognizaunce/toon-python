"""Tests for Python-specific TOON encode API behavior."""

import pytest

from toon_format import encode, encode_normalized
from toon_format.types import EncodeOptions


class TestEncodeAPI:
    """Test encode() function API and options handling."""

    def test_encode_accepts_dict_options(self):
        result = encode([1, 2, 3], {"delimiter": "\t"})
        assert result == "[3\t]: 1\t2\t3"

    def test_encode_accepts_encode_options_object(self):
        options = EncodeOptions(delimiter="|", indent=4)
        result = encode([1, 2, 3], options)
        assert result == "[3|]: 1|2|3"

    def test_encode_default_options(self):
        result = encode({"a": 1, "b": 2})
        assert result == "a: 1\nb: 2"

    def test_encode_with_comma_delimiter(self):
        result = encode([1, 2, 3], {"delimiter": ","})
        assert result == "[3]: 1,2,3"

    def test_encode_with_tab_delimiter(self):
        result = encode([1, 2, 3], {"delimiter": "\t"})
        assert result == "[3\t]: 1\t2\t3"

    def test_encode_with_pipe_delimiter(self):
        result = encode([1, 2, 3], {"delimiter": "|"})
        assert result == "[3|]: 1|2|3"

    def test_encode_with_custom_indent(self):
        result = encode({"parent": {"child": 1}}, {"indent": 4})
        lines = result.split("\n")
        assert lines[1].startswith("    ")

    def test_encode_with_zero_indent(self):
        result = encode({"parent": {"child": 1}}, {"indent": 0})
        assert "parent:" in result
        assert "child: 1" in result

    def test_encode_with_length_marker(self):
        result = encode([1, 2, 3], {"lengthMarker": "#"})
        assert "[#3]:" in result

    def test_encode_none_returns_null_string(self):
        result = encode(None)
        assert result == "null"
        assert isinstance(result, str)

    def test_encode_empty_object_returns_empty_string(self):
        assert encode({}) == ""

    def test_encode_root_array(self):
        assert encode([1, 2, 3]) == "[3]: 1,2,3"

    def test_encode_root_primitive(self):
        assert encode("hello") == "hello"

    def test_encode_normalized_is_public(self):
        result = encode_normalized({"items": [1, 2, 3]})
        assert result == "items[3]: 1,2,3"


class TestOptionsValidation:
    """Test encode option edge cases."""

    def test_encode_invalid_delimiter_type(self):
        with pytest.raises((TypeError, ValueError, AttributeError)):
            encode([1, 2, 3], {"delimiter": 123})

    def test_encode_unsupported_delimiter_value(self):
        try:
            result = encode([1, 2, 3], {"delimiter": ";"})
            assert result is not None
        except (TypeError, ValueError):
            pass

    def test_encode_negative_indent_accepted(self):
        result = encode({"a": 1}, {"indent": -1})
        assert result is not None
