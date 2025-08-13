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
    
    # Phase 5 - Plan Engine thresholds
    ENABLE_PLAN_ENGINE = get_env_value('ENABLE_PLAN_ENGINE', 'true').lower() in ('true', '1', 'yes')
    ANOMALY_RHR_THRESHOLD = get_env_value('ANOMALY_RHR_THRESHOLD', 7, int)
    ANOMALY_SLEEP_MIN = get_env_value('ANOMALY_SLEEP_MIN', 6.5, float)
    ANOMALY_STRESS_HIGH = get_env_value('ANOMALY_STRESS_HIGH', 80, int)
    SLEEP_VARIANCE_TARGET = get_env_value('SLEEP_VARIANCE_TARGET', 30, int)  # minutes
    SLEEP_VARIANCE_THRESHOLD = get_env_value('SLEEP_VARIANCE_THRESHOLD', 60, int)  # minutes
    
    # UI feature flags
    ENABLE_INSIGHT_CARD = get_env_value('ENABLE_INSIGHT_CARD', 'false').lower() in ('true', '1', 'yes')
    ENABLE_COACH_CHIP = get_env_value('ENABLE_COACH_CHIP', 'false').lower() in ('true', '1', 'yes')
    
    @classmethod
    def print_config(cls):
        """Print current configuration for debugging."""
        print("📋 Phase 3-5 Configuration:")
        print("\n  Phase 3 Ops:")
        print(f"    Integrity failure threshold: {cls.INTEGRITY_FAILURE_THRESHOLD_PCT}%")
        print(f"    Integrity analysis window: {cls.INTEGRITY_ANALYSIS_DAYS} days")
        print(f"    Completeness drop threshold: {cls.COMPLETENESS_DROP_THRESHOLD_PCT}%")
        print(f"    Completeness windows: {cls.COMPLETENESS_SHORT_WINDOW_DAYS}d vs {cls.COMPLETENESS_LONG_WINDOW_DAYS}d")
        print(f"    Battery minimum: {cls.BATTERY_MIN_PERCENT}%")
        print(f"    Auto-run success target: {cls.AUTO_RUN_SUCCESS_TARGET_PCT}%")
        print(f"    Auto-run analysis window: {cls.AUTO_RUN_ANALYSIS_DAYS} days")
        print(f"    Quarantine enabled: {cls.QUARANTINE_ENABLED}")
        print(f"    Retention days: {cls.RETENTION_DAYS} (telemetry: {cls.RETENTION_TELEMETRY_DAYS}, quarantine: {cls.RETENTION_QUARANTINE_DAYS})")
        print("\n  Phase 5 Plan Engine:")
        print(f"    Plan Engine enabled: {cls.ENABLE_PLAN_ENGINE}")
        print(f"    Anomaly RHR threshold: +{cls.ANOMALY_RHR_THRESHOLD} bpm")
        print(f"    Anomaly sleep minimum: {cls.ANOMALY_SLEEP_MIN} hours")
        print(f"    Anomaly stress high: {cls.ANOMALY_STRESS_HIGH}")
        print(f"    Sleep variance target: ±{cls.SLEEP_VARIANCE_TARGET} min")
        print(f"    Sleep variance threshold: {cls.SLEEP_VARIANCE_THRESHOLD} min")
        print(f"    UI: Insight card={cls.ENABLE_INSIGHT_CARD}, Coach chip={cls.ENABLE_COACH_CHIP}")


# Backwards compatibility - export key values
INTEGRITY_FAILURE_THRESHOLD = Config.INTEGRITY_FAILURE_THRESHOLD_PCT
COMPLETENESS_DROP_THRESHOLD = Config.COMPLETENESS_DROP_THRESHOLD_PCT
BATTERY_MIN_PERCENT = Config.BATTERY_MIN_PERCENT


if __name__ == '__main__':
    Config.print_config()