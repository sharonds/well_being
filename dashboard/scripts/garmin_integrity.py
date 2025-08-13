#!/usr/bin/env python3
"""
Garmin data integrity and observability module.
Privacy-first: No raw metrics exported, only presence masks and aggregates.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

# Schema version for migration safety
SCHEMA_VERSION = "2.0.0"

class DataIntegrity:
    """Handles data integrity, presence tracking, and telemetry."""
    
    @staticmethod
    def calculate_metrics_mask(record: Dict) -> int:
        """
        Calculate bitfield for metrics presence.
        Bit 0: steps present
        Bit 1: resting HR present  
        Bit 2: sleep present
        Bit 3: stress present
        """
        mask = 0
        metrics = record.get('metrics', {})
        
        if metrics.get('steps', 0) > 0:
            mask |= 1 << 0
        if metrics.get('restingHeartRate', 0) > 0:
            mask |= 1 << 1
        if metrics.get('sleepHours', 0) > 0:
            mask |= 1 << 2
        if metrics.get('stress', 0) > 0:
            mask |= 1 << 3
            
        return mask
    
    @staticmethod
    def create_telemetry_record(record: Dict, auto_run: bool = False) -> Dict:
        """
        Create privacy-preserving telemetry record.
        No raw metrics, only presence and aggregate score.
        """
        mask = DataIntegrity.calculate_metrics_mask(record)
        
        return {
            "date": record.get('date'),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "schema_version": SCHEMA_VERSION,
            "auto_run": 1 if auto_run else 0,
            "steps_present": 1 if (mask & 1) else 0,
            "rhr_present": 1 if (mask & 2) else 0,
            "sleep_present": 1 if (mask & 4) else 0,
            "stress_present": 1 if (mask & 8) else 0,
            "metrics_mask": mask,
            "score": record.get('score', 0),
            "band": record.get('band', 'Unknown'),
            "completeness_pct": bin(mask).count('1') * 25  # Each metric = 25%
        }
    
    @staticmethod
    def validate_score_invariants(record: Dict) -> Tuple[bool, str]:
        """
        Validate scoring invariants.
        Returns (is_valid, error_message)
        """
        score = record.get('score', 0)
        
        # Score bounds check
        if not 0 <= score <= 100:
            return False, f"Score {score} out of bounds [0,100]"
        
        # Band consistency check
        band = record.get('band', '')
        if score >= 80 and band != "Go for it":
            return False, f"Score {score} inconsistent with band {band}"
        elif 60 <= score < 80 and band != "Maintain":
            return False, f"Score {score} inconsistent with band {band}"
        elif score < 60 and band != "Take it easy":
            return False, f"Score {score} inconsistent with band {band}"
        
        # Metrics presence vs score check
        mask = DataIntegrity.calculate_metrics_mask(record)
        if mask == 0 and score > 0:
            return False, "No metrics present but score > 0"
            
        return True, "Valid"
    
    @staticmethod
    def handle_timezone_shift(fetch_time: datetime, last_run_utc: Optional[str]) -> bool:
        """
        Check if fetch should proceed considering timezone/DST.
        Prevents double-runs during timezone changes.
        """
        if not last_run_utc:
            return True
            
        last_run = datetime.fromisoformat(last_run_utc)
        hours_since_last = (fetch_time - last_run).total_seconds() / 3600
        
        # Minimum 20 hours between runs (handles DST)
        return hours_since_last >= 20
    
    @staticmethod
    def hash_formula() -> str:
        """
        Generate hash of scoring formula for drift detection.
        In real implementation, would hash the actual ScoreEngine.mc file.
        """
        formula_definition = """
        steps: 10k=25, 7.5k=20, 5k=15, 2.5k=10, else=5
        rhr: <50=25, <60=20, <70=15, <80=10, else=5
        sleep: 8h+=25, 7h=20, 6h=15, 5h=10, else=5
        stress: <=25=25, <=40=20, <=55=15, <=70=10, else=5
        """
        return hashlib.sha256(formula_definition.encode()).hexdigest()[:8]

class MigrationSafety:
    """Handle schema migrations safely."""
    
    @staticmethod
    def migrate_record(record: Dict, from_version: str, to_version: str) -> Dict:
        """
        Migrate record between schema versions.
        Preserves data integrity during upgrades.
        """
        if from_version == "1.0.0" and to_version == "2.0.0":
            # Add new fields with safe defaults
            if 'schema_version' not in record:
                record['schema_version'] = to_version
            if 'metrics_mask' not in record:
                record['metrics_mask'] = DataIntegrity.calculate_metrics_mask(record)
        
        return record
    
    @staticmethod
    def validate_migration(old_records: list, new_records: list) -> bool:
        """
        Validate that migration preserved essential data.
        """
        if len(old_records) != len(new_records):
            return False
            
        for old, new in zip(old_records, new_records):
            # Essential fields must be preserved
            if old.get('date') != new.get('date'):
                return False
            if old.get('score') != new.get('score'):
                return False
                
        return True

def run_integrity_checks(data_file: str) -> Dict:
    """
    Run comprehensive integrity checks on fetched data.
    Returns summary of checks.
    """
    results = {
        "total_records": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "completeness_avg": 0,
        "metrics_presence": {
            "steps": 0,
            "rhr": 0,
            "sleep": 0,
            "stress": 0
        },
        "formula_hash": DataIntegrity.hash_formula(),
        "schema_version": SCHEMA_VERSION,
        "errors": []
    }
    
    try:
        with open(data_file, 'r') as f:
            records = [json.loads(line) for line in f]
            
        results["total_records"] = len(records)
        completeness_sum = 0
        
        for record in records:
            # Validate invariants
            is_valid, error = DataIntegrity.validate_score_invariants(record)
            if is_valid:
                results["valid_records"] += 1
            else:
                results["invalid_records"] += 1
                results["errors"].append(f"{record.get('date')}: {error}")
            
            # Track metrics presence
            telemetry = DataIntegrity.create_telemetry_record(record)
            results["metrics_presence"]["steps"] += telemetry["steps_present"]
            results["metrics_presence"]["rhr"] += telemetry["rhr_present"]
            results["metrics_presence"]["sleep"] += telemetry["sleep_present"]
            results["metrics_presence"]["stress"] += telemetry["stress_present"]
            completeness_sum += telemetry["completeness_pct"]
        
        if records:
            results["completeness_avg"] = completeness_sum / len(records)
            
    except Exception as e:
        results["errors"].append(f"File processing error: {e}")
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python garmin_integrity.py <data_file.jsonl>")
        sys.exit(1)
    
    results = run_integrity_checks(sys.argv[1])
    
    print("\n📊 Data Integrity Report")
    print("=" * 40)
    print(f"Schema Version: {results['schema_version']}")
    print(f"Formula Hash: {results['formula_hash']}")
    print(f"Total Records: {results['total_records']}")
    print(f"Valid Records: {results['valid_records']}")
    print(f"Invalid Records: {results['invalid_records']}")
    print(f"Average Completeness: {results['completeness_avg']:.1f}%")
    print("\nMetrics Presence:")
    for metric, count in results['metrics_presence'].items():
        pct = (count / results['total_records'] * 100) if results['total_records'] > 0 else 0
        print(f"  {metric}: {count}/{results['total_records']} ({pct:.1f}%)")
    
    if results['errors']:
        print("\n⚠️ Errors Found:")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"  - {error}")
    
    sys.exit(0 if results['invalid_records'] == 0 else 1)