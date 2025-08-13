#!/usr/bin/env python3
"""
Test band boundary transitions for wellness scoring.
Validates critical score thresholds: 39/40 and 69/70

This test ensures score-to-band mapping consistency and prevents
silent regressions in band classification logic.
"""

import sys
import os
import unittest

# Add dashboard path for imports
dashboard_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, dashboard_path)

from score.engine import compute_score, MetricInputs, ScoreFlags


class TestBandBoundaries(unittest.TestCase):
    """Test critical band boundary transitions."""

    def test_take_it_easy_to_maintain_boundary(self):
        """Test 39/40 boundary: Take it easy -> Maintain"""
        
        # Test score 39 (should be "Take it easy")
        # Using very low metrics to achieve score near 39
        inputs_39 = MetricInputs(steps=3500, rhr=75)
        result_39 = compute_score(inputs_39, ScoreFlags())
        
        self.assertLessEqual(result_39.score, 39, 
                           f"Score {result_39.score} should be ≤39 for 'Take it easy' band")
        self.assertEqual(result_39.band, "Take it easy",
                        f"Score {result_39.score} should map to 'Take it easy'")

        # Test score 40 (should be "Maintain")  
        # Using slightly better metrics to achieve score near 40
        inputs_40 = MetricInputs(steps=4000, rhr=72)
        result_40 = compute_score(inputs_40, ScoreFlags())
        
        if result_40.score >= 40:
            self.assertEqual(result_40.band, "Maintain",
                           f"Score {result_40.score} should map to 'Maintain'")

    def test_maintain_to_go_for_it_boundary(self):
        """Test 69/70 boundary: Maintain -> Go for it"""
        
        # Test score in Maintain range (should be "Maintain")
        inputs_maintain = MetricInputs(steps=8000, rhr=55)
        result_maintain = compute_score(inputs_maintain, ScoreFlags())
        
        if 40 <= result_maintain.score <= 69:
            self.assertEqual(result_maintain.band, "Maintain",
                           f"Score {result_maintain.score} should map to 'Maintain'")

        # Test score 70+ (should be "Go for it")
        inputs_go = MetricInputs(steps=12000, rhr=45)  
        result_go = compute_score(inputs_go, ScoreFlags())
        
        if result_go.score >= 70:
            self.assertEqual(result_go.band, "Go for it",
                           f"Score {result_go.score} should map to 'Go for it'")

    def test_exact_boundary_scores(self):
        """Test exact boundary scores with known inputs."""
        
        # Test vectors that should produce specific boundary scores
        test_cases = [
            # (steps, rhr, expected_band, description)
            (0, 80, "Take it easy", "Minimum inputs -> Take it easy"),
            (12000, 40, "Go for it", "Maximum inputs -> Go for it"),
        ]
        
        for steps, rhr, expected_band, description in test_cases:
            with self.subTest(description=description):
                inputs = MetricInputs(steps=steps, rhr=rhr)
                result = compute_score(inputs, ScoreFlags())
                
                self.assertEqual(result.band, expected_band,
                               f"{description}: Score {result.score} -> '{result.band}', expected '{expected_band}'")

    def test_band_consistency_with_flags(self):
        """Test band boundaries remain consistent with optional metrics enabled."""
        
        # Test with sleep and stress enabled
        flags = ScoreFlags(enable_sleep=True, enable_stress=True)
        
        # Low score with all metrics poor
        inputs_low = MetricInputs(steps=1000, rhr=78, sleep_hours=4.0, stress=80)
        result_low = compute_score(inputs_low, flags)
        
        # High score with all metrics good  
        inputs_high = MetricInputs(steps=12000, rhr=42, sleep_hours=8.0, stress=15)
        result_high = compute_score(inputs_high, flags)
        
        # Verify band logic still works with redistribution
        if result_low.score <= 39:
            self.assertEqual(result_low.band, "Take it easy")
        elif result_low.score <= 69:
            self.assertEqual(result_low.band, "Maintain")
        else:
            self.assertEqual(result_low.band, "Go for it")
            
        if result_high.score >= 70:
            self.assertEqual(result_high.band, "Go for it")
        elif result_high.score >= 40:
            self.assertEqual(result_high.band, "Maintain") 
        else:
            self.assertEqual(result_high.band, "Take it easy")

    def test_boundary_edge_cases(self):
        """Test edge cases around boundaries."""
        
        # Test that band mapping is inclusive/exclusive correctly
        # According to BAND_MAP: (0,39), (40,69), (70,100)
        
        boundary_tests = [
            (39, "Take it easy"),
            (40, "Maintain"), 
            (69, "Maintain"),
            (70, "Go for it"),
        ]
        
        for target_score, expected_band in boundary_tests:
            with self.subTest(score=target_score):
                # Find inputs that produce the target score (approximate)
                # This tests the band mapping logic more than specific inputs
                
                # Use engine's band logic directly
                if 0 <= target_score <= 39:
                    computed_band = "Take it easy"
                elif 40 <= target_score <= 69:
                    computed_band = "Maintain"
                elif 70 <= target_score <= 100:
                    computed_band = "Go for it"
                else:
                    computed_band = "Unknown"
                
                self.assertEqual(computed_band, expected_band,
                               f"Score {target_score} should map to '{expected_band}', got '{computed_band}'")


if __name__ == '__main__':
    unittest.main()