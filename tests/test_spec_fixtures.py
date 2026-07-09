"""Tests for official TOON encode spec fixtures."""

import json
from pathlib import Path
from typing import Any

import pytest

from toon_format import encode
from toon_format.types import EncodeOptions

FIXTURES_DIR = Path(__file__).parent / "fixtures"
ENCODE_DIR = FIXTURES_DIR / "encode"


def load_fixture_file(filepath: Path) -> dict[str, Any]:
    """Load a fixture JSON file."""
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def get_all_encode_fixtures() -> list[tuple]:
    """Get all encode test cases from fixture files."""
    test_cases = []

    for fixture_file in sorted(ENCODE_DIR.glob("*.json")):
        fixture_data = load_fixture_file(fixture_file)
        fixture_name = fixture_file.stem

        for test in fixture_data.get("tests", []):
            test_id = f"{fixture_name}::{test['name']}"
            test_cases.append((test_id, test, fixture_name))

    return test_cases


class TestEncodeFixtures:
    """Test all encode fixtures from the TOON specification."""

    @pytest.mark.parametrize("test_id,test_data,fixture_name", get_all_encode_fixtures())
    def test_encode(self, test_id: str, test_data: dict[str, Any], fixture_name: str):
        input_data = test_data["input"]
        expected = test_data["expected"]
        options_dict = test_data.get("options", {})

        options = EncodeOptions(
            indent=options_dict.get("indent", 2),
            delimiter=options_dict.get("delimiter", ","),
            lengthMarker=options_dict.get("lengthMarker", ""),
        )

        result = encode(input_data, options=options)
        assert result == expected, (
            f"Encode mismatch in {test_id}\n"
            f"Input: {input_data!r}\n"
            f"Expected: {expected!r}\n"
            f"Got: {result!r}"
        )


def count_tests_in_fixture(fixture_path: Path) -> int:
    """Count the number of test cases in a fixture file."""
    fixture_data = load_fixture_file(fixture_path)
    return len(fixture_data.get("tests", []))


def get_fixture_stats() -> dict[str, Any]:
    """Get statistics about the loaded encode fixtures."""
    encode_files = sorted(ENCODE_DIR.glob("*.json"))

    encode_stats = {
        "files": len(encode_files),
        "tests": sum(count_tests_in_fixture(f) for f in encode_files),
        "by_file": {f.stem: count_tests_in_fixture(f) for f in encode_files},
    }

    return {
        "encode": encode_stats,
        "total_files": encode_stats["files"],
        "total_tests": encode_stats["tests"],
    }


if __name__ == "__main__":
    stats = get_fixture_stats()
    print("TOON Encode Fixture Statistics")
    print("=" * 50)
    print(f"\nEncode Fixtures: {stats['encode']['files']} files, {stats['encode']['tests']} tests")
    for name, count in stats["encode"]["by_file"].items():
        print(f"  - {name}: {count} tests")
    print(f"\nTotal: {stats['total_files']} fixture files, {stats['total_tests']} test cases")
