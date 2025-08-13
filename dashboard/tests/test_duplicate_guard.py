#!/usr/bin/env python3
"""
Test suite for duplicate ingestion guard.
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.duplicate_guard import (
    load_existing_records,
    check_duplicate,
    filter_duplicates,
    append_unique_records,
    validate_no_duplicates
)

class TestDuplicateGuard(unittest.TestCase):
    
    def setUp(self):
        """Create temporary files for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_data.jsonl')
        self.target_file = os.path.join(self.temp_dir, 'target_data.jsonl')
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_record(self, date: str, score: int = 65, schema_version: str = "v2.0.0"):
        """Create a test wellness record."""
        return {
            "date": date,
            "metrics": {
                "steps": 8000,
                "restingHeartRate": 55,
                "sleepHours": 7.5,
                "stress": 40
            },
            "score": score,
            "band": "Maintain",
            "schema_version": schema_version
        }
    
    def write_records(self, filepath: str, records: list):
        """Write records to a JSONL file."""
        with open(filepath, 'w') as f:
            for record in records:
                f.write(json.dumps(record) + '\n')
    
    def test_no_duplicates_in_clean_data(self):
        """Test that clean data passes validation."""
        records = [
            self.create_test_record("2025-08-01"),
            self.create_test_record("2025-08-02"),
            self.create_test_record("2025-08-03")
        ]
        self.write_records(self.test_file, records)
        
        self.assertTrue(validate_no_duplicates(self.test_file))
    
    def test_detect_duplicate_dates(self):
        """Test detection of duplicate dates with same schema."""
        records = [
            self.create_test_record("2025-08-01", 65),
            self.create_test_record("2025-08-02", 70),
            self.create_test_record("2025-08-01", 68),  # Duplicate date
        ]
        self.write_records(self.test_file, records)
        
        self.assertFalse(validate_no_duplicates(self.test_file))
    
    def test_allow_same_date_different_schema(self):
        """Test that same date with different schema versions is allowed."""
        records = [
            self.create_test_record("2025-08-01", 65, "v1.0.0"),
            self.create_test_record("2025-08-01", 68, "v2.0.0"),  # Same date, different schema
        ]
        self.write_records(self.test_file, records)
        
        self.assertTrue(validate_no_duplicates(self.test_file))
    
    def test_filter_duplicates_from_batch(self):
        """Test filtering duplicates when appending new records."""
        # Existing records
        existing = [
            self.create_test_record("2025-08-01"),
            self.create_test_record("2025-08-02"),
        ]
        self.write_records(self.target_file, existing)
        
        # New records with some duplicates
        new_records = [
            self.create_test_record("2025-08-02"),  # Duplicate
            self.create_test_record("2025-08-03"),  # New
            self.create_test_record("2025-08-01"),  # Duplicate
            self.create_test_record("2025-08-04"),  # New
        ]
        
        unique = filter_duplicates(new_records, self.target_file)
        
        self.assertEqual(len(unique), 2)
        self.assertEqual(unique[0]['date'], "2025-08-03")
        self.assertEqual(unique[1]['date'], "2025-08-04")
    
    def test_idempotent_double_fetch(self):
        """Test that running fetch twice produces no new records."""
        records = [
            self.create_test_record("2025-08-01"),
            self.create_test_record("2025-08-02"),
            self.create_test_record("2025-08-03"),
        ]
        
        # First write
        self.write_records(self.test_file, records)
        count1 = append_unique_records(self.test_file, self.target_file)
        self.assertEqual(count1, 3)
        
        # Second write (should be all duplicates)
        count2 = append_unique_records(self.test_file, self.target_file)
        self.assertEqual(count2, 0)
        
        # Verify target has no duplicates
        self.assertTrue(validate_no_duplicates(self.target_file))
    
    def test_check_duplicate_function(self):
        """Test the check_duplicate function."""
        existing = {
            ("2025-08-01", "v2.0.0"),
            ("2025-08-02", "v2.0.0"),
        }
        
        # Test duplicate
        record1 = self.create_test_record("2025-08-01")
        self.assertTrue(check_duplicate(record1, existing))
        
        # Test non-duplicate
        record2 = self.create_test_record("2025-08-03")
        self.assertFalse(check_duplicate(record2, existing))
        
        # Test different schema version
        record3 = self.create_test_record("2025-08-01", schema_version="v3.0.0")
        self.assertFalse(check_duplicate(record3, existing))
    
    def test_boundary_conditions(self):
        """Test edge cases and boundary conditions."""
        # Empty file
        open(self.test_file, 'w').close()  # Create empty file
        self.assertTrue(validate_no_duplicates(self.test_file))
        
        # Single record
        self.write_records(self.test_file, [self.create_test_record("2025-08-01")])
        self.assertTrue(validate_no_duplicates(self.test_file))
        
        # Missing date field
        bad_record = {"score": 65, "band": "Maintain"}
        self.write_records(self.test_file, [bad_record])
        self.assertTrue(validate_no_duplicates(self.test_file))  # Should pass as no date to duplicate
    
    def test_within_batch_duplicates(self):
        """Test that duplicates within a single batch are caught."""
        new_records = [
            self.create_test_record("2025-08-01"),
            self.create_test_record("2025-08-02"),
            self.create_test_record("2025-08-01"),  # Duplicate within batch
        ]
        
        # Empty target file
        unique = filter_duplicates(new_records, self.target_file)
        
        # Should only have 2 unique records
        self.assertEqual(len(unique), 2)
        dates = [r['date'] for r in unique]
        self.assertIn("2025-08-01", dates)
        self.assertIn("2025-08-02", dates)

if __name__ == '__main__':
    unittest.main()