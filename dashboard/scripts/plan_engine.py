#!/usr/bin/env python3
"""
Plan Engine - Deterministic daily training and recovery plan generation.

Phase 5A: Generates personalized daily plans based on wellness metrics,
with anomaly detection and conservative fallbacks for missing data.
"""

import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class PlanOutput:
    """Structure for plan engine output."""
    plan_type: str  # 'easy', 'maintain', 'hard'
    minutes_range: str  # e.g., "30-40", "45-60"
    addons: List[str]  # ['core', 'breath', 'nsdr', 'walk']
    why: List[str]  # Top 1-2 reasons/deltas
    triggers: List[str] = None  # ['coach', 'nudge']
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {k: v for k, v in asdict(self).items() if v is not None}


class PlanEngine:
    """Deterministic plan generation engine."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize with configuration."""
        self.config = config or {}
        
        # Anomaly thresholds
        self.anomaly_rhr_threshold = self.config.get('ANOMALY_RHR_THRESHOLD', 7)
        self.anomaly_sleep_min = self.config.get('ANOMALY_SLEEP_MIN', 6.5)
        self.anomaly_stress_threshold = self.config.get('ANOMALY_STRESS_HIGH', 80)
        
        # Sleep variance thresholds
        self.sleep_variance_target = self.config.get('SLEEP_VARIANCE_TARGET', 30)
        self.sleep_variance_threshold = self.config.get('SLEEP_VARIANCE_THRESHOLD', 60)
        
        # Baseline ranges (in minutes)
        self.baseline_minutes = {
            'easy': (20, 40),
            'maintain': (45, 60),
            'hard': (50, 70)
        }
    
    def generate_plan(self, inputs: Dict) -> PlanOutput:
        """
        Generate a daily plan based on wellness metrics.
        
        Args:
            inputs: Dictionary with metrics:
                - band: str (required)
                - score: int (required)
                - delta: int
                - rhr_delta_7d: float
                - sleep_hours: float
                - sleep_var_14d: float (minutes)
                - stress_midday: float
                - stress_daily: float
                - steps_trend_7d: float
                - hrv_delta: float (optional)
                - sugar_flag: bool (optional)
        
        Returns:
            PlanOutput with plan details
        """
        # Extract inputs with defaults
        band = inputs.get('band', 'Maintain')
        score = inputs.get('score', 50)
        delta = inputs.get('delta', 0)
        rhr_delta = inputs.get('rhr_delta_7d', 0)
        sleep_hours = inputs.get('sleep_hours', 7.5)
        sleep_var = inputs.get('sleep_var_14d', 30)
        stress = inputs.get('stress_midday') or inputs.get('stress_daily', 50)
        steps_trend = inputs.get('steps_trend_7d', 0)
        hrv_delta = inputs.get('hrv_delta')
        sugar_flag = inputs.get('sugar_flag', False)
        
        # Check for anomaly conditions
        is_anomaly, anomaly_reasons = self._check_anomaly(
            rhr_delta, sleep_hours, stress, hrv_delta, sugar_flag
        )
        
        # Determine plan type based on anomaly and band
        if is_anomaly:
            plan_type = 'easy'
            minutes_range = "20-40"
            addons = ['nsdr', 'breath']
            why = anomaly_reasons[:2]  # Top 2 reasons
        elif band == "Take it easy":
            plan_type = 'easy'
            minutes_range = "30-40"
            addons = ['breath']
            why = [f"Recovery day (score {score})"]
        elif band == "Go for it":
            plan_type = 'hard'
            minutes_range = "50-70"
            addons = ['core', 'breath']
            why = [f"Strong metrics (score {score})"]
        else:  # Maintain
            plan_type = 'maintain'
            minutes_range = "45-60"
            addons = ['core', 'breath']
            why = ["Stable sleep/RHR"]
        
        # Add walk if steps trending down
        if steps_trend < -500:  # Significant downward trend
            addons.append('walk')
            why.append(f"Steps trending down ({int(steps_trend)}/day)")
        
        # Check for triggers
        triggers = []
        if sleep_var > self.sleep_variance_threshold:
            triggers.append('coach')
        
        # Build output
        return PlanOutput(
            plan_type=plan_type,
            minutes_range=minutes_range,
            addons=addons,
            why=why[:2],  # Limit to top 2
            triggers=triggers if triggers else None
        )
    
    def _check_anomaly(self, rhr_delta: float, sleep_hours: float, 
                      stress: float, hrv_delta: Optional[float], 
                      sugar_flag: bool) -> Tuple[bool, List[str]]:
        """
        Check for anomaly conditions.
        
        Returns:
            Tuple of (is_anomaly, list of reasons)
        """
        anomaly_reasons = []
        
        # RHR anomaly
        if rhr_delta >= self.anomaly_rhr_threshold:
            anomaly_reasons.append(f"RHR +{rhr_delta:.0f}")
        
        # Sleep anomaly
        if sleep_hours < self.anomaly_sleep_min:
            anomaly_reasons.append(f"Sleep {sleep_hours:.1f}h")
        
        # Stress anomaly
        if stress > self.anomaly_stress_threshold:
            anomaly_reasons.append(f"High stress ({stress:.0f})")
        
        # Sugar + HRV anomaly
        if sugar_flag and hrv_delta is not None and hrv_delta < 0:
            anomaly_reasons.append("Sugar impact on HRV")
        
        is_anomaly = len(anomaly_reasons) > 0
        return is_anomaly, anomaly_reasons
    
    def generate_plan_text(self, plan: PlanOutput, inputs: Dict) -> str:
        """
        Generate human-readable plan text using copy templates.
        
        Args:
            plan: PlanOutput from generate_plan
            inputs: Original inputs for context
        
        Returns:
            Formatted plan text
        """
        # Base activity text
        if plan.plan_type == 'easy':
            base = f"Easy {plan.minutes_range}m"
        elif plan.plan_type == 'maintain':
            base = f"Steady {plan.minutes_range}m"
        else:  # hard
            base = "Quality (≤+10%): warm-up + intervals"
        
        # Add-ons text
        addon_map = {
            'core': 'Core 10m',
            'breath': '10m breathing',
            'nsdr': 'NSDR 10-20m',
            'walk': '20-30m walk'
        }
        addon_texts = [addon_map.get(a, a) for a in plan.addons[:2]]  # Max 2 addons
        
        # Combine
        if addon_texts:
            activity = f"{base} + {' + '.join(addon_texts)}"
        else:
            activity = base
        
        # Why text
        why_text = f"Why: {', '.join(plan.why)}" if plan.why else ""
        
        return f"{activity}. {why_text}".strip()
    
    def generate_conservative_plan(self, reason: str = "Using last known metrics") -> PlanOutput:
        """
        Generate a conservative plan when metrics are missing.
        
        Args:
            reason: Explanation for conservative plan
        
        Returns:
            Conservative PlanOutput
        """
        return PlanOutput(
            plan_type='easy',
            minutes_range="20-30",
            addons=['breath'],
            why=[reason, "Conservative approach"],
            triggers=None
        )


def generate_daily_plan(data_dir: str = "dashboard/data") -> Dict:
    """
    Generate today's plan if not already exists.
    
    Args:
        data_dir: Directory for data files
        
    Returns:
        Generated plan dictionary
    """
    import os
    import sys
    
    # Add parent directories to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    from dashboard.config import Config
    from dashboard.utils.file_utils import atomic_write_jsonl
    
    # Check if plan already exists for today
    today = date.today().isoformat()
    plan_file = os.path.join(data_dir, "plan_daily.jsonl")
    
    # Load existing plans
    existing_plans = []
    if os.path.exists(plan_file):
        with open(plan_file, 'r') as f:
            for line in f:
                try:
                    existing_plans.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    # Check if today's plan exists
    for plan in existing_plans:
        if plan.get('date') == today and not plan.get('recompute'):
            logger.info(f"Plan already exists for {today}")
            return plan
    
    # Load latest wellness data
    wellness_file = os.path.join(data_dir, "garmin_wellness.jsonl")
    latest_metrics = None
    
    if os.path.exists(wellness_file):
        with open(wellness_file, 'r') as f:
            lines = f.readlines()
            if lines:
                try:
                    # Get last 7 days for trend calculation
                    recent_records = []
                    for line in lines[-7:]:
                        recent_records.append(json.loads(line))
                    
                    if recent_records:
                        latest_metrics = recent_records[-1]
                        
                        # Calculate RHR delta (7-day)
                        if len(recent_records) >= 7:
                            rhr_values = [r.get('restingHeartRate', 0) for r in recent_records if r.get('restingHeartRate')]
                            if len(rhr_values) >= 2:
                                latest_metrics['rhr_delta_7d'] = rhr_values[-1] - sum(rhr_values[:-1]) / len(rhr_values[:-1])
                        
                        # Calculate steps trend
                        if len(recent_records) >= 7:
                            steps_values = [(i, r.get('steps', 0)) for i, r in enumerate(recent_records) if r.get('steps')]
                            if len(steps_values) >= 2:
                                # Simple linear regression for trend
                                n = len(steps_values)
                                sum_x = sum(x for x, _ in steps_values)
                                sum_y = sum(y for _, y in steps_values)
                                sum_xy = sum(x * y for x, y in steps_values)
                                sum_x2 = sum(x * x for x, _ in steps_values)
                                
                                if n * sum_x2 - sum_x * sum_x != 0:
                                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                                    latest_metrics['steps_trend_7d'] = slope
                
                except json.JSONDecodeError:
                    logger.error("Failed to parse wellness data")
    
    # Initialize plan engine
    engine = PlanEngine({
        'ANOMALY_RHR_THRESHOLD': getattr(Config, 'ANOMALY_RHR_THRESHOLD', 7),
        'ANOMALY_SLEEP_MIN': getattr(Config, 'ANOMALY_SLEEP_MIN', 6.5),
        'ANOMALY_STRESS_HIGH': getattr(Config, 'ANOMALY_STRESS_HIGH', 80),
        'SLEEP_VARIANCE_TARGET': getattr(Config, 'SLEEP_VARIANCE_TARGET', 30),
        'SLEEP_VARIANCE_THRESHOLD': getattr(Config, 'SLEEP_VARIANCE_THRESHOLD', 60)
    })
    
    # Generate plan
    if latest_metrics:
        # Map wellness data to plan inputs
        inputs = {
            'band': latest_metrics.get('band', 'Maintain'),
            'score': latest_metrics.get('score', 50),
            'delta': latest_metrics.get('score', 50) - 50,  # Delta from baseline
            'rhr_delta_7d': latest_metrics.get('rhr_delta_7d', 0),
            'sleep_hours': latest_metrics.get('sleepHours', 7.5),
            'stress_daily': latest_metrics.get('stressLevel', 50),
            'steps_trend_7d': latest_metrics.get('steps_trend_7d', 0)
        }
        
        plan = engine.generate_plan(inputs)
        plan_text = engine.generate_plan_text(plan, inputs)
    else:
        # Generate conservative plan
        plan = engine.generate_conservative_plan("No recent wellness data")
        plan_text = "Easy 20-30m + 10m breathing. Why: No recent wellness data, Conservative approach"
        inputs = {}
    
    # Create plan record
    plan_record = {
        'date': today,
        'created_at': datetime.now().isoformat(),
        'schema_version': 'v1.0.0',
        'plan': plan.to_dict(),
        'plan_text': plan_text,
        'inputs_summary': {
            'band': inputs.get('band', 'unknown'),
            'score': inputs.get('score', 0),
            'rhr_delta_7d': round(inputs.get('rhr_delta_7d', 0), 1),
            'sleep_hours': round(inputs.get('sleep_hours', 0), 1)
        }
    }
    
    # Append to plan file (atomic)
    existing_plans.append(plan_record)
    
    # Keep only last 90 days
    cutoff_date = (date.today() - timedelta(days=90)).isoformat()
    existing_plans = [p for p in existing_plans if p.get('date', '') >= cutoff_date]
    
    # Write atomically
    if not atomic_write_jsonl(existing_plans, plan_file):
        logger.error("Failed to write plan file")
        return plan_record
    
    logger.info(f"Generated plan for {today}: {plan_text}")
    return plan_record


if __name__ == "__main__":
    # CLI testing
    import sys
    
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Test mode with sample inputs
        engine = PlanEngine()
        
        # Test cases
        test_cases = [
            {
                'name': 'Normal day',
                'inputs': {
                    'band': 'Maintain',
                    'score': 65,
                    'rhr_delta_7d': 2,
                    'sleep_hours': 7.5,
                    'stress_daily': 45
                }
            },
            {
                'name': 'Anomaly - high RHR',
                'inputs': {
                    'band': 'Maintain',
                    'score': 55,
                    'rhr_delta_7d': 8,
                    'sleep_hours': 7.0,
                    'stress_daily': 50
                }
            },
            {
                'name': 'Anomaly - poor sleep',
                'inputs': {
                    'band': 'Take it easy',
                    'score': 40,
                    'rhr_delta_7d': 3,
                    'sleep_hours': 5.5,
                    'stress_daily': 60
                }
            },
            {
                'name': 'Go for it day',
                'inputs': {
                    'band': 'Go for it',
                    'score': 85,
                    'rhr_delta_7d': -1,
                    'sleep_hours': 8.5,
                    'stress_daily': 30
                }
            }
        ]
        
        for test in test_cases:
            print(f"\n{test['name']}:")
            print(f"  Inputs: {test['inputs']}")
            plan = engine.generate_plan(test['inputs'])
            plan_text = engine.generate_plan_text(plan, test['inputs'])
            print(f"  Plan: {plan_text}")
            print(f"  Details: {plan.to_dict()}")
    else:
        # Generate actual daily plan
        plan = generate_daily_plan()
        print(f"\n📋 Today's Plan ({plan['date']}):")
        print(f"  {plan['plan_text']}")
        if plan.get('plan', {}).get('triggers'):
            print(f"  ⚠️ Triggers: {', '.join(plan['plan']['triggers'])}")