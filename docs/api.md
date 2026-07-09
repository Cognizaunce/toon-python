# API Reference

Complete API documentation for the encode-only `toon_format` Python package.

## Core Functions

### `encode(value, options=None)`

Converts a Python value to a TOON format string after normalizing Python-specific values to JSON-compatible values.

**Parameters:**
- `value` (Any): Python value to encode
- `options` (dict | EncodeOptions, optional): Encoding configuration

**Returns:** `str` - TOON-formatted string

**Examples:**

```python
from toon_format import encode

encode({"name": "Alice", "age": 30})
# name: Alice
# age: 30

encode([1, 2, 3], {"delimiter": "\t"})
# [3\t]: 1\t2\t3
```

Use `encode()` when data may contain native Python values such as `datetime`, `Decimal`, `set`, `Path`, non-finite floats, or callables.

---

### `encode_normalized(value, options=None)`

Converts an already-normalized JSON-compatible value to a TOON format string without the normalization pass.

**Parameters:**
- `value` (JsonValue): A JSON-compatible value (`dict`, `list`, `str`, `int`, `float`, `bool`, or `None`)
- `options` (dict | EncodeOptions, optional): Encoding configuration

**Returns:** `str` - TOON-formatted string

**Example:**

```python
import json
from toon_format import encode_normalized

data = json.loads('{"items": [{"id": 1}, {"id": 2}]}')
encode_normalized(data)
# items[2]{id}:
#   1
#   2
```

Use `encode_normalized()` for the fastest path when data came from `json.loads()` or another JSON-compatible source.

---

### `encode_json_to_toon(json_text, delimiter=",", indent=2, length_marker=False)`

Parses a JSON string with the standard library `json` module and encodes it as TOON.

**Parameters:**
- `json_text` (str): JSON document to parse and encode
- `delimiter` (str): Array value separator, default `","`
- `indent` (int): Spaces per indentation level, default `2`
- `length_marker` (bool | str): Use `"#"` to prefix array lengths, default `False`

**Returns:** `str` - TOON-formatted string

**Example:**

```python
from toon_format.cli import encode_json_to_toon

encode_json_to_toon('{"items": [1, 2, 3]}')
# items[3]: 1,2,3
```

Despite the module name, this package does not currently expose a command-line interface.

---

## Options

### `EncodeOptions`

TypedDict for encoding configuration. Use dict syntax to create options.

**Fields:**
- `delimiter` (str, optional): Array value separator
  - `","` - Comma (default)
  - `"\t"` - Tab
  - `"|"` - Pipe
- `indent` (int, optional): Spaces per indentation level (default: `2`)
- `lengthMarker` (Literal["#"] | Literal[False], optional): Prefix for array lengths
  - `False` - No marker (default)
  - `"#"` - Add `#` prefix, e.g. `[#5]`

**Example:**

```python
from toon_format import encode
from toon_format.types import EncodeOptions

options: EncodeOptions = {
    "delimiter": "\t",
    "indent": 4,
    "lengthMarker": "#",
}

data = [{"id": 1}, {"id": 2}]
print(encode(data, options))
# [#2\t]{id}:
#     1
#     2
```

---

## Type Normalization

`encode()` normalizes non-JSON Python values before encoding:

| Python Type | Normalized To |
|-------------|---------------|
| `datetime.datetime`, `datetime.date` | ISO 8601 string |
| `decimal.Decimal` | `float` |
| `tuple`, `set`, `frozenset` | `list` |
| `pathlib.Path` | `str` |
| `float("inf")`, `float("-inf")`, `float("nan")` | `None` |
| Functions / callables | `None` |
| Integers larger than `2**53 - 1` | `str` |
| `-0.0` | `0` |

**Example:**

```python
from datetime import datetime
from decimal import Decimal
from toon_format import encode

data = {
    "created_at": datetime(2024, 1, 15, 10, 30),
    "price": Decimal("19.99"),
    "tags": {"alpha", "beta"},
    "infinity": float("inf"),
}

encode(data)
# created_at: "2024-01-15T10:30:00"
# price: 19.99
# tags[2]: alpha,beta
# infinity: null
```

---

## Advanced Usage

### Custom Delimiters

Use different delimiters based on your data:

```python
from toon_format import encode

encode([1, 2, 3])
# [3]: 1,2,3

encode(["a,b", "c,d"], {"delimiter": "\t"})
# [2\t]: a,b\tc,d

encode([1, 2, 3], {"delimiter": "|"})
# [3|]: 1|2|3
```

### Length Markers

Add `#` for explicit array length markers:

```python
from toon_format import encode

users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

encode(users, {"lengthMarker": "#"})
# [#2]{id,name}:
#   1,Alice
#   2,Bob
```

### Zero Indentation

Use `indent=0` for minimal whitespace while preserving structure:

```python
from toon_format import encode

encode({"outer": {"inner": 1}}, {"indent": 0})
# outer:
#  inner: 1
```

---

## Type Hints

The package includes inline type hints and a `py.typed` marker for static analysis:

```python
from typing import Any
from toon_format import encode
from toon_format.types import EncodeOptions

data: dict[str, Any] = {"key": "value"}
options: EncodeOptions = {"delimiter": ","}
result: str = encode(data, options)
```

---

## Performance Considerations

- Use `encode_normalized()` when data is already JSON-compatible.
- Tabular arrays are most compact for uniform object arrays.
- The encoder caches indentation strings and escaped keys during an encode call.
- Output is assembled through an internal line writer before being joined into the final string.

---

## See Also

- [Format Specification](format.md) - Detailed format rules and examples
- [LLM Integration](llm-integration.md) - Best practices for using TOON with LLMs
- [TOON Specification](https://github.com/toon-format/spec) - Official specification
