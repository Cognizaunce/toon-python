# TOON Format for Python

[![Tests](https://github.com/toon-format/toon-python/actions/workflows/test.yml/badge.svg)](https://github.com/toon-format/toon-python/actions)
[![Python Versions](https://img.shields.io/pypi/pyversions/toon_format.svg)](https://pypi.org/project/toon_format/)

> **Beta Status (v0.9.x):** This library is being reworked as an encode-only JSON/Python-to-TOON package for internal conversion workflows. API may change before a stable release.

Compact, human-readable TOON encoding for LLM contexts. TOON combines YAML-like indentation with CSV-like tabular arrays to reduce tokens for structured data while keeping output readable.

**Key Features:** Python object to TOON encoding, fast JSON-compatible encode path, tabular arrays for uniform primitive objects, array length markers, Python 3.8+, focused encode test coverage.

## Installation

```bash
git clone https://github.com/toon-format/toon-python.git
cd toon-python
uv sync
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/toon-format/toon-python.git
```

## Quick Start

```python
from toon_format import encode

encode({"name": "Alice", "age": 30})
# name: Alice
# age: 30

encode([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
# [2]{id,name}:
#   1,Alice
#   2,Bob
```

For data that came from `json.loads()` or another JSON parser and is already JSON-compatible, use `encode_normalized()` to skip Python-specific normalization:

```python
import json
from toon_format import encode_normalized

data = json.loads(json_text)
data["request_id"] = "abc-123"

toon = encode_normalized(data)
```

If your edits introduce native Python values such as `datetime`, `Decimal`, `set`, `Path`, `float("nan")`, or callables, use `encode()` instead so those values are normalized first.

```python
from datetime import datetime
from toon_format import encode

data["created_at"] = datetime.now()
toon = encode(data)
```

## JSON String Helper

The package keeps a helper for JSON string to TOON string conversion:

```python
from toon_format.cli import encode_json_to_toon

toon = encode_json_to_toon('{"items": [1, 2, 3]}')
# items[3]: 1,2,3
```

Despite the module name, this package no longer exposes a command-line interface. The former `toon` console script and TOON decoding APIs have been removed.

## API Reference

### `encode(value, options=None) -> str`

Encodes arbitrary Python values after normalizing Python-specific types to JSON-compatible values.

```python
from toon_format import encode

encode({"id": 123}, {"delimiter": "\t", "indent": 4, "lengthMarker": "#"})
```

Normalization includes:

| Python Type | Encoded As |
|-------------|------------|
| `datetime.datetime`, `datetime.date` | ISO 8601 strings |
| `decimal.Decimal` | float |
| `tuple`, `set`, `frozenset` | list |
| `pathlib.Path` | string |
| `float("inf")`, `float("-inf")`, `float("nan")` | `null` |
| callables / unsupported objects | `null` |
| `-0.0` | `0` |

### `encode_normalized(value, options=None) -> str`

Encodes already-normalized JSON-compatible data without the normalization pass. This is the fastest path after parsing and mutating JSON-compatible data.

```python
import json
from toon_format import encode_normalized

data = json.loads(json_text)
data["status"] = "ready"

toon = encode_normalized(data)
```

Use this only when values are `dict`, `list`, `str`, `int`, `float`, `bool`, or `None`.

### `encode_json_to_toon(json_text, delimiter=",", indent=2, length_marker=False) -> str`

Parses a JSON string with the standard library `json` module and then uses `encode_normalized()`.

```python
from toon_format.cli import encode_json_to_toon

encode_json_to_toon('{"items": [1, 2, 3]}', delimiter="|")
# items[3|]: 1|2|3
```

### Options

Options are accepted as a plain dict or `EncodeOptions`.

| Option | Default | Description |
|--------|---------|-------------|
| `delimiter` | `","` | Array value separator. Supports `","`, `"\t"`, and `"|"`. |
| `indent` | `2` | Spaces per indentation level. |
| `lengthMarker` | `False` | Use `"#"` to prefix array lengths, e.g. `items[#3]:`. |

## Format Examples

| Type | Python Input | TOON Output |
|------|--------------|-------------|
| Object | `{"name": "Alice", "age": 30}` | `name: Alice`<br>`age: 30` |
| Primitive Array | `[1, 2, 3]` | `[3]: 1,2,3` |
| Tabular Array | `[{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]` | `[2]{id,name}:`<br>&nbsp;&nbsp;`1,A`<br>&nbsp;&nbsp;`2,B` |
| Mixed Array | `[{"x": 1}, 42, "hi"]` | `[3]:`<br>&nbsp;&nbsp;`- x: 1`<br>&nbsp;&nbsp;`- 42`<br>&nbsp;&nbsp;`- hi` |

Tabular arrays are used only when every object has the same keys and every value is primitive. Arrays with nested objects or arrays use list format.

## Pydantic Integration

The optional Pydantic integration supports TOON encoding for schemas and model instances.

```bash
pip install "toon-python[pydantic]"
```

```python
from toon_format.pydantic import ToonPydanticModel

class User(ToonPydanticModel):
    name: str
    age: int

schema_toon = User.schema_to_toon()
model_toon = User(name="Alice", age=30).model_dump_toon()
```

TOON-to-Pydantic validation has been removed with the decode API.

## Optimization Summary

The encoder has been optimized for the common internal workflow:

```text
JSON string -> json.loads() -> mutate Python object -> encode_normalized()
```

Implemented optimizations:

- `encode_normalized()` skips the recursive normalization pass for already JSON-compatible data.
- JSON string helper now parses once with `json.loads()` and calls `encode_normalized()`.
- Encoding logic is consolidated in `_encoding.py`.
- Early-exit array classification avoids repeated scans and quickly rejects non-tabular nested object arrays.
- Encoded keys are cached per encoder instance.
- String/key validation regexes are precompiled.
- Primitive array and tabular row joins avoid unnecessary intermediate work.
- Hot paths cache delimiter and length marker values on the encoder.

Benchmark settings:

```text
stdlib json only
median of 13 repeats
5 loops per repeat
GC disabled during timed loops
```

`encode()` vs `encode_normalized()` on already JSON-compatible data:

| Payload | `encode()` | `encode_normalized()` | Speedup |
|---------|------------|-----------------------|---------|
| `tabular_5k` | 47.23 ms | 30.11 ms | 1.57x |
| `primitive_100k` | 73.63 ms | 54.40 ms | 1.35x |
| `non_tabular_objects_5k` | 70.41 ms | 50.32 ms | 1.40x |
| `nested_arrays_10k` | 49.57 ms | 36.33 ms | 1.36x |
| `strings_50k` | 111.05 ms | 103.17 ms | 1.08x |

End-to-end standard-library JSON parse plus TOON encoding:

| Payload | `json.loads()` + `encode_normalized()` |
|---------|----------------------------------------|
| `tabular_5k` | 33.76 ms |
| `primitive_100k` | 62.65 ms |
| `non_tabular_objects_5k` | 51.93 ms |
| `nested_arrays_10k` | 39.14 ms |
| `strings_50k` | 106.89 ms |

## Development

```bash
uv sync
uv run pytest
uv run ruff check src/ tests/
uv run ruff format src/ tests/
uv run mypy src/
```

The test suite is encode-only and covers public API behavior, normalization, numeric/string handling, Pydantic encoding, and official encode fixtures.

## Project Status

This fork is currently focused on fast JSON/Python-to-TOON encoding for internal LLM workflows. Decode APIs, parser/scanner modules, and CLI conversion have been removed.

## License

MIT License - see [LICENSE](LICENSE) for details.
