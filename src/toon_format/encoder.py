# Copyright (c) 2025 TOON Format Organization
# SPDX-License-Identifier: MIT
"""Core TOON encoding functionality.

This module provides helpers for converting Python and JSON values to TOON format
strings. Handles option resolution and coordinates the encoding pipeline:
normalization → encoding → writing.
"""

import json
from typing import Any

from ._encoding import ToonEncoder
from .constants import DEFAULT_DELIMITER, DELIMITERS
from .normalize import normalize_value
from .types import EncodeOptions, JsonValue, ResolvedEncodeOptions
from .writer import LineWriter


def encode(value: Any, options: EncodeOptions | None = None) -> str:
    """Encode a value into TOON format.

    Args:
        value: The value to encode (must be JSON-serializable)
        options: Optional encoding options

    Returns:
        TOON-formatted string
    """
    normalized = normalize_value(value)
    return encode_normalized(normalized, options)


def encode_normalized(value: JsonValue, options: EncodeOptions | None = None) -> str:
    """Encode an already-normalized JSON-compatible value into TOON format.

    This skips Python-specific normalization and is intended for values produced by
    JSON parsers such as ``json.loads``.
    """
    resolved_options = resolve_options(options)
    writer = LineWriter(resolved_options.indent)
    ToonEncoder(resolved_options, writer).write_value(value, 0)
    return writer.to_string()


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

    return encode_normalized(data, options)


def resolve_options(options: EncodeOptions | None) -> ResolvedEncodeOptions:
    """Resolve encoding options with defaults.

    Args:
        options: Optional user-provided options

    Returns:
        Resolved options with defaults applied
    """
    if options is None:
        return ResolvedEncodeOptions()

    indent = options.get("indent", 2)
    delimiter = options.get("delimiter", DEFAULT_DELIMITER)
    length_marker = options.get("lengthMarker", False)

    # Resolve delimiter if it's a key
    if delimiter in DELIMITERS:
        delimiter = DELIMITERS[delimiter]

    return ResolvedEncodeOptions(indent=indent, delimiter=delimiter, length_marker=length_marker)
