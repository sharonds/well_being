using Toybox.System as Sys;

class ScoreEngine {
    // Feature flags (Phase 2 & 3). When false, metrics are ignored even if passed to computeDynamic.
    public static var ENABLE_SLEEP = false;
    public static var ENABLE_STRESS = false;
    public static var ENABLE_HRV = false; // Phase 3

    // Base weights as per PRD Section 7.2 with HRV support (Phase 3)
    // No HRV: steps 0.40, restingHR 0.30, sleep 0.20, stress 0.10
    // With HRV: steps 0.35, restingHR 0.25, sleep 0.15, stress 0.10, hrv 0.15
    public const BASE_W_STEPS_NO_HRV = 0.40;
    public const BASE_W_RHR_NO_HRV   = 0.30;
    public const BASE_W_SLEEP_NO_HRV = 0.20;
    public const BASE_W_STRESS_NO_HRV= 0.10;
    
    public const BASE_W_STEPS_WITH_HRV = 0.35;
    public const BASE_W_RHR_WITH_HRV   = 0.25;
    public const BASE_W_SLEEP_WITH_HRV = 0.15;
    public const BASE_W_STRESS_WITH_HRV= 0.10;
    public const BASE_W_HRV = 0.15;

    // Dynamic weight selection based on HRV enablement
    public static function getBaseWeights() {
        if (ENABLE_HRV) {
            return {
                :steps => BASE_W_STEPS_WITH_HRV,
                :rhr => BASE_W_RHR_WITH_HRV,
                :sleep => BASE_W_SLEEP_WITH_HRV,
                :stress => BASE_W_STRESS_WITH_HRV,
                :hrv => BASE_W_HRV
            };
        } else {
            return {
                :steps => BASE_W_STEPS_NO_HRV,
                :rhr => BASE_W_RHR_NO_HRV,
                :sleep => BASE_W_SLEEP_NO_HRV,
                :stress => BASE_W_STRESS_NO_HRV,
                :hrv => 0.0
            };
        }
    }

    // Compute Phase 1 score (steps + resting HR only) using redistribution logic.
    // Preserved for backward compatibility tests.
    public static function computePhase1(steps, restingHR) {
        if (steps == null || restingHR == null) { return null; }
        try {
            var stepsNorm = _normSteps(steps);
            var rhrInvNorm = _invRestingHR(restingHR);
            var weights = getBaseWeights();
            var total = weights[:steps] + weights[:rhr]; 
            var wSteps = weights[:steps] / total; 
            var wRhr = weights[:rhr] / total;     
            var raw = wSteps * stepsNorm + wRhr * rhrInvNorm;
            return _roundScore(raw);
        } catch(e) {
            Sys.println("Error computePhase1: " + e.getErrorMessage());
            gLogBuffer.log("Error computePhase1: " + e.getErrorMessage());
            return null;
        }
    }

    // Generic Phase 2+ score computation supporting optional sleep, stress & HRV with weight redistribution.
    // If feature flags disable a metric or its value is null, it's excluded and remaining weights are renormalized.
    public static function computeScore(steps, restingHR, sleepHours, stressValue, hrvValue) {
        if (steps == null || restingHR == null) { // Minimum required metrics
            return null;
        }
        try {
            var startTime = Sys.getTimer();
            var weights = getBaseWeights();
            
            // Collect tuples: [isPresent, baseWeight, normalizedValue]
            var entries = [];
            
            // Steps (always considered if non-null)
            var stepsNorm = _normSteps(steps);
            entries.add({:present=>steps != null, :w=>weights[:steps], :v=>stepsNorm});
            
            // Resting HR
            var rhrNorm = _invRestingHR(restingHR);
            entries.add({:present=>restingHR != null, :w=>weights[:rhr], :v=>rhrNorm});
            
            // Sleep
            var sleepPresent = (ENABLE_SLEEP && sleepHours != null);
            var sleepNorm = _normSleep(sleepHours);
            entries.add({:present=>sleepPresent, :w=>weights[:sleep], :v=>sleepNorm});
            
            // Stress
            var stressPresent = (ENABLE_STRESS && stressValue != null);
            var stressNorm = _invStress(stressValue);
            entries.add({:present=>stressPresent, :w=>weights[:stress], :v=>stressNorm});
            
            // HRV (Phase 3)
            var hrvPresent = (ENABLE_HRV && hrvValue != null);
            var hrvNorm = _normHRV(hrvValue);
            entries.add({:present=>hrvPresent, :w=>weights[:hrv], :v=>hrvNorm});

            // Sum base weights of present metrics
            var sumW = 0.0;
            for (var i=0; i<entries.size(); i++) { 
                if (entries[i][:present]) { 
                    sumW += entries[i][:w]; 
                } 
            }
            if (sumW <= 0) { return null; }

            var raw = 0.0;
            for (var j=0; j<entries.size(); j++) {
                var e = entries[j];
                if (e[:present]) {
                    var activeW = e[:w] / sumW;
                    raw += activeW * e[:v];
                }
            }
            
            var duration = Sys.getTimer() - startTime;
            gLogBuffer.log("Score computation took " + (duration/1000.0) + "ms");
            
            return _roundScore(raw);
        } catch(e2) {
            var errorMsg = "Error computeScore: " + e2.getErrorMessage();
            Sys.println(errorMsg);
            gLogBuffer.log(errorMsg);
            return null;
        }
    }

    // Convenience method that matches Phase 2 signature (without HRV)
    public static function computeScorePhase2(steps, restingHR, sleepHours, stressValue) {
        return computeScore(steps, restingHR, sleepHours, stressValue, null);
    }

    // Internal rounding helper (floor(x+0.5) equivalent via add 0.5 then toNumber)
    private static function _roundScore(raw) {
        var score = (raw * 100 + 0.5).toNumber();
        if (score > 100) score = 100; if (score < 0) score = 0;
        return score;
    }

    // Normalization helpers
    public static function _normSteps(steps) {
        if (steps == null) return 0.0;
        return (steps < 0 ? 0 : (steps > 12000 ? 12000 : steps)) / 12000.0;
    }

    public static function _invRestingHR(rhr) {
        if (rhr == null) return 0.0;
        if (rhr < 40) rhr = 40; if (rhr > 80) rhr = 80;
        return (80 - rhr) / 40.0;
    }

    public static function _normSleep(sleepHrs) {
        if (sleepHrs == null) return 0.0;
        if (sleepHrs < 0) sleepHrs = 0; if (sleepHrs > 8) sleepHrs = 8;
        return sleepHrs / 8.0;
    }

    public static function _invStress(stress) {
        if (stress == null) return 0.0;
        if (stress < 0) stress = 0; if (stress > 100) stress = 100;
        return 1 - (stress / 100.0);
    }
    
    // Phase 3: HRV normalization (40-120ms range per PRD)
    public static function _normHRV(hrv) {
        if (hrv == null) return 0.0;
        if (hrv < 40) hrv = 40; if (hrv > 120) hrv = 120;
        return (hrv - 40) / 80.0;
    }
}
