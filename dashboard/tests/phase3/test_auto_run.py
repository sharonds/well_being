"""Tests for AC1: Auto-run tracking."""
import os
import pytest
import sys
sys.path.insert(0, 'dashboard')

from scripts.phase3.auto_run_tracker import (
    add_auto_run_flag,
    calculate_success_rate
)

def test_auto_run_flag_manual():
    """Test auto_run is 0 for manual execution."""
    # Clear environment
    for key in ['GITHUB_ACTIONS', 'CRON_JOB', 'AUTOMATED_RUN']:
        os.environ.pop(key, None)
    
    record = {'date': '2025-08-14'}
    result = add_auto_run_flag(record)
    assert result['auto_run'] == 0

def test_auto_run_flag_automated():
    """Test auto_run is 1 for automated execution."""
    os.environ['GITHUB_ACTIONS'] = 'true'
    
    record = {'date': '2025-08-14'}
    result = add_auto_run_flag(record)
    assert result['auto_run'] == 1
    
    os.environ.pop('GITHUB_ACTIONS')

def test_success_rate_calculation():
    """Test success rate calculation."""
    records = [
        {'date': '2025-08-01', 'auto_run': 1},
        {'date': '2025-08-02', 'auto_run': 1},
        {'date': '2025-08-03', 'auto_run': 0},
        {'date': '2025-08-04', 'auto_run': 1},
    ]
    rate = calculate_success_rate(records)
    assert rate == 75.0
