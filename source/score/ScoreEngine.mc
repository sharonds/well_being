using Toybox.System as Sys;

class ScoreEngine {
    // Compute Phase 1 score (steps + resting HR only) using redistribution logic.
    // Returns integer 0-100, or null if inputs are invalid.
    public static function computePhase1(steps, restingHR) {
        // Validate inputs
        if (steps == null || restingHR == null) {
            return null;
        }
        
        try {
            var stepsNorm = _normSteps(steps);
            var rhrInvNorm = _invRestingHR(restingHR);
            
            // Original weights (steps 0.40, rhr 0.30) -> normalize since only two metrics present
            var total = 0.40 + 0.30; // 0.70
            var wSteps = 0.40 / total; // ≈0.5714
            var wRhr = 0.30 / total; // ≈0.4286
            
            var raw = wSteps * stepsNorm + wRhr * rhrInvNorm;
            var score = (raw * 100 + 0.5).toNumber(); // Add 0.5 for proper rounding
            if (score > 100) score = 100; if (score < 0) score = 0;
            return score;
        } catch (e) {
            Sys.println("Error computing score: " + e.getErrorMessage());
            return null;
        }
    }

    // Normalization helpers
    public static function _normSteps(steps) { 
        if (steps == null) return 0.0;
        return (steps < 0 ? 0 : (steps > 12000 ? 12000 : steps)) / 12000.0; 
    }
    
    public static function _invRestingHR(rhr) {
        if (rhr == null) return 0.0;
        if (rhr < 40) rhr = 40; if (rhr > 80) rhr = 80;
        return (80 - rhr) / 40.0; // 0 (worst) to 1 (best)
    }
}
