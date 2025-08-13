"""
Centralized configuration for dashboard operational parameters.
Loads values from environment variables with sensible defaults.
"""

import os
from typing import Optional, Union


def get_env_value(key: str, default: Union[str, int, float], value_type: type = str) -> Union[str, int, float]:
    """Get environment variable with type conversion and default."""
    value = os.getenv(key)
    if value is None:
        return default
    
    if value_type == int:
        try:
            return int(value)
        except ValueError:
            return default
    elif value_type == float:
        try:
            return float(value)
        except ValueError:
            return default
    else:
        return value


# Phase 3 Operational Thresholds
class Config:
    """Centralized configuration for Phase 3 operational parameters."""
    
    # AC3: Integrity monitoring
    INTEGRITY_FAILURE_THRESHOLD_PCT = get_env_value('INTEGRITY_FAILURE_THRESHOLD_PCT', 1.0, float)
    INTEGRITY_ANALYSIS_DAYS = get_env_value('INTEGRITY_ANALYSIS_DAYS', 14, int)
    
    # AC7: Completeness monitoring  
    COMPLETENESS_DROP_THRESHOLD_PCT = get_env_value('COMPLETENESS_DROP_THRESHOLD_PCT', 20.0, float)
    COMPLETENESS_SHORT_WINDOW_DAYS = get_env_value('COMPLETENESS_SHORT_WINDOW_DAYS', 7, int)
    COMPLETENESS_LONG_WINDOW_DAYS = get_env_value('COMPLETENESS_LONG_WINDOW_DAYS', 30, int)
    
    # AC4: Battery safeguard
    BATTERY_MIN_PERCENT = get_env_value('BATTERY_MIN_PERCENT', 15, int)
    
    # AC1: Auto-run success rate
    AUTO_RUN_SUCCESS_TARGET_PCT = get_env_value('AUTO_RUN_SUCCESS_TARGET_PCT', 90.0, float)
    AUTO_RUN_ANALYSIS_DAYS = get_env_value('AUTO_RUN_ANALYSIS_DAYS', 14, int)
    
    # General operational
    MAX_ERROR_SAMPLES = get_env_value('MAX_ERROR_SAMPLES', 10, int)
    QUARANTINE_ENABLED = get_env_value('QUARANTINE_ENABLED', 'false').lower() in ('true', '1', 'yes')
    
    # Retention policy
    RETENTION_DAYS = get_env_value('RETENTION_DAYS', 30, int)
    RETENTION_TELEMETRY_DAYS = get_env_value('RETENTION_TELEMETRY_DAYS', 30, int)
    RETENTION_QUARANTINE_DAYS = get_env_value('RETENTION_QUARANTINE_DAYS', 7, int)
    
    @classmethod
    def print_config(cls):
        """Print current configuration for debugging."""
        print("📋 Phase 3 Configuration:")
        print(f"  Integrity failure threshold: {cls.INTEGRITY_FAILURE_THRESHOLD_PCT}%")
        print(f"  Integrity analysis window: {cls.INTEGRITY_ANALYSIS_DAYS} days")
        print(f"  Completeness drop threshold: {cls.COMPLETENESS_DROP_THRESHOLD_PCT}%")
        print(f"  Completeness windows: {cls.COMPLETENESS_SHORT_WINDOW_DAYS}d vs {cls.COMPLETENESS_LONG_WINDOW_DAYS}d")
        print(f"  Battery minimum: {cls.BATTERY_MIN_PERCENT}%")
        print(f"  Auto-run success target: {cls.AUTO_RUN_SUCCESS_TARGET_PCT}%")
        print(f"  Auto-run analysis window: {cls.AUTO_RUN_ANALYSIS_DAYS} days")
        print(f"  Quarantine enabled: {cls.QUARANTINE_ENABLED}")
        print(f"  Retention days: {cls.RETENTION_DAYS} (telemetry: {cls.RETENTION_TELEMETRY_DAYS}, quarantine: {cls.RETENTION_QUARANTINE_DAYS})")


# Backwards compatibility - export key values
INTEGRITY_FAILURE_THRESHOLD = Config.INTEGRITY_FAILURE_THRESHOLD_PCT
COMPLETENESS_DROP_THRESHOLD = Config.COMPLETENESS_DROP_THRESHOLD_PCT
BATTERY_MIN_PERCENT = Config.BATTERY_MIN_PERCENT


if __name__ == '__main__':
    Config.print_config()