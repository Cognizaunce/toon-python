"""Tests for the _utils module."""

from toon_format._utils import (
    escape_string,
    is_boolean_or_null_literal,
)


class TestLiteralUtilities:
    """Tests for literal detection helpers."""

    def test_boolean_or_null_literals(self):
        """Test true, false, and null are detected as reserved literals."""
        assert is_boolean_or_null_literal("true")
        assert is_boolean_or_null_literal("false")
        assert is_boolean_or_null_literal("null")

    def test_non_reserved_literals(self):
        """Test non-reserved values are not detected as literals."""
        assert not is_boolean_or_null_literal("")
        assert not is_boolean_or_null_literal("hello")
        assert not is_boolean_or_null_literal("True")


class TestEscapeString:
    """Tests for escape_string function."""

    def test_escape_backslash(self):
        """Test backslashes are escaped correctly."""
        assert escape_string("path\\to\\file") == "path\\\\to\\\\file"

    def test_escape_double_quote(self):
        """Test double quotes are escaped correctly."""
        assert escape_string('say "hello"') == 'say \\"hello\\"'

    def test_escape_newline(self):
        """Test newlines are escaped correctly."""
        assert escape_string("line1\nline2") == "line1\\nline2"

    def test_escape_carriage_return(self):
        """Test carriage returns are escaped correctly."""
        assert escape_string("line1\rline2") == "line1\\rline2"

    def test_escape_tab(self):
        """Test tabs are escaped correctly."""
        assert escape_string("col1\tcol2") == "col1\\tcol2"

    def test_escape_all_special_chars(self):
        """Test all special characters are escaped in one string."""
        input_str = 'test\n\r\t\\"value"'
        expected = 'test\\n\\r\\t\\\\\\"value\\"'
        assert escape_string(input_str) == expected

    def test_escape_empty_string(self):
        """Test empty string remains empty."""
        assert escape_string("") == ""

    def test_escape_no_special_chars(self):
        """Test string without special chars is unchanged."""
        assert escape_string("hello world") == "hello world"
