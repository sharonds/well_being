#!/usr/bin/env python3
"""
AC3: Data integrity monitoring.
Track integrity failures and ensure <1% failure rate over 14 days.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

def load_telemetry_records(file_path: str) -> List[Dict]:
    """Load telemetry records from JSONL file."""
    records = []
    if not Path(file_path).exists():
        return records
    
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    return records

def validate_record_integrity(record: Dict) -> Tuple[bool, List[str]]:
    """Validate integrity of a single telemetry record.
    
    Returns (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields check
    required_fields = ['date', 'score', 'band']
    for field in required_fields:
        if field not in record:
            errors.append(f"Missing required field: {field}")
    
    # Score validation
    if 'score' in record:
        score = record['score']
        if not isinstance(score, (int, float)):
            errors.append("Score must be numeric")
        elif not (0 <= score <= 100):
            errors.append(f"Score {score} out of valid range [0-100]")
    
    # Band validation  
    if 'band' in record:
        valid_bands = ["Take it easy", "Maintain", "Go for it"]
        if record['band'] not in valid_bands:
            errors.append(f"Invalid band '{record['band']}', must be one of {valid_bands}")
    
    # Score-Band consistency check
    if 'score' in record and 'band' in record:
        score = record['score']
        band = record['band']
        expected_band = get_expected_band(score)
        if band != expected_band:
            errors.append(f"Band '{band}' inconsistent with score {score}, expected '{expected_band}'")
    
    # Date format validation
    if 'date' in record:
        try:
            datetime.strptime(record['date'], '%Y-%m-%d')
        except ValueError:
            errors.append(f"Invalid date format: {record['date']}")
    
    # Auto-run field validation
    if 'auto_run' in record:
        if record['auto_run'] not in [0, 1]:
            errors.append(f"auto_run must be 0 or 1, got {record['auto_run']}")
    
    # Metrics mask validation
    if 'metrics_mask' in record:
        mask = record['metrics_mask']
        if not isinstance(mask, int) or not (0 <= mask <= 15):
            errors.append(f"metrics_mask must be integer 0-15, got {mask}")
    
    return len(errors) == 0, errors

def get_expected_band(score: float) -> str:
    """Get expected band for a given score."""
    if score < 40:
        return "Take it easy"
    elif score < 70:
        return "Maintain"
    else:
        return "Go for it"

def calculate_integrity_failure_rate(records: List[Dict], days: int = 14) -> Dict:
    """Calculate integrity failure rate over N days.
    
    AC3: Ensure <1% integrity failures over 14 days.
    """
    # Filter to last N days
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    recent_records = [r for r in records if r.get('date', '') >= cutoff_date]
    
    if not recent_records:
        return {
            'total_records': 0,
            'failed_records': 0,
            'failure_rate_pct': 0.0,
            'alert': False,
            'errors': []
        }
    
    failed_records = 0
    all_errors = []
    
    for record in recent_records:
        is_valid, errors = validate_record_integrity(record)
        if not is_valid:
            failed_records += 1
            all_errors.extend([f"Date {record.get('date', 'unknown')}: {err}" for err in errors])
    
    failure_rate = (failed_records / len(recent_records)) * 100
    alert_triggered = failure_rate >= 1.0  # AC3: <1% threshold
    
    result = {
        'total_records': len(recent_records),
        'failed_records': failed_records,
        'failure_rate_pct': round(failure_rate, 2),
        'alert': alert_triggered,
        'errors': all_errors[:10],  # Limit to first 10 errors
        'days_analyzed': days
    }
    
    if alert_triggered:
        logger.warning(f"INTEGRITY_FAILURE_RATE: {failure_rate:.2f}% >= 1.0% threshold "
                      f"({failed_records}/{len(recent_records)} records)")
    else:
        logger.info(f"Integrity check OK: {failure_rate:.2f}% failure rate "
                   f"({failed_records}/{len(recent_records)} records)")
    
    return result

def add_integrity_fail_count(record: Dict) -> Dict:
    """Add integrity_fail_count field to record.
    
    This field tracks cumulative integrity failures for monitoring.
    """
    is_valid, errors = validate_record_integrity(record)
    
    # Add fail count (0 for valid, 1 for invalid)
    record['integrity_fail_count'] = 0 if is_valid else 1
    
    if not is_valid:
        logger.warning(f"Integrity failure in record {record.get('date', 'unknown')}: {errors}")
    
    return record

def generate_integrity_report(file_path: str) -> Dict:
    """Generate comprehensive integrity monitoring report."""
    records = load_telemetry_records(file_path)
    
    if not records:
        return {
            'error': 'No telemetry records found',
            'file_path': file_path
        }
    
    # Calculate failure rates for different time windows
    rate_14d = calculate_integrity_failure_rate(records, 14)
    rate_7d = calculate_integrity_failure_rate(records, 7)
    rate_30d = calculate_integrity_failure_rate(records, 30)
    
    # Overall stats
    total_failed = 0
    all_errors = []
    for record in records:
        is_valid, errors = validate_record_integrity(record)
        if not is_valid:
            total_failed += 1
            all_errors.extend(errors)
    
    overall_failure_rate = (total_failed / len(records)) * 100 if records else 0
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'file_analyzed': file_path,
        'total_records': len(records),
        'failure_rates': {
            '7_days': rate_7d,
            '14_days': rate_14d,
            '30_days': rate_30d
        },
        'overall': {
            'total_failed': total_failed,
            'overall_failure_rate_pct': round(overall_failure_rate, 2),
            'unique_error_types': len(set(all_errors))
        },
        'ac3_compliance': rate_14d['failure_rate_pct'] < 1.0
    }
    
    return report

def main():
    """CLI interface for integrity monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor data integrity')
    parser.add_argument('file', help='Telemetry JSONL file to analyze')
    parser.add_argument('--days', type=int, default=14,
                       help='Days to analyze (default: 14)')
    parser.add_argument('--report', action='store_true',
                       help='Generate full report')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    if args.report:
        report = generate_integrity_report(args.file)
        print(json.dumps(report, indent=2))
    else:
        records = load_telemetry_records(args.file)
        result = calculate_integrity_failure_rate(records, args.days)
        
        if result['alert']:
            print(f"🚨 ALERT: Integrity failure rate too high")
            print(f"   Failure rate: {result['failure_rate_pct']}% (threshold: 1.0%)")
            print(f"   Failed records: {result['failed_records']}/{result['total_records']}")
            if result['errors']:
                print(f"   Sample errors:")
                for error in result['errors'][:3]:
                    print(f"     • {error}")
            exit(1)
        else:
            print(f"✅ Integrity check passed")
            print(f"   Failure rate: {result['failure_rate_pct']}% over {args.days} days")
            print(f"   Records: {result['failed_records']}/{result['total_records']} failed")
            exit(0)

if __name__ == '__main__':
    main()