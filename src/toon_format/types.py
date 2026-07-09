# Copyright (c) 2025 TOON Format Organization
# SPDX-License-Identifier: MIT
"""Type definitions for TOON format.

Defines type aliases and TypedDict classes for JSON values, encoding options,
and internal types used throughout the package.
"""

from typing import Any, Literal, TypedDict

# JSON-compatible types
JsonPrimitive = str | int | float | bool | None
JsonObject = dict[str, Any]
JsonArray = list[Any]
JsonValue = JsonPrimitive | JsonArray | JsonObject

# Delimiter type
Delimiter = str
DelimiterKey = Literal["comma", "tab", "pipe"]


class EncodeOptions(TypedDict, total=False):
    """Options for TOON encoding.

    Attributes:
        indent: Number of spaces per indentation level (default: 2)
        delimiter: Delimiter character for arrays (default: comma)
        lengthMarker: Optional marker to prefix array lengths (default: False)
    """

    indent: int
    delimiter: Delimiter
    lengthMarker: Literal["#"] | Literal[False]


class ResolvedEncodeOptions:
    """Resolved encoding options with defaults applied."""

    def __init__(
        self,
        indent: int = 2,
        delimiter: str = ",",
        length_marker: Literal["#"] | Literal[False] = False,
    ) -> None:
        self.indent = indent
        self.delimiter = delimiter
        self.lengthMarker: str | Literal[False] = length_marker


# Depth type for tracking indentation level
Depth = int
