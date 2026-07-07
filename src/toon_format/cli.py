# Copyright (c) 2025 TOON Format Organization
# SPDX-License-Identifier: MIT
"""JSON-to-TOON conversion helper."""

import json

from .encoder import encode_normalized
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

    return encode_normalized(data, options)
