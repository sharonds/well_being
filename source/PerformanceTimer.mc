using Toybox.System as Sys;

// Performance timing utility for Phase 3
// Provides simple timing harness to ensure score computation < 50ms
class PerformanceTimer {
    
    // Measure execution time of score computation
    public static function measureScoreComputation(steps, restingHR, sleepHours, stressValue, hrvValue) {
        var results = {};
        
        try {
            // Test Phase 1 computation
            var startTime = Sys.getTimer();
            var scoreP1 = ScoreEngine.computePhase1(steps, restingHR);
            var phase1Time = Sys.getTimer() - startTime;
            
            // Test dynamic computation
            startTime = Sys.getTimer();
            var scoreDyn = ScoreEngine.computeScore(steps, restingHR, sleepHours, stressValue, hrvValue);
            var dynamicTime = Sys.getTimer() - startTime;
            
            // Test recommendation mapping
            startTime = Sys.getTimer();
            var rec = RecommendationMapper.getRecommendation(scoreP1);
            var recommendationTime = Sys.getTimer() - startTime;
            
            results[:phase1Time] = phase1Time;
            results[:dynamicTime] = dynamicTime;
            results[:recommendationTime] = recommendationTime;
            results[:totalTime] = phase1Time + dynamicTime + recommendationTime;
            results[:scoreP1] = scoreP1;
            results[:scoreDyn] = scoreDyn;
            results[:recommendation] = rec;
            results[:success] = true;
            
            Logger.add(Logger.INFO, "Performance: P1=" + phase1Time + "ms Dyn=" + dynamicTime + "ms Rec=" + recommendationTime + "ms");
            
        } catch(e) {
            Logger.add(Logger.ERROR, "Performance measurement failed: " + e.getErrorMessage());
            results[:success] = false;
            results[:error] = e.getErrorMessage();
        }
        
        return results;
    }
    
    // Run comprehensive performance test suite
    public static function runPerformanceTests() {
        Logger.add(Logger.INFO, "Starting performance test suite");
        
        var testCases = [
            // [steps, restingHR, sleep, stress, hrv, description]
            [8000, 55, null, null, null, "Example A (Phase 1)"],
            [12500, 48, 7, 35, null, "Example B (Phase 2)"],
            [3000, 70, null, null, null, "Example C (Phase 1)"],
            [12000, 45, 8, 20, 80, "All metrics (Phase 3)"]
        ];
        
        var allPassed = true;
        var maxTime = 0;
        
        for (var i = 0; i < testCases.size(); i++) {
            var testCase = testCases[i];
            var results = measureScoreComputation(testCase[0], testCase[1], testCase[2], testCase[3], testCase[4]);
            
            if (results[:success]) {
                var totalTime = results[:totalTime];
                if (totalTime > maxTime) {
                    maxTime = totalTime;
                }
                
                var passed = (totalTime < 50);
                if (!passed) {
                    allPassed = false;
                    Logger.add(Logger.WARN, "Performance FAIL: " + testCase[5] + " took " + totalTime + "ms");
                } else {
                    Logger.add(Logger.INFO, "Performance PASS: " + testCase[5] + " took " + totalTime + "ms");
                }
                
                Sys.println("Perf test " + (i+1) + ": " + testCase[5] + " - " + totalTime + "ms " + (passed ? "PASS" : "FAIL"));
            } else {
                allPassed = false;
                Logger.add(Logger.ERROR, "Performance test failed: " + testCase[5]);
                Sys.println("Perf test " + (i+1) + ": " + testCase[5] + " - ERROR");
            }
        }
        
        Sys.println("Performance summary: Max time " + maxTime + "ms, Target <50ms " + (allPassed ? "PASS" : "FAIL"));
        Logger.add(Logger.INFO, "Performance test suite completed. Max time: " + maxTime + "ms");
        
        return allPassed;
    }
    
    // Simple timing stub for environments without high-resolution timing
    public static function getTimingStub() {
        return {
            :available => false,
            :message => "High-resolution timing not available on this platform",
            :fallback => "Using Sys.getTimer() millisecond resolution"
        };
    }
}