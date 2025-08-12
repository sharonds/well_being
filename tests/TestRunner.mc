// Unit tests for ScoreEngine and RecommendationMapper (Phase 1-3)
// These tests validate the examples from the PRD
using Toybox.System as Sys;

class TestRunner {
    public static function runAllTests() {
        var results = [];
        
        // Phase 1 & 2 existing tests (preserved for regression)
        results.add(testScoreEngineExampleA());
        results.add(testScoreEngineExampleC()); 
        results.add(testScoreEngineExampleBFull());
        results.add(testRedistributionPermutationMissingSleep());
        results.add(testScoreEngineBounds());
        results.add(testBackwardCompatibilityPhase1());
        
        // Recommendation mapper tests
        results.add(testRecommendationBands());
        results.add(testRecommendationEdgeCases());
        
        // Phase 3 new tests
        results.add(testHRVIntegration());
        results.add(testHRVWeightRedistribution());
        results.add(testEnhancedErrorHandling());
        results.add(testLogBufferFunctionality());
        results.add(testPerformanceRequirement());
        
        // Report results
        var passed = 0;
        var total = results.size();
        for (var i = 0; i < results.size(); i++) {
            if (results[i]) {
                passed++;
            }
        }
        
        Sys.println("Tests: " + passed + "/" + total + " passed");
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
        // Enable flags, disable HRV to match Phase 2 behavior
        ScoreEngine.ENABLE_SLEEP = true; 
        ScoreEngine.ENABLE_STRESS = true;
        ScoreEngine.ENABLE_HRV = false;
        var score = ScoreEngine.computeScorePhase2(12500, 48, 7, 35);
        var expected = 88;
        var passed = (score == expected);
        Sys.println("Example B: score=" + score + " expected=" + expected + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }

    // Redistribution permutation: Missing sleep only (stress disabled or null)
    public static function testRedistributionPermutationMissingSleep() {
        ScoreEngine.ENABLE_SLEEP = false; 
        ScoreEngine.ENABLE_STRESS = false;
        ScoreEngine.ENABLE_HRV = false;
        var scoreDyn = ScoreEngine.computeScorePhase2(8000, 55, null, null);
        var scoreP1 = ScoreEngine.computePhase1(8000, 55);
        var passed = (scoreDyn == scoreP1 && scoreDyn == 65);
        Sys.println("Redistrib missing sleep: dyn=" + scoreDyn + " phase1=" + scoreP1 + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }

    // Backward compatibility: When flags disabled, computeScore should match Phase1
    public static function testBackwardCompatibilityPhase1() {
        ScoreEngine.ENABLE_SLEEP = false; 
        ScoreEngine.ENABLE_STRESS = false;
        ScoreEngine.ENABLE_HRV = false;
        var scoreDyn = ScoreEngine.computeScorePhase2(3000, 70, 7, 35); // Extra metrics provided but flags off
        var scoreP1 = ScoreEngine.computePhase1(3000, 70);
        var passed = (scoreDyn == scoreP1 && scoreDyn == 25);
        Sys.println("Backward compat: dyn=" + scoreDyn + " phase1=" + scoreP1 + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }
    
    // Test bounds enforcement (0-100)
    public static function testScoreEngineBounds() {
        ScoreEngine.ENABLE_HRV = false; // Use Phase 1 weights
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
    
    // Phase 3: Test HRV integration with feature flag
    public static function testHRVIntegration() {
        // Test with HRV disabled (should ignore HRV value)
        ScoreEngine.ENABLE_SLEEP = false; 
        ScoreEngine.ENABLE_STRESS = false;
        ScoreEngine.ENABLE_HRV = false;
        var scoreNoHRV = ScoreEngine.computeScore(8000, 55, null, null, 50);
        var scorePhase1 = ScoreEngine.computePhase1(8000, 55);
        
        // Test with HRV enabled (should include HRV in calculation)
        ScoreEngine.ENABLE_HRV = true;
        var scoreWithHRV = ScoreEngine.computeScore(8000, 55, null, null, 50);
        
        var passed = (scoreNoHRV == scorePhase1 && scoreWithHRV != scoreNoHRV);
        Sys.println("HRV integration: noHRV=" + scoreNoHRV + " withHRV=" + scoreWithHRV + " phase1=" + scorePhase1 + " " + (passed ? "PASS" : "FAIL"));
        
        // Reset for other tests
        ScoreEngine.ENABLE_HRV = false;
        return passed;
    }
    
    // Phase 3: Test HRV weight redistribution
    public static function testHRVWeightRedistribution() {
        // Test weight redistribution with HRV enabled
        ScoreEngine.ENABLE_SLEEP = true; 
        ScoreEngine.ENABLE_STRESS = true;
        ScoreEngine.ENABLE_HRV = true;
        
        // All metrics present - should use HRV weights
        var weights = ScoreEngine.getBaseWeights();
        var weightsOk = (weights[:steps] == 0.35 && 
                        weights[:rhr] == 0.25 && 
                        weights[:sleep] == 0.15 && 
                        weights[:stress] == 0.10 && 
                        weights[:hrv] == 0.15);
        
        // Test actual computation with all metrics
        var score = ScoreEngine.computeScore(10000, 50, 7, 30, 60);
        var scoreOk = (score != null && score >= 0 && score <= 100);
        
        var passed = weightsOk && scoreOk;
        Sys.println("HRV weights: steps=" + weights[:steps] + " hrv=" + weights[:hrv] + " score=" + score + " " + (passed ? "PASS" : "FAIL"));
        
        // Reset for other tests
        ScoreEngine.ENABLE_SLEEP = false; 
        ScoreEngine.ENABLE_STRESS = false;
        ScoreEngine.ENABLE_HRV = false;
        return passed;
    }
    
    // Phase 3: Test enhanced error handling
    public static function testEnhancedErrorHandling() {
        // Test that fetchAllMetrics doesn't crash even with null returns
        // (simulated by our current stub implementation)
        var metrics = MetricProvider.fetchAllMetrics();
        var structureOk = (metrics.hasKey(:steps) && 
                          metrics.hasKey(:restingHR) && 
                          metrics.hasKey(:sleepHours) && 
                          metrics.hasKey(:stressLevel) && 
                          metrics.hasKey(:hrv) && 
                          metrics.hasKey(:errors));
        
        // Test that score computation handles null values gracefully
        var scoreWithNulls = ScoreEngine.computeScore(null, null, null, null, null);
        var nullsOk = (scoreWithNulls == null); // Should return null for insufficient data
        
        var passed = structureOk && nullsOk;
        Sys.println("Error handling: structure=" + structureOk + " nulls=" + nullsOk + " " + (passed ? "PASS" : "FAIL"));
        return passed;
    }
    
    // Phase 3: Test log buffer functionality
    public static function testLogBufferFunctionality() {
        // Clear buffer and test basic logging
        gLogBuffer.clear();
        gLogBuffer.log("Test message 1");
        gLogBuffer.log("Test message 2");
        
        var entries = gLogBuffer.getEntries();
        var basicOk = (entries.size() == 2);
        
        // Test buffer capacity (add more than 20 entries)
        for (var i = 3; i <= 25; i++) {
            gLogBuffer.log("Test message " + i);
        }
        
        var allEntries = gLogBuffer.getEntries();
        var capacityOk = (allEntries.size() == 20); // Should cap at 20
        
        // Test getLatest functionality
        var latest = gLogBuffer.getLatest(5);
        var latestOk = (latest.size() == 5);
        
        var passed = basicOk && capacityOk && latestOk;
        Sys.println("Log buffer: basic=" + basicOk + " capacity=" + capacityOk + " latest=" + latestOk + " " + (passed ? "PASS" : "FAIL"));
        
        gLogBuffer.clear(); // Clean up for other tests
        return passed;
    }
    
    // Phase 3: Test performance requirement (<50ms)
    public static function testPerformanceRequirement() {
        ScoreEngine.ENABLE_SLEEP = true; 
        ScoreEngine.ENABLE_STRESS = true;
        ScoreEngine.ENABLE_HRV = true;
        
        var startTime = Sys.getTimer();
        
        // Perform multiple score computations to get average timing
        for (var i = 0; i < 10; i++) {
            ScoreEngine.computeScore(10000, 50, 7, 30, 60);
        }
        
        var endTime = Sys.getTimer();
        var totalDuration = endTime - startTime;
        var avgDuration = totalDuration / 10; // microseconds
        var avgMs = avgDuration / 1000.0; // milliseconds
        
        var passed = (avgMs < 50.0); // Should be under 50ms per computation
        Sys.println("Performance: avg=" + avgMs + "ms target=<50ms " + (passed ? "PASS" : "FAIL"));
        
        // Reset for other tests
        ScoreEngine.ENABLE_SLEEP = false; 
        ScoreEngine.ENABLE_STRESS = false;
        ScoreEngine.ENABLE_HRV = false;
        return passed;
    }
}