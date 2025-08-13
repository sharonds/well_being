#!/usr/bin/env python3
"""
Privacy scan for telemetry data.
Ensures no raw health metrics or PII leak into telemetry.
"""

import json
import re
import sys
from typing import Dict, List, Tuple

# Allowed numeric fields with their valid ranges
ALLOWED_NUMERIC_FIELDS = {
    'score': (0, 100),
    'completeness_pct': (0.0, 100.0),
    'auto_run': (0, 1),
    'metrics_mask': (0, 15),  # 4-bit mask for 4 metrics
    'integrity_fail_count': (0, 100),
    'schema_version': None,  # String, not numeric
}

# Forbidden patterns that suggest raw health data
FORBIDDEN_PATTERNS = [
    (r'"[^"]*":\s*\d{4,}\b', 'Large number (>999) detected - possible raw steps'),
    (r'\bsteps["\']?\s*:\s*\d+', 'Raw steps value detected'),
    (r'\brestingHeartRate["\']?\s*:\s*\d+', 'Raw heart rate detected'),
    (r'\bsleepHours["\']?\s*:\s*[\d.]+', 'Raw sleep hours detected'),
    (r'\bstress["\']?\s*:\s*\d+', 'Raw stress value detected'),
    (r'\bhrv["\']?\s*:\s*\d+', 'Raw HRV value detected'),
    (r'\bcalories["\']?\s*:\s*\d+', 'Raw calories detected'),
    (r'\bweight["\']?\s*:\s*[\d.]+', 'Raw weight detected'),
    (r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', 'Email address detected'),
]

def scan_record_for_violations(record: Dict) -> List[str]:
    """
    Scan a single telemetry record for privacy violations.
    Returns list of violation messages.
    """
    violations = []
    
    # Check for forbidden raw metrics in the record structure
    if 'metrics' in record and isinstance(record['metrics'], dict):
        violations.append("Raw 'metrics' object found - should only have presence flags")
    
    # Check numeric fields are within allowed ranges
    for field, value in record.items():
        if isinstance(value, (int, float)):
            if field not in ALLOWED_NUMERIC_FIELDS:
                violations.append(f"Unexpected numeric field '{field}' with value {value}")
            elif ALLOWED_NUMERIC_FIELDS[field] is not None:
                min_val, max_val = ALLOWED_NUMERIC_FIELDS[field]
                if not (min_val <= value <= max_val):
                    violations.append(f"Field '{field}' value {value} outside allowed range [{min_val}, {max_val}]")
    
    # Check for large numbers that might be raw metrics
    record_str = json.dumps(record)
    for pattern, message in FORBIDDEN_PATTERNS:
        if re.search(pattern, record_str, re.IGNORECASE):
            violations.append(message)
    
    # Check for presence of required privacy fields
    if 'metrics_mask' not in record and 'presence_mask' not in record:
        violations.append("Missing metrics_mask/presence_mask field")
    
    return violations

def scan_telemetry_file(filepath: str) -> Tuple[bool, List[str]]:
    """
    Scan a telemetry JSONL file for privacy violations.
    Returns (is_clean, list_of_violations).
    """
    all_violations = []
    line_num = 0
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line_num += 1
                if not line.strip():
                    continue
                
                try:
                    record = json.loads(line)
                    violations = scan_record_for_violations(record)
                    if violations:
                        for v in violations:
                            all_violations.append(f"Line {line_num}: {v}")
                except json.JSONDecodeError as e:
                    all_violations.append(f"Line {line_num}: Invalid JSON - {e}")
    
    except FileNotFoundError:
        all_violations.append(f"File not found: {filepath}")
    
    return len(all_violations) == 0, all_violations

def generate_clean_telemetry_record(date: str, score: int, band: str,
                                   completeness: float = 75.0,
                                   auto_run: bool = False) -> Dict:
    """
    Generate a privacy-compliant telemetry record.
    """
    return {
        "date": date,
        "score": score,
        "band": band,
        "metrics_mask": 15,  # All 4 metrics present
        "completeness_pct": completeness,
        "auto_run": 1 if auto_run else 0,
        "schema_version": "v2.0.0",
        "timestamp_utc": f"{date}T12:00:00Z"
    }

def main():
    """CLI interface for privacy scanning."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Privacy scan for telemetry data')
    parser.add_argument('file', help='Telemetry file to scan')
    parser.add_argument('--strict', action='store_true',
                       help='Fail on any numeric value > 100')
    
    args = parser.parse_args()
    
    is_clean, violations = scan_telemetry_file(args.file)
    
    if is_clean:
        print(f"✅ Privacy scan PASSED - no violations found")
        sys.exit(0)
    else:
        print(f"❌ Privacy scan FAILED - {len(violations)} violations found:")
        for v in violations[:10]:  # Show first 10
            print(f"   {v}")
        if len(violations) > 10:
            print(f"   ... and {len(violations) - 10} more")
        sys.exit(1)

if __name__ == "__main__":
    main()