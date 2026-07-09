# Copyright (c) 2025 TOON Format Organization
# SPDX-License-Identifier: MIT
"""Public TOON encoding API.

This package exposes helpers for converting Python and JSON-compatible values to
TOON format strings. Public helpers resolve options and coordinate the encoding
pipeline: normalization -> encoding -> writing.
"""

import json
from typing import Any

from .constants import DEFAULT_DELIMITER, DELIMITERS
from .normalize import normalize_value
from .toon_encoder import ToonEncoder
from .types import Delimiter, DelimiterKey, EncodeOptions, JsonValue, ResolvedEncodeOptions
from .writer import LineWriter

__version__ = "0.9.0-beta.1"
__all__ = [
    "encode",
    "encode_json_to_toon",
    "encode_normalized",
    "Delimiter",
    "DelimiterKey",
    "EncodeOptions",
]


def encode(value: Any, options: EncodeOptions | None = None) -> str:
    """Encode a value into TOON format."""
    normalized = normalize_value(value)
    return encode_normalized(normalized, options)


def encode_normalized(value: JsonValue, options: EncodeOptions | None = None) -> str:
    """Encode an already-normalized JSON-compatible value into TOON format.

    This skips Python-specific normalization and is intended for values produced by
    JSON parsers such as ``json.loads``.
    """
    resolved_options = _resolve_options(options)
    writer = LineWriter(resolved_options.indent)
    ToonEncoder(resolved_options, writer).write_value(value, 0)
    return writer.to_string()


def encode_json_to_toon(
    json_text: str,
    delimiter: str = ",",
    indent: int = 2,
    length_marker: bool = False,
) -> str:
    """Encode JSON text to TOON format."""
    data = json.loads(json_text)

    options: EncodeOptions = {
        "indent": indent,
        "delimiter": delimiter,
        "lengthMarker": "#" if length_marker else False,
    }

    return encode_normalized(data, options)


def _resolve_options(options: EncodeOptions | None) -> ResolvedEncodeOptions:
    """Resolve encoding options with defaults."""
    if options is None:
        return ResolvedEncodeOptions()

    indent = options.get("indent", 2)
    delimiter = options.get("delimiter", DEFAULT_DELIMITER)
    length_marker = options.get("lengthMarker", False)

    if delimiter in DELIMITERS:
        delimiter = DELIMITERS[delimiter]

    return ResolvedEncodeOptions(indent=indent, delimiter=delimiter, length_marker=length_marker)
