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
            Logger.add(Logger.ERROR, "Error fetching steps: " + e.getErrorMessage());
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
            Logger.add(Logger.ERROR, "Error fetching resting HR: " + e.getErrorMessage());
            return null;
        }
    }
    
    // Future Phase 2: sleep duration, stress, HRV
    public static function getSleepHours() {
        // Phase 2 stub: return Example B sleep when feature flag later toggled
        try {
            return 7; // hours
        } catch (e) {
            Logger.add(Logger.ERROR, "Error fetching sleep: " + e.getErrorMessage());
            return null;
        }
    }
    
    public static function getStressLevel() {
        // Phase 2 stub: return Example B stress value
        try {
            return 35; // Garmin stress 0-100
        } catch (e) {
            Logger.add(Logger.ERROR, "Error fetching stress: " + e.getErrorMessage());
            return null;
        }
    }
    
    // Phase 3: HRV metric provider
    public static function getHRV() {
        // Phase 3 stub: return null by default (simulates absence)
        // Future: integrate with Toybox.Health HRV APIs when available
        try {
            // For testing, return stub HRV value when enabled
            if (ScoreEngine.ENABLE_HRV) {
                return 50; // ms (example value in 20-120 range)
            }
            return null;
        } catch (e) {
            Logger.add(Logger.ERROR, "Error fetching HRV: " + e.getErrorMessage());
            return null;
        }
    }
    
    // Utility to check if we have minimum required metrics for Phase 1
    public static function hasMinimumMetrics() {
        return (getSteps() != null && getRestingHeartRate() != null); // unchanged for backward compat
    }
}