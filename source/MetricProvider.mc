using Toybox.System as Sys;
using Toybox.ActivityMonitor as AM;
using Toybox.UserProfile;

// Metric interface for Phase 1: Steps and Resting HR stubs
class MetricProvider {
    // Returns steps count for last 24h or null if unavailable
    public static function getSteps() {
        // Real ActivityMonitor integration (AC1)
        try {
            var info = AM.getInfo();
            return info != null ? info.steps : null;
        } catch (e) {
            Logger.add("ERROR", ErrorCodes.METRIC_STEPS + ": " + e.getErrorMessage());
            return null;
        }
    }
    
    // Returns resting heart rate in BPM or null if unavailable
    public static function getRestingHeartRate() {
        // Real UserProfile integration (AC1)
        try {
            var profile = UserProfile.getProfile();
            return profile != null ? profile.restingHeartRate : null;
        } catch (e) {
            Logger.add("ERROR", ErrorCodes.METRIC_RHR + ": " + e.getErrorMessage());
            return null;
        }
    }
    
    // Sleep duration from last night (hours) or null if unavailable
    public static function getSleepHours() {
        // Real sleep API integration (AC1)
        try {
            var info = AM.getInfo();
            if (info != null && info has :sleepTime && info.sleepTime != null) {
                // Convert milliseconds to hours
                return info.sleepTime / (1000 * 60 * 60);
            }
            return null; // Sleep data not available
        } catch (e) {
            Logger.add("ERROR", ErrorCodes.METRIC_SLEEP + ": " + e.getErrorMessage());
            return null;
        }
    }
    
    public static function getStressLevel() {
        // Real stress API integration (AC1) 
        try {
            // Note: Stress APIs vary by device - using best available method
            var info = AM.getInfo();
            if (info != null && info has :stress && info.stress != null) {
                return info.stress; // Current stress level 0-100
            }
            return null; // Stress data not available
        } catch (e) {
            Logger.add("ERROR", ErrorCodes.METRIC_STRESS + ": " + e.getErrorMessage());
            return null;
        }
    }

    // Phase 3 HRV stub (ms). Return null by default to simulate absence unless tests inject value.
    public static function getHRV() {
        return null; // Future: integrate with Health API providing rMSSD-like metric
    }
    
    // Utility to check if we have minimum required metrics for Phase 1
    public static function hasMinimumMetrics() {
        return (getSteps() != null && getRestingHeartRate() != null); // unchanged for backward compat
    }
}