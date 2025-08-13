#!/usr/bin/env python3
"""
Adherence Tracker - Track user feedback and plan completion.

Phase 5A: Logs daily adherence (what was done) and energy ratings.
"""

import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class AdherenceRecord:
    """Structure for adherence tracking."""
    date: str
    completed_tasks: List[str]  # ['core', 'meditation_am', 'breath']
    energy_rating: Optional[int]  # 1-10 scale
    plan_type: str  # 'easy', 'maintain', 'hard'
    adherence_pct: float  # Percentage of planned tasks completed
    logged_at: str
    schema_version: str = 'v1.0.0'
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class AdherenceTracker:
    """Track and analyze plan adherence."""
    
    def __init__(self, data_dir: str = "dashboard/data"):
        """Initialize tracker with data directory."""
        self.data_dir = data_dir
        self.adherence_file = f"{data_dir}/adherence_daily.jsonl"
    
    def log_adherence(self, completed: List[str], energy: Optional[int] = None,
                     planned: Optional[List[str]] = None) -> AdherenceRecord:
        """
        Log daily adherence and energy rating.
        
        Args:
            completed: List of completed tasks
            energy: Energy rating (1-10)
            planned: List of planned tasks (for calculating adherence %)
            
        Returns:
            AdherenceRecord that was logged
        """
        import os
        import sys
        
        # Add parent directories to path
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from dashboard.utils.file_utils import atomic_append
        
        today = date.today().isoformat()
        
        # Get today's plan for context
        plan_type = 'unknown'
        if planned is None:
            planned = self._get_todays_planned_tasks()
            
        # Get plan type from plan file
        plan_file = f"{self.data_dir}/plan_daily.jsonl"
        if os.path.exists(plan_file):
            with open(plan_file, 'r') as f:
                for line in f:
                    try:
                        plan = json.loads(line)
                        if plan.get('date') == today:
                            plan_type = plan.get('plan', {}).get('plan_type', 'unknown')
                            if planned is None:
                                # Extract planned tasks from plan
                                planned = plan.get('plan', {}).get('addons', [])
                                # Add tier-1 tasks
                                planned.extend(['core', 'meditation_am', 'meditation_pm', 'breath'])
                            break
                    except json.JSONDecodeError:
                        continue
        
        # Calculate adherence percentage
        if planned:
            completed_set = set(completed)
            planned_set = set(planned)
            adherence_pct = len(completed_set & planned_set) / len(planned_set) * 100
        else:
            adherence_pct = 0
        
        # Create record
        record = AdherenceRecord(
            date=today,
            completed_tasks=completed,
            energy_rating=energy,
            plan_type=plan_type,
            adherence_pct=round(adherence_pct, 1),
            logged_at=datetime.now().isoformat()
        )
        
        # Append to file
        record_json = json.dumps(record.to_dict()) + '\n'
        if not atomic_append(self.adherence_file, record_json):
            logger.error("Failed to log adherence")
        
        logger.info(f"Logged adherence for {today}: {adherence_pct:.0f}% complete, energy {energy}/10")
        return record
    
    def _get_todays_planned_tasks(self) -> List[str]:
        """Get today's planned tasks from plan file."""
        # Default Tier-1 tasks
        tier1 = ['core', 'meditation_am', 'meditation_pm', 'breath']
        
        import os
        today = date.today().isoformat()
        plan_file = f"{self.data_dir}/plan_daily.jsonl"
        
        if os.path.exists(plan_file):
            with open(plan_file, 'r') as f:
                for line in f:
                    try:
                        plan = json.loads(line)
                        if plan.get('date') == today:
                            addons = plan.get('plan', {}).get('addons', [])
                            return tier1 + addons
                    except json.JSONDecodeError:
                        continue
        
        return tier1
    
    def get_adherence_stats(self, days: int = 7) -> Dict:
        """
        Get adherence statistics for the last N days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with adherence statistics
        """
        import os
        from datetime import timedelta
        
        if not os.path.exists(self.adherence_file):
            return {
                'avg_adherence_pct': 0,
                'avg_energy': 0,
                'days_logged': 0,
                'tier1_completion_pct': 0
            }
        
        # Load recent records
        cutoff_date = (date.today() - timedelta(days=days)).isoformat()
        records = []
        
        with open(self.adherence_file, 'r') as f:
            for line in f:
                try:
                    record = json.loads(line)
                    if record.get('date', '') >= cutoff_date:
                        records.append(record)
                except json.JSONDecodeError:
                    continue
        
        if not records:
            return {
                'avg_adherence_pct': 0,
                'avg_energy': 0,
                'days_logged': 0,
                'tier1_completion_pct': 0
            }
        
        # Calculate statistics
        total_adherence = sum(r.get('adherence_pct', 0) for r in records)
        energy_ratings = [r.get('energy_rating') for r in records if r.get('energy_rating')]
        
        # Tier-1 completion
        tier1_tasks = {'core', 'meditation_am', 'meditation_pm', 'breath'}
        tier1_completions = []
        for r in records:
            completed = set(r.get('completed_tasks', []))
            tier1_done = len(completed & tier1_tasks)
            tier1_completions.append(tier1_done / len(tier1_tasks) * 100)
        
        return {
            'avg_adherence_pct': round(total_adherence / len(records), 1) if records else 0,
            'avg_energy': round(sum(energy_ratings) / len(energy_ratings), 1) if energy_ratings else 0,
            'days_logged': len(records),
            'tier1_completion_pct': round(sum(tier1_completions) / len(tier1_completions), 1) if tier1_completions else 0,
            'total_days': days
        }
    
    def get_energy_trend(self, days: int = 14) -> List[Tuple[str, int]]:
        """
        Get energy rating trend over time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of (date, energy) tuples
        """
        import os
        from datetime import timedelta
        
        if not os.path.exists(self.adherence_file):
            return []
        
        cutoff_date = (date.today() - timedelta(days=days)).isoformat()
        energy_trend = []
        
        with open(self.adherence_file, 'r') as f:
            for line in f:
                try:
                    record = json.loads(line)
                    if record.get('date', '') >= cutoff_date:
                        if record.get('energy_rating'):
                            energy_trend.append((
                                record['date'],
                                record['energy_rating']
                            ))
                except json.JSONDecodeError:
                    continue
        
        return sorted(energy_trend)


def log_daily_adherence(completed_tasks: List[str], energy: int = None) -> Dict:
    """
    Convenience function to log daily adherence.
    
    Args:
        completed_tasks: List of completed task IDs
        energy: Energy rating (1-10)
        
    Returns:
        Logged adherence record as dict
    """
    tracker = AdherenceTracker()
    record = tracker.log_adherence(completed_tasks, energy)
    return record.to_dict()


if __name__ == "__main__":
    # CLI interface for testing
    import sys
    
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'log':
            # Log adherence: python adherence_tracker.py log core breath 7
            tasks = []
            energy = None
            
            for arg in sys.argv[2:]:
                if arg.isdigit():
                    energy = int(arg)
                else:
                    tasks.append(arg)
            
            record = log_daily_adherence(tasks, energy)
            print(f"✅ Logged: {record['completed_tasks']}")
            if energy:
                print(f"⚡ Energy: {energy}/10")
            print(f"📊 Adherence: {record['adherence_pct']}%")
            
        elif sys.argv[1] == 'stats':
            # Show stats: python adherence_tracker.py stats [days]
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            
            tracker = AdherenceTracker()
            stats = tracker.get_adherence_stats(days)
            
            print(f"\n📊 Adherence Stats ({days} days):")
            print(f"  Average adherence: {stats['avg_adherence_pct']}%")
            print(f"  Average energy: {stats['avg_energy']}/10")
            print(f"  Tier-1 completion: {stats['tier1_completion_pct']}%")
            print(f"  Days logged: {stats['days_logged']}/{stats['total_days']}")
            
        elif sys.argv[1] == 'trend':
            # Show energy trend: python adherence_tracker.py trend
            tracker = AdherenceTracker()
            trend = tracker.get_energy_trend(14)
            
            if trend:
                print("\n⚡ Energy Trend (14 days):")
                for date_str, energy in trend:
                    bar = '█' * energy + '░' * (10 - energy)
                    print(f"  {date_str}: [{bar}] {energy}/10")
            else:
                print("No energy data logged yet")
    else:
        print("Usage:")
        print("  Log: python adherence_tracker.py log <tasks...> [energy]")
        print("       Example: python adherence_tracker.py log core breath meditation_am 7")
        print("  Stats: python adherence_tracker.py stats [days]")
        print("  Trend: python adherence_tracker.py trend")