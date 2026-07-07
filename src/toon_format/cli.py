# Copyright (c) 2025 TOON Format Organization
# SPDX-License-Identifier: MIT
"""Command-line interface for TOON encoding/decoding.

Provides the `toon` command-line tool for converting between JSON and TOON formats.
Supports auto-detection based on file extensions and content, with options for
delimiters, indentation, and validation modes.
"""

import json

from . import decode, encode
from .types import DecodeOptions, EncodeOptions


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


def decode_toon_to_json(
    toon_text: str,
    indent: int = 2,
    strict: bool = True,
) -> str:
    """Decode TOON text to JSON format.

    Args:
        toon_text: TOON input string
        indent: Indentation size
        strict: Whether to use strict validation

    Returns:
        JSON-formatted string

    Raises:
        ToonDecodeError: If TOON is invalid
    """
    options = DecodeOptions(indent=indent, strict=strict)
    data = decode(toon_text, options)

    return json.dumps(data, indent=indent, ensure_ascii=False)
