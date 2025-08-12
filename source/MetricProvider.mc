using Toybox.System as Sys;

// Metric interface for Phase 1: Steps and Resting HR stubs
class MetricProvider {
    // Returns steps count for last 24h or null if unavailable
    public static function getSteps() {
        // Phase 1 stub: return test vector A value (8000 steps)
        // Future: integrate with Toybox.ActivityMonitor or similar
        try {
            return 8000;
        } catch (e) {
            Sys.println("Error fetching steps: " + e.getErrorMessage());
            return null;
        }
    }
    
    // Returns resting heart rate in BPM or null if unavailable
    public static function getRestingHeartRate() {
        // Phase 1 stub: return test vector A value (55 BPM)
        // Future: integrate with Toybox.Health or similar
        try {
            return 55;
        } catch (e) {
            Sys.println("Error fetching resting HR: " + e.getErrorMessage());
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