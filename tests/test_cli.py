"""Integration tests for the encode-only CLI module."""

import json
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from toon_format.cli import encode_json_to_toon, main


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


class TestCLIMain:
    """Integration tests for the encode-only main CLI function."""

    def test_encode_from_file_to_stdout(self, tmp_path):
        input_file = tmp_path / "input.json"
        input_file.write_text('{"name": "Alice"}')

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            with patch("sys.argv", ["toon", str(input_file), "--encode"]):
                result = main()
                assert result == 0
                assert "name: Alice" in mock_stdout.getvalue()

    def test_encode_from_stdin_to_stdout(self):
        with patch("sys.stdin", StringIO('{"name": "Bob"}')):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with patch("sys.argv", ["toon", "-", "--encode"]):
                    result = main()
                    assert result == 0
                    assert "name: Bob" in mock_stdout.getvalue()

    def test_encode_to_output_file(self, tmp_path):
        input_file = tmp_path / "input.json"
        output_file = tmp_path / "output.toon"
        input_file.write_text('{"name": "Dave"}')

        with patch("sys.argv", ["toon", str(input_file), "-o", str(output_file), "--encode"]):
            result = main()
            assert result == 0
            assert "name: Dave" in output_file.read_text()

    def test_auto_detect_json_extension(self, tmp_path):
        input_file = tmp_path / "data.json"
        input_file.write_text('{"test": true}')

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            with patch("sys.argv", ["toon", str(input_file)]):
                result = main()
                assert result == 0
                assert "test: true" in mock_stdout.getvalue()

    def test_auto_detect_json_content(self, tmp_path):
        input_file = tmp_path / "data.txt"
        input_file.write_text('{"format": "json"}')

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            with patch("sys.argv", ["toon", str(input_file)]):
                result = main()
                assert result == 0
                assert "format: json" in mock_stdout.getvalue()

    def test_auto_detect_stdin_json(self):
        with patch("sys.stdin", StringIO('{"source": "stdin"}')):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with patch("sys.argv", ["toon", "-"]):
                    result = main()
                    assert result == 0
                    assert "source: stdin" in mock_stdout.getvalue()

    def test_custom_delimiter_option(self, tmp_path):
        input_file = tmp_path / "input.json"
        input_file.write_text('{"items": [1, 2, 3]}')

        with patch("sys.stdout", new_callable=StringIO):
            with patch("sys.argv", ["toon", str(input_file), "--encode", "--delimiter", "|"]):
                assert main() == 0

    def test_custom_indent_option(self, tmp_path):
        input_file = tmp_path / "input.json"
        input_file.write_text('{"outer": {"inner": 1}}')

        with patch("sys.stdout", new_callable=StringIO):
            with patch("sys.argv", ["toon", str(input_file), "--encode", "--indent", "4"]):
                assert main() == 0

    def test_length_marker_option(self, tmp_path):
        input_file = tmp_path / "input.json"
        input_file.write_text('{"items": [1, 2, 3]}')

        with patch("sys.stdout", new_callable=StringIO):
            with patch("sys.argv", ["toon", str(input_file), "--encode", "--length-marker"]):
                assert main() == 0

    def test_error_file_not_found(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            with patch("sys.argv", ["toon", "nonexistent.json"]):
                result = main()
                assert result == 1
                assert "not found" in mock_stderr.getvalue()

    def test_error_decode_not_available(self, tmp_path):
        input_file = tmp_path / "input.toon"
        input_file.write_text("name: Test")

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            with patch("sys.argv", ["toon", str(input_file), "--decode"]):
                result = main()
                assert result == 1
                assert "decode" in mock_stderr.getvalue().lower()

    def test_error_both_encode_and_decode(self, tmp_path):
        input_file = tmp_path / "input.txt"
        input_file.write_text("test")

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            with patch("sys.argv", ["toon", str(input_file), "--encode", "--decode"]):
                result = main()
                assert result == 1
                assert "Cannot specify both" in mock_stderr.getvalue()

    def test_error_during_encoding(self, tmp_path):
        input_file = tmp_path / "input.json"
        input_file.write_text('{"invalid": broken}')

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            with patch("sys.argv", ["toon", str(input_file), "--encode"]):
                result = main()
                assert result == 1
                assert "Error during encode" in mock_stderr.getvalue()

    def test_error_reading_input(self):
        mock_stdin = MagicMock()
        mock_stdin.read.side_effect = OSError("Read failed")

        with patch("sys.stdin", mock_stdin):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                with patch("sys.argv", ["toon", "-", "--encode"]):
                    result = main()
                    assert result == 1
                    assert "Error reading input" in mock_stderr.getvalue()

    def test_error_writing_output(self, tmp_path):
        input_file = tmp_path / "input.json"
        input_file.write_text('{"test": true}')
        output_file = tmp_path / "readonly" / "output.toon"

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            with patch("sys.argv", ["toon", str(input_file), "-o", str(output_file), "--encode"]):
                result = main()
                assert result == 1
                assert "Error writing output" in mock_stderr.getvalue()
