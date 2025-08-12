using Toybox.System as Sys;

class ScoreEngine {
    // Feature flags (Phase 2 & 3). When false, sleep/stress/hrv are ignored even if passed to compute functions.
    public static var ENABLE_SLEEP = false;
    public static var ENABLE_STRESS = false;
    public static var ENABLE_HRV = false; // Phase 3: HRV feature flag (default false)

    // Base weights as per PRD Section 7.2 
    // Phase 1-2 (no HRV): steps 0.40, restingHR 0.30, sleep 0.20, stress 0.10
    // Phase 3 (with HRV): steps 0.35, restingHR 0.25, sleep 0.20, stress 0.10, hrv 0.10
    public const BASE_W_STEPS_NO_HRV = 0.40;
    public const BASE_W_RHR_NO_HRV   = 0.30;
    public const BASE_W_SLEEP_NO_HRV = 0.20;
    public const BASE_W_STRESS_NO_HRV= 0.10;
    
    // Phase 3: HRV weights (when ENABLE_HRV is true)
    public const BASE_W_STEPS_HRV = 0.35;
    public const BASE_W_RHR_HRV   = 0.25;
    public const BASE_W_SLEEP_HRV = 0.20;
    public const BASE_W_STRESS_HRV= 0.10;
    public const BASE_W_HRV       = 0.10;
    
    // Current base weights (dynamic based on HRV flag)
    public static function BASE_W_STEPS() { return ENABLE_HRV ? BASE_W_STEPS_HRV : BASE_W_STEPS_NO_HRV; }
    public static function BASE_W_RHR() { return ENABLE_HRV ? BASE_W_RHR_HRV : BASE_W_RHR_NO_HRV; }
    public static function BASE_W_SLEEP() { return ENABLE_HRV ? BASE_W_SLEEP_HRV : BASE_W_SLEEP_NO_HRV; }
    public static function BASE_W_STRESS() { return ENABLE_HRV ? BASE_W_STRESS_HRV : BASE_W_STRESS_NO_HRV; }

    // Compute Phase 1 score (steps + resting HR only) using redistribution logic.
    // Preserved for backward compatibility tests.
    public static function computePhase1(steps, restingHR) {
        if (steps == null || restingHR == null) { return null; }
        try {
            var stepsNorm = _normSteps(steps);
            var rhrInvNorm = _invRestingHR(restingHR);
            var total = BASE_W_STEPS_NO_HRV + BASE_W_RHR_NO_HRV; // Always use Phase 1 weights for backward compatibility
            var wSteps = BASE_W_STEPS_NO_HRV / total; // ≈0.5714
            var wRhr = BASE_W_RHR_NO_HRV / total;     // ≈0.4286
            var raw = wSteps * stepsNorm + wRhr * rhrInvNorm;
            return _roundScore(raw);
        } catch(e) {
            Logger.add(Logger.ERROR, "Error computePhase1: " + e.getErrorMessage());
            return null;
        }
    }

    // Generic Phase 2+ score computation supporting optional sleep, stress, and HRV with weight redistribution.
    // If feature flags disable a metric or its value is null, it's excluded and remaining weights are renormalized.
    public static function computeScore(steps, restingHR, sleepHours, stressValue, hrvValue) {
        if (steps == null || restingHR == null) { // Minimum required metrics
            return null;
        }
        try {
            // Collect tuples: [isPresent, baseWeight, normalizedValue]
            var entries = [];
            // Steps (always considered if non-null)
            var stepsNorm = _normSteps(steps);
            entries.add({:present=>steps != null, :w=>BASE_W_STEPS(), :v=>stepsNorm});
            // Resting HR
            var rhrNorm = _invRestingHR(restingHR);
            entries.add({:present=>restingHR != null, :w=>BASE_W_RHR(), :v=>rhrNorm});
            // Sleep
            var sleepPresent = (ENABLE_SLEEP && sleepHours != null);
            var sleepNorm = _normSleep(sleepHours);
            entries.add({:present=>sleepPresent, :w=>BASE_W_SLEEP(), :v=>sleepNorm});
            // Stress
            var stressPresent = (ENABLE_STRESS && stressValue != null);
            var stressNorm = _invStress(stressValue);
            entries.add({:present=>stressPresent, :w=>BASE_W_STRESS(), :v=>stressNorm});
            // HRV (Phase 3)
            var hrvPresent = (ENABLE_HRV && hrvValue != null);
            var hrvNorm = _normHRV(hrvValue);
            entries.add({:present=>hrvPresent, :w=>BASE_W_HRV, :v=>hrvNorm});

            // Sum base weights of present metrics
            var sumW = 0.0;
            for (var i=0; i<entries.size(); i++) { if (entries[i][:present]) { sumW += entries[i][:w]; } }
            if (sumW <= 0) { return null; }

            var raw = 0.0;
            for (var j=0; j<entries.size(); j++) {
                var e = entries[j];
                if (e[:present]) {
                    var activeW = e[:w] / sumW;
                    raw += activeW * e[:v];
                }
            }
            return _roundScore(raw);
        } catch(e2) {
            Logger.add(Logger.ERROR, "Error computeScore: " + e2.getErrorMessage());
            return null;
        }
    }
    
    // Backward compatibility overload for Phase 2 calls (4 parameters)
    public static function computeScore(steps, restingHR, sleepHours, stressValue) {
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
    
    // Phase 3: HRV normalization (direct: higher HRV is better)
    // Assumes HRV range 20-120ms for readiness scaling
    public static function _normHRV(hrvMs) {
        if (hrvMs == null) return 0.0;
        // Clamp to expected range and normalize (20ms = 0.0, 120ms = 1.0)
        var clamped = (hrvMs < 20) ? 20 : ((hrvMs > 120) ? 120 : hrvMs);
        return (clamped - 20) / (120 - 20);
    }
}
