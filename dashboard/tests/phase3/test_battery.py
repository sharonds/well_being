"""Tests for AC4: Battery safeguard."""
import os
import sys
sys.path.insert(0, 'dashboard')

from scripts.phase3.battery_safeguard import should_skip_battery

def test_skip_when_battery_low():
    """Test skip when battery below threshold."""
    os.environ['BATTERY_LEVEL'] = '10'
    assert should_skip_battery(15) == True
    os.environ.pop('BATTERY_LEVEL')

def test_proceed_when_battery_sufficient():
    """Test proceed when battery above threshold."""
    os.environ['BATTERY_LEVEL'] = '50'
    assert should_skip_battery(15) == False
    os.environ.pop('BATTERY_LEVEL')

def test_proceed_when_battery_unknown():
    """Test proceed when battery level unknown."""
    os.environ.pop('BATTERY_LEVEL', None)
    assert should_skip_battery(15) == False
