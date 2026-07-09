"""Tests for encoder numeric detection utilities."""

from toon_format._encoding import is_numeric_like


class TestNumericLike:
    """Tests for is_numeric_like (encoder utility)."""

    def test_valid_integers(self):
        """Test valid integers are recognized as numeric-like."""
        assert is_numeric_like("0")
        assert is_numeric_like("1")
        assert is_numeric_like("42")
        assert is_numeric_like("-1")
        assert is_numeric_like("-42")

    def test_valid_floats(self):
        """Test valid floats are recognized as numeric-like."""
        assert is_numeric_like("0.0")
        assert is_numeric_like("0.5")
        assert is_numeric_like("3.14")
        assert is_numeric_like("-2.5")

    def test_scientific_notation(self):
        """Test scientific notation is recognized as numeric-like."""
        assert is_numeric_like("1e10")
        assert is_numeric_like("1.5e10")
        assert is_numeric_like("1e-10")
        assert is_numeric_like("2.5E+3")

    def test_octal_like_numbers(self):
        """Test octal-like numbers (leading zeros) are recognized as numeric-like."""
        # These LOOK like numbers so they need quoting
        assert is_numeric_like("01")
        assert is_numeric_like("0123")
        assert is_numeric_like("00")

    def test_non_numeric_strings(self):
        """Test non-numeric strings are not numeric-like."""
        assert not is_numeric_like("")
        assert not is_numeric_like("abc")
        assert not is_numeric_like("hello")
        assert not is_numeric_like("12abc")

    def test_edge_cases(self):
        """Test edge cases."""
        assert not is_numeric_like("")
        assert not is_numeric_like(" ")
        assert not is_numeric_like("--5")
