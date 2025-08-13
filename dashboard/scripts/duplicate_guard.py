#!/usr/bin/env python3
"""
Duplicate ingestion guard for idempotent data pipeline.
Prevents duplicate records for the same (date, schema_version) combination.
"""

import json
import os
import sys
from typing import Dict, Set, Tuple, List
from datetime import datetime

# Add dashboard path for utils import
dashboard_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, dashboard_path)
from utils.schema_utils import normalize_schema_version

def load_existing_records(filepath: str) -> Set[Tuple[str, str]]:
    """
    Load existing records and return set of (date, schema_version) tuples.
    """
    existing = set()
    
    if not os.path.exists(filepath):
        return existing
    
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    record = json.loads(line)
                    date = record.get('date', '')
                    schema_version = record.get('schema_version', 'v1.0.0')
                    # Normalize schema version to prevent v1.0.0 vs 2.0.0 duplicates
                    normalized_version = normalize_schema_version(schema_version)
                    if date:
                        existing.add((date, normalized_version))
                except json.JSONDecodeError:
                    continue
    
    return existing

def check_duplicate(record: Dict, existing: Set[Tuple[str, str]]) -> bool:
    """
    Check if a record would be a duplicate based on normalized schema version.
    Uses schema version normalization to prevent v1.0.0 vs 2.0.0 duplicates.
    Returns True if duplicate exists.
    """
    date = record.get('date', '')
    schema_version = record.get('schema_version', 'v1.0.0')
    
    if not date:
        return False
    
    # Normalize schema version to catch format inconsistencies
    normalized_version = normalize_schema_version(schema_version)
    return (date, normalized_version) in existing

def check_duplicate_in_records(record: Dict, existing_records: List[Dict]) -> bool:
    """
    Convenience function to check duplicates against a list of existing records.
    Converts records to normalized (date, schema_version) set for comparison.
    """
    existing_set = set()
    for existing_record in existing_records:
        date = existing_record.get('date', '')
        schema_version = existing_record.get('schema_version', 'v1.0.0')
        normalized_version = normalize_schema_version(schema_version)
        if date:
            existing_set.add((date, normalized_version))
    
    return check_duplicate(record, existing_set)

def filter_duplicates(new_records: List[Dict], target_file: str) -> List[Dict]:
    """
    Filter out duplicate records based on existing data.
    Returns list of non-duplicate records.
    """
    existing = load_existing_records(target_file)
    unique_records = []
    duplicates_found = []
    
    for record in new_records:
        if check_duplicate(record, existing):
            duplicates_found.append(record.get('date', 'unknown'))
        else:
            unique_records.append(record)
            # Add to existing set to prevent duplicates within batch
            date = record.get('date', '')
            schema_version = record.get('schema_version', 'v1.0.0')
            # Normalize schema version for consistency
            normalized_version = normalize_schema_version(schema_version)
            if date:
                existing.add((date, normalized_version))
    
    if duplicates_found:
        print(f"⚠️  Found {len(duplicates_found)} duplicate records for dates: {', '.join(duplicates_found)}")
        print("   These will be skipped to maintain idempotence.")
    
    return unique_records

def append_unique_records(source_file: str, target_file: str) -> int:
    """
    Append only unique records from source to target.
    Returns count of records added.
    """
    # Load new records
    new_records = []
    with open(source_file, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    new_records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    # Filter duplicates
    unique_records = filter_duplicates(new_records, target_file)
    
    if not unique_records:
        print("✅ No new records to add (all would be duplicates)")
        return 0
    
    # Append unique records
    with open(target_file, 'a') as f:
        for record in unique_records:
            f.write(json.dumps(record) + '\n')
    
    print(f"✅ Added {len(unique_records)} unique records")
    return len(unique_records)

def validate_no_duplicates(filepath: str) -> bool:
    """
    Validate that a file contains no duplicate (date, schema_version) pairs.
    Returns True if no duplicates found.
    """
    seen = set()
    duplicates = []
    
    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            if line.strip():
                try:
                    record = json.loads(line)
                    date = record.get('date', '')
                    schema_version = record.get('schema_version', 'v1.0.0')
                    
                    if date:
                        key = (date, schema_version)
                        if key in seen:
                            duplicates.append(f"Line {line_num}: {date} (schema {schema_version})")
                        else:
                            seen.add(key)
                except json.JSONDecodeError:
                    print(f"⚠️  Invalid JSON at line {line_num}")
    
    if duplicates:
        print(f"❌ Found {len(duplicates)} duplicate entries:")
        for dup in duplicates[:5]:  # Show first 5
            print(f"   {dup}")
        if len(duplicates) > 5:
            print(f"   ... and {len(duplicates) - 5} more")
        return False
    
    print(f"✅ No duplicates found in {len(seen)} records")
    return True

def main():
    """CLI interface for duplicate guard."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Duplicate guard for wellness data')
    parser.add_argument('command', choices=['check', 'append', 'validate'],
                       help='Command to execute')
    parser.add_argument('file', help='File to check or validate')
    parser.add_argument('--target', help='Target file for append command')
    
    args = parser.parse_args()
    
    if args.command == 'validate':
        success = validate_no_duplicates(args.file)
        sys.exit(0 if success else 1)
    
    elif args.command == 'append':
        if not args.target:
            print("❌ --target required for append command")
            sys.exit(1)
        count = append_unique_records(args.file, args.target)
        sys.exit(0 if count >= 0 else 1)
    
    elif args.command == 'check':
        # Check if file would have duplicates if appended to itself
        with open(args.file, 'r') as f:
            records = [json.loads(line) for line in f if line.strip()]
        
        seen = set()
        has_internal_dups = False
        for record in records:
            date = record.get('date', '')
            schema_version = record.get('schema_version', 'v1.0.0')
            key = (date, schema_version)
            if key in seen:
                has_internal_dups = True
                print(f"❌ Internal duplicate found: {date}")
            else:
                seen.add(key)
        
        if not has_internal_dups:
            print(f"✅ No internal duplicates in {len(records)} records")
        
        sys.exit(0 if not has_internal_dups else 1)

if __name__ == "__main__":
    main()