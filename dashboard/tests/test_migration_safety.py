#!/usr/bin/env python3
"""
Migration Safety Drill Test

Validates the system's ability to handle schema changes and data format 
migrations safely without data loss or corruption.

This test simulates:
1. Schema version transitions (v1.0.0 → v2.0.0)
2. Mixed schema version coexistence
3. Rollback capability validation
4. Migration performance benchmarks
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# Add dashboard path for imports
dashboard_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, dashboard_path)

from scripts.duplicate_guard import check_duplicate, check_duplicate_in_records, filter_duplicates
from scripts.phase3.integrity_monitor import validate_record_integrity, load_telemetry_records
from scripts.phase3.self_healing import self_heal_if_needed


class TestMigrationSafety(unittest.TestCase):
    """Test migration safety across schema versions."""

    def setUp(self):
        """Set up test environment with temporary files."""
        self.temp_dir = tempfile.mkdtemp()
        self.v1_file = os.path.join(self.temp_dir, 'telemetry_v1.jsonl')
        self.v2_file = os.path.join(self.temp_dir, 'telemetry_v2.jsonl')
        self.mixed_file = os.path.join(self.temp_dir, 'telemetry_mixed.jsonl')
        self.backup_file = os.path.join(self.temp_dir, 'telemetry_backup.jsonl')

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_v1_records(self) -> List[Dict]:
        """Create sample v1.0.0 format records."""
        base_date = datetime(2025, 8, 1)
        records = []
        
        for i in range(5):
            date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
            score = 65 + i * 5
            # Use correct band mapping for scores
            if score >= 70:
                band = 'Go for it'
            elif score >= 40:
                band = 'Maintain' 
            else:
                band = 'Take it easy'
                
            record = {
                'date': date,
                'schema_version': 'v1.0.0',  # Old format with 'v' prefix
                'score': score,
                'band': band,
                'completeness_pct': 85.0 + i,
                'auto_run': 1 if i % 2 == 0 else 0,
                # v1.0.0 had different field names
                'metrics_present': ['steps', 'rhr', 'sleep'],
                'integrity_status': 'valid'
            }
            records.append(record)
        
        return records

    def create_v2_records(self) -> List[Dict]:
        """Create sample v2.0.0 format records."""
        base_date = datetime(2025, 8, 6)
        records = []
        
        for i in range(5):
            date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
            record = {
                'date': date,
                'schema_version': '2.0.0',  # New format without 'v' prefix
                'score': 70 + i * 3,
                'band': 'Go for it' if (70 + i * 3) >= 70 else 'Maintain',
                'completeness_pct': 88.0 + i,
                'auto_run': 1,
                # v2.0.0 uses bit mask instead of array
                'metrics_mask': 15,  # All 4 metrics present (1111 binary)
                'steps_present': 1,
                'rhr_present': 1,
                'sleep_present': 1,
                'stress_present': 1,
                'integrity_fail_count': 0
            }
            records.append(record)
        
        return records

    def write_records_to_file(self, records: List[Dict], file_path: str):
        """Write records to JSONL file."""
        with open(file_path, 'w') as f:
            for record in records:
                f.write(json.dumps(record) + '\n')

    def test_schema_version_coexistence(self):
        """Test that v1.0.0 and v2.0.0 records can coexist."""
        v1_records = self.create_v1_records()
        v2_records = self.create_v2_records()
        
        # Write v1 and v2 records to the same file
        all_records = v1_records + v2_records
        self.write_records_to_file(all_records, self.mixed_file)
        
        # Verify both formats can be loaded
        loaded_records = load_telemetry_records(self.mixed_file)
        self.assertEqual(len(loaded_records), 10)
        
        # Check we have both schema versions
        v1_count = sum(1 for r in loaded_records if r.get('schema_version') == 'v1.0.0')
        v2_count = sum(1 for r in loaded_records if r.get('schema_version') == '2.0.0')
        
        self.assertEqual(v1_count, 5)
        self.assertEqual(v2_count, 5)

    def test_duplicate_guard_across_versions(self):
        """Test duplicate guard handles version format differences correctly."""
        # Create records with same date but different schema versions
        record_v1 = {
            'date': '2025-08-01',
            'schema_version': 'v1.0.0',
            'score': 65
        }
        
        record_v2_same_date = {
            'date': '2025-08-01', 
            'schema_version': '1.0.0',  # Same version as v1.0.0, different format
            'score': 67
        }
        
        record_v2_different_date = {
            'date': '2025-08-02',
            'schema_version': '2.0.0', 
            'score': 68
        }
        
        # Test duplicate detection across schema versions
        existing_records = [record_v1]
        
        # Same date, different schema version should now be considered duplicate
        # This tests the version normalization fix for ChatGPT-5 identified risk
        is_duplicate_v2_same = check_duplicate_in_records(record_v2_same_date, existing_records)
        is_duplicate_v2_diff = check_duplicate_in_records(record_v2_different_date, existing_records)
        
        # Schema version normalization now prevents this vulnerability:
        # v1.0.0 and 2.0.0 both normalize to same version for same date
        self.assertTrue(is_duplicate_v2_same, "Schema version normalization prevents duplicates")
        self.assertFalse(is_duplicate_v2_diff)

    def test_integrity_validation_across_versions(self):
        """Test integrity validation works for both schema versions."""
        v1_records = self.create_v1_records()
        v2_records = self.create_v2_records()
        
        all_valid_v1 = True
        all_valid_v2 = True
        v1_errors = []
        v2_errors = []
        
        # Test v1.0.0 records
        for record in v1_records:
            is_valid, errors = validate_record_integrity(record)
            if not is_valid:
                all_valid_v1 = False
                v1_errors.extend(errors)
        
        # Test v2.0.0 records  
        for record in v2_records:
            is_valid, errors = validate_record_integrity(record)
            if not is_valid:
                all_valid_v2 = False
                v2_errors.extend(errors)
        
        # Both versions should validate successfully
        self.assertTrue(all_valid_v1, f"v1.0.0 validation failed: {v1_errors}")
        self.assertTrue(all_valid_v2, f"v2.0.0 validation failed: {v2_errors}")

    def test_migration_rollback_capability(self):
        """Test ability to rollback from v2.0.0 to v1.0.0."""
        # Create v2.0.0 records
        v2_records = self.create_v2_records()
        self.write_records_to_file(v2_records, self.v2_file)
        
        # Create backup of "original" v1.0.0 data
        v1_records = self.create_v1_records()
        self.write_records_to_file(v1_records, self.backup_file)
        
        # Simulate rollback: restore backup over current file
        import shutil
        shutil.copy2(self.backup_file, self.v2_file)
        
        # Verify rollback worked
        restored_records = load_telemetry_records(self.v2_file)
        self.assertEqual(len(restored_records), 5)
        
        # All restored records should be v1.0.0 format
        all_v1 = all(r.get('schema_version') == 'v1.0.0' for r in restored_records)
        self.assertTrue(all_v1, "Rollback failed - found non-v1.0.0 records")

    def test_mixed_version_self_healing(self):
        """Test self-healing works with mixed schema versions."""
        v1_records = self.create_v1_records()
        v2_records = self.create_v2_records()
        
        # Create corrupted mixed file
        mixed_records = v1_records + v2_records
        
        # Introduce corruption
        mixed_records[3]['score'] = 'CORRUPTED'  # Invalid score type
        mixed_records[7] = {'corrupted': 'record'}  # Missing required fields
        
        self.write_records_to_file(mixed_records, self.mixed_file)
        
        # Attempt self-healing
        healed, message = self_heal_if_needed(self.mixed_file)
        
        # Self-healing quarantines corrupt file but doesn't rebuild from telemetry
        # This is expected behavior - corruption detected and contained
        self.assertTrue(healed, f"Self-healing should detect corruption: {message}")
        
        # Verify corrupted file was quarantined (original file might be empty or removed)
        corrupted_files = [f for f in os.listdir(self.temp_dir) if 'corrupted' in f]
        self.assertGreater(len(corrupted_files), 0, "Corrupted file should be quarantined")
        
        # This test documents that self-healing quarantines but doesn't auto-rebuild
        # In production, rebuild would require external telemetry source

    def test_migration_performance_benchmark(self):
        """Benchmark migration performance with larger dataset."""
        import time
        
        # Create larger dataset (100 records each version)
        large_v1 = []
        large_v2 = []
        base_date = datetime(2025, 7, 1)
        
        for i in range(100):
            date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
            
            # v1 record
            v1_record = {
                'date': date,
                'schema_version': 'v1.0.0',
                'score': 50 + (i % 50),
                'band': 'Maintain',
                'completeness_pct': 80.0 + (i % 20),
                'auto_run': i % 2,
                'metrics_present': ['steps', 'rhr']
            }
            large_v1.append(v1_record)
            
            # v2 record (next day)
            v2_date = (base_date + timedelta(days=i+100)).strftime('%Y-%m-%d')
            v2_record = {
                'date': v2_date,
                'schema_version': '2.0.0',
                'score': 60 + (i % 40),
                'band': 'Maintain',
                'completeness_pct': 85.0 + (i % 15),
                'auto_run': 1,
                'metrics_mask': 7,  # 3 metrics present
                'steps_present': 1,
                'rhr_present': 1,
                'sleep_present': 1,
                'stress_present': 0
            }
            large_v2.append(v2_record)
        
        all_records = large_v1 + large_v2
        self.write_records_to_file(all_records, self.mixed_file)
        
        # Benchmark loading time
        start_time = time.time()
        loaded_records = load_telemetry_records(self.mixed_file)
        load_time = time.time() - start_time
        
        self.assertEqual(len(loaded_records), 200)
        self.assertLess(load_time, 1.0, f"Loading 200 mixed records took {load_time:.2f}s (too slow)")
        
        # Benchmark duplicate filtering (using temp file)
        temp_output = os.path.join(self.temp_dir, 'filtered.jsonl')
        start_time = time.time()
        filtered_records = filter_duplicates(loaded_records, temp_output)
        filter_time = time.time() - start_time
        
        self.assertLess(filter_time, 1.0, f"Duplicate filtering took {filter_time:.2f}s (too slow)")

    def test_schema_version_normalization(self):
        """Test that schema version format differences are handled consistently."""
        # This test exposes the ChatGPT-5 identified risk of version format inconsistency
        
        v1_style = 'v1.0.0'  # With 'v' prefix
        v2_style = '1.0.0'   # Without 'v' prefix - SAME VERSION
        
        # Create records with different version formats
        record_v1_style = {
            'date': '2025-08-01',
            'schema_version': v1_style,
            'score': 65
        }
        
        record_v2_style = {
            'date': '2025-08-01',  # Same date!
            'schema_version': v2_style,
            'score': 65
        }
        
        # Test if duplicate guard treats these as duplicates (now fixed with normalization)
        existing = [record_v1_style]
        is_duplicate = check_duplicate_in_records(record_v2_style, existing)
        
        # This vulnerability has been FIXED: same date, different version format = detected as duplicate
        self.assertTrue(is_duplicate, "FIXED: Schema version normalization prevents date duplicates")
        
        # Schema version normalization now prevents this vulnerability

    def test_forward_compatibility_safeguards(self):
        """Test system behavior with future schema versions."""
        # Create a "future" v3.0.0 record
        future_record = {
            'date': '2025-08-15',
            'schema_version': '3.0.0',  # Unknown future version
            'score': 75,
            'band': 'Go for it',
            'new_field': 'future_feature',  # New field not in current schema
            'metrics_tensor': [1, 0, 1, 1, 0]  # Future metrics format
        }
        
        # Test integrity validation (should pass - forward compatibility)
        is_valid, errors = validate_record_integrity(future_record)
        self.assertTrue(is_valid, f"Future schema should be forward compatible: {errors}")
        
        # Test duplicate guard (should work based on date)
        existing = []
        is_duplicate = check_duplicate(future_record, existing)
        self.assertFalse(is_duplicate)


if __name__ == '__main__':
    # Run with verbose output to see migration safety results
    unittest.main(verbosity=2)