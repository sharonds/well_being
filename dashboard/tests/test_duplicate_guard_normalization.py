#!/usr/bin/env python3
"""
Test duplicate guard with schema version normalization.
Ensures v1.0.0 and 2.0.0 formats are treated consistently.
"""

import json
import os
import sys
import tempfile
import unittest
from typing import Dict, List

# Add dashboard path for imports
dashboard_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, dashboard_path)

from scripts.duplicate_guard import (
    check_duplicate, 
    check_duplicate_in_records, 
    filter_duplicates,
    validate_no_duplicates,
    load_existing_records
)
from utils.schema_utils import normalize_schema_version


class TestDuplicateGuardNormalization(unittest.TestCase):
    """Test duplicate guard handles schema version format differences."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_data.jsonl')
    
    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_schema_version_normalization(self):
        """Test that different version formats are normalized correctly."""
        test_cases = [
            ("v1.0.0", "1.0.0"),
            ("2.0.0", "2.0.0"),
            ("v3", "3.0.0"),
            ("1.0", "1.0.0"),
            ("V2.1.5", "2.1.5"),
            (None, "0.0.0"),
            ("invalid", "0.0.0")
        ]
        
        for input_version, expected in test_cases:
            with self.subTest(version=input_version):
                result = normalize_schema_version(input_version)
                self.assertEqual(result, expected, 
                    f"normalize_schema_version({input_version!r}) should return {expected!r}")
    
    def test_duplicate_detection_with_v_prefix(self):
        """Test that v1.0.0 and 1.0.0 are detected as duplicates."""
        # Create file with v1.0.0 format
        records_v1 = [
            {"date": "2025-08-13", "schema_version": "v1.0.0", "score": 50},
            {"date": "2025-08-14", "schema_version": "v1.0.0", "score": 55},
        ]
        
        with open(self.test_file, 'w') as f:
            for record in records_v1:
                f.write(json.dumps(record) + '\n')
        
        # Load existing records
        existing = load_existing_records(self.test_file)
        
        # Check that records without 'v' prefix are detected as duplicates
        duplicate_record = {"date": "2025-08-13", "schema_version": "1.0.0", "score": 50}
        is_dup = check_duplicate(duplicate_record, existing)
        self.assertTrue(is_dup, "Should detect v1.0.0 and 1.0.0 as duplicates")
        
        # Check that different date is not a duplicate
        new_record = {"date": "2025-08-15", "schema_version": "1.0.0", "score": 60}
        is_dup = check_duplicate(new_record, existing)
        self.assertFalse(is_dup, "Different date should not be a duplicate")
    
    def test_mixed_version_formats_in_same_file(self):
        """Test handling of mixed version formats in the same file."""
        # Create file with mixed formats
        records = [
            {"date": "2025-08-13", "schema_version": "v1.0.0", "score": 50},
            {"date": "2025-08-13", "schema_version": "1.0.0", "score": 50},  # Duplicate!
            {"date": "2025-08-14", "schema_version": "v2.0.0", "score": 55},
            {"date": "2025-08-14", "schema_version": "2.0.0", "score": 55},  # Duplicate!
            {"date": "2025-08-15", "schema_version": "v1.0.0", "score": 60},
        ]
        
        with open(self.test_file, 'w') as f:
            for record in records:
                f.write(json.dumps(record) + '\n')
        
        # Validate should detect duplicates
        has_no_dups = validate_no_duplicates(self.test_file)
        self.assertFalse(has_no_dups, "Should detect duplicates with mixed version formats")
    
    def test_filter_duplicates_with_normalization(self):
        """Test that filter_duplicates properly normalizes versions."""
        # Create initial file
        existing_records = [
            {"date": "2025-08-13", "schema_version": "v1.0.0", "score": 50},
            {"date": "2025-08-14", "schema_version": "v2.0.0", "score": 55},
        ]
        
        with open(self.test_file, 'w') as f:
            for record in existing_records:
                f.write(json.dumps(record) + '\n')
        
        # Try to add records with different format
        new_records = [
            {"date": "2025-08-13", "schema_version": "1.0.0", "score": 50},  # Duplicate
            {"date": "2025-08-14", "schema_version": "2.0.0", "score": 55},  # Duplicate
            {"date": "2025-08-15", "schema_version": "1.0.0", "score": 60},  # New
        ]
        
        filtered = filter_duplicates(new_records, self.test_file)
        
        # Should only include the truly new record
        self.assertEqual(len(filtered), 1, "Should filter out normalized duplicates")
        self.assertEqual(filtered[0]["date"], "2025-08-15", "Should keep only new record")
    
    def test_version_transition_safety(self):
        """Test that version transitions (v1 -> v2) work correctly."""
        # Simulate migration from v1.0.0 to v2.0.0
        records = []
        
        # Day 1-3: v1.0.0 format
        for day in range(13, 16):
            records.append({
                "date": f"2025-08-{day:02d}",
                "schema_version": "v1.0.0",
                "score": 50 + day
            })
        
        # Day 4-6: Transition to 2.0.0 (no v prefix)
        for day in range(16, 19):
            records.append({
                "date": f"2025-08-{day:02d}",
                "schema_version": "2.0.0",
                "score": 50 + day
            })
        
        with open(self.test_file, 'w') as f:
            for record in records:
                f.write(json.dumps(record) + '\n')
        
        # Verify no duplicates
        has_no_dups = validate_no_duplicates(self.test_file)
        self.assertTrue(has_no_dups, "Version transition should not create duplicates")
        
        # Try to add duplicate with different version format
        duplicate_attempt = {
            "date": "2025-08-13",
            "schema_version": "1.0.0",  # Without 'v' prefix
            "score": 63
        }
        
        existing = load_existing_records(self.test_file)
        is_dup = check_duplicate(duplicate_attempt, existing)
        self.assertTrue(is_dup, "Should detect duplicate despite version format difference")
    
    def test_batch_duplicate_detection(self):
        """Test duplicate detection within a batch of new records."""
        new_records = [
            {"date": "2025-08-13", "schema_version": "v1.0.0", "score": 50},
            {"date": "2025-08-13", "schema_version": "1.0.0", "score": 50},  # Dup in batch
            {"date": "2025-08-14", "schema_version": "v1.0.0", "score": 55},
            {"date": "2025-08-14", "schema_version": "V1.0.0", "score": 55},  # Dup in batch
        ]
        
        # Filter should catch duplicates within the batch itself
        filtered = filter_duplicates(new_records, self.test_file)
        
        self.assertEqual(len(filtered), 2, "Should filter duplicates within batch")
        unique_dates = {r["date"] for r in filtered}
        self.assertEqual(unique_dates, {"2025-08-13", "2025-08-14"}, 
                        "Should keep one record per date")
    
    def test_edge_cases(self):
        """Test edge cases in version normalization."""
        edge_cases = [
            {"date": "2025-08-13", "schema_version": None, "score": 50},
            {"date": "2025-08-14", "schema_version": "", "score": 55},
            {"date": "2025-08-15", "schema_version": "vvv1.0.0", "score": 60},
            {"date": "2025-08-16", "schema_version": "1.0.0.0", "score": 65},
        ]
        
        with open(self.test_file, 'w') as f:
            for record in edge_cases:
                f.write(json.dumps(record) + '\n')
        
        # Should handle edge cases without crashing
        try:
            has_no_dups = validate_no_duplicates(self.test_file)
            # We don't care about the result, just that it doesn't crash
            self.assertIsInstance(has_no_dups, bool, "Should return boolean")
        except Exception as e:
            self.fail(f"Should handle edge cases without crashing: {e}")


if __name__ == '__main__':
    unittest.main()