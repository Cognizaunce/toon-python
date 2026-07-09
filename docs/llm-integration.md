# LLM Integration Guide

Best practices for using TOON as a compact, readable encoding for data you send to Large Language Models.

This Python package is currently encode-only. Use it to convert Python or JSON-compatible data into TOON before adding that data to prompts, tool inputs, retrieval context, logs, or model-facing examples. If you need to parse model-generated TOON back into Python, use a decoder from another implementation or request JSON for structured outputs.

## Why TOON for LLMs?

Traditional JSON spends many tokens on structural characters:
- Braces and brackets: `{}`, `[]`
- Repeated quotes around every key
- Commas between every element

TOON reduces that overhead while keeping structure visible to humans and models.

**JSON:**

```json
{"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
```

**TOON:**

```toon
users[2]{id,name}:
  1,Alice
  2,Bob
```

## Basic Integration Pattern

Encode your data before inserting it into a prompt:

```python
from toon_format import encode

records = {
    "users": [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "viewer"},
    ]
}

context = encode(records)

prompt = f"""Analyze the following user records.

TOON context:
{context}
"""
```

When writing prompts manually, code blocks can help the model distinguish TOON data from surrounding natural language.

## Encoding Options

### Length Markers

Use `lengthMarker="#"` when exact counts matter in the prompt:

```python
from toon_format import encode

data = {"items": ["a", "b", "c"]}
encode(data, {"lengthMarker": "#"})
# items[#3]: a,b,c
```

You can then tell the model that `[#3]` means the array contains exactly three items.

### Delimiter Selection

Choose delimiters based on the data:

```python
from toon_format import encode

encode(data, {"delimiter": "\t"})  # Useful when values contain commas
encode(data, {"delimiter": "|"})   # Useful when values contain tabs
encode(data, {"delimiter": ","})   # Default
```

## Prompting Strategies

### Few-Shot Examples

Show the model the shape you expect:

```
Use the following TOON context when answering.

Example users:
users[2]{id,name,role}:
  1,Alice,admin
  2,Bob,viewer

Question: Which users can change settings?
```

### Explicit Rules

When asking a model to reason over TOON, include the important conventions:

```
TOON notes:
- `key: value` represents object fields
- Indentation represents nesting
- `[N]` indicates array length
- `[N]{fields}:` indicates a tabular array with named columns
- Strings may be quoted when needed
```

## Real-World Use Cases

### Structured Context

```python
from toon_format import encode

support_ticket = {
    "ticket": {
        "id": "T-123",
        "priority": "high",
        "messages": [
            {"from": "user", "text": "Login fails after password reset"},
            {"from": "agent", "text": "Asked for browser and timestamp"},
        ],
    }
}

toon_context = encode(support_ticket)
```

```toon
ticket:
  id: T-123
  priority: high
  messages[2]{from,text}:
    user,Login fails after password reset
    agent,Asked for browser and timestamp
```

### Configuration Summaries

```python
from toon_format import encode

config = {
    "app": "myapp",
    "port": 8080,
    "database": {"host": "localhost", "port": 5432, "name": "myapp_db"},
    "features": ["auth", "logging", "cache"],
}

toon_config = encode(config)
```

### Retrieval Results

```python
from toon_format import encode_normalized

results = [
    {"doc_id": "a1", "score": 0.94, "title": "Password reset"},
    {"doc_id": "b2", "score": 0.89, "title": "Account recovery"},
]

retrieval_context = encode_normalized({"results": results})
```

## Token Efficiency Best Practices

### Prefer Tabular Data for Uniform Objects

Less compact:

```toon
users[3]:
  - id: 1
    name: Alice
  - id: 2
    name: Bob
  - id: 3
    name: Charlie
```

More compact:

```toon
users[3]{id,name}:
  1,Alice
  2,Bob
  3,Charlie
```

The encoder automatically uses tabular form for arrays of objects with the same primitive fields.

### Minimize Unnecessary Nesting

```toon
items[2]: a,b
```

is cheaper and easier to scan than deeply nested wrappers when the extra hierarchy is not meaningful.

### Use Compact Keys When Appropriate

```toon
id: 123
name: Alice
```

is more efficient than long repeated field names when abbreviations are clear in context.

## Common Pitfalls

### Expecting This Package to Decode Model Output

This package currently encodes Python/JSON data to TOON. It does not parse TOON responses back into Python.

For structured model output that your Python application must parse, prefer JSON mode, tool calling, or another TOON decoder.

### Forgetting Quoting Rules in Manual Examples

Numeric-looking strings, booleans, `null`, strings with delimiters, and strings with structural characters may need quotes:

```toon
code: "123"
status: "true"
```

The encoder handles this automatically when you generate TOON from Python data.

## Resources

- [Format Specification](format.md) - Complete TOON syntax reference
- [API Reference](api.md) - Encoding API documentation
- [Official Spec](https://github.com/toon-format/spec) - Normative specification
- [Benchmarks](https://github.com/toon-format/toon#benchmarks) - Token efficiency analysis

## Summary

Key takeaways:
- Use TOON to send compact structured context to LLMs.
- Prefer `encode_normalized()` for data that is already JSON-compatible.
- Let the encoder handle quoting, delimiters, and tabular arrays.
- Use JSON, tool calling, or another decoder when you need parseable model output.
