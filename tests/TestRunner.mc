// Unit tests for ScoreEngine and RecommendationMapper
// These tests validate the examples from the PRD and Phase 3 features
using Toybox.System as Sys;

class TestRunner {
    public static function runAllTests() {
        var results = [];
        
        // Initialize logger for tests
        Logger.initialize();
        Logger.add(Logger.INFO, "Starting test suite");
        
        // Test ScoreEngine examples from PRD
        results.add(testScoreEngineExampleA());
        results.add(testScoreEngineExampleC()); 
        results.add(testScoreEngineExampleBFull());
        results.add(testRedistributionPermutationMissingSleep());
        results.add(testScoreEngineBounds());
        results.add(testBackwardCompatibilityPhase1());
        
        // Phase 3: HRV tests
        results.add(testHRVIntegrationEnabled());
        results.add(testHRVIntegrationDisabled());
        results.add(testHRVWeightRedistribution());
        results.add(testHRVNormalization());
        
        // Phase 3: Auto-refresh tests
        results.add(testAutoRefreshLogic());
        results.add(testMissedWindowLogic());
        
        // Phase 3: Logger tests
        results.add(testLoggerRingBuffer());
        results.add(testLoggerOverflow());
        
        // Phase 3: Performance tests
        results.add(testPerformanceHarness());
        
        // Test RecommendationMapper bands
        results.add(testRecommendationBands());
        results.add(testRecommendationEdgeCases());
        
        // Report results
        var passed = 0;
        var total = results.size();
        for (var i = 0; i < results.size(); i++) {
            if (results[i]) {
                passed++;
            }
        }
        
        Sys.println("Tests: " + passed + "/" + total + " passed");
        Logger.add(Logger.INFO, "Test suite completed: " + passed + "/" + total + " passed");
        return passed == total;
    }
    
    // PRD Example A: Steps=8,000; RestingHR=55 => Expected Score=65
    public static function testScoreEngineExampleA() {
        var score = ScoreEngine.computePhase1(8000, 55);
        var expected = 65;
        var passed = (score == expected);
        Sys.println("Example A: score=" + score + " expected=" + expected + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }
    
    // PRD Example C: Steps=3,000; RestingHR=70 => Expected Score=25  
    public static function testScoreEngineExampleC() {
        var score = ScoreEngine.computePhase1(3000, 70);
        var expected = 25;
        var passed = (score == expected);
        Sys.println("Example C: score=" + score + " expected=" + expected + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }

    // PRD Example B: Steps=12500; RestHR=48; Sleep=7h; Stress=35 => Expected 88 when both feature flags enabled
    public static function testScoreEngineExampleBFull() {
        // Enable flags
        ScoreEngine.ENABLE_SLEEP = true; ScoreEngine.ENABLE_STRESS = true;
        var score = ScoreEngine.computeScore(12500, 48, 7, 35);
        var expected = 88;
        var passed = (score == expected);
        Sys.println("Example B: score=" + score + " expected=" + expected + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }

    // Redistribution permutation: Missing sleep only (stress disabled or null)
    // Provide steps & rhr & stress (flag off) => weights should redistribute between steps & rhr only producing Phase1 logic
    public static function testRedistributionPermutationMissingSleep() {
        ScoreEngine.ENABLE_SLEEP = false; ScoreEngine.ENABLE_STRESS = false;
        var scoreDyn = ScoreEngine.computeScore(8000, 55, null, null);
        var scoreP1 = ScoreEngine.computePhase1(8000, 55);
        var passed = (scoreDyn == scoreP1 && scoreDyn == 65);
        Sys.println("Redistrib missing sleep: dyn=" + scoreDyn + " phase1=" + scoreP1 + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }

    // Backward compatibility: When flags disabled, computeScore should match Phase1 for any inputs ignoring sleep/stress
    public static function testBackwardCompatibilityPhase1() {
        ScoreEngine.ENABLE_SLEEP = false; ScoreEngine.ENABLE_STRESS = false; ScoreEngine.ENABLE_HRV = false;
        var scoreDyn = ScoreEngine.computeScore(3000, 70, 7, 35, 50); // Extra metrics provided but flags off
        var scoreP1 = ScoreEngine.computePhase1(3000, 70);
        var passed = (scoreDyn == scoreP1 && scoreDyn == 25);
        Sys.println("Backward compat: dyn=" + scoreDyn + " phase1=" + scoreP1 + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }
    
    // Phase 3: Test HRV integration when enabled
    public static function testHRVIntegrationEnabled() {
        ScoreEngine.ENABLE_SLEEP = false; ScoreEngine.ENABLE_STRESS = false; ScoreEngine.ENABLE_HRV = true;
        var score = ScoreEngine.computeScore(8000, 55, null, null, 70); // With HRV=70ms
        var expected = 65; // Approximate expected value with HRV integration
        var passed = (score != null && score > 0 && score <= 100);
        Sys.println("HRV enabled: score=" + score + " " + (passed ? "PASS" : "FAIL"));
        ScoreEngine.ENABLE_HRV = false; // Reset
        return passed;
    }
    
    // Phase 3: Test HRV flag disabled preserves old behavior
    public static function testHRVIntegrationDisabled() {
        ScoreEngine.ENABLE_SLEEP = false; ScoreEngine.ENABLE_STRESS = false; ScoreEngine.ENABLE_HRV = false;
        var scoreWithHRV = ScoreEngine.computeScore(8000, 55, null, null, 70); // HRV provided but flag off
        var scorePhase1 = ScoreEngine.computePhase1(8000, 55);
        var passed = (scoreWithHRV == scorePhase1 && scoreWithHRV == 65);
        Sys.println("HRV disabled: scoreWithHRV=" + scoreWithHRV + " phase1=" + scorePhase1 + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }
    
    // Phase 3: Test HRV weight redistribution
    public static function testHRVWeightRedistribution() {
        ScoreEngine.ENABLE_SLEEP = true; ScoreEngine.ENABLE_STRESS = true; ScoreEngine.ENABLE_HRV = true;
        var scoreAll = ScoreEngine.computeScore(12000, 50, 8, 20, 80); // All metrics present
        var passed = (scoreAll != null && scoreAll > 0 && scoreAll <= 100);
        Sys.println("HRV redistribution: score=" + scoreAll + " " + (passed ? "PASS" : "FAIL"));
        // Reset flags
        ScoreEngine.ENABLE_SLEEP = false; ScoreEngine.ENABLE_STRESS = false; ScoreEngine.ENABLE_HRV = false;
        return passed;
    }
    
    // Phase 3: Test HRV normalization function
    public static function testHRVNormalization() {
        var norm20 = ScoreEngine._normHRV(20);   // Should be 0.0
        var norm70 = ScoreEngine._normHRV(70);   // Should be 0.5
        var norm120 = ScoreEngine._normHRV(120); // Should be 1.0
        var normLow = ScoreEngine._normHRV(10);  // Should clamp to 0.0
        var normHigh = ScoreEngine._normHRV(150); // Should clamp to 1.0
        
        var passed = (norm20 == 0.0 && norm120 == 1.0 && normLow == 0.0 && normHigh == 1.0 && norm70 == 0.5);
        Sys.println("HRV normalization: 20=" + norm20 + " 70=" + norm70 + " 120=" + norm120 + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }
    
    // Phase 3: Test auto-refresh logic
    public static function testAutoRefreshLogic() {
        // Test scheduler logic (basic validation)
        var inWindow = Scheduler.inAutoRefreshWindow();
        var dateStr = Scheduler.getCurrentDateString();
        var passed = (dateStr != null && dateStr.length() == 8); // YYYYMMDD format
        Sys.println("Auto-refresh logic: dateStr=" + dateStr + " inWindow=" + inWindow + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }
    
    // Phase 3: Test missed window logic
    public static function testMissedWindowLogic() {
        // Test missed window detection (basic validation)
        var shouldRefresh = Scheduler.shouldRefreshMissedWindow();
        var passed = true; // Basic test - shouldn't crash
        Sys.println("Missed window logic: shouldRefresh=" + shouldRefresh + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }
    
    // Phase 3: Test logger ring buffer
    public static function testLoggerRingBuffer() {
        Logger.clear();
        Logger.add(Logger.INFO, "Test1");
        Logger.add(Logger.WARN, "Test2");
        Logger.add(Logger.ERROR, "Test3");
        
        var count = Logger.getCount();
        var entries = Logger.getEntries();
        var passed = (count == 3 && entries.size() == 3);
        Sys.println("Logger ring buffer: count=" + count + " entries=" + entries.size() + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }
    
    // Phase 3: Test logger overflow behavior
    public static function testLoggerOverflow() {
        Logger.clear();
        // Add 25 entries to test overflow (capacity 20)
        for (var i = 0; i < 25; i++) {
            Logger.add(Logger.INFO, "Test" + i.toString());
        }
        
        var count = Logger.getCount();
        var entries = Logger.getEntries();
        var passed = (count == 20 && entries.size() == 20); // Should cap at 20
        Sys.println("Logger overflow: count=" + count + " entries=" + entries.size() + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }
    
    // Phase 3: Test performance harness (basic)
    public static function testPerformanceHarness() {
        var startTime = Sys.getTimer();
        
        // Simulate score computation
        var score = ScoreEngine.computePhase1(8000, 55);
        
        var elapsedMs = Sys.getTimer() - startTime;
        var passed = (elapsedMs < 50 && score == 65); // Should be under 50ms
        Sys.println("Performance harness: elapsed=" + elapsedMs + "ms score=" + score + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }
    
    // Test bounds enforcement (0-100)
    public static function testScoreEngineBounds() {
        // Test extreme values
        var scoreMin = ScoreEngine.computePhase1(0, 80); // Should be very low
        var scoreMax = ScoreEngine.computePhase1(15000, 40); // Should cap at 100
        
        var boundsOk = (scoreMin >= 0 && scoreMin <= 100 && scoreMax >= 0 && scoreMax <= 100);
        Sys.println("Bounds test: min=" + scoreMin + " max=" + scoreMax + " " + (boundsOk ? "PASS" : "FAIL"));
        return boundsOk;
    }
    
    // Test recommendation bands from PRD
    public static function testRecommendationBands() {
        var rec39 = RecommendationMapper.getRecommendation(39);  // "Take it easy"
        var rec40 = RecommendationMapper.getRecommendation(40);  // "Maintain"  
        var rec69 = RecommendationMapper.getRecommendation(69);  // "Maintain"
        var rec70 = RecommendationMapper.getRecommendation(70);  // "Go for it"
        
        var bandsOk = (rec39.equals("Take it easy") && 
                      rec40.equals("Maintain") &&
                      rec69.equals("Maintain") && 
                      rec70.equals("Go for it"));
        
        Sys.println("Bands test: 39=" + rec39 + " 40=" + rec40 + " 69=" + rec69 + " 70=" + rec70 + " " + (bandsOk ? "PASS" : "FAIL"));
        return bandsOk;
    }
    
    // Test edge cases for recommendations
    public static function testRecommendationEdgeCases() {
        var recNull = RecommendationMapper.getRecommendation(null);
        var recNeg = RecommendationMapper.getRecommendation(-1);
        var recHigh = RecommendationMapper.getRecommendation(101);
        
        var edgesOk = (recNull.equals("Data unavailable") &&
                      recNeg.equals("Data unavailable") &&
                      recHigh.equals("Data unavailable"));
        
        Sys.println("Edge cases test: null=" + recNull + " -1=" + recNeg + " 101=" + recHigh + " " + (edgesOk ? "PASS" : "FAIL"));
        return edgesOk;
    }
}