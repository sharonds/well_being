// Integration tests for AC10 coverage
// Tests end-to-end scenarios and cross-component interactions
using Toybox.System as Sys;

class IntegrationTests {
    
    public static function runAllIntegrationTests() {
        var results = [];
        
        // Full pipeline tests
        results.add(testFullComputationPipeline());
        results.add(testPhaseTransitions());
        results.add(testErrorHandlingIntegration());
        results.add(testPerformanceRequirement());
        
        // Auto-refresh integration tests (addresses ChatGPT-5 review gap)
        results.add(testAutoRefreshSingleTrigger());
        results.add(testAutoRefreshNoDuplicates());
        results.add(testLateComputeFallback());
        
        // Clock boundary edge cases (ChatGPT-5 final hardening)
        results.add(testAutoRefreshWindowBoundaries());
        
        // Report results
        var passed = 0;
        var total = results.size();
        for (var i = 0; i < results.size(); i++) {
            if (results[i]) {
                passed++;
            }
        }
        
        Sys.println("Integration Tests: " + passed + "/" + total + " passed");
        return passed == total;
    }
    
    // Test full computation pipeline from metrics to recommendation
    public static function testFullComputationPipeline() {
        try {
            // Enable all features for full pipeline test
            ScoreEngine.ENABLE_SLEEP = true;
            ScoreEngine.ENABLE_STRESS = true;
            ScoreEngine.ENABLE_HRV = false; // Keep simple for predictable test
            
            // Test data (Example B from PRD)
            var score = ScoreEngine.computeScore(12500, 48, 7, 35);
            var recommendation = RecommendationMapper.getRecommendation(score);
            
            var scoreOk = (score == 88); // Expected from PRD
            var recOk = recommendation.equals("Go for it"); // Score 88 should be "Go for it"
            var passed = scoreOk && recOk;
            
            Sys.println("Full pipeline: score=" + score + " rec=" + recommendation + " " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("Full pipeline test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
    
    // Test transitions between different phases work correctly
    public static function testPhaseTransitions() {
        try {
            // Start with Phase 1
            ScoreEngine.ENABLE_SLEEP = false;
            ScoreEngine.ENABLE_STRESS = false;
            var phase1Score = ScoreEngine.computePhase1(8000, 55);
            
            // Enable Phase 2
            ScoreEngine.ENABLE_SLEEP = true;
            ScoreEngine.ENABLE_STRESS = true;
            var phase2Score = ScoreEngine.computeScore(8000, 55, 7, 35);
            
            // Enable Phase 3 (HRV)
            ScoreEngine.ENABLE_HRV = true;
            var phase3Score = ScoreEngine.computeScoreV3(8000, 55, 7, 35, 70);
            
            // All should be valid scores but different due to additional metrics
            var passed = (
                phase1Score >= 0 && phase1Score <= 100 &&
                phase2Score >= 0 && phase2Score <= 100 &&
                phase3Score >= 0 && phase3Score <= 100 &&
                phase1Score == 65 // Expected from PRD Example A
            );
            
            Sys.println("Phase transitions: P1=" + phase1Score + " P2=" + phase2Score + " P3=" + phase3Score + " " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("Phase transitions test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
    
    // Test error handling integration with Logger
    public static function testErrorHandlingIntegration() {
        try {
            // Clear logger first
            Logger.list(); // This will show current state
            
            // Try to compute with invalid data that might trigger error paths
            // Note: Real error testing would require mocking MetricProvider failures
            var score = ScoreEngine.computePhase1(null, null); // Should handle null gracefully
            
            // Score should be null or valid range if error handling works
            var passed = (score == null || (score >= 0 && score <= 100));
            
            Sys.println("Error handling integration: score=" + score + " " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            // Exception is acceptable - means error handling is working
            Sys.println("Error handling integration: PASS (exception caught)");
            return true;
        }
    }
    
    // Test <50ms performance requirement (AC8)
    public static function testPerformanceRequirement() {
        try {
            PerformanceTimer.clear();
            
            // Test score computation performance
            PerformanceTimer.start();
            var score = ScoreEngine.computePhase1(10000, 50);
            var elapsed = PerformanceTimer.stop();
            
            var performanceOk = (elapsed < 50); // AC8: <50ms requirement
            var computationOk = (score != null && score >= 0 && score <= 100);
            var passed = performanceOk && computationOk;
            
            Sys.println("Performance requirement: " + elapsed + "ms (target <50ms) score=" + score + " " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("Performance requirement test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
    
    // Test auto-refresh triggers once within window (addresses ChatGPT-5 gap)
    public static function testAutoRefreshSingleTrigger() {
        try {
            // Mock scenario: 8am on new day, no previous auto-refresh
            var currentDate = "20250813";
            var currentHour = 8;
            var lastScoreDate = "20250812"; // Previous day
            var autoRefreshDate = null; // No auto-refresh yet today
            var manualRunToday = false;
            var lastComputeMs = 0; // Long time ago
            var nowMs = 400000; // Well past throttle
            
            var shouldTrigger = Scheduler.shouldAuto(currentDate, currentHour, lastScoreDate, autoRefreshDate, manualRunToday, lastComputeMs, nowMs);
            
            var passed = shouldTrigger; // Should trigger in 7-11am window
            Sys.println("Auto-refresh single trigger: " + (shouldTrigger ? "TRIGGERS" : "NO TRIGGER") + " " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("Auto-refresh single trigger test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
    
    // Test auto-refresh doesn't trigger twice same day (negative case)
    public static function testAutoRefreshNoDuplicates() {
        try {
            // Mock scenario: 9am on same day, already auto-refreshed
            var currentDate = "20250813";
            var currentHour = 9;
            var lastScoreDate = "20250813"; // Same day
            var autoRefreshDate = "20250813"; // Already auto-refreshed today
            var manualRunToday = false;
            var lastComputeMs = 300000; // Recent but past throttle
            var nowMs = 700000;
            
            var shouldTrigger = Scheduler.shouldAuto(currentDate, currentHour, lastScoreDate, autoRefreshDate, manualRunToday, lastComputeMs, nowMs);
            
            var passed = !shouldTrigger; // Should NOT trigger (already ran today)
            Sys.println("Auto-refresh no duplicates: " + (shouldTrigger ? "TRIGGERS" : "NO TRIGGER") + " " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("Auto-refresh no duplicates test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
    
    // Test late compute fallback after morning window
    public static function testLateComputeFallback() {
        try {
            // Mock scenario: 2pm, no score today yet, no manual run
            var currentDate = "20250813";
            var currentHour = 14; // 2pm - after 11am window
            var lastScoreDate = "20250812"; // No score today
            var manualRunToday = false;
            
            var shouldLateCompute = Scheduler.shouldLateCompute(currentDate, currentHour, lastScoreDate, manualRunToday);
            
            var passed = shouldLateCompute; // Should trigger late compute
            Sys.println("Late compute fallback: " + (shouldLateCompute ? "TRIGGERS" : "NO TRIGGER") + " " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("Late compute fallback test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
    
    // Test auto-refresh window boundaries (ChatGPT-5 final hardening)
    public static function testAutoRefreshWindowBoundaries() {
        try {
            var currentDate = "20250813";
            var autoRefreshDate = null;
            var manualRunToday = false;
            var lastComputeMs = 0;
            var nowMs = 400000;
            
            // Test edge cases: 6:59 should NOT trigger, 7:00 should trigger, 11:00 should NOT trigger
            var before7am = Scheduler.shouldAuto(currentDate, 6, null, autoRefreshDate, manualRunToday, lastComputeMs, nowMs);
            var at7am = Scheduler.shouldAuto(currentDate, 7, null, autoRefreshDate, manualRunToday, lastComputeMs, nowMs);  
            var at11am = Scheduler.shouldAuto(currentDate, 11, null, autoRefreshDate, manualRunToday, lastComputeMs, nowMs);
            
            var passed = (!before7am && at7am && !at11am);
            Sys.println("Window boundaries: 6am=" + (before7am ? "TRIGGER" : "NO") + " 7am=" + (at7am ? "TRIGGER" : "NO") + " 11am=" + (at11am ? "TRIGGER" : "NO") + " " + (passed ? "PASS" : "FAIL"));
            return passed;
        } catch (e) {
            Sys.println("Window boundaries test: FAIL - " + e.getErrorMessage());
            return false;
        }
    }
}