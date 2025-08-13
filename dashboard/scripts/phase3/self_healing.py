#!/usr/bin/env python3
"""
AC8: Self-healing persistence.
Detect corrupted history files, quarantine them, and rebuild from telemetry.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

def validate_history_file(file_path: str) -> Tuple[bool, List[str]]:
    """Validate integrity of a history file.
    
    Returns (is_valid, list_of_errors)
    """
    errors = []
    
    if not Path(file_path).exists():
        errors.append(f"History file does not exist: {file_path}")
        return False, errors
    
    try:
        records = []
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        record = json.loads(line)
                        records.append(record)
                    except json.JSONDecodeError as e:
                        errors.append(f"Line {line_num}: Invalid JSON - {e}")
        
        if not records:
            errors.append("File is empty or contains no valid records")
            return False, errors
        
        # Validate record structure
        for i, record in enumerate(records):
            # Check required fields
            required_fields = ['date', 'score', 'band']
            for field in required_fields:
                if field not in record:
                    errors.append(f"Record {i+1}: Missing required field '{field}'")
            
            # Validate score range
            if 'score' in record:
                score = record['score']
                if not isinstance(score, (int, float)) or not (0 <= score <= 100):
                    errors.append(f"Record {i+1}: Invalid score {score}")
            
            # Validate date format
            if 'date' in record:
                try:
                    datetime.strptime(record['date'], '%Y-%m-%d')
                except ValueError:
                    errors.append(f"Record {i+1}: Invalid date format {record['date']}")
        
        # Check for duplicates
        dates_seen = set()
        for record in records:
            date = record.get('date')
            if date in dates_seen:
                errors.append(f"Duplicate date found: {date}")
            else:
                dates_seen.add(date)
        
        return len(errors) == 0, errors
        
    except Exception as e:
        errors.append(f"Failed to read file: {e}")
        return False, errors

def quarantine_corrupted_file(file_path: str) -> str:
    """Move corrupted file to quarantine location.
    
    Returns path to quarantined file.
    """
    file_path_obj = Path(file_path)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    quarantine_path = file_path_obj.parent / f"{file_path_obj.stem}.corrupted_{timestamp}{file_path_obj.suffix}"
    
    shutil.move(file_path, quarantine_path)
    logger.warning(f"QUARANTINE: Moved corrupted file {file_path} to {quarantine_path}")
    
    return str(quarantine_path)

def rebuild_from_telemetry(output_path: str, telemetry_files: List[str] = None) -> bool:
    """Rebuild history from clean telemetry records.
    
    Args:
        output_path: Path where to write rebuilt history
        telemetry_files: List of telemetry files to use as source
    
    Returns:
        True if rebuild successful
    """
    if telemetry_files is None:
        # Default telemetry files to check
        telemetry_files = [
            'dashboard/data/garmin_wellness.jsonl',
            'data/garmin_wellness.jsonl',
            'garmin_wellness.jsonl'
        ]
    
    all_records = []
    
    # Collect records from all telemetry files
    for tel_file in telemetry_files:
        if Path(tel_file).exists():
            try:
                with open(tel_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                record = json.loads(line)
                                # Only include records with essential fields
                                if 'date' in record and 'score' in record and 'band' in record:
                                    all_records.append(record)
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                logger.warning(f"Could not read telemetry file {tel_file}: {e}")
    
    if not all_records:
        logger.error("No valid telemetry records found for rebuild")
        return False
    
    # Remove duplicates, keeping most recent
    unique_records = {}
    for record in all_records:
        date = record['date']
        if date not in unique_records or record.get('timestamp_utc', '') > unique_records[date].get('timestamp_utc', ''):
            unique_records[date] = record
    
    # Sort by date
    sorted_records = sorted(unique_records.values(), key=lambda r: r['date'])
    
    # Write rebuilt history
    try:
        Path(output_path).parent.mkdir(exist_ok=True)
        with open(output_path, 'w') as f:
            for record in sorted_records:
                f.write(json.dumps(record) + '\n')
        
        logger.info(f"RECOVERED_HISTORY: Rebuilt {len(sorted_records)} records to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to write rebuilt history: {e}")
        return False

def self_heal_if_needed(history_path: str, telemetry_files: List[str] = None) -> Tuple[bool, str]:
    """Check history file and self-heal if corrupted.
    
    Returns (is_healthy, status_message)
    """
    try:
        is_valid, errors = validate_history_file(history_path)
        
        if is_valid:
            return True, "History file is healthy"
        
        logger.warning(f"History file corruption detected: {len(errors)} errors")
        for error in errors[:5]:  # Log first 5 errors
            logger.warning(f"  {error}")
        
        # Quarantine the corrupted file
        quarantine_path = quarantine_corrupted_file(history_path)
        
        # Attempt to rebuild
        rebuild_success = rebuild_from_telemetry(history_path, telemetry_files)
        
        if rebuild_success:
            # Validate the rebuilt file
            is_rebuilt_valid, rebuild_errors = validate_history_file(history_path)
            if is_rebuilt_valid:
                return True, f"Successfully healed: quarantined to {quarantine_path}, rebuilt from telemetry"
            else:
                return False, f"Rebuild failed validation: {len(rebuild_errors)} errors remain"
        else:
            return False, "Failed to rebuild from telemetry"
            
    except Exception as e:
        logger.error(f"Self-healing process failed: {e}")
        return False, f"Self-healing process failed: {e}"

def create_corrupt_test_file(file_path: str) -> None:
    """Create a intentionally corrupted file for testing."""
    corrupt_data = [
        '{"date": "2025-08-01", "score": 65, "band": "Maintain"}',  # Valid
        '{"date": "2025-08-02", "score": 999, "band": "Invalid"}',  # Invalid score and band
        '{"date": "invalid-date", "score": 70}',                    # Invalid date, missing band
        'invalid json line',                                         # Invalid JSON
        '{"date": "2025-08-01", "score": 75, "band": "Go for it"}', # Duplicate date
    ]
    
    with open(file_path, 'w') as f:
        for line in corrupt_data:
            f.write(line + '\n')

def main():
    """CLI interface for self-healing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Self-healing persistence')
    parser.add_argument('history_file', help='History file to check/heal')
    parser.add_argument('--telemetry', nargs='*', 
                       help='Telemetry files to use for rebuild (default: auto-detect)')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate, do not heal')
    parser.add_argument('--create-corrupt', action='store_true',
                       help='Create corrupt test file (for testing)')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    if args.create_corrupt:
        create_corrupt_test_file(args.history_file)
        print(f"Created corrupt test file: {args.history_file}")
        return
    
    if args.validate_only:
        is_valid, errors = validate_history_file(args.history_file)
        if is_valid:
            print("✅ History file is valid")
            exit(0)
        else:
            print(f"❌ History file has {len(errors)} validation errors:")
            for error in errors[:10]:
                print(f"   • {error}")
            exit(1)
    
    # Perform self-healing
    is_healthy, message = self_heal_if_needed(args.history_file, args.telemetry)
    
    if is_healthy:
        print(f"✅ {message}")
        exit(0)
    else:
        print(f"❌ {message}")
        exit(1)

if __name__ == '__main__':
    main()