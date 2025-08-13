"""AC1: Auto-run tracking for telemetry."""
import os
import sys
from datetime import datetime
from typing import Dict, Optional

# Add dashboard path for config import
dashboard_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, dashboard_path)
from config import Config

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

def calculate_success_rate(records: list, days: Optional[int] = None) -> float:
    """Calculate auto-refresh success rate over N days.
    
    Returns percentage of distinct calendar days with successful auto-run.
    Normalized by unique dates to prevent record count inflation.
    """
    if days is None:
        days = Config.AUTO_RUN_ANALYSIS_DAYS
    # AC1: Calculate auto-refresh success rate
    if not records:
        return 0.0
    
    # Group records by date to count distinct days
    dates_with_auto_run = set()
    all_dates = set()
    
    for record in records:
        date_str = record.get('date', '')
        if date_str:
            all_dates.add(date_str)
            if record.get('auto_run') == 1:
                dates_with_auto_run.add(date_str)
    
    if not all_dates:
        return 0.0
    
    # Calculate percentage of distinct days with auto-run
    return (len(dates_with_auto_run) / len(all_dates)) * 100
