#!/usr/bin/env python3
"""
Test suite for PlanEngine - Phase 5A.

Tests anomaly detection, boundary conditions, and plan generation logic.
"""

import unittest
import sys
import os
from datetime import date

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dashboard.scripts.plan_engine import PlanEngine, PlanOutput


class TestPlanEngine(unittest.TestCase):
    """Test cases for PlanEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = PlanEngine({
            'ANOMALY_RHR_THRESHOLD': 7,
            'ANOMALY_SLEEP_MIN': 6.5,
            'ANOMALY_STRESS_HIGH': 80,
            'SLEEP_VARIANCE_THRESHOLD': 60
        })
    
    def test_normal_maintain_day(self):
        """Test normal day with stable metrics."""
        inputs = {
            'band': 'Maintain',
            'score': 65,
            'rhr_delta_7d': 2,
            'sleep_hours': 7.5,
            'stress_daily': 45,
            'steps_trend_7d': 100
        }
        
        plan = self.engine.generate_plan(inputs)
        
        self.assertEqual(plan.plan_type, 'maintain')
        self.assertEqual(plan.minutes_range, '45-60')
        self.assertIn('core', plan.addons)
        self.assertIn('breath', plan.addons)
        self.assertIsNone(plan.triggers)
    
    def test_anomaly_rhr_exactly_7(self):
        """Test RHR anomaly at exact threshold."""
        inputs = {
            'band': 'Maintain',
            'score': 55,
            'rhr_delta_7d': 7,  # Exact threshold
            'sleep_hours': 7.0,
            'stress_daily': 50
        }
        
        plan = self.engine.generate_plan(inputs)
        
        self.assertEqual(plan.plan_type, 'easy')
        self.assertEqual(plan.minutes_range, '20-40')
        self.assertIn('nsdr', plan.addons)
        self.assertIn('RHR +7', plan.why[0])
    
    def test_anomaly_rhr_above_threshold(self):
        """Test RHR anomaly above threshold."""
        inputs = {
            'band': 'Go for it',  # Should be overridden
            'score': 75,
            'rhr_delta_7d': 10,
            'sleep_hours': 8.0,
            'stress_daily': 40
        }
        
        plan = self.engine.generate_plan(inputs)
        
        self.assertEqual(plan.plan_type, 'easy')  # Anomaly overrides band
        self.assertIn('RHR +10', plan.why[0])
    
    def test_anomaly_sleep_below_threshold(self):
        """Test sleep anomaly below 6.5 hours."""
        inputs = {
            'band': 'Maintain',
            'score': 45,
            'rhr_delta_7d': 2,
            'sleep_hours': 6.0,  # Below threshold
            'stress_daily': 50
        }
        
        plan = self.engine.generate_plan(inputs)
        
        self.assertEqual(plan.plan_type, 'easy')
        self.assertIn('Sleep 6.0h', plan.why[0])
    
    def test_sleep_exactly_65_not_anomaly(self):
        """Test sleep at exactly 6.5 hours is not anomaly."""
        inputs = {
            'band': 'Maintain',
            'score': 60,
            'rhr_delta_7d': 2,
            'sleep_hours': 6.5,  # Exact boundary
            'stress_daily': 50
        }
        
        plan = self.engine.generate_plan(inputs)
        
        self.assertEqual(plan.plan_type, 'maintain')  # Not anomaly
        self.assertNotIn('Sleep', ' '.join(plan.why))
    
    def test_anomaly_high_stress(self):
        """Test stress anomaly above threshold."""
        inputs = {
            'band': 'Maintain',
            'score': 55,
            'rhr_delta_7d': 2,
            'sleep_hours': 7.5,
            'stress_daily': 85  # Above threshold
        }
        
        plan = self.engine.generate_plan(inputs)
        
        self.assertEqual(plan.plan_type, 'easy')
        self.assertIn('High stress', plan.why[0])
    
    def test_anomaly_sugar_and_hrv(self):
        """Test sugar flag with negative HRV delta."""
        inputs = {
            'band': 'Maintain',
            'score': 60,
            'rhr_delta_7d': 2,
            'sleep_hours': 7.5,
            'stress_daily': 50,
            'sugar_flag': True,
            'hrv_delta': -5
        }
        
        plan = self.engine.generate_plan(inputs)
        
        self.assertEqual(plan.plan_type, 'easy')
        self.assertIn('Sugar impact on HRV', ' '.join(plan.why))
    
    def test_multiple_anomalies(self):
        """Test multiple anomaly conditions."""
        inputs = {
            'band': 'Go for it',
            'score': 70,
            'rhr_delta_7d': 8,
            'sleep_hours': 5.5,
            'stress_daily': 90
        }
        
        plan = self.engine.generate_plan(inputs)
        
        self.assertEqual(plan.plan_type, 'easy')
        self.assertEqual(len(plan.why), 2)  # Limited to top 2
        # Should include highest priority anomalies
        reasons_text = ' '.join(plan.why)
        self.assertIn('RHR', reasons_text)
        self.assertIn('Sleep', reasons_text)
    
    def test_go_for_it_band_no_anomaly(self):
        """Test 'Go for it' band generates hard plan when no anomaly."""
        inputs = {
            'band': 'Go for it',
            'score': 85,
            'rhr_delta_7d': -1,
            'sleep_hours': 8.5,
            'stress_daily': 30
        }
        
        plan = self.engine.generate_plan(inputs)
        
        self.assertEqual(plan.plan_type, 'hard')
        self.assertEqual(plan.minutes_range, '50-70')
        self.assertIn('core', plan.addons)
    
    def test_take_it_easy_band(self):
        """Test 'Take it easy' band generates easy plan."""
        inputs = {
            'band': 'Take it easy',
            'score': 40,
            'rhr_delta_7d': 2,
            'sleep_hours': 7.5,
            'stress_daily': 50
        }
        
        plan = self.engine.generate_plan(inputs)
        
        self.assertEqual(plan.plan_type, 'easy')
        self.assertEqual(plan.minutes_range, '30-40')
        self.assertIn('Recovery day', plan.why[0])
    
    def test_steps_trending_down(self):
        """Test steps trending down adds walk addon."""
        inputs = {
            'band': 'Maintain',
            'score': 65,
            'rhr_delta_7d': 2,
            'sleep_hours': 7.5,
            'stress_daily': 45,
            'steps_trend_7d': -600  # Significant downward trend
        }
        
        plan = self.engine.generate_plan(inputs)
        
        self.assertIn('walk', plan.addons)
        self.assertTrue(any('Steps trending down' in reason for reason in plan.why))
    
    def test_sleep_variance_trigger(self):
        """Test high sleep variance triggers coach."""
        inputs = {
            'band': 'Maintain',
            'score': 65,
            'rhr_delta_7d': 2,
            'sleep_hours': 7.5,
            'stress_daily': 45,
            'sleep_var_14d': 75  # Above threshold
        }
        
        plan = self.engine.generate_plan(inputs)
        
        self.assertIsNotNone(plan.triggers)
        self.assertIn('coach', plan.triggers)
    
    def test_missing_optional_metrics(self):
        """Test plan generation with missing optional metrics."""
        inputs = {
            'band': 'Maintain',
            'score': 60
            # Missing: rhr_delta, sleep_hours, stress, etc.
        }
        
        plan = self.engine.generate_plan(inputs)
        
        # Should generate maintain plan with defaults
        self.assertEqual(plan.plan_type, 'maintain')
        self.assertIsNotNone(plan.minutes_range)
        self.assertIsNotNone(plan.addons)
    
    def test_conservative_plan(self):
        """Test conservative plan generation."""
        plan = self.engine.generate_conservative_plan("Test reason")
        
        self.assertEqual(plan.plan_type, 'easy')
        self.assertEqual(plan.minutes_range, '20-30')
        self.assertIn('breath', plan.addons)
        self.assertIn("Test reason", plan.why[0])
        self.assertIn("Conservative approach", plan.why[1])
    
    def test_plan_text_generation_easy(self):
        """Test text generation for easy plan."""
        plan = PlanOutput(
            plan_type='easy',
            minutes_range='30-40',
            addons=['breath', 'nsdr'],
            why=['RHR +7', 'Sleep 6.0h']
        )
        inputs = {'rhr_delta_7d': 7, 'sleep_hours': 6.0}
        
        text = self.engine.generate_plan_text(plan, inputs)
        
        self.assertIn("Easy 30-40m", text)
        self.assertIn("10m breathing", text)
        self.assertIn("NSDR", text)
        self.assertIn("Why: RHR +7, Sleep 6.0h", text)
    
    def test_plan_text_generation_hard(self):
        """Test text generation for hard plan."""
        plan = PlanOutput(
            plan_type='hard',
            minutes_range='50-70',
            addons=['core', 'breath'],
            why=['Strong metrics (score 85)']
        )
        inputs = {'score': 85}
        
        text = self.engine.generate_plan_text(plan, inputs)
        
        self.assertIn("Quality (≤+10%)", text)
        self.assertIn("warm-up + intervals", text)
        self.assertIn("Core 10m", text)
    
    def test_plan_output_serialization(self):
        """Test PlanOutput serialization to dict."""
        plan = PlanOutput(
            plan_type='maintain',
            minutes_range='45-60',
            addons=['core', 'breath'],
            why=['Stable metrics'],
            triggers=None
        )
        
        plan_dict = plan.to_dict()
        
        self.assertEqual(plan_dict['plan_type'], 'maintain')
        self.assertEqual(plan_dict['minutes_range'], '45-60')
        self.assertIn('core', plan_dict['addons'])
        self.assertNotIn('triggers', plan_dict)  # None values excluded
    
    def test_never_hard_on_anomaly(self):
        """Test that hard plans are never generated during anomaly."""
        # Test all anomaly conditions
        anomaly_inputs = [
            {'rhr_delta_7d': 7, 'band': 'Go for it'},
            {'sleep_hours': 6.0, 'band': 'Go for it'},
            {'stress_daily': 85, 'band': 'Go for it'},
            {'sugar_flag': True, 'hrv_delta': -5, 'band': 'Go for it'}
        ]
        
        for inputs in anomaly_inputs:
            # Add defaults
            inputs.update({
                'score': 80,
                'rhr_delta_7d': inputs.get('rhr_delta_7d', 0),
                'sleep_hours': inputs.get('sleep_hours', 8),
                'stress_daily': inputs.get('stress_daily', 40)
            })
            
            plan = self.engine.generate_plan(inputs)
            
            self.assertNotEqual(plan.plan_type, 'hard', 
                              f"Generated hard plan with anomaly inputs: {inputs}")
            self.assertEqual(plan.plan_type, 'easy')


if __name__ == '__main__':
    unittest.main()