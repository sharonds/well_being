#!/usr/bin/env python3
"""
Fix integrity issues by recalculating scores and bands using the unified engine.
This will correct any historical data that was calculated with different formulas.
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple

# Add dashboard to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from score.engine import compute_score, MetricInputs, ScoreFlags


def recalculate_record(record: Dict) -> Tuple[Dict, bool]:
    """
    Recalculate score and band for a record using the unified engine.
    
    Returns:
        Tuple of (updated_record, was_changed)
    """
    metrics = record['metrics']
    
    # Convert to engine format
    inputs = MetricInputs(
        steps=metrics.get('steps'),
        rhr=metrics.get('restingHeartRate'),
        sleep_hours=metrics.get('sleepHours'),
        stress=metrics.get('stress')
    )
    
    # Use flags based on metric availability
    flags = ScoreFlags(
        enable_sleep=metrics.get('sleepHours') is not None,
        enable_stress=metrics.get('stress') is not None
    )
    
    # Compute score using unified engine
    result = compute_score(inputs, flags)
    
    # Check if update needed
    was_changed = False
    updated_record = record.copy()
    
    if record.get('score') != result.score:
        print(f"  Score correction for {record['date']}: {record.get('score')} -> {result.score}")
        updated_record['score'] = result.score
        was_changed = True
    
    if record.get('band') != result.band:
        print(f"  Band correction for {record['date']}: '{record.get('band')}' -> '{result.band}'")
        updated_record['band'] = result.band
        was_changed = True
    
    return updated_record, was_changed


def fix_integrity_issues(input_file: str, output_file: str = None) -> Dict:
    """
    Fix integrity issues in wellness data by recalculating all scores.
    
    Args:
        input_file: Path to input JSONL file
        output_file: Optional output file (defaults to overwriting input)
        
    Returns:
        Dictionary with statistics
    """
    if output_file is None:
        output_file = input_file
    
    print(f"🔧 Fixing integrity issues in {input_file}")
    
    # Read all records
    records = []
    with open(input_file, 'r') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    # Process each record
    updated_records = []
    changes_made = 0
    score_fixes = 0
    band_fixes = 0
    
    for record in records:
        updated, was_changed = recalculate_record(record)
        updated_records.append(updated)
        
        if was_changed:
            changes_made += 1
            if record.get('score') != updated['score']:
                score_fixes += 1
            if record.get('band') != updated['band']:
                band_fixes += 1
    
    # Write back if changes were made
    if changes_made > 0:
        print(f"\n✏️ Writing {len(updated_records)} corrected records to {output_file}")
        # Write records back to file
        with open(output_file, 'w') as f:
            for record in updated_records:
                f.write(json.dumps(record) + '\n')
        print(f"✅ Fixed {changes_made} records ({score_fixes} scores, {band_fixes} bands)")
    else:
        print("✅ No corrections needed - all records are valid")
    
    return {
        'total_records': len(records),
        'changes_made': changes_made,
        'score_fixes': score_fixes,
        'band_fixes': band_fixes
    }


def verify_integrity(file_path: str) -> Tuple[int, List[str]]:
    """
    Verify integrity after fixes.
    
    Returns:
        Tuple of (failure_count, error_messages)
    """
    failures = 0
    errors = []
    
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                
                # Recalculate
                metrics = record['metrics']
                inputs = MetricInputs(
                    steps=metrics.get('steps'),
                    rhr=metrics.get('restingHeartRate'),
                    sleep_hours=metrics.get('sleepHours'),
                    stress=metrics.get('stress')
                )
                flags = ScoreFlags(
                    enable_sleep=metrics.get('sleepHours') is not None,
                    enable_stress=metrics.get('stress') is not None
                )
                result = compute_score(inputs, flags)
                
                # Check for mismatches
                if record['score'] != result.score or record['band'] != result.band:
                    failures += 1
                    errors.append(f"Date {record['date']}: score={record['score']} vs {result.score}, "
                                f"band='{record['band']}' vs '{result.band}'")
    
    return failures, errors


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix integrity issues in wellness data')
    parser.add_argument('input_file', help='Input JSONL file to fix')
    parser.add_argument('--output', '-o', help='Output file (default: overwrite input)')
    parser.add_argument('--verify-only', action='store_true', help='Only verify, do not fix')
    
    args = parser.parse_args()
    
    if args.verify_only:
        print(f"🔍 Verifying integrity of {args.input_file}")
        failures, errors = verify_integrity(args.input_file)
        
        if failures == 0:
            print("✅ All records pass integrity check")
            return 0
        else:
            print(f"❌ {failures} integrity failures found:")
            for error in errors[:5]:  # Show first 5
                print(f"  • {error}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more")
            return 1
    
    # Fix integrity issues
    stats = fix_integrity_issues(args.input_file, args.output)
    
    # Verify after fix
    print(f"\n🔍 Verifying integrity after fixes...")
    failures, errors = verify_integrity(args.output or args.input_file)
    
    if failures == 0:
        print("✅ All records now pass integrity check!")
        return 0
    else:
        print(f"⚠️ {failures} records still failing after fix")
        for error in errors[:3]:
            print(f"  • {error}")
        return 1


if __name__ == '__main__':
    sys.exit(main())