// Unit tests for ScoreEngine and RecommendationMapper
// These tests validate the examples from the PRD
using Toybox.System as Sys;

class TestRunner {
    public static function runAllTests() {
        var results = [];
        
        // Test ScoreEngine examples from PRD
        results.add(testScoreEngineExampleA());
        results.add(testScoreEngineExampleC()); 
    results.add(testScoreEngineExampleBFull());
    results.add(testRedistributionPermutationMissingSleep());
        results.add(testScoreEngineBounds());
    results.add(testBackwardCompatibilityPhase1());
        
        // Test RecommendationMapper bands
        results.add(testRecommendationBands());
        results.add(testRecommendationEdgeCases());
    // Phase 3 tests
    results.add(testSchedulerAutoWindow());
    results.add(testSchedulerLateOpen());
    results.add(testHRVWeighting());
    results.add(testLoggerRingBuffer());
        
        // Report results
        var passed = 0;
        var total = results.size();
        for (var i = 0; i < results.size(); i++) {
            if (results[i]) {
                passed++;
            }
        }
        
        Sys.println("Core Tests: " + passed + "/" + total + " passed");
        return passed == total;
    }
    
    // AC10: Comprehensive test suite runner
    public static function runComprehensiveTestSuite() {
        Sys.println("=== Running Comprehensive Test Suite (AC10) ===");
        
        var coreResults = runAllTests();
        var infraResults = InfrastructureTests.runAllInfrastructureTests();
        var integrationResults = IntegrationTests.runAllIntegrationTests();
        
        var allPassed = coreResults && infraResults && integrationResults;
        
        Sys.println("=== Test Suite Summary ===");
        Sys.println("Core Tests: " + (coreResults ? "PASS" : "FAIL"));
        Sys.println("Infrastructure Tests: " + (infraResults ? "PASS" : "FAIL"));  
        Sys.println("Integration Tests: " + (integrationResults ? "PASS" : "FAIL"));
        Sys.println("Overall Result: " + (allPassed ? "✅ PASS" : "❌ FAIL"));
        
        return allPassed;
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
        ScoreEngine.ENABLE_SLEEP = false; ScoreEngine.ENABLE_STRESS = false;
        var scoreDyn = ScoreEngine.computeScore(3000, 70, 7, 35); // Extra metrics provided but flags off
        var scoreP1 = ScoreEngine.computePhase1(3000, 70);
        var passed = (scoreDyn == scoreP1 && scoreDyn == 25);
        Sys.println("Backward compat: dyn=" + scoreDyn + " phase1=" + scoreP1 + " " + (passed ? "PASS" : "FAIL"));
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

    // Auto-refresh should trigger within window when not already run.
    public static function testSchedulerAutoWindow() {
        var ok = Scheduler.shouldAuto("20250812", 7, null, null, false, 0, 400000);
        Sys.println("Scheduler auto window: " + (ok ? "PASS" : "FAIL"));
        return ok;
    }

    // Late open after 8: should compute if no score
    public static function testSchedulerLateOpen() {
        var late = Scheduler.shouldLateCompute("20250812", 9, null, false);
        Sys.println("Scheduler late open: " + (late ? "PASS" : "FAIL"));
        return late;
    }

    // HRV weighting & backward compat
    public static function testHRVWeighting() {
        // With HRV disabled, V3 should match Phase 2 computeScore
        ScoreEngine.ENABLE_SLEEP = true; ScoreEngine.ENABLE_STRESS = true; ScoreEngine.ENABLE_HRV = false;
        var noHrv = ScoreEngine.computeScoreV3(12500, 48, 7, 35, null);
        var phase2 = ScoreEngine.computeScore(12500, 48, 7, 35);
        var passNoHrv = (noHrv == phase2 && noHrv == 88);
        // Enable HRV with mid value (e.g., 70ms). Expect score different but within bounds.
        ScoreEngine.ENABLE_HRV = true;
        var withHrv = ScoreEngine.computeScoreV3(12500, 48, 7, 35, 70);
        var passBounds = (withHrv != null && withHrv >= 0 && withHrv <= 100);
        var passed = passNoHrv && passBounds;
        Sys.println("HRV weighting test: noHrv=" + noHrv + " withHrv=" + withHrv + " " + (passed?"PASS":"FAIL"));
        return passed;
    }

    // Logger ring buffer overwrite behavior
    public static function testLoggerRingBuffer() {
        // Add more than capacity
        for (var i=0;i<25;i++){ Logger.add("INFO", "msg" + i.toString()); }
        var list = Logger.list();
        var sizeOk = (list.size() == 20);
        // Oldest should be msg5 if capacity 20 (we added 0..24 -> last 20 are 5..24)
        var oldest = list[0][:msg];
        var expectedOldest = "msg5";
        var orderOk = (oldest.equals(expectedOldest));
        var passed = sizeOk && orderOk;
        Sys.println("Logger ring buffer: sizeOk="+sizeOk+" orderOk="+orderOk+" "+(passed?"PASS":"FAIL"));
        return passed;
    }
}