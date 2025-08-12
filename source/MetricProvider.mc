using Toybox.System as Sys;

// Metric interface with enhanced error handling and HRV support (Phase 3)
class MetricProvider {
    // Returns steps count for last 24h or null if unavailable
    public static function getSteps() {
        try {
            // Phase 1 stub: return test vector A value (8000 steps)
            // Future: integrate with Toybox.ActivityMonitor or similar
            var steps = 8000;
            gLogBuffer.log("Steps fetched: " + steps);
            return steps;
        } catch (e) {
            var errorMsg = "Error fetching steps: " + e.getErrorMessage();
            Sys.println(errorMsg);
            gLogBuffer.log(errorMsg);
            return null;
        }
    }
    
    // Returns resting heart rate in BPM or null if unavailable
    public static function getRestingHeartRate() {
        try {
            // Phase 1 stub: return test vector A value (55 BPM)
            // Future: integrate with Toybox.Health or similar
            var rhr = 55;
            gLogBuffer.log("Resting HR fetched: " + rhr);
            return rhr;
        } catch (e) {
            var errorMsg = "Error fetching resting HR: " + e.getErrorMessage();
            Sys.println(errorMsg);
            gLogBuffer.log(errorMsg);
            return null;
        }
    }
    
    // Phase 2: Sleep duration with enhanced error handling
    public static function getSleepHours() {
        try {
            // Phase 2 stub: return Example B sleep when feature flag later toggled
            var sleep = 7; // hours
            gLogBuffer.log("Sleep hours fetched: " + sleep + "h");
            return sleep;
        } catch (e) {
            var errorMsg = "Error fetching sleep: " + e.getErrorMessage();
            Sys.println(errorMsg);
            gLogBuffer.log(errorMsg);
            return null;
        }
    }
    
    // Phase 2: Stress level with enhanced error handling
    public static function getStressLevel() {
        try {
            // Phase 2 stub: return Example B stress value
            var stress = 35; // Garmin stress 0-100
            gLogBuffer.log("Stress level fetched: " + stress);
            return stress;
        } catch (e) {
            var errorMsg = "Error fetching stress: " + e.getErrorMessage();
            Sys.println(errorMsg);
            gLogBuffer.log(errorMsg);
            return null;
        }
    }
    
    // Phase 3: HRV metric with enhanced error handling
    public static function getHRV() {
        try {
            // Phase 3 stub: return example HRV value for testing
            // Future: integrate with Toybox.Health HRV APIs if available
            var hrv = 45; // milliseconds, typical range 20-100
            gLogBuffer.log("HRV fetched: " + hrv + "ms");
            return hrv;
        } catch (e) {
            var errorMsg = "Error fetching HRV: " + e.getErrorMessage();
            Sys.println(errorMsg);
            gLogBuffer.log(errorMsg);
            return null;
        }
    }
    
    // Utility to check if we have minimum required metrics for Phase 1
    public static function hasMinimumMetrics() {
        return (getSteps() != null && getRestingHeartRate() != null); // unchanged for backward compat
    }
    
    // Phase 3: Batch metric fetch with comprehensive error handling
    public static function fetchAllMetrics() {
        gLogBuffer.log("Starting metric fetch batch");
        var startTime = Sys.getTimer();
        
        var metrics = {
            :steps => null,
            :restingHR => null,
            :sleepHours => null,
            :stressLevel => null,
            :hrv => null,
            :errors => []
        };
        
        // Fetch each metric independently - if one fails, others continue
        try {
            metrics[:steps] = getSteps();
        } catch (e) {
            metrics[:errors].add("steps: " + e.getErrorMessage());
        }
        
        try {
            metrics[:restingHR] = getRestingHeartRate();
        } catch (e) {
            metrics[:errors].add("restingHR: " + e.getErrorMessage());
        }
        
        try {
            metrics[:sleepHours] = getSleepHours();
        } catch (e) {
            metrics[:errors].add("sleep: " + e.getErrorMessage());
        }
        
        try {
            metrics[:stressLevel] = getStressLevel();
        } catch (e) {
            metrics[:errors].add("stress: " + e.getErrorMessage());
        }
        
        try {
            metrics[:hrv] = getHRV();
        } catch (e) {
            metrics[:errors].add("hrv: " + e.getErrorMessage());
        }
        
        var duration = Sys.getTimer() - startTime;
        gLogBuffer.log("Metric fetch completed in " + (duration/1000.0) + "ms");
        
        if (metrics[:errors].size() > 0) {
            gLogBuffer.log("Fetch errors: " + metrics[:errors].size());
        }
        
        return metrics;
    }
}