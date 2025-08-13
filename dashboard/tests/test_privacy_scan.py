#!/usr/bin/env python3
"""
Test suite for telemetry privacy scanning.
"""

import json
import os
import tempfile
import unittest

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.privacy_scan import (
    scan_record_for_violations,
    scan_telemetry_file,
    generate_clean_telemetry_record
)

class TestPrivacyScan(unittest.TestCase):
    
    def setUp(self):
        """Create temporary files for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'telemetry.jsonl')
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_clean_telemetry_passes(self):
        """Test that clean telemetry records pass privacy scan."""
        record = generate_clean_telemetry_record(
            "2025-08-13", 65, "Maintain", 75.0, True
        )
        violations = scan_record_for_violations(record)
        self.assertEqual(len(violations), 0)
    
    def test_detect_raw_metrics_object(self):
        """Test detection of raw metrics object."""
        record = {
            "date": "2025-08-13",
            "score": 65,
            "metrics": {  # This should be flagged
                "steps": 8000,
                "restingHeartRate": 55
            }
        }
        violations = scan_record_for_violations(record)
        self.assertTrue(any("Raw 'metrics' object" in v for v in violations))
    
    def test_detect_large_numbers(self):
        """Test detection of large numbers that might be raw steps."""
        record = {
            "date": "2025-08-13",
            "score": 65,
            "band": "Maintain",
            "steps_value": 12345,  # Should be flagged
            "metrics_mask": 15
        }
        violations = scan_record_for_violations(record)
        self.assertTrue(any("Large number" in v for v in violations))
        self.assertTrue(any("Unexpected numeric field 'steps_value'" in v for v in violations))
    
    def test_detect_email_address(self):
        """Test detection of email addresses (PII)."""
        record = {
            "date": "2025-08-13",
            "score": 65,
            "user": "test@example.com",  # Should be flagged
            "metrics_mask": 15
        }
        violations = scan_record_for_violations(record)
        self.assertTrue(any("Email address detected" in v for v in violations))
    
    def test_detect_raw_health_metrics(self):
        """Test detection of various raw health metrics."""
        bad_records = [
            {"date": "2025-08-13", "steps": 8000},
            {"date": "2025-08-13", "restingHeartRate": 55},
            {"date": "2025-08-13", "sleepHours": 7.5},
            {"date": "2025-08-13", "stress": 40},
            {"date": "2025-08-13", "calories": 2000},
            {"date": "2025-08-13", "weight": 70.5},
        ]
        
        for record in bad_records:
            violations = scan_record_for_violations(record)
            self.assertTrue(len(violations) > 0, f"Failed to detect violation in {record}")
    
    def test_validate_numeric_ranges(self):
        """Test validation of allowed numeric field ranges."""
        # Score out of range
        record = {
            "date": "2025-08-13",
            "score": 150,  # Should be flagged (>100)
            "metrics_mask": 15,
            "auto_run": 1
        }
        violations = scan_record_for_violations(record)
        self.assertTrue(any("outside allowed range" in v for v in violations))
        
        # Auto_run out of range
        record = {
            "date": "2025-08-13",
            "score": 65,
            "metrics_mask": 15,
            "auto_run": 2  # Should be flagged (not 0 or 1)
        }
        violations = scan_record_for_violations(record)
        self.assertTrue(any("auto_run" in v and "outside allowed range" in v for v in violations))
    
    def test_missing_metrics_mask(self):
        """Test detection of missing metrics_mask/presence_mask."""
        record = {
            "date": "2025-08-13",
            "score": 65,
            "band": "Maintain"
            # Missing metrics_mask
        }
        violations = scan_record_for_violations(record)
        self.assertTrue(any("Missing metrics_mask" in v for v in violations))
    
    def test_file_scanning(self):
        """Test scanning of entire telemetry file."""
        # Write mix of clean and violating records
        records = [
            generate_clean_telemetry_record("2025-08-01", 65, "Maintain"),
            {"date": "2025-08-02", "score": 70, "steps": 10000},  # Violation
            generate_clean_telemetry_record("2025-08-03", 75, "Go for it"),
        ]
        
        with open(self.test_file, 'w') as f:
            for record in records:
                f.write(json.dumps(record) + '\n')
        
        is_clean, violations = scan_telemetry_file(self.test_file)
        self.assertFalse(is_clean)
        self.assertTrue(any("Line 2" in v for v in violations))
    
    def test_boundary_band_values(self):
        """Test that band boundaries are correctly enforced."""
        # Test score boundaries
        test_cases = [
            (0, True),    # Min valid
            (100, True),  # Max valid
            (-1, False),  # Below min
            (101, False), # Above max
        ]
        
        for score, should_pass in test_cases:
            record = {
                "date": "2025-08-13",
                "score": score,
                "band": "Maintain",
                "metrics_mask": 15,
                "auto_run": 0
            }
            violations = scan_record_for_violations(record)
            if should_pass:
                self.assertEqual(len(violations), 0, f"Score {score} should pass")
            else:
                self.assertTrue(len(violations) > 0, f"Score {score} should fail")

if __name__ == '__main__':
    unittest.main()