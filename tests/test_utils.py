"""Tests for internal encoding utility helpers."""

from toon_format import encode
from toon_format._encoding import escape_string


class TestStringQuoting:
    """Tests for string quoting behavior protected by internal literal checks."""

    def test_reserved_literals_are_quoted(self):
        """Boolean and null literal strings are quoted to preserve string type."""
        assert encode(["true", "false", "null"]) == '[3]: "true","false","null"'

    def test_numeric_like_strings_are_quoted(self):
        """Numeric-looking strings are quoted to preserve string type."""
        assert encode(["0", "42", "-1", "3.14", "1e10", "01"]) == (
            '[6]: "0","42","-1","3.14","1e10","01"'
        )

    def test_plain_strings_remain_unquoted(self):
        """Non-reserved, non-numeric strings can stay unquoted."""
        assert encode(["hello", "True", "abc123"]) == "[3]: hello,True,abc123"


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
