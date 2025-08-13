#!/usr/bin/env python3
"""
AC7: Completeness delta monitoring.
Compare 7-day vs 30-day completeness averages and alert on regression.
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

def calculate_completeness_pct(record: Dict) -> float:
    """Calculate completeness percentage for a record.
    
    Based on metrics_mask or presence of metrics fields.
    """
    # If we have completeness_pct field, use it
    if 'completeness_pct' in record:
        return float(record['completeness_pct'])
    
    # Calculate from metrics_mask (4 bits for 4 metrics)
    if 'metrics_mask' in record:
        mask = int(record['metrics_mask'])
        present_count = bin(mask).count('1')
        return (present_count / 4) * 100.0
    
    # Fallback: check for presence of raw metrics
    metrics = record.get('metrics', {})
    if not metrics:
        return 0.0
    
    total_metrics = 4  # steps, resting HR, sleep, stress
    present_count = 0
    
    if metrics.get('steps', 0) > 0:
        present_count += 1
    if metrics.get('restingHeartRate', 0) > 0:
        present_count += 1
    if metrics.get('sleepHours', 0) > 0:
        present_count += 1
    if metrics.get('stress', 0) > 0:
        present_count += 1
    
    return (present_count / total_metrics) * 100.0

def filter_records_by_days(records: List[Dict], days: int) -> List[Dict]:
    """Filter records to last N days."""
    if not records:
        return []
    
    # Sort by date (most recent first)
    sorted_records = sorted(records, key=lambda r: r.get('date', ''), reverse=True)
    
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    return [r for r in sorted_records if r.get('date', '') >= cutoff_date]

def calculate_avg_completeness(records: List[Dict]) -> float:
    """Calculate average completeness percentage across records."""
    if not records:
        return 0.0
    
    completeness_values = [calculate_completeness_pct(r) for r in records]
    return sum(completeness_values) / len(completeness_values)

def check_completeness_regression(records: List[Dict], threshold_pct: float = 20.0) -> Dict:
    """Check for completeness regression.
    
    AC7: Alert if 7-day completeness drops >threshold% below 30-day baseline.
    
    Args:
        records: List of telemetry records
        threshold_pct: Alert threshold (default 20%)
    
    Returns:
        Dict with alert status and metrics
    """
    records_7d = filter_records_by_days(records, 7)
    records_30d = filter_records_by_days(records, 30)
    
    avg_7d = calculate_avg_completeness(records_7d)
    avg_30d = calculate_avg_completeness(records_30d)
    
    # Calculate percentage drop
    if avg_30d == 0:
        drop_pct = 0 if avg_7d == 0 else 100
    else:
        drop_pct = ((avg_30d - avg_7d) / avg_30d) * 100
    
    # Don't trigger alert if 7-day average is 0 (no recent data)
    # This prevents false alerts when there's simply no recent data
    alert_triggered = drop_pct > threshold_pct and avg_7d > 0
    
    result = {
        'alert': alert_triggered,
        'drop_percentage': round(drop_pct, 1),
        'avg_7d': round(avg_7d, 1),
        'avg_30d': round(avg_30d, 1),
        'threshold': threshold_pct,
        'records_7d_count': len(records_7d),
        'records_30d_count': len(records_30d)
    }
    
    if alert_triggered:
        logger.warning(f"COMPLETENESS_REGRESSION: 7d avg {avg_7d:.1f}% is {drop_pct:.1f}% below 30d avg {avg_30d:.1f}%")
    else:
        logger.info(f"Completeness check OK: 7d={avg_7d:.1f}%, 30d={avg_30d:.1f}%, drop={drop_pct:.1f}%")
    
    return result

def generate_completeness_report(file_path: str) -> Dict:
    """Generate completeness monitoring report."""
    records = load_telemetry_records(file_path)
    
    if not records:
        return {
            'error': 'No telemetry records found',
            'file_path': file_path
        }
    
    regression_check = check_completeness_regression(records)
    
    # Add additional metrics
    all_completeness = [calculate_completeness_pct(r) for r in records]
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_records': len(records),
        'regression_check': regression_check,
        'overall_stats': {
            'min_completeness': round(min(all_completeness, default=0), 1),
            'max_completeness': round(max(all_completeness, default=0), 1),
            'avg_completeness': round(sum(all_completeness) / len(all_completeness), 1) if all_completeness else 0
        }
    }
    
    return report

def main():
    """CLI interface for completeness monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor data completeness trends')
    parser.add_argument('file', help='Telemetry JSONL file to analyze')
    parser.add_argument('--threshold', type=float, default=20.0,
                       help='Alert threshold percentage (default: 20%)')
    parser.add_argument('--report', action='store_true',
                       help='Generate full report')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    if args.report:
        report = generate_completeness_report(args.file)
        print(json.dumps(report, indent=2))
    else:
        records = load_telemetry_records(args.file)
        result = check_completeness_regression(records, args.threshold)
        
        if result['alert']:
            print(f"🚨 ALERT: Completeness regression detected")
            print(f"   7-day average: {result['avg_7d']}%")
            print(f"   30-day average: {result['avg_30d']}%")
            print(f"   Drop: {result['drop_percentage']}% (threshold: {result['threshold']}%)")
            exit(1)
        else:
            print(f"✅ Completeness check passed")
            print(f"   7-day: {result['avg_7d']}%, 30-day: {result['avg_30d']}%")
            exit(0)

if __name__ == '__main__':
    main()