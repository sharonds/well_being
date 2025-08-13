"""AC1: Auto-run tracking for telemetry."""
import os
from datetime import datetime
from typing import Dict

def add_auto_run_flag(record: Dict) -> Dict:
    """Add auto_run flag to telemetry record.
    
    AC1 Implementation:
    - 1 if running from cron/GitHub Actions
    - 0 if manual execution
    """
    # AC1: Detect automated execution context
    is_automated = bool(
        os.getenv('GITHUB_ACTIONS') or      # GitHub Actions
        os.getenv('CRON_JOB') or           # Cron job
        os.getenv('AUTOMATED_RUN') or      # Custom automation flag
        os.getenv('CI')                    # Generic CI environment
    )
    record['auto_run'] = 1 if is_automated else 0
    return record

def calculate_success_rate(records: list, days: int = 14) -> float:
    """Calculate auto-refresh success rate over N days.
    
    Returns percentage of days with successful auto-run.
    """
    # AC1: Calculate auto-refresh success rate
    if not records:
        return 0.0
    
    # Filter records to last N days if more than N
    if len(records) > days:
        records = records[-days:]
    
    # Count successful auto-runs
    auto_runs = sum(1 for r in records if r.get('auto_run') == 1)
    return (auto_runs / len(records)) * 100
