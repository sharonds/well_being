using Toybox.System as Sys;

// Metric interface for Phase 1: Steps and Resting HR stubs
class MetricProvider {
    // Returns steps count for last 24h or null if unavailable
    public static function getSteps() {
        // Phase 1 stub: return test vector A value (8000 steps)
        // Future: integrate with Toybox.ActivityMonitor or similar
        return 8000;
    }
    
    // Returns resting heart rate in BPM or null if unavailable
    public static function getRestingHeartRate() {
        // Phase 1 stub: return test vector A value (55 BPM)
        // Future: integrate with Toybox.Health or similar
        return 55;
    }
    
    // Future Phase 2: sleep duration, stress, HRV
    public static function getSleepHours() {
        return null; // Not implemented in Phase 1
    }
    
    public static function getStressLevel() {
        return null; // Not implemented in Phase 1  
    }
}