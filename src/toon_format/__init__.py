# Copyright (c) 2025 TOON Format Organization
# SPDX-License-Identifier: MIT
"""TOON Format for Python.

Token-Oriented Object Notation (TOON) is a compact, human-readable serialization
format optimized for LLM contexts. Achieves 30-60% token reduction vs JSON while
maintaining readability and structure.

This package provides encoding functionality for the TOON specification (v1.3).

Example:
    >>> from toon_format import encode
    >>> data = {"name": "Alice", "age": 30}
    >>> toon = encode(data)
    >>> print(toon)
    name: Alice
    age: 30
"""

from .encoder import encode
from .types import DecodeOptions, Delimiter, DelimiterKey, EncodeOptions

__version__ = "0.9.0-beta.1"
__all__ = [
    "encode",
    "Delimiter",
    "DelimiterKey",
    "EncodeOptions",
    "DecodeOptions",
]
