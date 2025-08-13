#!/usr/bin/env python3
"""
Automated integrity remediation for wellness data.
Auto-corrects band-only mismatches and quarantines non-deterministic errors.
"""

import json
import sys
import os
import shutil
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Add dashboard to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from score.engine import compute_score, MetricInputs, ScoreFlags
from config import Config
from utils.file_utils import atomic_write_jsonl


class IntegrityRemediator:
    """Automated remediation for integrity failures."""
    
    def __init__(self, file_path: str, quarantine_dir: str = None):
        """
        Initialize remediator.
        
        Args:
            file_path: Path to wellness JSONL file
            quarantine_dir: Directory for quarantined records (default: file_dir/quarantine)
        """
        self.file_path = file_path
        self.quarantine_dir = quarantine_dir or os.path.join(
            os.path.dirname(file_path), 'quarantine'
        )
        
        # Ensure quarantine directory exists if needed
        if Config.QUARANTINE_ENABLED:
            os.makedirs(self.quarantine_dir, exist_ok=True)
    
    def diagnose_record(self, record: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """
        Diagnose a record's integrity issue.
        
        Returns:
            Tuple of (is_fixable, error_type, corrected_record)
        """
        metrics = record.get('metrics', {})
        
        # Recalculate using engine
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
        
        try:
            result = compute_score(inputs, flags)
            
            # Check for mismatches
            score_mismatch = record.get('score') != result.score
            band_mismatch = record.get('band') != result.band
            
            if score_mismatch and band_mismatch:
                # Both wrong - likely formula drift
                corrected = record.copy()
                corrected['score'] = result.score
                corrected['band'] = result.band
                return True, 'formula_drift', corrected
            
            elif band_mismatch and not score_mismatch:
                # Band-only mismatch - boundary issue
                corrected = record.copy()
                corrected['band'] = result.band
                return True, 'band_boundary', corrected
            
            elif score_mismatch and not band_mismatch:
                # Score wrong but band correct - suspicious
                return False, 'score_inconsistency', None
            
            else:
                # No issues
                return True, 'valid', record
                
        except Exception as e:
            # Non-deterministic error
            return False, f'computation_error: {str(e)}', None
    
    def remediate(self, dry_run: bool = False) -> Dict:
        """
        Perform automated remediation.
        
        Args:
            dry_run: If True, only report what would be done
            
        Returns:
            Remediation report
        """
        print(f"🔧 {'[DRY RUN] ' if dry_run else ''}Starting integrity remediation for {self.file_path}")
        
        # Read all records
        records = []
        with open(self.file_path, 'r') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        
        # Categorize records
        fixed_records = []
        quarantined_records = []
        unchanged_records = []
        
        remediation_stats = {
            'formula_drift': 0,
            'band_boundary': 0,
            'score_inconsistency': 0,
            'computation_error': 0,
            'valid': 0
        }
        
        for record in records:
            is_fixable, error_type, corrected = self.diagnose_record(record)
            
            if error_type in remediation_stats:
                remediation_stats[error_type] += 1
            else:
                remediation_stats['computation_error'] += 1
            
            if error_type == 'valid':
                unchanged_records.append(record)
            elif is_fixable and corrected:
                fixed_records.append(corrected)
                print(f"  ✅ Fixed {error_type} for {record.get('date')}")
            else:
                quarantined_records.append(record)
                print(f"  🔒 Quarantining {record.get('date')} due to {error_type}")
        
        # Calculate new failure rate
        total_valid = len(unchanged_records) + len(fixed_records)
        total_records = len(records)
        new_failure_rate = ((total_records - total_valid) / total_records * 100) if total_records > 0 else 0
        
        # Apply remediation if not dry run
        if not dry_run:
            # Backup original
            backup_path = f"{self.file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(self.file_path, backup_path)
            print(f"📦 Backed up original to {backup_path}")
            
            # Write remediated records using atomic write
            valid_records = unchanged_records + fixed_records
            if not atomic_write_jsonl(valid_records, self.file_path):
                print(f"❌ Failed to write remediated records")
                return report
            
            # Quarantine bad records if enabled
            if Config.QUARANTINE_ENABLED and quarantined_records:
                quarantine_file = os.path.join(
                    self.quarantine_dir,
                    f"quarantine_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
                )
                if not atomic_write_jsonl(quarantined_records, quarantine_file):
                    print(f"⚠️ Failed to write quarantine file")
                print(f"🔒 Quarantined {len(quarantined_records)} records to {quarantine_file}")
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': dry_run,
            'file': self.file_path,
            'original_records': total_records,
            'remediation_stats': remediation_stats,
            'actions': {
                'fixed': len(fixed_records),
                'quarantined': len(quarantined_records),
                'unchanged': len(unchanged_records)
            },
            'integrity': {
                'original_failure_rate_pct': round(
                    (remediation_stats['formula_drift'] + 
                     remediation_stats['band_boundary'] + 
                     remediation_stats['score_inconsistency'] + 
                     remediation_stats['computation_error']) / total_records * 100, 2
                ) if total_records > 0 else 0,
                'new_failure_rate_pct': round(new_failure_rate, 2),
                'meets_threshold': new_failure_rate < Config.INTEGRITY_FAILURE_THRESHOLD_PCT
            }
        }
        
        return report
    
    def verify_post_remediation(self) -> Tuple[float, bool]:
        """
        Verify integrity after remediation.
        
        Returns:
            Tuple of (failure_rate_pct, meets_threshold)
        """
        failures = 0
        total = 0
        
        with open(self.file_path, 'r') as f:
            for line in f:
                if line.strip():
                    total += 1
                    record = json.loads(line)
                    is_fixable, error_type, _ = self.diagnose_record(record)
                    if error_type != 'valid':
                        failures += 1
        
        failure_rate = (failures / total * 100) if total > 0 else 0
        meets_threshold = failure_rate < Config.INTEGRITY_FAILURE_THRESHOLD_PCT
        
        return failure_rate, meets_threshold


def main():
    """CLI interface for automated remediation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-remediate integrity issues')
    parser.add_argument('file', help='Wellness JSONL file to remediate')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--quarantine-dir', help='Directory for quarantined records')
    parser.add_argument('--json', action='store_true',
                       help='Output report as JSON')
    
    args = parser.parse_args()
    
    # Create remediator
    remediator = IntegrityRemediator(args.file, args.quarantine_dir)
    
    # Perform remediation
    report = remediator.remediate(dry_run=args.dry_run)
    
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("\n📊 Remediation Report:")
        print(f"  Original records: {report['original_records']}")
        print(f"  Fixed: {report['actions']['fixed']}")
        print(f"  Quarantined: {report['actions']['quarantined']}")
        print(f"  Unchanged: {report['actions']['unchanged']}")
        print(f"\n  Original failure rate: {report['integrity']['original_failure_rate_pct']}%")
        print(f"  New failure rate: {report['integrity']['new_failure_rate_pct']}%")
        print(f"  Meets threshold (<{Config.INTEGRITY_FAILURE_THRESHOLD_PCT}%): "
              f"{'✅ Yes' if report['integrity']['meets_threshold'] else '❌ No'}")
    
    # Verify if not dry run
    if not args.dry_run:
        print("\n🔍 Verifying post-remediation integrity...")
        failure_rate, meets_threshold = remediator.verify_post_remediation()
        print(f"  Final failure rate: {failure_rate:.2f}%")
        print(f"  Status: {'✅ PASS' if meets_threshold else '❌ FAIL'}")
        
        return 0 if meets_threshold else 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())