# Documentation

Documentation for the encode-only `toon_format` Python package.

## Quick Links

- [API Reference](api.md) - Public encoding APIs and options
- [Format Specification](format.md) - TOON syntax and examples
- [LLM Integration](llm-integration.md) - Best practices for using encoded TOON in LLM workflows

## Getting Started

New to TOON? Start here:

1. Read the [main README](../README.md) for installation and quick start examples
2. Review the [Format Specification](format.md) to understand TOON syntax
3. Check the [API Reference](api.md) for `encode()` and `encode_normalized()` usage
4. See [LLM Integration](llm-integration.md) for prompt/context patterns

## Documentation Structure

### [API Reference](api.md)

Complete reference for public encoding APIs:
- `encode()` - Convert Python values to TOON
- `encode_normalized()` - Convert already-normalized JSON-compatible values to TOON
- `encode_json_to_toon()` - Convert a JSON string to TOON
- `EncodeOptions` - Encoding configuration
- Type normalization rules
- Advanced encoding usage patterns

### [Format Specification](format.md)

Detailed explanation of TOON format rules:
- Objects and nesting
- Arrays, including primitive and tabular forms
- Delimiters
- String quoting rules
- Primitives
- Indentation
- Complete format examples

### [LLM Integration](llm-integration.md)

Best practices for LLM usage:
- Why TOON for LLM contexts
- Encoding data before sending it to a model
- Prompting strategies
- Token efficiency techniques
- Real-world use cases

## Roadmap

The following features are planned for future releases:

- **Comprehensive Benchmarks**: Detailed token efficiency comparisons across data structures and LLM models
- **Official Documentation Site**: Dedicated documentation website with interactive examples and tutorials

## External Resources

- [Official TOON Specification](https://github.com/toon-format/spec) - Normative spec
- [TypeScript Reference](https://github.com/toon-format/toon) - Original implementation
- [Test Fixtures](../tests/README.md) - Spec compliance test suite
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute

## Examples

### Basic Encoding

```python
from toon_format import encode

data = {"name": "Alice", "age": 30}
print(encode(data))
# name: Alice
# age: 30
```

### Fast Path for JSON-Compatible Data

```python
import json
from toon_format import encode_normalized

data = json.loads('{"items": [{"id": 1}, {"id": 2}]}')
print(encode_normalized(data))
# items[2]{id}:
#   1
#   2
```

### With Options

```python
from toon_format import encode

encode([1, 2, 3], {"delimiter": "\t", "lengthMarker": "#"})
# [#3\t]: 1\t2\t3
```

## Support

- **Bug Reports:** [GitHub Issues](https://github.com/toon-format/toon-python/issues)
- **Questions:** [GitHub Discussions](https://github.com/toon-format/toon-python/discussions)
- **Contributing:** See [CONTRIBUTING.md](../CONTRIBUTING.md)

## License

MIT License - see [LICENSE](../LICENSE)
