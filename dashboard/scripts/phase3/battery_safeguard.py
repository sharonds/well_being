"""AC4: Battery-aware safe mode."""
import logging
from typing import Optional

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

def should_skip_battery(threshold: int = 15) -> bool:
    """Determine if fetch should skip due to low battery.
    
    AC4: Skip if battery < threshold (default 15%).
    """
    level = get_battery_level()
    if level is None:
        return False  # Can't determine, proceed
    
    if level < threshold:
        logger.info(f"SKIP_BATTERY: {level}% < {threshold}%")
        return True
    return False
