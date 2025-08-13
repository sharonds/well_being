#!/usr/bin/env python3
"""
CLI tool for testing Phase 5 Plan Engine functionality.
"""

import json
import sys
import os
from datetime import date, datetime

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dashboard.scripts.plan_engine import PlanEngine, generate_daily_plan
from dashboard.scripts.adherence_tracker import AdherenceTracker, log_daily_adherence
from dashboard.config import Config


def test_plan_generation():
    """Test plan generation with various scenarios."""
    print("\n🧪 Testing Plan Generation\n" + "=" * 40)
    
    engine = PlanEngine()
    
    # Test scenarios
    scenarios = [
        {
            'name': '✅ Normal Maintain Day',
            'inputs': {
                'band': 'Maintain',
                'score': 65,
                'rhr_delta_7d': 2,
                'sleep_hours': 7.5,
                'stress_daily': 45,
                'steps_trend_7d': 100
            }
        },
        {
            'name': '⚠️ Anomaly: High RHR',
            'inputs': {
                'band': 'Go for it',
                'score': 70,
                'rhr_delta_7d': 8,
                'sleep_hours': 7.0,
                'stress_daily': 50
            }
        },
        {
            'name': '⚠️ Anomaly: Poor Sleep',
            'inputs': {
                'band': 'Maintain',
                'score': 45,
                'rhr_delta_7d': 3,
                'sleep_hours': 5.5,
                'stress_daily': 60
            }
        },
        {
            'name': '🚀 Go For It Day',
            'inputs': {
                'band': 'Go for it',
                'score': 85,
                'rhr_delta_7d': -1,
                'sleep_hours': 8.5,
                'stress_daily': 30,
                'steps_trend_7d': 500
            }
        },
        {
            'name': '🛡️ Conservative (Missing Data)',
            'inputs': {
                'band': 'Maintain',
                'score': 50
                # Missing most metrics
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}")
        print("-" * 40)
        
        # Generate plan
        plan = engine.generate_plan(scenario['inputs'])
        plan_text = engine.generate_plan_text(plan, scenario['inputs'])
        
        # Display results
        print(f"📋 Plan: {plan_text}")
        print(f"   Type: {plan.plan_type}")
        print(f"   Minutes: {plan.minutes_range}")
        print(f"   Add-ons: {', '.join(plan.addons)}")
        if plan.triggers:
            print(f"   Triggers: {', '.join(plan.triggers)}")


def test_adherence_logging():
    """Test adherence tracking."""
    print("\n📊 Testing Adherence Tracking\n" + "=" * 40)
    
    tracker = AdherenceTracker()
    
    # Simulate logging adherence
    print("\nLogging sample adherence...")
    record = tracker.log_adherence(
        completed=['core', 'breath', 'meditation_am'],
        energy=7,
        planned=['core', 'breath', 'meditation_am', 'meditation_pm']
    )
    
    print(f"✅ Logged for {record.date}")
    print(f"   Completed: {', '.join(record.completed_tasks)}")
    print(f"   Energy: {record.energy_rating}/10")
    print(f"   Adherence: {record.adherence_pct}%")
    
    # Get stats
    stats = tracker.get_adherence_stats(7)
    print(f"\n📈 7-Day Stats:")
    print(f"   Average adherence: {stats['avg_adherence_pct']}%")
    print(f"   Average energy: {stats['avg_energy']}/10")
    print(f"   Days logged: {stats['days_logged']}/{stats['total_days']}")
    print(f"   Tier-1 completion: {stats['tier1_completion_pct']}%")


def generate_todays_plan():
    """Generate and display today's plan."""
    print("\n📅 Today's Plan\n" + "=" * 40)
    
    plan = generate_daily_plan()
    
    print(f"\nDate: {plan['date']}")
    print(f"Plan: {plan['plan_text']}")
    
    if plan.get('plan'):
        print(f"\nDetails:")
        print(f"  Type: {plan['plan']['plan_type']}")
        print(f"  Minutes: {plan['plan']['minutes_range']}")
        print(f"  Add-ons: {', '.join(plan['plan']['addons'])}")
        
        if plan['plan'].get('triggers'):
            print(f"  Triggers: {', '.join(plan['plan']['triggers'])}")
    
    print(f"\nInputs Summary:")
    for key, value in plan.get('inputs_summary', {}).items():
        print(f"  {key}: {value}")


def show_config():
    """Display current configuration."""
    print("\n⚙️ Configuration\n" + "=" * 40)
    
    print(f"\nPlan Engine Status: {'✅ ENABLED' if Config.ENABLE_PLAN_ENGINE else '❌ DISABLED'}")
    
    print(f"\nAnomaly Thresholds:")
    print(f"  RHR Delta: +{Config.ANOMALY_RHR_THRESHOLD} bpm")
    print(f"  Sleep Minimum: {Config.ANOMALY_SLEEP_MIN} hours")
    print(f"  Stress High: {Config.ANOMALY_STRESS_HIGH}")
    
    print(f"\nSleep Variance:")
    print(f"  Target: ±{Config.SLEEP_VARIANCE_TARGET} minutes")
    print(f"  Alert Threshold: {Config.SLEEP_VARIANCE_THRESHOLD} minutes")
    
    print(f"\nUI Features:")
    print(f"  Insight Card: {'✅' if Config.ENABLE_INSIGHT_CARD else '❌'}")
    print(f"  Coach Chip: {'✅' if Config.ENABLE_COACH_CHIP else '❌'}")


def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Phase 5 Plan Engine CLI")
        print("=" * 40)
        print("\nUsage:")
        print("  python test_plan_cli.py test     - Run test scenarios")
        print("  python test_plan_cli.py today    - Generate today's plan")
        print("  python test_plan_cli.py log      - Log adherence")
        print("  python test_plan_cli.py stats    - Show adherence stats")
        print("  python test_plan_cli.py config   - Show configuration")
        print("  python test_plan_cli.py all      - Run all tests")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == 'test':
        test_plan_generation()
    
    elif command == 'today':
        generate_todays_plan()
    
    elif command == 'log':
        # Log adherence with tasks from command line
        tasks = sys.argv[2:] if len(sys.argv) > 2 else ['core', 'breath']
        energy = 7  # Default
        
        # Check if last arg is a number (energy rating)
        if tasks and tasks[-1].isdigit():
            energy = int(tasks[-1])
            tasks = tasks[:-1]
        
        record = log_daily_adherence(tasks, energy)
        print(f"✅ Logged adherence: {record['adherence_pct']}%")
        print(f"   Tasks: {', '.join(record['completed_tasks'])}")
        if record.get('energy_rating'):
            print(f"   Energy: {record['energy_rating']}/10")
    
    elif command == 'stats':
        tracker = AdherenceTracker()
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        
        stats = tracker.get_adherence_stats(days)
        trend = tracker.get_energy_trend(14)
        
        print(f"\n📊 Adherence Stats ({days} days):")
        print(f"  Average adherence: {stats['avg_adherence_pct']}%")
        print(f"  Average energy: {stats['avg_energy']}/10")
        print(f"  Tier-1 completion: {stats['tier1_completion_pct']}%")
        print(f"  Days logged: {stats['days_logged']}/{stats['total_days']}")
        
        if trend:
            print(f"\n⚡ Energy Trend (14 days):")
            for date_str, energy in trend[-7:]:  # Show last 7
                bar = '█' * energy + '░' * (10 - energy)
                print(f"  {date_str}: [{bar}] {energy}/10")
    
    elif command == 'config':
        show_config()
    
    elif command == 'all':
        show_config()
        test_plan_generation()
        test_adherence_logging()
        generate_todays_plan()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()