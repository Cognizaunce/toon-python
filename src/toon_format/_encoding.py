# Copyright (c) 2025 TOON Format Organization
# SPDX-License-Identifier: MIT
"""Internal TOON encoding helpers."""

import re
from decimal import Decimal
from typing import Dict, List, Literal, Optional, Tuple, Union, cast

from ._literal_utils import is_boolean_or_null_literal
from ._string_utils import escape_string
from .constants import (
    CLOSE_BRACE,
    CLOSE_BRACKET,
    COLON,
    COMMA,
    DOUBLE_QUOTE,
    FALSE_LITERAL,
    LIST_ITEM_MARKER,
    LIST_ITEM_PREFIX,
    NULL_LITERAL,
    NUMERIC_REGEX,
    OCTAL_REGEX,
    OPEN_BRACE,
    OPEN_BRACKET,
    TRUE_LITERAL,
    VALID_KEY_REGEX,
)
from .normalize import (
    is_json_array,
    is_json_object,
    is_json_primitive,
)
from .types import (
    Delimiter,
    Depth,
    JsonArray,
    JsonObject,
    JsonPrimitive,
    JsonValue,
    ResolvedEncodeOptions,
)
from .writer import LineWriter

ARRAY_PRIMITIVE = "primitive"
ARRAY_ARRAYS = "arrays"
ARRAY_OBJECTS_TABULAR = "objects_tabular"
ARRAY_OBJECTS_LIST = "objects_list"
ARRAY_MIXED = "mixed"

_CONTROL_CHARS_PATTERN = re.compile(r"[\n\r\t]")
_NUMERIC_PATTERN = re.compile(NUMERIC_REGEX, re.IGNORECASE)
_OCTAL_PATTERN = re.compile(OCTAL_REGEX)
_STRUCTURAL_CHARS_PATTERN = re.compile(r"[\[\]{}]")
_VALID_KEY_PATTERN = re.compile(VALID_KEY_REGEX, re.IGNORECASE)


class ToonEncoder:
    """Stateful internal encoder for normalized JSON-compatible values."""

    def __init__(self, options: ResolvedEncodeOptions, writer: LineWriter) -> None:
        self.options = options
        self.writer = writer
        self._key_cache: Dict[str, str] = {}

    def write_value(self, value: JsonValue, depth: Depth = 0) -> None:
        """Encode a normalized value at the given depth."""
        if is_json_primitive(value):
            self.writer.push(depth, self.primitive(cast(JsonPrimitive, value)))
        elif is_json_array(value):
            self.write_array(cast(JsonArray, value), depth, None)
        elif is_json_object(value):
            self.write_object(cast(JsonObject, value), depth, None)

    def write_object(self, obj: JsonObject, depth: Depth, key: Optional[str]) -> None:
        """Encode an object."""
        if key:
            self.writer.push(depth, f"{self.key(key)}:")

        value_depth = depth if not key else depth + 1
        for obj_key, obj_value in obj.items():
            self.write_key_value_pair(obj_key, obj_value, value_depth)

    def write_key_value_pair(self, key: str, value: JsonValue, depth: Depth) -> None:
        """Encode one object field."""
        if is_json_primitive(value):
            self.writer.push(depth, f"{self.key(key)}: {self.primitive(value)}")
        elif is_json_array(value):
            self.write_array(cast(JsonArray, value), depth, key)
        elif is_json_object(value):
            self.write_object(cast(JsonObject, value), depth, key)

    def write_array(self, arr: JsonArray, depth: Depth, key: Optional[str]) -> None:
        """Encode an array using the most compact available representation."""
        if not arr:
            self.writer.push(depth, self.header(key, 0, None))
            return

        array_kind, tabular_header = classify_array(arr)
        if array_kind == ARRAY_PRIMITIVE:
            self.write_inline_primitive_array(arr, depth, key)
        elif array_kind == ARRAY_ARRAYS:
            self.write_array_of_arrays(arr, depth, key)
        elif array_kind == ARRAY_OBJECTS_TABULAR and tabular_header is not None:
            self.write_array_of_objects_as_tabular(arr, tabular_header, depth, key)
        else:
            self.write_mixed_array_as_list_items(arr, depth, key)

    def write_array_content(self, arr: JsonArray, depth: Depth) -> None:
        """Encode array content after a non-inline header has already been written."""
        if not arr:
            return

        array_kind, tabular_header = classify_array(arr)
        if array_kind == ARRAY_PRIMITIVE:
            self.write_primitive_array_list_item(arr, depth, None)
        elif array_kind == ARRAY_ARRAYS:
            for item in arr:
                item_kind, _ = classify_array(item)
                if item_kind == ARRAY_PRIMITIVE:
                    self.write_primitive_array_list_item(item, depth, None)
                else:
                    self.write_array(item, depth, None)
        elif array_kind == ARRAY_OBJECTS_TABULAR and tabular_header is not None:
            for obj in arr:
                self.writer.push(depth, self.primitive_row(obj, tabular_header))
        elif array_kind == ARRAY_OBJECTS_LIST:
            for item in arr:
                self.write_object_as_list_item(item, depth)
        else:
            for item in arr:
                if is_json_primitive(item):
                    self.writer.push(depth, f"{LIST_ITEM_PREFIX}{self.primitive(item)}")
                elif is_json_object(item):
                    self.write_object_as_list_item(item, depth)
                elif is_json_array(item):
                    self.write_array(cast(JsonArray, item), depth, None)

    def write_inline_primitive_array(
        self, arr: JsonArray, depth: Depth, key: Optional[str]
    ) -> None:
        """Encode an array of primitives on one line."""
        self.writer.push(depth, self.primitive_array_line(arr, key, list_item=False))

    def write_array_of_arrays(self, arr: JsonArray, depth: Depth, key: Optional[str]) -> None:
        """Encode an array whose items are arrays."""
        self.writer.push(depth, self.header(key, len(arr), None))

        for item in arr:
            item_kind, _ = classify_array(item)
            if item_kind == ARRAY_PRIMITIVE:
                self.write_primitive_array_list_item(item, depth + 1, None)
            else:
                self.write_array(item, depth + 1, None)

    def write_array_of_objects_as_tabular(
        self,
        arr: List[JsonObject],
        fields: List[str],
        depth: Depth,
        key: Optional[str],
    ) -> None:
        """Encode uniform primitive-only objects in tabular form."""
        self.writer.push(depth, self.header(key, len(arr), fields))

        for obj in arr:
            self.writer.push(depth + 1, self.primitive_row(obj, fields))

    def write_mixed_array_as_list_items(
        self, arr: JsonArray, depth: Depth, key: Optional[str]
    ) -> None:
        """Encode mixed or nested arrays using list items."""
        self.writer.push(depth, self.header(key, len(arr), None))

        for item in arr:
            if is_json_primitive(item):
                self.writer.push(depth + 1, f"{LIST_ITEM_PREFIX}{self.primitive(item)}")
            elif is_json_object(item):
                self.write_object_as_list_item(item, depth + 1)
            elif is_json_array(item):
                self.write_array_as_list_item(cast(JsonArray, item), depth + 1, None)

    def write_object_as_list_item(self, obj: JsonObject, depth: Depth) -> None:
        """Encode an object as a list item."""
        items = list(obj.items())
        if not items:
            self.writer.push(depth, LIST_ITEM_PREFIX.rstrip())
            return

        first_key, first_value = items[0]
        if is_json_primitive(first_value):
            self.writer.push(
                depth,
                f"{LIST_ITEM_PREFIX}{self.key(first_key)}: {self.primitive(first_value)}",
            )
        elif is_json_array(first_value):
            self.write_array_as_list_item(cast(JsonArray, first_value), depth, first_key)
        else:
            self.writer.push(depth, LIST_ITEM_PREFIX.rstrip())
            self.write_key_value_pair(first_key, first_value, depth + 1)

        for key, value in items[1:]:
            self.write_key_value_pair(key, value, depth + 1)

    def write_array_as_list_item(
        self, arr: JsonArray, depth: Depth, key: Optional[str]
    ) -> None:
        """Encode an array that appears as a list item or first object-list field."""
        array_kind, tabular_fields = classify_array(arr)
        if array_kind == ARRAY_PRIMITIVE:
            self.write_primitive_array_list_item(arr, depth, key)
            return

        self.writer.push(depth, f"{LIST_ITEM_PREFIX}{self.header(key, len(arr), tabular_fields)}")
        self.write_array_content(arr, depth + 1)

    def write_primitive_array_list_item(
        self, arr: JsonArray, depth: Depth, key: Optional[str]
    ) -> None:
        """Encode a primitive array with a list-item prefix."""
        self.writer.push(depth, self.primitive_array_line(arr, key, list_item=True))

    def primitive_array_line(
        self, arr: JsonArray, key: Optional[str], *, list_item: bool
    ) -> str:
        """Build one line for an inline primitive array."""
        line = self.header(key, len(arr), None)
        joined = self.join_primitives(arr)
        if joined:
            line += f" {joined}"
        if list_item:
            return f"{LIST_ITEM_PREFIX}{line}"
        return line

    def primitive_row(self, obj: JsonObject, fields: List[str]) -> str:
        """Build one tabular row for a primitive-only object."""
        delimiter = self.options.delimiter
        primitive = encode_primitive
        return delimiter.join([primitive(obj[field], delimiter) for field in fields])

    def join_primitives(self, values: JsonArray) -> str:
        """Encode and join primitive values with the active delimiter."""
        delimiter = self.options.delimiter
        primitive = encode_primitive
        return delimiter.join([primitive(value, delimiter) for value in values])

    def primitive(self, value: JsonPrimitive) -> str:
        """Encode one primitive with the active delimiter."""
        return encode_primitive(value, self.options.delimiter)

    def header(self, key: Optional[str], length: int, fields: Optional[List[str]]) -> str:
        """Build an array header with active options."""
        delimiter = self.options.delimiter
        marker_prefix = self.options.lengthMarker if self.options.lengthMarker else ""

        fields_str = ""
        if fields:
            encoded_fields = [self.key(field) for field in fields]
            fields_str = f"{OPEN_BRACE}{delimiter.join(encoded_fields)}{CLOSE_BRACE}"

        if delimiter != COMMA:
            length_str = f"{OPEN_BRACKET}{marker_prefix}{length}{delimiter}{CLOSE_BRACKET}"
        else:
            length_str = f"{OPEN_BRACKET}{marker_prefix}{length}{CLOSE_BRACKET}"

        if key:
            return f"{self.key(key)}{length_str}{fields_str}{COLON}"
        return f"{length_str}{fields_str}{COLON}"

    def key(self, key: str) -> str:
        """Encode an object key using this encoder's key cache."""
        cached = self._key_cache.get(key)
        if cached is None:
            cached = encode_key(key)
            self._key_cache[key] = cached
        return cached


def encode_value(
    value: JsonValue,
    options: ResolvedEncodeOptions,
    writer: LineWriter,
    depth: Depth = 0,
) -> None:
    """Encode a normalized value to TOON format."""
    ToonEncoder(options, writer).write_value(value, depth)


def classify_array(arr: JsonArray) -> Tuple[str, Optional[List[str]]]:
    """Classify an array with early exits for non-tabular and mixed arrays."""
    if not arr:
        return (ARRAY_PRIMITIVE, None)

    first = arr[0]
    if is_json_primitive(first):
        for item in arr[1:]:
            if not is_json_primitive(item):
                return (ARRAY_MIXED, None)
        return (ARRAY_PRIMITIVE, None)

    if is_json_array(first):
        for item in arr[1:]:
            if not is_json_array(item):
                return (ARRAY_MIXED, None)
        return (ARRAY_ARRAYS, None)

    if is_json_object(first):
        fields = list(first.keys())
        field_set = set(fields)
        if not all(is_json_primitive(value) for value in first.values()):
            return (ARRAY_OBJECTS_LIST, None)

        for item in arr[1:]:
            if not is_json_object(item):
                return (ARRAY_MIXED, None)
            if set(item.keys()) != field_set:
                return (ARRAY_OBJECTS_LIST, None)
            if not all(is_json_primitive(value) for value in item.values()):
                return (ARRAY_OBJECTS_LIST, None)

        return (ARRAY_OBJECTS_TABULAR, fields)

    return (ARRAY_MIXED, None)


def detect_tabular_header(arr: List[JsonObject], delimiter: str) -> Optional[List[str]]:
    """Detect if an object array can use tabular format and return header keys."""
    array_kind, fields = classify_array(arr)
    if array_kind == ARRAY_OBJECTS_TABULAR:
        return fields
    return None


def is_tabular_array(arr: List[JsonObject], delimiter: str) -> bool:
    """Check if an object array qualifies for tabular format."""
    return detect_tabular_header(arr, delimiter) is not None


def encode_primitive(value: JsonPrimitive, delimiter: str = COMMA) -> str:
    """Encode a primitive value."""
    if value is None:
        return NULL_LITERAL
    if isinstance(value, bool):
        return TRUE_LITERAL if value else FALSE_LITERAL
    if isinstance(value, (int, float)):
        if isinstance(value, int):
            return str(value)
        formatted = str(value)
        if "e" in formatted or "E" in formatted:
            formatted = format(Decimal(str(value)), "f")
        return formatted
    if isinstance(value, str):
        return encode_string_literal(value, delimiter)
    return str(value)


def encode_string_literal(value: str, delimiter: str = COMMA) -> str:
    """Encode a string, quoting only if necessary."""
    if is_safe_unquoted(value, delimiter):
        return value
    return f"{DOUBLE_QUOTE}{escape_string(value)}{DOUBLE_QUOTE}"


def encode_key(key: str) -> str:
    """Encode an object key."""
    if is_valid_unquoted_key(key):
        return key
    return f"{DOUBLE_QUOTE}{escape_string(key)}{DOUBLE_QUOTE}"


def join_encoded_values(values: List[str], delimiter: Delimiter) -> str:
    """Join encoded primitive values with a delimiter."""
    return delimiter.join(values)


def format_header(
    key: Optional[str],
    length: int,
    fields: Optional[List[str]],
    delimiter: Delimiter,
    length_marker: Union[str, Literal[False], None],
) -> str:
    """Format an array or table header."""
    marker_prefix = length_marker if length_marker else ""

    fields_str = ""
    if fields:
        encoded_fields = [encode_key(field) for field in fields]
        fields_str = f"{OPEN_BRACE}{delimiter.join(encoded_fields)}{CLOSE_BRACE}"

    if delimiter != COMMA:
        length_str = f"{OPEN_BRACKET}{marker_prefix}{length}{delimiter}{CLOSE_BRACKET}"
    else:
        length_str = f"{OPEN_BRACKET}{marker_prefix}{length}{CLOSE_BRACKET}"

    if key:
        return f"{encode_key(key)}{length_str}{fields_str}{COLON}"
    return f"{length_str}{fields_str}{COLON}"


def is_valid_unquoted_key(key: str) -> bool:
    """Check if a key can be used without quotes."""
    if not key:
        return False
    return bool(_VALID_KEY_PATTERN.match(key))


def is_safe_unquoted(value: str, delimiter: str = COMMA) -> bool:
    """Determine if a string value can be safely encoded without quotes."""
    if not value:
        return False
    if value != value.strip():
        return False
    if is_boolean_or_null_literal(value) or is_numeric_like(value):
        return False
    if COLON in value:
        return False
    if DOUBLE_QUOTE in value or "\\" in value:
        return False
    if _STRUCTURAL_CHARS_PATTERN.search(value):
        return False
    if _CONTROL_CHARS_PATTERN.search(value):
        return False
    if delimiter in value:
        return False
    return not value.startswith(LIST_ITEM_MARKER)


def is_numeric_like(value: str) -> bool:
    """Check if a string looks like a number and therefore needs quoting."""
    return bool(_NUMERIC_PATTERN.match(value) or _OCTAL_PATTERN.match(value))
