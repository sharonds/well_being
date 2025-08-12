using Toybox.System as Sys;

class ScoreEngine {
    // Compute Phase 1 score (steps + resting HR only) using redistribution logic.
    // Returns integer 0-100.
    public static function computePhase1(steps, restingHR) {
        var stepsNorm = _normSteps(steps);
        var rhrInvNorm = _invRestingHR(restingHR);
        // Original weights (steps 0.40, rhr 0.30) -> normalize since only two metrics present
        var total = 0.40 + 0.30; // 0.70
        var wSteps = 0.40 / total; // ≈0.5714
        var wRhr = 0.30 / total; // ≈0.4286
        var raw = wSteps * stepsNorm + wRhr * rhrInvNorm;
        var score = (raw * 100).toNumber();
        if (score > 100) score = 100; if (score < 0) score = 0;
        // Round to nearest integer
        return Sys.toNumber(score.format("%0.0f"));
    }

    // Normalization helpers
    public static function _normSteps(steps) { return (steps < 0 ? 0 : (steps > 12000 ? 12000 : steps)) / 12000.0; }
    public static function _invRestingHR(rhr) {
        if (rhr < 40) rhr = 40; if (rhr > 80) rhr = 80;
        return (80 - rhr) / 40.0; // 0 (worst) to 1 (best)
    }
}
