# Copyright (c) 2025 TOON Format Organization
# SPDX-License-Identifier: MIT
"""Command-line interface for TOON encoding/decoding.

Provides the `toon` command-line tool for converting between JSON and TOON formats.
Supports auto-detection based on file extensions and content, with options for
delimiters, indentation, and validation modes.
"""

import json
import sys
from argparse import ArgumentParser
from pathlib import Path

from . import encode
from .types import EncodeOptions


def encode_json_to_toon(
    json_text: str,
    delimiter: str = ",",
    indent: int = 2,
    length_marker: bool = False,
) -> str:
    """Encode JSON text to TOON format.

    Args:
        json_text: JSON input string
        delimiter: Delimiter character
        indent: Indentation size
        length_marker: Whether to add # prefix

    Returns:
        TOON-formatted string

    Raises:
        json.JSONDecodeError: If JSON is invalid
    """
    data = json.loads(json_text)

    options: EncodeOptions = {
        "indent": indent,
        "delimiter": delimiter,
        "lengthMarker": "#" if length_marker else False,
    }

    return encode(data, options)


def main() -> int:
    """Main CLI entry point for encode-only conversion."""
    parser = ArgumentParser(
        prog="toon",
        description="Convert JSON to TOON format",
    )
    parser.add_argument("input", type=str, help="Input file path (or - for stdin)")
    parser.add_argument("-o", "--output", type=str, help="Output file path")
    parser.add_argument("-e", "--encode", action="store_true", help="Force encode mode")
    parser.add_argument("-d", "--decode", action="store_true", help="Decode mode is unavailable")
    parser.add_argument(
        "--delimiter",
        type=str,
        choices=[",", "\t", "|"],
        default=",",
        help='Array delimiter: , (comma), \\t (tab), | (pipe) (default: ",")',
    )
    parser.add_argument("--indent", type=int, default=2, help="Indentation size (default: 2)")
    parser.add_argument(
        "--length-marker",
        action="store_true",
        help="Add # prefix to array lengths (e.g., items[#3])",
    )
    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="Ignored in encode-only builds",
    )

    args = parser.parse_args()

    if args.encode and args.decode:
        print("Error: Cannot specify both --encode and --decode", file=sys.stderr)
        return 1

    try:
        if args.input == "-":
            input_text = sys.stdin.read()
            input_path = None
        else:
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"Error: Input file not found: {args.input}", file=sys.stderr)
                return 1
            input_text = input_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        return 1

    if args.decode:
        print("Error during decode: TOON decoding is not available", file=sys.stderr)
        return 1

    if not args.encode:
        try:
            json.loads(input_text)
        except json.JSONDecodeError:
            print("Error during decode: TOON decoding is not available", file=sys.stderr)
            return 1

    try:
        output_text = encode_json_to_toon(
            input_text,
            delimiter=args.delimiter,
            indent=args.indent,
            length_marker=args.length_marker,
        )
    except Exception as e:
        print(f"Error during encode: {e}", file=sys.stderr)
        return 1

    try:
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output_text, encoding="utf-8")
        else:
            print(output_text)
    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
