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
    
    // Future Phase 2: sleep duration, stress, HRV
    public static function getSleepHours() {
        // Phase 2 stub: return Example B sleep when feature flag later toggled
        return 7; // hours
    }
    
    public static function getStressLevel() {
        // Phase 2 stub: return Example B stress value
        return 35; // Garmin stress 0-100
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