#!/usr/bin/env python3
"""Validate daily record JSON lines against schema and integrity rules.
Usage:
  PYTHONPATH=. python3 dashboard/scripts/validate_daily_records.py path/to/records.jsonl

Checks:
- JSON Schema compliance
- contribution sum integrity: abs(sum(contrib) - score/100) < 0.01
- required keys present (enforced by schema)
"""
from __future__ import annotations
import json, sys, math, pathlib
from typing import Any

try:
    import jsonschema  # type: ignore
except ImportError as e:
    print("Missing dependency: jsonschema. Install with 'pip install jsonschema'", file=sys.stderr)
    sys.exit(2)

SCHEMA_PATH = pathlib.Path(__file__).parent.parent / "schema" / "daily_record.schema.json"

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    schema = json.load(f)

validator = jsonschema.Draft202012Validator(schema)


def validate_record(obj: dict[str, Any], line_no: int) -> list[str]:
    errors = []
    for err in validator.iter_errors(obj):
        errors.append(f"schema:{err.message}")
    # Integrity: contribution sum close to score/100
    try:
        contrib_sum = sum(float(v) for v in obj.get("contrib", {}).values())
        expected = float(obj.get("score", 0)) / 100.0
        if math.fabs(contrib_sum - expected) >= 0.01:
            errors.append(f"integrity:contrib_sum={contrib_sum:.5f} expected≈{expected:.5f}")
    except Exception as e:  # pragma: no cover
        errors.append(f"integrity:exception:{e}")
    return [f"line {line_no}: {e}" for e in errors]


def main():
    if len(sys.argv) != 2:
        print("Usage: validate_daily_records.py <path.jsonl>", file=sys.stderr)
        return 1
    path = pathlib.Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                all_errors.append(f"line {i}: invalid json: {e}")
                continue
            all_errors.extend(validate_record(obj, i))

    if all_errors:
        print("VALIDATION FAILED")
        for err in all_errors:
            print(err)
        return 1
    print("VALIDATION PASSED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
