# TOON Encode Tests

This directory contains the encode-only test suite for the Python TOON package. The current package focuses on converting Python and JSON-compatible data into TOON; decode, scanner, parser, and CLI conversion tests have been removed.

## Purpose

The tests serve four main purposes:

- **Encode conformance:** Verify output matches the official TOON encode fixtures.
- **Regression coverage:** Catch changes in formatting, quoting, normalization, and options.
- **Performance-path safety:** Protect `encode_normalized()` and the optimized encoder internals.
- **Integration coverage:** Check JSON string conversion and optional Pydantic encoding helpers.

## Directory Structure

```text
tests/
├── fixtures.schema.json    # JSON Schema for fixture validation
├── fixtures/
│   └── encode/             # Encoding fixtures (JSON-compatible value -> TOON)
│       ├── primitives.json
│       ├── objects.json
│       ├── arrays-primitive.json
│       ├── arrays-tabular.json
│       ├── arrays-nested.json
│       ├── arrays-objects.json
│       ├── delimiters.json
│       ├── normalization.json
│       ├── whitespace.json
│       └── options.json
├── conftest.py             # Shared pytest fixtures
├── test_api.py             # Public encode API behavior
├── test_cli.py             # `encode_json_to_toon()` helper behavior
├── test_encoder.py         # Python-specific encoder behavior
├── test_normalize_functions.py
├── test_numeric_detection.py
├── test_pydantic.py        # Pydantic schema/model TOON encoding
├── test_spec_fixtures.py   # Official encode fixture runner
├── test_string_utils.py
└── test_utils.py
```

## Fixture Format

Encode fixture files follow the JSON structure defined in [`fixtures.schema.json`](./fixtures.schema.json):

```json
{
  "version": "1.3",
  "category": "encode",
  "description": "Brief description of test category",
  "tests": [
    {
      "name": "descriptive test name",
      "input": {"id": 1},
      "expected": "id: 1",
      "options": {},
      "specSection": "6",
      "note": "Optional explanation"
    }
  ]
}
```

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `version` | Yes | TOON specification version, e.g. `"1.3"` |
| `category` | Yes | Test category; currently `"encode"` |
| `description` | Yes | Brief description of what the fixture tests |
| `tests` | Yes | Array of test cases |
| `tests[].name` | Yes | Descriptive test name |
| `tests[].input` | Yes | JSON-compatible input value to encode |
| `tests[].expected` | Yes | Expected TOON string |
| `tests[].options` | No | Encoder options |
| `tests[].specSection` | No | Reference to a TOON specification section |
| `tests[].note` | No | Optional explanation for special cases |
| `tests[].minSpecVersion` | No | Minimum spec version required |

## Encoder Options

```json
{
  "delimiter": ",",
  "indent": 2,
  "lengthMarker": ""
}
```

- `delimiter`: `","` (comma, default), `"\t"` (tab), or `"|"` (pipe)
- `indent`: Number of spaces per indentation level (default: `2`)
- `lengthMarker`: `"#"` to prefix array lengths, or `""` for no marker

## Running Tests

```bash
uv run pytest
uv run ruff check src/ tests/
```

Useful focused runs:

```bash
uv run pytest tests/test_spec_fixtures.py
uv run pytest tests/test_api.py tests/test_cli.py tests/test_encoder.py
uv run pytest tests/test_numeric_detection.py tests/test_string_utils.py tests/test_utils.py
```

## Test Coverage

### Encode Fixtures (`fixtures/encode/`)

| File | Description | Spec Areas |
|------|-------------|------------|
| `primitives.json` | String, number, boolean, null encoding and escaping | primitives |
| `objects.json` | Simple objects, nested objects, key encoding | objects |
| `arrays-primitive.json` | Inline primitive arrays and empty arrays | arrays |
| `arrays-tabular.json` | Tabular format with headers and rows | tabular arrays |
| `arrays-nested.json` | Arrays of arrays and mixed arrays | nested arrays |
| `arrays-objects.json` | Objects as list items and complex nesting | object arrays |
| `delimiters.json` | Tab and pipe delimiter options | delimiters |
| `normalization.json` | Python/JSON normalization behavior | normalization |
| `whitespace.json` | Formatting invariants and indentation | whitespace |
| `options.json` | Length marker and delimiter combinations | options |

### Python-Specific Tests

- `test_api.py`: Public `encode()` and `encode_normalized()` behavior.
- `test_cli.py`: `encode_json_to_toon()` JSON string helper.
- `test_encoder.py`: Python-specific encoding edge cases.
- `test_normalize_functions.py`: Normalization helpers for native Python values.
- `test_numeric_detection.py`: Numeric-looking string detection.
- `test_pydantic.py`: Pydantic schema/model TOON encoding.
- `test_string_utils.py` and `test_utils.py`: Internal string and literal helpers.

## Adding Test Cases

To add encode fixture coverage:

1. Choose the appropriate file in `fixtures/encode/`.
2. Add a test case with `name`, `input`, `expected`, and optional `options`.
3. Include `specSection` or `note` when the behavior is subtle.
4. Run `uv run pytest tests/test_spec_fixtures.py`.
5. Run `uv run pytest` before submitting changes.

For Python-specific behavior, prefer a focused test module such as `test_encoder.py`, `test_api.py`, or `test_normalize_functions.py`.

## Notes

The repository may still keep upstream decode fixture files for reference, but this Python package does not run decode tests and does not expose decode APIs.
