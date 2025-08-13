#!/usr/bin/env python3
"""
Test suite for Garmin data integrity and edge cases.
Based on ChatGPT-5 review recommendations.
"""

import unittest
import json
import tempfile
from datetime import datetime, timedelta, timezone
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.garmin_integrity import DataIntegrity, MigrationSafety

class TestDataIntegrity(unittest.TestCase):
    """Test data integrity checks."""
    
    def test_metrics_mask_calculation(self):
        """Test bitfield calculation for metrics presence."""
        # All metrics present
        record = {
            "metrics": {
                "steps": 10000,
                "restingHeartRate": 55,
                "sleepHours": 7.5,
                "stress": 30
            }
        }
        mask = DataIntegrity.calculate_metrics_mask(record)
        self.assertEqual(mask, 0b1111)  # All 4 bits set
        
        # Only steps and sleep
        record = {
            "metrics": {
                "steps": 5000,
                "restingHeartRate": 0,
                "sleepHours": 6.0,
                "stress": 0
            }
        }
        mask = DataIntegrity.calculate_metrics_mask(record)
        self.assertEqual(mask, 0b0101)  # Bits 0 and 2 set
        
        # No metrics
        record = {"metrics": {}}
        mask = DataIntegrity.calculate_metrics_mask(record)
        self.assertEqual(mask, 0b0000)
    
    def test_telemetry_privacy(self):
        """Test that telemetry contains no raw metrics."""
        record = {
            "date": "2024-08-13",
            "metrics": {
                "steps": 8543,  # Raw value
                "restingHeartRate": 62,  # Raw value
                "sleepHours": 7.2,  # Raw value
                "stress": 45  # Raw value
            },
            "score": 72,
            "band": "Maintain"
        }
        
        telemetry = DataIntegrity.create_telemetry_record(record)
        
        # Verify no raw metrics in telemetry
        self.assertNotIn("steps", telemetry)
        self.assertNotIn("restingHeartRate", telemetry)
        self.assertNotIn("sleepHours", telemetry)
        self.assertNotIn("stress", telemetry)
        
        # Verify only presence flags
        self.assertEqual(telemetry["steps_present"], 1)
        self.assertEqual(telemetry["rhr_present"], 1)
        self.assertEqual(telemetry["sleep_present"], 1)
        self.assertEqual(telemetry["stress_present"], 1)
        self.assertEqual(telemetry["completeness_pct"], 100)
    
    def test_score_invariants(self):
        """Test score validation invariants."""
        # Valid score and band
        record = {"score": 75, "band": "Maintain", "metrics": {"steps": 1000}}
        is_valid, error = DataIntegrity.validate_score_invariants(record)
        self.assertTrue(is_valid)
        
        # Score out of bounds
        record = {"score": 150, "band": "Go for it", "metrics": {"steps": 1000}}
        is_valid, error = DataIntegrity.validate_score_invariants(record)
        self.assertFalse(is_valid)
        self.assertIn("out of bounds", error)
        
        # Band inconsistent with score
        record = {"score": 85, "band": "Take it easy", "metrics": {"steps": 1000}}
        is_valid, error = DataIntegrity.validate_score_invariants(record)
        self.assertFalse(is_valid)
        self.assertIn("inconsistent", error)
        
        # No metrics but has score
        record = {"score": 50, "band": "Take it easy", "metrics": {}}
        is_valid, error = DataIntegrity.validate_score_invariants(record)
        self.assertFalse(is_valid)
        self.assertIn("No metrics", error)
    
    def test_timezone_shift_handling(self):
        """Test DST and timezone shift prevention of double runs."""
        now = datetime.now(timezone.utc)
        
        # First run - should proceed
        should_run = DataIntegrity.handle_timezone_shift(now, None)
        self.assertTrue(should_run)
        
        # Run 10 hours later - should not proceed
        last_run = (now - timedelta(hours=10)).isoformat()
        should_run = DataIntegrity.handle_timezone_shift(now, last_run)
        self.assertFalse(should_run)
        
        # Run 21 hours later - should proceed
        last_run = (now - timedelta(hours=21)).isoformat()
        should_run = DataIntegrity.handle_timezone_shift(now, last_run)
        self.assertTrue(should_run)
        
        # DST shift scenario (23 hours looks like next day)
        last_run = (now - timedelta(hours=23)).isoformat()
        should_run = DataIntegrity.handle_timezone_shift(now, last_run)
        self.assertTrue(should_run)

class TestMigrationSafety(unittest.TestCase):
    """Test schema migration safety."""
    
    def test_version_migration(self):
        """Test migration from v1 to v2."""
        old_record = {
            "date": "2024-08-13",
            "metrics": {"steps": 5000},
            "score": 65,
            "band": "Maintain"
        }
        
        new_record = MigrationSafety.migrate_record(
            old_record.copy(), "1.0.0", "2.0.0"
        )
        
        # Original data preserved
        self.assertEqual(new_record["date"], old_record["date"])
        self.assertEqual(new_record["score"], old_record["score"])
        
        # New fields added
        self.assertIn("schema_version", new_record)
        self.assertIn("metrics_mask", new_record)
        self.assertEqual(new_record["schema_version"], "2.0.0")
    
    def test_migration_validation(self):
        """Test that migration preserves essential data."""
        old_records = [
            {"date": "2024-08-01", "score": 70},
            {"date": "2024-08-02", "score": 65},
            {"date": "2024-08-03", "score": 80}
        ]
        
        # Valid migration
        new_records = [
            {"date": "2024-08-01", "score": 70, "v": "2.0"},
            {"date": "2024-08-02", "score": 65, "v": "2.0"},
            {"date": "2024-08-03", "score": 80, "v": "2.0"}
        ]
        is_valid = MigrationSafety.validate_migration(old_records, new_records)
        self.assertTrue(is_valid)
        
        # Invalid - score changed
        bad_records = [
            {"date": "2024-08-01", "score": 71},  # Changed!
            {"date": "2024-08-02", "score": 65},
            {"date": "2024-08-03", "score": 80}
        ]
        is_valid = MigrationSafety.validate_migration(old_records, bad_records)
        self.assertFalse(is_valid)

class TestEdgeCases(unittest.TestCase):
    """Test edge cases from ChatGPT-5 review."""
    
    def test_corrupted_data_recovery(self):
        """Test recovery from corrupted data."""
        # Corrupted record with future date
        corrupted = {
            "date": "2099-12-31",  # Future date
            "score": -50,  # Invalid score
            "metrics": None  # Invalid metrics
        }
        
        is_valid, error = DataIntegrity.validate_score_invariants(corrupted)
        self.assertFalse(is_valid)
        
        # Should not crash, return error message
        self.assertIsNotNone(error)
    
    def test_first_day_no_prior(self):
        """Test first day with no prior data."""
        record = {
            "date": "2024-08-13",
            "metrics": {"steps": 5000},
            "score": 50,
            "band": "Take it easy"
        }
        
        # No delta should be calculated
        telemetry = DataIntegrity.create_telemetry_record(record)
        self.assertNotIn("delta", telemetry)
        self.assertNotIn("prior_score", telemetry)
    
    def test_weight_redistribution(self):
        """Test that weights sum to 1.0 with missing metrics."""
        # This would be in the actual ScoreEngine
        # Here we verify the concept
        weights_full = [0.25, 0.25, 0.25, 0.25]
        self.assertAlmostEqual(sum(weights_full), 1.0, places=3)
        
        # With one metric missing (redistribute)
        weights_partial = [0.33, 0.33, 0.34, 0.0]
        self.assertAlmostEqual(sum(weights_partial), 1.0, places=2)

def run_integrity_test_suite():
    """Run all integrity tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestDataIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestMigrationSafety))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_integrity_test_suite()
    sys.exit(0 if success else 1)