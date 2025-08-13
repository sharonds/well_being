#!/usr/bin/env python3
"""
Test auto-run metric normalization to ensure it's calculated by distinct days.
Verifies that multiple records on the same day don't inflate the success rate.
"""

import unittest
import sys
import os

# Add dashboard path
dashboard_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, dashboard_path)

from scripts.phase3.auto_run_tracker import calculate_success_rate


class TestAutoRunNormalization(unittest.TestCase):
    """Test auto-run success rate calculation with day normalization."""
    
    def test_single_day_multiple_records(self):
        """Test that multiple records on same day count as one day."""
        # 3 records on same day, all auto-run
        records = [
            {'date': '2025-08-13', 'auto_run': 1},
            {'date': '2025-08-13', 'auto_run': 1},
            {'date': '2025-08-13', 'auto_run': 1},
        ]
        
        # Should be 100% (1 day with auto-run / 1 total day)
        rate = calculate_success_rate(records)
        self.assertEqual(rate, 100.0, "Multiple records on same day should count as one day")
    
    def test_mixed_days_with_duplicates(self):
        """Test mixed success with duplicate dates."""
        records = [
            # Day 1: Multiple auto-runs (should count as 1 successful day)
            {'date': '2025-08-11', 'auto_run': 1},
            {'date': '2025-08-11', 'auto_run': 1},
            # Day 2: Mixed (any auto-run makes the day successful)
            {'date': '2025-08-12', 'auto_run': 0},
            {'date': '2025-08-12', 'auto_run': 1},
            # Day 3: All manual (unsuccessful day)
            {'date': '2025-08-13', 'auto_run': 0},
            {'date': '2025-08-13', 'auto_run': 0},
        ]
        
        # 2 successful days out of 3 = 66.67%
        rate = calculate_success_rate(records)
        self.assertAlmostEqual(rate, 66.67, places=1, 
                              msg="Should be 2/3 days with auto-run")
    
    def test_all_manual_runs(self):
        """Test all manual runs should give 0% success."""
        records = [
            {'date': '2025-08-11', 'auto_run': 0},
            {'date': '2025-08-12', 'auto_run': 0},
            {'date': '2025-08-13', 'auto_run': 0},
        ]
        
        rate = calculate_success_rate(records)
        self.assertEqual(rate, 0.0, "All manual runs should give 0% success")
    
    def test_all_auto_runs(self):
        """Test all auto runs should give 100% success."""
        records = [
            {'date': '2025-08-11', 'auto_run': 1},
            {'date': '2025-08-12', 'auto_run': 1},
            {'date': '2025-08-13', 'auto_run': 1},
        ]
        
        rate = calculate_success_rate(records)
        self.assertEqual(rate, 100.0, "All auto runs should give 100% success")
    
    def test_empty_records(self):
        """Test empty records should give 0%."""
        rate = calculate_success_rate([])
        self.assertEqual(rate, 0.0, "Empty records should give 0%")
    
    def test_records_without_dates(self):
        """Test records without dates are ignored."""
        records = [
            {'auto_run': 1},  # No date
            {'date': '2025-08-13', 'auto_run': 1},
        ]
        
        # Only 1 valid record with date
        rate = calculate_success_rate(records)
        self.assertEqual(rate, 100.0, "Should only count records with dates")
    
    def test_distinct_day_counting(self):
        """Test that success rate is truly based on distinct days."""
        # Scenario: 7 days, but many more records
        records = []
        
        # Day 1-5: Auto-run (5 days)
        for day in range(7, 12):
            for _ in range(3):  # 3 records per day
                records.append({
                    'date': f'2025-08-{day:02d}',
                    'auto_run': 1
                })
        
        # Day 6-7: Manual (2 days)
        for day in range(12, 14):
            for _ in range(2):  # 2 records per day
                records.append({
                    'date': f'2025-08-{day:02d}',
                    'auto_run': 0
                })
        
        # Total: 5 auto days out of 7 = 71.43%
        rate = calculate_success_rate(records)
        self.assertAlmostEqual(rate, 71.43, places=1,
                              msg="Should be 5/7 days with auto-run regardless of record count")
    
    def test_real_world_scenario(self):
        """Test with realistic data similar to production."""
        # Simulating a week with varying patterns
        records = [
            # Monday: Morning auto-run
            {'date': '2025-08-05', 'auto_run': 1, 'time': '08:00'},
            # Tuesday: Manual check + auto-run
            {'date': '2025-08-06', 'auto_run': 0, 'time': '07:30'},
            {'date': '2025-08-06', 'auto_run': 1, 'time': '09:00'},
            # Wednesday: Auto-run only
            {'date': '2025-08-07', 'auto_run': 1, 'time': '08:30'},
            # Thursday: Multiple manual checks
            {'date': '2025-08-08', 'auto_run': 0, 'time': '10:00'},
            {'date': '2025-08-08', 'auto_run': 0, 'time': '14:00'},
            {'date': '2025-08-08', 'auto_run': 0, 'time': '18:00'},
            # Friday: Auto-run
            {'date': '2025-08-09', 'auto_run': 1, 'time': '08:00'},
            # Weekend: No runs
            # Monday: Auto-run
            {'date': '2025-08-12', 'auto_run': 1, 'time': '08:00'},
            # Tuesday: Manual only
            {'date': '2025-08-13', 'auto_run': 0, 'time': '09:00'},
        ]
        
        # Days with auto-run: 05, 06, 07, 09, 12 = 5 days
        # Total days: 05, 06, 07, 08, 09, 12, 13 = 7 days
        # Success rate: 5/7 = 71.43%
        rate = calculate_success_rate(records)
        self.assertAlmostEqual(rate, 71.43, places=1,
                              msg="Real-world scenario should calculate correctly")


if __name__ == '__main__':
    unittest.main()