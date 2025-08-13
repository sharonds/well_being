"""AC4: Battery-aware safe mode."""
import logging
import os
import sys
from typing import Optional

# Add dashboard path for config import
dashboard_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, dashboard_path)
from config import Config

logger = logging.getLogger(__name__)

def get_battery_level() -> Optional[int]:
    """Get current battery level (platform-specific).
    
    Returns None if unable to determine.
    """
    # TODO: Implement platform-specific battery check
    # For testing, use environment variable
    import os
    if os.getenv('BATTERY_LEVEL'):
        return int(os.getenv('BATTERY_LEVEL'))
    return None

def should_skip_battery(threshold: Optional[int] = None) -> bool:
    """Determine if fetch should skip due to low battery.
    
    AC4: Skip if battery < threshold (from config).
    """
    if threshold is None:
        threshold = Config.BATTERY_MIN_PERCENT
        
    level = get_battery_level()
    if level is None:
        return False  # Can't determine, proceed
    
    if level < threshold:
        logger.info(f"SKIP_BATTERY: {level}% < {threshold}%")
        return True
    return False
